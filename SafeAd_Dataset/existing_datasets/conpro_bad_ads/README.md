# Bad News / ConPro Online Ads Dataset

- **Identifier**: `conpro_bad_ads`
- **Source**: [https://github.com/eric-zeng/conpro-bad-ads-data](https://github.com/eric-zeng/conpro-bad-ads-data)
- **Paper**: Zeng et al., "Bad News: Clickbait and Deceptive Ads on News and Misinformation Websites", ConPro 2020
- **Modality**: Multimodal (Ad screenshots, Landing page screenshots, Tabular metadata)
- **Verified License**: Academic Research Only (No commercial grant)

## Labels & Mapping Policy
Source annotations contain 14 qualitative codes. Mapping into SafeAd categories:
- `Potentially Unwanted Software` -> `UNSAFE_FOR_ALL` (malvertising / software safety violation)
- `Investing`, `Mortgage` -> `SAFE_18_PLUS` (financial risk / mature advertorial)
- All other categories (`Product`, `Content Farm`, `Supplements`, `Sponsored Search`, etc.) -> `UNASSIGNED` (component research on clickbait & deceptive claims without forcing arbitrary ad bans).

## Acquisition
1. Public metadata in `dataset.csv` (2,246 entries).
2. Large screenshots archive is downloaded manually from Google Drive (`12sCuxv38RPlrRKUs-hjl-JrTDQ4J_HcR`) into `screenshots/`.
3. Synchronize with Google Drive storage root: `gdrive://safead-storage/SafeAd_Dataset/existing_datasets/conpro_bad_ads/`.
