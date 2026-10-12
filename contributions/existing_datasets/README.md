# Existing Datasets Contribution Area

**Contributor**: Member 1 (Senior Dataset Engineer)  
**Branch**: `feature/member1-existing-datasets`  
**Contribution Manifest**: [`existing_datasets_manifest.csv`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/contributions/existing_datasets/existing_datasets_manifest.csv)

---

## Scope & Responsibilities
- Collect, investigate, verify, and register pre-existing public and research benchmark datasets.
- Ensure strict separation between public candidate datasets and custom advertisements (handled by Sourav and Juwel).
- Preserve raw third-party labels without forcing arbitrary conversion into the 4-tier SafeAd policy.
- Enforce cryptographic integrity (SHA-256) and schema validation across all manifests.

---

## Contributed Partitions

1. [`conpro_bad_ads`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/conpro_bad_ads/): Deceptive, clickbait, and problematic online news ads (ConPro 2020).
2. [`hateful_memes`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/hateful_memes/): Multimodal hate speech and benign confounders (Meta / NeurIPS 2020).
3. [`dehate`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/dehate/): Short-form video hate speech detection with temporal localization (ACM MM 2025).
4. [`jigsaw_toxic`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/jigsaw_toxic/): Multilingual text toxicity and threat classification (Jigsaw / Google).
5. [`utkface`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/utkface/): Continuous age facial images (0-116 years) for age estimation component (AICIP).
6. [`fairface`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/SafeAd_Dataset/existing_datasets/fairface/): Balanced demographic face dataset across 7 races, 2 genders, and 9 age bins (WACV 2021).

---

## Manifest Compliance
The consolidated manifest [`existing_datasets_manifest.csv`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/contributions/existing_datasets/existing_datasets_manifest.csv) passes 100% schema validation against [`schemas/manifest_schema.json`](file:///c:/Users/hello/OneDrive/Documents/Dataset%20collection/schemas/manifest_schema.json).
