# Emotion Detection

Finetuned available pretrained Malaya-Speech speaker vector models to do Emotion Detection.

**This directory is very lack of comments, able to understand Tensorflow, Tensorflow estimator, Tensorflow Dataset is really helpful**.

## how-to

1. Generate dataset [prepare/emotion.ipynb](prepare/emotion.ipynb).

2. Run any finetuning scripts,

**VGGVOX v1**,

```bash
python3 finetune-vggvox-v1.py
```

**VGGVOX v2**,

```bash
python3 finetune-vggvox-v2.py
```

3. Export the model for production, example for vggvox-v2, [export/vggvox-v2.ipynb](export/vggvox-v2.ipynb)

## Download

1. VGGVox V2, last update 21th October 2020, [vggvox-v2-emotion-detection-150k.tar.gz](https://f000.backblazeb2.com/file/malaya-speech-model/finetuned/vggvox-v2-emotion-detection-150k.tar.gz)

Tensorboard, https://tensorboard.dev/experiment/HWSxx3ViQOmTBo4QpDmwvw/

2. VGGVox V1, last update 7th October 2020, [vggvox-v1-language-detection-140k.tar.gz](https://f000.backblazeb2.com/file/malaya-speech-model/finetuned/vggvox-v1-language-detection-140k.tar.gz)

Tensorboard, https://tensorboard.dev/experiment/bBsNGv7xROmmFAdDEvoE1A/

3. Deep Speaker, last update 21th October 2020, [deep-speaker-emotion-detection-100k.tar.gz](https://f000.backblazeb2.com/file/malaya-speech-model/finetuned/deep-speaker-emotion-detection-100k.tar.gz)

Tensorboard, https://tensorboard.dev/experiment/CnC3bvZfR4ykukJ9oCKEKQ/