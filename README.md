# Analyzing Gender Bias in Multilingual Machine Translation

This project contains the code to conduct experiments for exploring gender bias in multilingual MT in the context of _gender preservation_.
It supports comparing pivot-based and zero-shot translation to study the influence of the bridge language—the language participating in all language pairs during training—and the effect of language-agnostic hidden representations on models’ ability to preserve the feminine and masculine gender equally well in their outputs.
The project contains resources to evaluate three different model modifications that encourage language-agnostic representations: 
- removing a residual connection in a middle Transformer encoder to lift positional correspondences to the input tokens; 
- promoting similar source and target language representations through an auxiliary loss; and 
- joint adversarial training penalizing successful recovery of source language signals from the representations;

and to probe models' hidden representations for gender signals (using a token- or sentence-level gender classifier).

## Software

First off: This repository is based on [NMTGMinor](https://github.com/quanpn90/NMTGMinor). 
Please see [here](https://github.com/quanpn90/NMTGMinor) for its main contributors.

Create virtual environment from [environment.yml](../../environment.yml) by:

```
conda env create -f environment.yml
```

Clone this repo and switch to the branch `dev`.
```
git clone https://github.com/nlp-dke/NMTGMinor.git
git checkout dev
```

### Dependency/Requirements
For training:
* Python version >= 3.7 (most recommended)
* [PyTorch](https://pytorch.org/) >= 1.0.1
* [apex](https://github.com/nvidia/apex) when using half- or mixed-precision training 
  
For preprocessing:
* [subword-nmt](https://github.com/rsennrich/subword-nmt)
* [sentencepiece](https://github.com/google/sentencepiece)
* [Moses](https://github.com/moses-smt/mosesdecoder) for tokenization of languages in Latin script

For evaluation:
* [sacreBLEU](https://github.com/mjpost/sacrebleu)


### Preprocessing
First source the config file:
```
source ./recipes/zero-shot/config.sh
```
Preprocess and binarize the datasets:
```
# mustc
bash ./recipes/zero-shot/mustc/prepro.mustc.sh
bash ./recipes/zero-shot/mustc/binarize.mustc.sh

# mustshe
bash ./recipes/zero-shot/mustshe/prepare.mustshe.sh
bash ./recipes/zero-shot/mustshe/prepro.mustshe.sh
bash ./recipes/zero-shot/mustc/binarize.mustshe.sh

# gender classifier (mustshe)
bash ./recipes/zero-shot/mustshe/create.classifier.training.data.sh
bash ./recipes/zero-shot/mustshe/prepro.mustshe.classifier.sh
bash ./recipes/zero-shot/mustshe/binarize.gender.mustshe.sh
```

### Training

#### Baseline 
To train the baseline:
```
bash ./recipes/zero-shot/mustc/train.sh
```

#### Removed Residual Connection
To train the baseline with residual removed in the middle encoder layer:
```
bash ./recipes/zero-shot/mustc/train.remove.residual.sh
```

#### Similarity Regularizer
To train the baseline (with or without residual removed in the middle encoder layer) with auxiliary similarity loss, resume training:
```
bash ./recipes/zero-shot/mustc/train.similarity.baseline.mustc.sh
bash ./recipes/zero-shot/mustc/train.similarity.remove.residual.mustc.sh
```
Note: Set 
```-load_from``` for resuming of training; should point to the trained model (e.g., the averaged model ```model.pt```)

#### Adversarial Language Classifier
To train the baseline (with or without residual removed in the middle encoder layer) with auxiliary similarity loss, resume training:
```
bash ./recipes/zero-shot/mustc/train.adversarial.baseline.mustc.sh
bash ./recipes/zero-shot/mustc/train.adversarial.remove.residual.mustc.sh
```
Note: Set 
```-load_from``` for resuming of training; should point to the trained model (e.g., the averaged model ```model.pt```)

#### Gender Classifier
To train the sentence-level or token-level classifier: 
```
bash ./recipes/zero-shot/mustshe/train.gender.baseline.mustshe.sh
bash ./recipes/zero-shot/mustshe/train.gender.remove.residual.mustshe.sh
```
Note: Set 
```-load_from``` for resuming of training; should point to the trained model (e.g., the averaged model ```model.pt```)


### Test
```
# zero-shot
bash ./recipes/zero-shot/mustshe/pred.mustshe.sh $MODEL_NAME 
# pivot
bash ./recipes/zero-shot/mustshe/pred.pivot.mustshe.sh $MODEL_NAME 
```
`$MODEL_NAME` is directory name containing the trained model (`model.pt`).

Summary of the results (incl. BLEU and accuracy): 
```
bash ./utils/summarize_results.sh
```


## Data

Our experiments are run on two datasets: MuST-C, MuST-SHE.

- MuST-C (release v1.2): [download](https://ict.fbk.eu/must-c/), [paper](https://aclanthology.org/N19-1202.pdf) 
- MuST-SHE (release v1.2): [download](https://ict.fbk.eu/must-she/), [paper](https://arxiv.org/abs/2104.06001)

To download MuST-C with command line one could use: 
```
 bash ./recipes/zero-shot/mustc/download.mustc.sh 
 ```

**Please note: The target files start with language tags, since we do not specifically add BOS tokens again. If your implementation automatically append language/BOS tags to target sentences, please make sure to remove the tags in the target files.**

### Dataset Description

#### MuST-C

We formed three training corpora that are subsets of MuST-C with language pairs en-X (125K-267K sentences per direction), de-X (103K-223K), and es-X (102K-258K). In this process, we excluded Arabic, Chinese, Persian, Turkish, and Vietnamese.

#### MuST-SHE

The test set is a subset of MuST-SHE. As MuST-SHE is a subset of MuST-C, we remove overlapping sentence and take a multiway subset of all languages, using English as pivot. In this process, we excluded Spanish (es), as we needed zero-shot directions for all models (trained with the different MuST-C training sets). This resulted in 278 sentences with speaker-related (category 1) and speaker-independent (category 2) gender agreement.

|            | Feminine Referent<br />(Female/Male Speaker) | Masculine Referent<br />(Female/Male Speaker) | Total<br />(Female/Male Speaker) |
|------------|-----------------------------------------:|------------------------------------------:|-----------------------------:|
| Category 1 | 64 (64/0)                               | 56 (0/56)                                | 120 (64/56)                 |
| Category 2 | 72 (58/14)                              | 86 (27/59)                               | 158 (85/73)                 |
| Total      | 136 (122/14)                            | 142 (27/115)                             | 278 (148/129)               |

For gender classification, we kept Spanish translations. We augmented with two sets of labels: sentence-level gender label (1552 feminine, 1562 masculine) and token-level labels (113,934 neuter, 5425 feminine, 5431  masculine).


## Experiments

### Hyperparameters
- number of encoder layers: 5
- number of decoder layers: 5
- attention heads: 8
- embedding size: 512
- inner size: 2048
- dropout rate: 0.2
- label smoothing rate: 0.1
- optimizer: Adam
- learning rate schedule from [Vaswani et al.](https://arxiv.org/abs/1706.03762) with 8K warumup steps
- epochs: 64

#### Removed Residual Connection
- residual removed at layer: 3

#### Similarity Regularizer
- epochs (resume training): 10
- similarity measured by L2 distance based on meanpooled sentence embeddings (```-sim_loss_type 11```)
- auxiliary loss weight: 0.1

#### Adversarial Language Classifier
- epochs (resume training): 10
- number of classifier languages: 2 (binary: EN or not EN)
- classifier mid layer size: 128

#### Gender Classifier
- epochs: 100
- freeze encoder and decoder
- warmup steps: 400
- sentence-level embeddings: average pooling
