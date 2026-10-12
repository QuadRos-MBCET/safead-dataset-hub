# FairFace Balanced Demographic Face Dataset

- **Identifier**: `fairface`
- **Source**: [https://github.com/joojs/fairface](https://github.com/joojs/fairface) (and [https://github.com/dchen236/FairFace](https://github.com/dchen236/FairFace))
- **Paper**: Karkkainen & Joo, "FairFace: Face Attribute Dataset for Balanced Race, Gender, and Age for Bias Measurement and Mitigation", WACV 2021
- **Modality**: Image (108,501 balanced facial crops)
- **Verified License**: CC BY 4.0 (Creative Commons Attribution 4.0 International)

## Component Role in SafeAd
FairFace is utilized for:
- Evaluating and auditing demographic bias in our face-age estimation models (`sooraj_face_age_core`).
- Ensuring fair age verification across 7 racial/ethnic groups and both genders.

## Policy Mapping Rule
**Crucial**: These images are facial portrait crops, NOT commercial advertisements.
Therefore, their SafeAd advertising label MUST remain **`UNASSIGNED`**.
Original annotations (`age_bracket`, `gender`, `race`) are strictly preserved in `source_label` and `notes`.
