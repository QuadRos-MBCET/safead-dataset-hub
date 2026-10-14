# UTKFace Large-Scale Face Dataset

- **Identifier**: `utkface`
- **Source**: [https://github.com/aicip/UTKFace](https://github.com/aicip/UTKFace)
- **Organization**: AICIP, University of Tennessee
- **Modality**: Image (20,000+ faces in the wild)
- **Verified License**: Non-commercial Research Purposes Only

## Component Role in SafeAd
UTKFace provides continuous age-annotated facial images (ages 0 to 116) used exclusively for:
- Training and benchmarking the **Face-Age Estimation Component** (`sooraj_face_age_core`).
- Detecting underage actors in age-restricted advertising creatives.

## Policy Mapping Rule
**Crucial**: These images are facial portrait crops, NOT commercial advertisements.
Therefore, their SafeAd advertising label MUST remain **`UNASSIGNED`**.
Original annotations (`age`, `gender`, `race`) are strictly preserved in `source_label` and `notes`.

## Working Mirrors & Download Links
The historical Google Drive folder from the original 2017 paper is frequently inaccessible due to drive permissions. The aligned and cropped images (~107 MB) are reliably mirrored at:
- **Hugging Face (`py97/UTKFace-Cropped`)**: [https://huggingface.co/datasets/py97/UTKFace-Cropped/tree/main](https://huggingface.co/datasets/py97/UTKFace-Cropped/tree/main) (Direct archive: `UTKFace.tar.gz`)
- **Kaggle Mirror (`jangedoo/utkface-new`)**: [https://www.kaggle.com/datasets/jangedoo/utkface-new](https://www.kaggle.com/datasets/jangedoo/utkface-new) (Contains `utkface_aligned_cropped` and `crop_part1`)
- **Extraction Target**: `D:\SafeAd_Dataset\existing_datasets\utkface\faces\`
