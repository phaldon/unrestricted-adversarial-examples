# Unrestricted Adversarial Examples Challenge

In the Unrestricted Adversarial Examples Challenge, attackers submit arbitrary adversarial inputs, and defenders are expected to assign low confidence to difficult inputs while retaining high confidence and accuracy on a clean, unambiguous test set.

You can learn more about the motivation and structure of the contest in our recent paper:

**Unrestricted Adversarial Examples**<br>
*Tom B. Brown, Nicholas Carlini, Chiyuan Zhang, Catherine Olsson, Paul Christiano and Ian Goodfellow*<br>
[Arxiv paper preprint](https://drive.google.com/open?id=1T0yiu9LPv_Qh-qYhYFLj9dxjnkca8fkG)

This repository contains code for the warm-up to the challenge, as well as [the public proposal for the contest](contest_proposal.md).

![image](https://user-images.githubusercontent.com/306655/44686400-f0b74800-aa02-11e8-8967-fa354244813f.png)


## The warm-up to the contest
### <a name="leaderboard"></a>Leaderboard
We include three attacks in the warm-up phase of the challenge:

- 1000 Linfinity-ball adversarial examples generated by SPSA
- 1000 spatial adversarial examples (via grid search)
- 100 L2-ball adversarial examples generated by a decision-only attack

The top five distinct models for each dataset are shown below. You can see all submissions in [the full scoreboard](scoreboard.md). 

##### Two-Class MNIST
| Defense               | Submitted by  | Spatial grid acc.<br>at 80% cov. | SPSA L-infty acc.<br>at 80% cov. | L2-ball acc.<br>at 80% cov. |  Submission Date |
| --------------------- | ------------- | ------------ |--------------- |--------------- | --------------- |
| [MadryPGD LeNet Baseline](#)  |  ?? |    **??**    |     **??**   |     **??**     |  Aug 28th, 2018 |
| [Undefended LeNet Baseline](#)   |  Google Brain   |    0.0%    |     0.0%    |     0.0%     |  Aug 27th, 2018 |

##### Bird or Bicycle
| Defense               | Submitted by  | Spatial grid acc.<br>at 80% cov. | SPSA L-infty acc.<br>at 80% cov. | L2-ball acc.<br>at 80% cov. |  Submission Date |
| --------------------- | ------------- | ------------ |--------------- |--------------- | --------------- |
| [Pytorch ResNet trained on bird-or-bicycle extras](unrestricted_advex/undefended_pytorch_resnet)  |  ?? |    **??**    |     **??**   |     **??**     |  Aug 28th, 2018 |
| [Keras ResNet trained on ImageNet](unrestricted_advex/undefended_keras_resnet)   |  Google Brain   |    0.0%    |     0.0%    |     0.0%     |  Aug 27th, 2018 |


### Submitting a defense for the warm-up

The [warm-up before the contest](warmup.md) is currently underway and is accepting submissions. If you have additional questions, feel free to [submit a new GitHub issue](https://github.com/google/unrestricted-adversarial-examples/issues/new) with the "question" tag and we will respond shortly.

## The contest

The contest phase will begin after the warm-up attacks have been conclusively solved. We have published the [contest proposal](https://github.com/google/unrestricted-adversarial-examples/blob/master/contest_proposal.md) and are soliciting feedback from the community.

## Running tests

```bash
pytest
```

## Authors
