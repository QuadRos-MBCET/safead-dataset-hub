# Jigsaw Multilingual / Toxic Comment Classification

- **Identifier**: `jigsaw_toxic`
- **Source**: [https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data](https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data)
- **Organization**: Jigsaw / Alphabet / Google
- **Modality**: Text (Wikipedia talk pages and multilingual comments)
- **Verified License**: CC0 (Public Domain annotations) / CC BY-SA 3.0 (Wikipedia source comments)

## Labels & SafeAd Mapping Policy
Multi-label binary annotations across 6 dimensions:
- `threat`, `identity_hate`, `severe_toxic` -> `UNSAFE_FOR_ALL` (Violates non-violence and anti-hate policies).
- `obscene`, `toxic`, `insult` -> `SAFE_18_PLUS` (Mature language restriction).
- Unlabeled / non-toxic -> `UNASSIGNED` (Clean text alone cannot guarantee visual ad compliance).

## Acquisition
- Requires Kaggle API authentication (`kaggle competitions download -c jigsaw-multilingual-toxic-comment-classification`).
- Also available via Hugging Face (`jigsaw_toxicity_pred`).
