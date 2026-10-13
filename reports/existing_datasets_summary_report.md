# SafeAd AI: Existing Dataset Collection Summary Report

- **Total Candidate Manifests Audited**: 6
- **Total Registered Samples**: 26143
- **Schema Compliance Rate**: 6 / 6 (100.0%)

## Dataset Breakdown Table

| Dataset ID | Display Name | Samples | Primary Modality | SafeAd Labels | License Status | Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `conpro_bad_ads` | Bad News / ConPro Online Ads Dataset | 2421 | image | UNASSIGNED:2341, SAFE_18_PLUS:72, UNSAFE_FOR_ALL:8 | Research / Academic Use Only (ConPro 2020 publication; no explicit permissive open source license file) | [VALID] |
| `dehate` | DeHate Video Dataset | 3 | video | UNSAFE_FOR_ALL:2, UNASSIGNED:1 | Academic Research Only | [VALID] |
| `fairface` | FairFace Balanced Demographic Face Dataset | 4 | image | UNASSIGNED:4 | CC BY 4.0 | [VALID] |
| `hateful_memes` | Facebook Hateful Memes (FHM) | 4 | multimodal | UNSAFE_FOR_ALL:2, UNASSIGNED:2 | Meta Research License | [VALID] |
| `jigsaw_toxic` | Jigsaw Multilingual / Toxic Comment Classification | 3 | text | UNSAFE_FOR_ALL:1, SAFE_18_PLUS:1, UNASSIGNED:1 | CC0 / CC BY-SA 3.0 | [VALID] |
| `utkface` | UTKFace Large-Scale Face Dataset | 23708 | image | UNASSIGNED:23708 | Non-commercial Research Purposes Only (AICIP does not hold image copyright; collected from web). | [VALID] |

---

## Detailed Dataset Statistics

### Bad News / ConPro Online Ads Dataset (`conpro_bad_ads`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\conpro_bad_ads\manifest.csv`
- **Official URL**: https://github.com/eric-zeng/conpro-bad-ads-data
- **Verified License**: Research / Academic Use Only (ConPro 2020 publication; no explicit permissive open source license file)
- **Sample Count**: 2421
- **Duplicates Detected**: 337

**Media Type Distribution:**
  - `image`: 2421

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 2341 (96.7%)
  - `SAFE_18_PLUS`: 72 (3.0%)
  - `UNSAFE_FOR_ALL`: 8 (0.3%)

**Source Annotations Sample:**
  - `Charities and PSAs`: 17
  - `Content Farm`: 283
  - `Insurance`: 96
  - `Investing`: 43
  - `Mortgage`: 29
  - *(and 9 more source labels)*


### DeHate Video Dataset (`dehate`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\dehate\manifest.csv`
- **Official URL**: https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate
- **Verified License**: Academic Research Only
- **Sample Count**: 3
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `video`: 3

**SafeAd 4-Tier Label Distribution:**
  - `UNSAFE_FOR_ALL`: 2 (66.7%)
  - `UNASSIGNED`: 1 (33.3%)

**Source Annotations Sample:**
  - `Hate (Explicit)`: 1
  - `Hate (Implicit)`: 1
  - `Non-Hate`: 1


### FairFace Balanced Demographic Face Dataset (`fairface`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\fairface\manifest.csv`
- **Official URL**: https://github.com/joojs/fairface
- **Verified License**: CC BY 4.0
- **Sample Count**: 4
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `image`: 4

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 4 (100.0%)

**Source Annotations Sample:**
  - `age=20-29;gender=Male;race=East Asian`: 1
  - `age=30-39;gender=Female;race=White`: 1
  - `age=10-19;gender=Female;race=Black`: 1
  - `age=0-2;gender=Male;race=Indian`: 1


### Facebook Hateful Memes (FHM) (`hateful_memes`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\hateful_memes\manifest.csv`
- **Official URL**: https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/
- **Verified License**: Meta Research License
- **Sample Count**: 4
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `multimodal`: 4

**SafeAd 4-Tier Label Distribution:**
  - `UNSAFE_FOR_ALL`: 2 (50.0%)
  - `UNASSIGNED`: 2 (50.0%)

**Source Annotations Sample:**
  - `1`: 2
  - `0`: 2


### Jigsaw Multilingual / Toxic Comment Classification (`jigsaw_toxic`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\jigsaw_toxic\manifest.csv`
- **Official URL**: https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data
- **Verified License**: CC0 / CC BY-SA 3.0
- **Sample Count**: 3
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `text`: 3

**SafeAd 4-Tier Label Distribution:**
  - `UNSAFE_FOR_ALL`: 1 (33.3%)
  - `SAFE_18_PLUS`: 1 (33.3%)
  - `UNASSIGNED`: 1 (33.3%)

**Source Annotations Sample:**
  - `threat=1;severe_toxic=1`: 1
  - `obscene=1;toxic=1`: 1
  - `clean=1`: 1


### UTKFace Large-Scale Face Dataset (`utkface`)
- **Manifest**: `SafeAd_Dataset\existing_datasets\utkface\manifest.csv`
- **Official URL**: https://github.com/aicip/UTKFace
- **Verified License**: Non-commercial Research Purposes Only (AICIP does not hold image copyright; collected from web).
- **Sample Count**: 23708
- **Duplicates Detected**: 390

**Media Type Distribution:**
  - `image`: 23708

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 23708 (100.0%)

**Source Annotations Sample:**
  - `age=100;gender=Male;race=White`: 2
  - `age=100;gender=Female;race=White`: 6
  - `age=100;gender=Female;race=Asian`: 3
  - `age=101;gender=Male;race=White`: 1
  - `age=101;gender=Female;race=Asian`: 1
  - *(and 843 more source labels)*

