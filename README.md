# SafeAd Dataset Hub (`safead-dataset-hub`)

Collaborative dataset repository and management tooling for the **SafeAd AI / SAFE-VISION** multimodal advertisement content safety and moderation project.

## Project Structure & Team Responsibilities

- **Project Coordinator**: Pre-existing public/research benchmark datasets, shared schema coordination, master integration, and final review acceptance.
- **Sourav**: Custom advertisements for `SAFE_FOR_ALL` and `SAFE_14_PLUS`.
  - Contribution Branch: `feature/sourav-safe-for-all-14-plus`
  - Contribution Manifest: `manifests/sourav/contribution_manifest.json`
  - Storage Location: `SafeAd_Dataset/custom_ads/sourav/{safe_for_all,safe_14_plus}/`
- **Juwel**: Custom advertisements for `SAFE_18_PLUS` and `UNSAFE_FOR_ALL`.
  - Contribution Branch: `feature/juwel-safe-18-plus-unsafe`
  - Contribution Manifest: `manifests/juwel/contribution_manifest.json`
  - Storage Location: `SafeAd_Dataset/custom_ads/juwel/{safe_18_plus,unsafe_for_all}/`

## Storage Policy

1. **No Large Media in Git**: All raw media files (images, videos) must be stored in the designated external storage backend (e.g., Google Drive / authorized cloud storage).
2. **Relative Paths & Storage URIs**: Manifests use relative paths (e.g. `SafeAd_Dataset/custom_ads/sourav/safe_for_all/...`) and storage URIs (e.g. `gdrive://SafeAd_Dataset/...`). Absolute local machine paths (`C:\Users\...`) are prohibited.
3. **Partitioned Manifests**: Contributors edit only their assigned contribution manifest under `manifests/<contributor>/contribution_manifest.json`.

## Common Labels

- `SAFE_FOR_ALL`: Suitable for general audiences including children. No violence, sexual themes, substances, gambling, or deceptive/scam claims.
- `SAFE_14_PLUS`: Suitable for teens 14+ and adults. Mild suggestive themes, mild action violence, or teen-targeted commodities, but free of adult-restricted items.
- `SAFE_18_PLUS`: Restricted to legal adults (alcohol, regulated gambling, adult dating, mature themes).
- `UNSAFE_FOR_ALL`: Prohibited content (explicit illegality, hate speech, severe violence, fraud, scam ads).

Refer to [ANNOTATION_POLICY.md](ANNOTATION_POLICY.md) for detailed guidelines.
