# SafeAd AI: Existing Dataset Collection Summary Report

- **Total Candidate Manifests Audited**: 7
- **Total Registered Samples**: 54887
- **Schema Compliance Rate**: 7 / 7 (100.0%)

## Dataset Breakdown Table

| Dataset ID | Display Name | Samples | Primary Modality | SafeAd Labels | License Status | Compliance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `conpro_bad_ads` | Bad News / ConPro Online Ads Dataset | 2421 | image | UNASSIGNED:2341, SAFE_18_PLUS:72, UNSAFE_FOR_ALL:8 | Research / Academic Use Only (ConPro 2020 publication; no explicit permissive open source license file) | [VALID] |
| `dehate` | DeHate Video Dataset | 6689 | video | UNASSIGNED:4569, UNSAFE_FOR_ALL:2120 | Academic Research Use Only (Strict Ethics Statement; confidential research use only; no permissive redistribution of raw platform videos) | [VALID] |
| `fairface` | FairFace Balanced Demographic Face Dataset | 10954 | image | UNASSIGNED:10954 | CC BY 4.0 (Creative Commons Attribution 4.0 International) | [VALID] |
| `hateful_memes` | Facebook Hateful Memes (FHM) | 1040 | image | UNSAFE_FOR_ALL:447, UNASSIGNED:593 | Meta Hateful Memes Research License (Non-commercial research only, privacy restrictions, Getty Images compilation restrictions) | [VALID] |
| `jigsaw_toxic` | Jigsaw Multilingual / Toxic Comment Classification | 10000 | text | UNASSIGNED:8970, UNSAFE_FOR_ALL:189, SAFE_18_PLUS:841 | CC0 (Public Domain) for Jigsaw annotations; underlying Wikipedia talk page comments licensed under CC BY-SA 3.0 | [VALID] |
| `utkface` | UTKFace Large-Scale Face Dataset | 23708 | image | UNASSIGNED:23708 | Non-commercial Research Purposes Only (AICIP does not hold image copyright; collected from web). | [VALID] |
| `Beer-Tv-Ads` | Beer TV Ads Dataset | 75 | video | SAFE_18_PLUS:75 | Research / Open Broadcast | [VALID] |

---

## Detailed Dataset Statistics

### Bad News / ConPro Online Ads Dataset (`conpro_bad_ads`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\conpro_bad_ads\manifest.csv`
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
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\dehate\manifest.csv`
- **Official URL**: https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate
- **Verified License**: Academic Research Use Only (Strict Ethics Statement; confidential research use only; no permissive redistribution of raw platform videos)
- **Sample Count**: 6689
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `video`: 6689

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 4569 (68.3%)
  - `UNSAFE_FOR_ALL`: 2120 (31.7%)

**Source Annotations Sample:**
  - `NonHate`: 4569
  - `Explicit [Targets: Gender, Religion]`: 5
  - `Implicit [Targets: Race]`: 223
  - `Implicit [Targets: Race, Immigration]`: 78
  - `Explicit [Targets: Race, Sexual Orientation]`: 33
  - *(and 48 more source labels)*


### FairFace Balanced Demographic Face Dataset (`fairface`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\fairface\manifest.csv`
- **Official URL**: https://github.com/joojs/fairface
- **Verified License**: CC BY 4.0 (Creative Commons Attribution 4.0 International)
- **Sample Count**: 10954
- **Duplicates Detected**: 2

**Media Type Distribution:**
  - `image`: 10954

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 10954 (100.0%)

**Source Annotations Sample:**
  - `age=3-9;gender=Male;race=East Asian`: 137
  - `age=3-9;gender=Male;race=Southeast Asian`: 113
  - `age=20-29;gender=Female;race=East Asian`: 384
  - `age=20-29;gender=Male;race=Latino_Hispanic`: 181
  - `age=20-29;gender=Female;race=Southeast Asian`: 250
  - *(and 121 more source labels)*


### Facebook Hateful Memes (FHM) (`hateful_memes`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\hateful_memes\manifest.csv`
- **Official URL**: https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/
- **Verified License**: Meta Hateful Memes Research License (Non-commercial research only, privacy restrictions, Getty Images compilation restrictions)
- **Sample Count**: 1040
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `image`: 1040

**SafeAd 4-Tier Label Distribution:**
  - `UNSAFE_FOR_ALL`: 447 (43.0%)
  - `UNASSIGNED`: 593 (57.0%)

**Source Annotations Sample:**
  - `1`: 447
  - `0`: 593


### Jigsaw Multilingual / Toxic Comment Classification (`jigsaw_toxic`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\jigsaw_toxic\manifest.csv`
- **Official URL**: https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data
- **Verified License**: CC0 (Public Domain) for Jigsaw annotations; underlying Wikipedia talk page comments licensed under CC BY-SA 3.0
- **Sample Count**: 10000
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `text`: 10000

**SafeAd 4-Tier Label Distribution:**
  - `UNASSIGNED`: 8970 (89.7%)
  - `UNSAFE_FOR_ALL`: 189 (1.9%)
  - `SAFE_18_PLUS`: 841 (8.4%)

**Source Annotations Sample:**
  - `clean`: 8970
  - `toxic;severe_toxic;obscene;insult`: 65
  - `toxic`: 359
  - `toxic;obscene;insult;identity_hate`: 42
  - `toxic;obscene;insult`: 225
  - *(and 28 more source labels)*


### UTKFace Large-Scale Face Dataset (`utkface`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\utkface\manifest.csv`
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


### Beer TV Ads Dataset (`Beer-Tv-Ads`)
- **Manifest**: `D:\SafeAd_Dataset\existing_datasets\video_ads\manifest.csv`
- **Official URL**: https://huggingface.co/datasets/dnaoblivion/Beer-Tv-Ads
- **Verified License**: Research / Open Broadcast
- **Sample Count**: 75
- **Duplicates Detected**: 0

**Media Type Distribution:**
  - `video`: 75

**SafeAd 4-Tier Label Distribution:**
  - `SAFE_18_PLUS`: 75 (100.0%)

**Source Annotations Sample:**
  - `Alcohol / Beer Commercial`: 75

