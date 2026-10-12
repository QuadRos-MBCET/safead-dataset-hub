# SafeAd AI: Comprehensive Pre-Existing Dataset Candidate Dossier

**Author**: Member 1 (Dataset Engineer)  
**Project**: SafeAd AI / SAFE-VISION (QuadRos-MBCET)  
**Collaborative Hub**: `safead-dataset-hub`  
**Assigned Branch**: `feature/member1-existing-datasets`  
**Date of Audit**: October 2026  
**Status**: All 6 candidate sources investigated and verified against primary sources.

---

## Executive Summary

As part of the SafeAd AI dataset engineering stream, pre-existing research datasets provide foundational training and benchmarking data for individual components (textual toxicity, multimodal hate/deception, face-age estimation, and video safety moderation). 

Crucially, **public research datasets are kept isolated** from custom team contributions (owned by Sourav and Juwel). Each candidate dataset is preserved in its own subdirectory under `SafeAd_Dataset/existing_datasets/<source_name>/` with its original annotations intact.

Under project guidelines:
1. **Never invent licenses, sizes, or access permissions.**
2. **Never force component labels into the 4-tier SafeAd policy** (`SAFE_FOR_ALL`, `SAFE_14_PLUS`, `SAFE_18_PLUS`, `UNSAFE_FOR_ALL`). If a sample does not have a 1:1 defensible mapping to ad publishing safety, its SafeAd label is marked `UNASSIGNED`.
3. **Restricted or gated datasets** require explicit authorization and manual acceptance of terms; collection tools must enforce dry-runs and reject bypass attempts.

---

## Summary Matrix of Candidate Datasets

| Dataset Identifier | Primary Modality | Primary Labels | Verified License | Commercial Use | Access Type | SafeAd Component Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **conpro_bad_ads** | Image + Text | 14 Ad/Landing Codes | Academic Research Only | Prohibited / Unlicensed | Public (GitHub + GDrive) | Deceptive ads, clickbait, scam detection |
| **hateful_memes** | Multimodal (Img+Txt) | Binary: Hateful (0/1) | Meta Research License | Prohibited | Gated (DrivenData / HF) | Multimodal hate speech & offensive memes |
| **dehate** | Video + Audio + Text | Explicit / Implicit Hate | Academic Research Only | Prohibited | Public Annotations / Restricted Videos | Temporal video hate localization |
| **jigsaw_toxic** | Text | 6 Toxicity Multi-labels | CC0 / CC BY-SA 3.0 | Permitted (Attribution) | Public (Kaggle Rules) | Voiceover ASR & OCR text toxicity |
| **utkface** | Image | Age (0-116), Gender, Race | Non-Commercial Research | Prohibited | Public (Google Drive) | Continuous face-age estimation training |
| **fairface** | Image | Age (9 bins), Gender, Race | CC BY 4.0 | Permitted (Attribution) | Public (Google Drive) | Demographic fairness & age bracket validation |

---

## Detailed Investigation Dossiers

```mermaid
flowchart TD
    subgraph Component Research Datasets
        A[ConPro Bad Ads] -->|Deceptive & Malvertising| MOD[Ad Moderation Engine]
        B[Hateful Memes] -->|Multimodal Hate & Slurs| MOD
        C[DeHate Video] -->|Video Temporal Violations| SAFEVISION[SAFE-VISION Video Guardrail]
        D[Jigsaw Toxic] -->|OCR & ASR Toxicity| TEXT[Text Moderation Submodule]
        E[UTKFace] -->|Continuous Face Age| AGE[Face-Age Estimator]
        F[FairFace] -->|Demographic Balanced Face Age| AGE
    end
    
    subgraph SafeAd Classification Output
        MOD -.->|Defensible Scams/Violations| UNSAFE[UNSAFE_FOR_ALL]
        MOD -.->|Age-gated Advertorials| AGE18[SAFE_18_PLUS]
        MOD -.->|Non-violating samples| UNASSIGN[UNASSIGNED (Research Only)]
        AGE -.->|Viewer / Actor Profiling| DECISION[Age-Aware Policy Filter]
    end
```

---

### 1. Bad News / ConPro Ads Dataset

- **Official Source URL**: [https://github.com/eric-zeng/conpro-bad-ads-data](https://github.com/eric-zeng/conpro-bad-ads-data)
- **Dataset Purpose & Modality**:
  - *Purpose*: Empirical study of low-quality, deceptive, clickbait, and problematic online ads appearing on mainstream news and misinformation sites.
  - *Modality*: Multimodal (Image screenshots of ads, full-page screenshots of landing pages, HTML trees, and tabular metadata).
- **Actual Label Types**:
  Qualitative editorial taxonomy with 14 distinct categorical codes:
  1. `Product` (1,215 ads)
  2. `Content Farm` (283 ads)
  3. `Supplements` (257 ads)
  4. `Sponsored Search` (196 ads)
  5. `Product Advertorial` (103 ads)
  6. `Insurance` (96 ads)
  7. `Self-Link` (82 ads)
  8. `Sponsored Editorial` (50 ads)
  9. `Investing` (43 ads)
  10. `Mortgage` (29 ads)
  11. `Political Campaign` (28 ads)
  12. `Charities and PSAs` (17 ads)
  13. `Political Poll` (14 ads)
  14. `Potentially Unwanted Software` (8 ads)
- **Potential Use in SafeAd**:
  - High utility for SafeAd's deceptive claims and malvertising classification.
  - `Potentially Unwanted Software` and deceptive scam landing pages map directly to `UNSAFE_FOR_ALL`.
  - Financial/mortgage/speculative investment pitches map to `SAFE_18_PLUS` (financial risk).
  - General e-commerce products, insurance, and PSAs remain `UNASSIGNED` to avoid corrupting ad policy definitions.
- **Access Requirements**:
  - Repository code and `dataset.csv` are publicly accessible on GitHub without authentication.
  - The ad screenshot image archive (~multi-GB) is hosted on a Google Drive share link specified in the repository README.
- **License and Attribution Requirements**:
  - Research / Academic Use Only. No formal OSS license file exists in the repository.
  - Attribution requirement: Cite Zeng et al., "Bad News: Clickbait and Deceptive Ads on News and Misinformation Websites", ConPro 2020.
- **Commercial / Non-Commercial Restrictions**:
  - Commercial use is not authorized; non-commercial research use only.
- **Download or Import Instructions**:
  1. Clone repository or download `dataset.csv`: `https://raw.githubusercontent.com/eric-zeng/conpro-bad-ads-data/master/dataset.csv`.
  2. Download screenshots `.tar.gz` from Google Drive (`12sCuxv38RPlrRKUs-hjl-JrTDQ4J_HcR`).
  3. Extract screenshots into `SafeAd_Dataset/existing_datasets/conpro_bad_ads/screenshots/`.
  4. Run automated import tool: `python tools/importer.py --source conpro_bad_ads --data-dir SafeAd_Dataset/existing_datasets/conpro_bad_ads`.
- **Known Limitations**:
  - Crawled in January 2020 (temporal decay of landing page URLs).
  - Labels reflect advertiser tactics rather than strict regulatory safety tiers.
- **Verification Status**:
  - **Verified**. Repository active, `dataset.csv` verified live with 2,246 ad annotations.

---

### 2. Facebook Hateful Memes (FHM)

- **Official Source URL**: [https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/](https://ai.meta.com/blog/hateful-memes-challenge-and-data-set/)
- **Dataset Purpose & Modality**:
  - *Purpose*: Multimodal benchmark specifically designed to detect multimodal hate speech containing "benign confounders" (where text and image are innocuous alone but hateful in combination).
  - *Modality*: Multimodal (Image + Embedded Text String).
- **Actual Label Types**:
  - Binary classification: `0` (not-hateful / benign) or `1` (hateful).
  - Metadata includes sample `id`, `img` file path, and `text` transcript.
- **Potential Use in SafeAd**:
  - Multimodal fusion submodule for detecting hateful tropes, derogatory memes, and offensive cultural slurs in ad creatives.
  - Hateful samples (`label=1`) map cleanly to `UNSAFE_FOR_ALL`.
  - Non-hateful samples (`label=0`) must remain `UNASSIGNED` for general ad moderation because benign memes are not standard commercial ads and may contain unrelated age-restricted humor.
- **Access Requirements**:
  - **Restricted / Gated Access**.
  - Requires creating an account on DrivenData (Competition 73) or authenticating via Hugging Face (`facebook/hateful_memes`) and agreeing to the Meta Hateful Memes Challenge Dataset License Agreement.
- **License and Attribution Requirements**:
  - Meta Hateful Memes Challenge License (`LICENSE.txt`).
  - Strict prohibition against re-identifying individuals.
  - Attribution to Kiela et al. (NeurIPS 2020).
  - Includes third-party imagery requiring stock attribution (e.g. Getty Images).
- **Commercial / Non-Commercial Restrictions**:
  - **Strictly Non-Commercial Research Only**. Commercial use strictly prohibited.
- **Download or Import Instructions**:
  1. Complete registration at DrivenData or Hugging Face.
  2. Download `train.jsonl`, `dev_seen.jsonl`, and `img.tar.gz`.
  3. Place files in `SafeAd_Dataset/existing_datasets/hateful_memes/`.
  4. Run importer tool: `python tools/importer.py --source hateful_memes --data-dir SafeAd_Dataset/existing_datasets/hateful_memes`.
- **Known Limitations**:
  - Extreme offensive content requiring ethical safeguard handling.
  - Memes differ stylistically from clean commercial corporate ads.
- **Verification Status**:
  - **Verified**. Terms, schema, and Hugging Face gated access confirmed; requires manual login token.

---

### 3. DeHate Video Dataset

- **Official Source URL**: [https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate](https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate)
- **Dataset Purpose & Modality**:
  - *Purpose*: Large-scale multimodal dataset for detection of explicit and implicit hate in short-form videos across TikTok and BitChute, featuring fine-grained temporal segment annotations.
  - *Modality*: Audio-Visual-Textual (Video clips, audio tracks, text transcripts).
- **Actual Label Types**:
  - Primary Classification: `Hate (Explicit)`, `Hate (Implicit)`, `Non-Hate`.
  - Target Demographic Groups (6 classes): `Race`, `Gender`, `Religion`, `Sexual Orientation`, `Disability`, `Immigration`.
  - Contributing Modality Attribution: `Text only`, `Visual only`, `Audio only`, `Visual + Audio`, `Visual + Text`, `Text + Audio`, `Visual + Audio + Text`.
  - Temporal Segment Boundaries: `start_time` and `end_time` (seconds).
- **Potential Use in SafeAd**:
  - Video-level safety guardrail in SAFE-VISION.
  - Temporal localization allows the SafeAd pipeline to highlight exact timestamps where video policy violations occur.
  - Explicit hate segments map to `UNSAFE_FOR_ALL`. Non-hate videos remain `UNASSIGNED`.
- **Access Requirements**:
  - Annotation spreadsheet `DeHate.xlsx` (6,689 video entries) is open on GitHub.
  - Full raw video clips require author contact or running platform scraping scripts respecting platform terms.
- **License and Attribution Requirements**:
  - Academic Research Use Only with strict ethics declaration.
  - Attribution requirement: Cite MM'25 paper "DeHate: A Holistic Hateful Video Dataset for Explicit and Implicit Hate Detection".
- **Commercial / Non-Commercial Restrictions**:
  - Non-commercial academic research only.
- **Download or Import Instructions**:
  1. Clone repository to acquire `DeHate.xlsx`: `https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate`.
  2. Acquire video media according to research protocol into `SafeAd_Dataset/existing_datasets/dehate_video/videos/`.
  3. Run importer tool: `python tools/importer.py --source dehate --data-dir SafeAd_Dataset/existing_datasets/dehate_video`.
- **Known Limitations**:
  - Third-party social platform video URLs are vulnerable to platform removal.
  - Short-form social media video style vs. polished commercial production ads.
- **Verification Status**:
  - **Verified**. GitHub repository verified live; `DeHate.xlsx` verified with 6,689 annotated records.

---

### 4. Jigsaw Toxic Comment Classification

- **Official Source URL**: [https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data](https://www.kaggle.com/c/jigsaw-multilingual-toxic-comment-classification/data)
- **Dataset Purpose & Modality**:
  - *Purpose*: Identify and categorize toxic text online to protect discussions across multilingual settings.
  - *Modality*: Text only (Wikipedia talk page comments and translated online remarks).
- **Actual Label Types**:
  Multi-label binary classification across 6 dimensions:
  1. `toxic` (0 or 1)
  2. `severe_toxic` (0 or 1)
  3. `obscene` (0 or 1)
  4. `threat` (0 or 1)
  5. `insult` (0 or 1)
  6. `identity_hate` (0 or 1)
- **Potential Use in SafeAd**:
  - Textual moderation submodule: evaluates ad transcriptions generated by speech-to-text (Whisper/ASR) and ad banner copy detected by OCR.
  - Comments with `threat`, `identity_hate`, or `severe_toxic` map to `UNSAFE_FOR_ALL`.
  - Comments with `obscene` language map to `SAFE_18_PLUS` (mature/profanity) or `UNSAFE_FOR_ALL`.
  - Non-toxic text samples remain `UNASSIGNED` (clean text does not imply the ad visual is safe).
- **Access Requirements**:
  - Kaggle user account required to accept competition terms.
  - Also mirrored publicly on Hugging Face (`jigsaw_toxicity_pred`) and TensorFlow Datasets.
- **License and Attribution Requirements**:
  - Released under **CC0 (Public Domain)** by Jigsaw and Google.
  - Underlying Wikipedia talk page comments licensed under **CC BY-SA 3.0**.
- **Commercial / Non-Commercial Restrictions**:
  - Permissive. Commercial use is legally permissible provided Wikipedia source text attribution requirements are respected.
- **Download or Import Instructions**:
  1. Authenticate with Kaggle API (`kaggle.json`).
  2. Run: `kaggle competitions download -c jigsaw-multilingual-toxic-comment-classification`.
  3. Extract CSV files into `SafeAd_Dataset/existing_datasets/jigsaw_toxic/`.
  4. Run importer tool: `python tools/importer.py --source jigsaw_toxic --data-dir SafeAd_Dataset/existing_datasets/jigsaw_toxic`.
- **Known Limitations**:
  - Text-only dataset; no visual ad banners or video assets.
  - High density of informal internet conversational slang rather than commercial ad slogans.
- **Verification Status**:
  - **Verified**. Kaggle competition and open licensing (CC0/CC-BY-SA) verified.

---

### 5. UTKFace Large-Scale Face Dataset

- **Official Source URL**: [https://github.com/aicip/UTKFace](https://github.com/aicip/UTKFace)
- **Dataset Purpose & Modality**:
  - *Purpose*: Benchmark face detection, continuous age estimation, age progression/regression, and facial landmark localization across a long age span (0 to 116 years old).
  - *Modality*: Image (20,000+ unconstrained in-the-wild facial photos and aligned/cropped facial images).
- **Actual Label Types**:
  Embedded in filename format: `[age]_[gender]_[race]_[date&time].jpg`:
  - `age`: Continuous integer from `0` to `116`.
  - `gender`: Binary integer (`0`: Male, `1`: Female).
  - `race`: Categorical integer (`0`: White, `1`: Black, `2`: Asian, `3`: Indian, `4`: Others).
  - `landmarks`: 68 landmark coordinate points.
- **Potential Use in SafeAd**:
  - Essential foundation for the **SafeAd Face-Age Estimation Component** (`sooraj_face_age_core`).
  - Used to verify user age profile feeds and detect minor actors in sensitive ad categories (e.g., gambling, alcohol).
  - *Crucial Policy Rule*: Face images are demographic calibration crops, NOT advertisements. Therefore, their SafeAd category label must be kept strictly **`UNASSIGNED`**.
- **Access Requirements**:
  - Direct public Google Drive links provided in the official GitHub README:
    - In-the-wild faces archive: 1.3 GB
    - Aligned & Cropped faces archive: 107 MB
    - 68 Landmark annotations: 12 MB
- **License and Attribution Requirements**:
  - Non-commercial research purposes only.
  - AICIP does not claim copyright over the underlying web-scraped images.
  - Attribution: Cite Zhang, Song, & Qi (AICIP, University of Tennessee).
- **Commercial / Non-Commercial Restrictions**:
  - **Strictly Non-Commercial**.
- **Download or Import Instructions**:
  1. Download aligned & cropped ZIP archive from the official Google Drive link (`0BxYys69jI14kU0I1YUQyY1ZDRUE`).
  2. Extract image files into `SafeAd_Dataset/existing_datasets/utkface/faces/`.
  3. Run importer tool: `python tools/importer.py --source utkface --data-dir SafeAd_Dataset/existing_datasets/utkface`.
- **Known Limitations**:
  - Long tail with fewer samples at extreme ages (>80 or <2).
  - Continuous ages have human estimator variance.
  - Single isolated face crops only.
- **Verification Status**:
  - **Verified**. Live GitHub repository and Google Drive archives verified active.

---

### 6. FairFace Balanced Demographic Face Dataset

- **Official Source URL**: [https://github.com/joojs/fairface](https://github.com/joojs/fairface) (also [https://github.com/dchen236/FairFace](https://github.com/dchen236/FairFace))
- **Dataset Purpose & Modality**:
  - *Purpose*: Mitigate algorithmic demographic bias in computer vision facial analysis by providing a balanced dataset across race, gender, and age.
  - *Modality*: Image (108,501 cropped facial images from YFCC-100M).
- **Actual Label Types**:
  - `race` (7 categories): `White`, `Black`, `Indian`, `East Asian`, `Southeast Asian`, `Middle Eastern`, `Latino_Hispanic`.
  - `gender` (2 categories): `Male`, `Female`.
  - `age` (9 discrete age bracket bins): `0-2`, `3-9`, `10-19`, `20-29`, `30-39`, `40-49`, `50-59`, `60-69`, `70+`.
  - `service_test` (binary test set flag).
- **Potential Use in SafeAd**:
  - Fairness auditing, demographic debiasing, and age bracket validation for the SafeAd age-aware system.
  - Directly validates age boundaries: minor protection (`0-2`, `3-9`), teen restriction (`10-19` mapped to 14+), and adult verification (`20-29`+ mapped to 18+).
  - *Crucial Policy Rule*: Facial photos are NOT ads; their SafeAd category label must remain strictly **`UNASSIGNED`**.
- **Access Requirements**:
  - Publicly accessible via Google Drive links hosted in the official GitHub repository.
- **License and Attribution Requirements**:
  - **CC BY 4.0 (Creative Commons Attribution 4.0 International)**.
  - Attribution: Cite Karkkainen & Joo, "FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age for Bias Measurement and Mitigation", WACV 2021.
- **Commercial / Non-Commercial Restrictions**:
  - Permissive. Commercial and non-commercial research allowed with proper attribution.
- **Download or Import Instructions**:
  1. Access Google Drive links in `dchen236/FairFace` README.
  2. Download `fairface_label_train.csv`, `fairface_label_val.csv`, and image zip (`fairface-img-margin125-trainval.zip`).
  3. Extract to `SafeAd_Dataset/existing_datasets/fairface/`.
  4. Run importer tool: `python tools/importer.py --source fairface --data-dir SafeAd_Dataset/existing_datasets/fairface`.
- **Known Limitations**:
  - Discrete age bins rather than continuous age values.
  - Facial bounding boxes cropped tightly; no contextual visual scenes or ad creative elements.
- **Verification Status**:
  - **Verified**. WACV 2021 publication and CC BY 4.0 license confirmed.

---

## Action Plan for Dataset Engineering

1. **Registry Integration**: Metadata stored in `registry/candidate_datasets.json` and queryable via `tools/registry.py`.
2. **Authorized Imports**: Importer parses original labels without forcing them into SafeAd classes, generating SHA-256 checksums and saving records in `SafeAd_Dataset/existing_datasets/<dataset>/manifest.csv`.
3. **Restricted Datasets Protocol**: Gated datasets (`hateful_memes`, `dehate_video`) remain in pending manual authentication mode until explicit tokens or author approvals are provided by the research team.
