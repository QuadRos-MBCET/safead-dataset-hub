# Facebook Hateful Memes (FHM) Dataset

- **Identifier**: `hateful_memes`
- **Source**: [https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/](https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/)
- **Competition**: DrivenData Competition 73 / Hugging Face `facebook/hateful_memes`
- **Paper**: Kiela et al., "The Hateful Memes Challenge: Detecting Hate Speech in Multimodal Memes", NeurIPS 2020
- **Modality**: Multimodal (Image + Embedded Text)
- **Verified License**: Meta Hateful Memes Research License (Strictly Non-Commercial, Getty Images restrictions)

## Access Requirements & Compliance Notice
- **Access Type**: Gated / Restricted
- Requires agreeing to Meta terms on DrivenData or Hugging Face.
- Automated tools must not bypass authentication.

## Labels & SafeAd Mapping Policy
- `label = 1 (hateful)` -> `UNSAFE_FOR_ALL` (Multimodal hate speech violates platform safety policies).
- `label = 0 (not-hateful)` -> `UNASSIGNED` (Benign memes cannot be presumed valid or safe commercial ads).
