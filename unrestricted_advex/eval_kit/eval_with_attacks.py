"""Evaluate a model with attacks."""
import os

import numpy as np
import tcu_images
import tensorflow as tf
import torch
import torchvision
from cleverhans.attacks import SPSA
from cleverhans.model import Model
from six.moves import xrange
from tensorflow.keras.applications.resnet50 import preprocess_input

from tcu_images import CLASS_NAME_TO_IMAGENET_CLASS


class CleverhansModelWrapper(Model):
  def __init__(self, model_fn):
    """
    Wrap a callable function that takes a numpy array of shape (N, C, H, W),
    and outputs a numpy vector of length N, with each element in range [0, 1].
    """
    self.nb_classes = 2
    self.model_fn = model_fn

  def fprop(self, x, **kwargs):
    logits_op = tf.py_func(self.model_fn, [x], tf.float32)
    return {'logits': logits_op}


def spsa_attack(model, batch_nchw, labels, epsilon=(16. / 255)): # (4. / 255)):
  with tf.Graph().as_default():
    # Prepare graph
    x_input = tf.placeholder(tf.float32, shape=(1,) + batch_nchw.shape[1:])
    y_label = tf.placeholder(tf.int32, shape=(1,))

    cleverhans_model = CleverhansModelWrapper(model)
    attack = SPSA(cleverhans_model)

    x_adv = attack.generate(
      x_input,
      y=y_label,
      epsilon=epsilon,
      num_steps=200,
      early_stop_loss_threshold=-1.,
      spsa_samples=32,
      is_debug=True)

    # Run computation
    all_x_adv_np = []
    with tf.Session() as sess:
      for i in xrange(len(batch_nchw)):
        x_adv_np = sess.run(x_adv, feed_dict={
          x_input: np.expand_dims(batch_nchw[i], axis=0),
          y_label: np.expand_dims(labels[i], axis=0),
        })
        all_x_adv_np.append(x_adv_np)
    return np.concatenate(all_x_adv_np)


def null_attack(model, x_np, y_np):
  del model, y_np  # unused
  return x_np


def run_attack(model, data_iter, attack_fn, max_num_batches=1, save_image_dir=None):
  """
  :param model: Model should output a
  :param data_iter:
  :param attack:
  :param max_num_batches:
  :return: (logits, labels)
  """
  all_labels = []
  all_logits = []
  for i_batch, (x_np, y_np) in enumerate(data_iter):
    if max_num_batches > 0 and i_batch >= max_num_batches:
      break

    x_adv = attack_fn(model, x_np, y_np)
    logits = model(x_adv)
    all_labels.append(y_np)
    all_logits.append(logits)

  if save_image_dir:
    for i, image_np in enumerate(x_adv):
      save_image_to_png(image_np, os.path.join(save_image_dir, "adv_image_%s.png" % i))

  return np.concatenate(all_logits), np.concatenate(all_labels)


def save_image_to_png(image_np, filename):
  from PIL import Image
  os.makedirs(os.path.dirname(filename), exist_ok=True)
  img = Image.fromarray(np.uint8(np.einsum('chw->hwc', image_np) * 255.), 'RGB')
  img.save(filename)


def get_torch_tcu_dataset_iter(batch_size):
  data_dir = tcu_images.get_dataset('train')

  train_dataset = torchvision.datasets.ImageFolder(
    data_dir,
    torchvision.transforms.Compose([
      torchvision.transforms.Resize(224),
      torchvision.transforms.ToTensor(),
    ]))

  data_loader = torch.utils.data.DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True)

  assert train_dataset.class_to_idx['bicycle'] == 0
  assert train_dataset.class_to_idx['bird'] == 1

  dataset_iter = [(x.numpy(), y.numpy()) for (x, y) in iter(data_loader)]
  return dataset_iter


def get_torch_tcu_model():
  pytorch_model = torchvision.models.resnet50(pretrained=True)
  pytorch_model = pytorch_model.cuda()
  pytorch_model.eval()  # switch to eval mode

  def model_fn(x_np):
    with torch.no_grad():
      x = torch.from_numpy(x_np).cuda()
      logits1000 = pytorch_model(x)

      bird_max_logit, _ = torch.max(
        logits1000[:, CLASS_NAME_TO_IMAGENET_CLASS['bird']], dim=1)
      bicycle_max_logit, _ = torch.max(
        logits1000[:, CLASS_NAME_TO_IMAGENET_CLASS['bicycle']], dim=1)
      logits = torch.cat((bicycle_max_logit[:, None],
                          bird_max_logit[:, None]), dim=1)
      return logits.cpu().numpy()

  return model_fn


def get_keras_tcu_model():
  tf.keras.backend.set_image_data_format('channels_first')

  k_model = tf.keras.applications.resnet50.ResNet50(
    include_top=True, weights='imagenet', input_tensor=None,
    input_shape=None, pooling=None, classes=1000)

  def model_wrapper(x_np):
    # it seems keras pre-trained model directly output softmax-ed probs
    x_np = preprocess_input(x_np * 255)
    prob1000 = k_model.predict_on_batch(x_np) / 10
    fake_logits1000 = np.log(prob1000)

    bird_max_logit = np.max(
      fake_logits1000[:, CLASS_NAME_TO_IMAGENET_CLASS['bird']], axis=1)
    bicycle_max_logit = np.max(
      fake_logits1000[:, CLASS_NAME_TO_IMAGENET_CLASS['bicycle']], axis=1)
    logits = np.concatenate((bicycle_max_logit[:, None],
                             bird_max_logit[:, None]), axis=1)
    return logits

  return model_wrapper


def evaluate_model(model_fn, dataset_iter):
  for (attack_fn, save_name) in [(null_attack, 'null_attack'),
                                 (spsa_attack, 'spsa_attack')]:
    logits, labels = run_attack(
      model_fn, dataset_iter, attack_fn, max_num_batches=1,
      save_image_dir=os.path.join('/tmp/eval_with_attacks', save_name))
    preds = (logits[:, 0] < logits[:, 1]).astype(np.int64)
    correct = np.equal(preds, labels).astype(np.float32)
    correct_fracs = np.sum(correct, axis=0) / len(labels)
    print(correct_fracs)


def main():
  tcu_dataset_iter = get_torch_tcu_dataset_iter(batch_size=4)
  model_fn = get_keras_tcu_model()
  evaluate_model(model_fn, tcu_dataset_iter)


if __name__ == '__main__':
  main()
