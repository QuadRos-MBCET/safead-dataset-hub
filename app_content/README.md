# SafeAd App Content Catalog (`app_content`)

This directory exposes approved, age-categorized social media images and reels for integration with the **SAFE-VISION / SafeAd AI** main application.

---

## 🛡️ Content Governance Policy

1. **Only Reviewed & Approved Media**: Every asset listed in [`content_manifest.json`](content_manifest.json) has `moderation_status: "APPROVED"`.
2. **Strict Age-Gating**:
   - `SAFE_FOR_ALL` (Minimum age: 0): Family-friendly, educational, everyday consumer, domestic items, wholesome commercials.
   - `SAFE_14_PLUS` (Minimum age: 14): Youth lifestyle, esports/gaming gear, sports/athletics, teen grooming, teen apparel.
   - `SAFE_18_PLUS` (Minimum age: 18): Financial investments/crypto, nightlife/alcohol, mature advertorials. *(In contribution pipeline)*.
   - `UNSAFE_FOR_ALL`: **NEVER included** in this manifest or in user-facing paths. Prohibited scams, deceptive ads, and malvertising are sequestered in evaluation-only test partitions.
3. **No File Redundancy**: Media files reside within their validated storage roots (`custom_ads/safe_ad_for_all/` and `custom_ads/safe_14_plus/`), referenced directly via portable relative `media_path`s. This avoids duplicating nearly 800 MB of binary media in git.

---

## 📋 Manifest Structure

The master index is [`content_manifest.json`](content_manifest.json).

```json
{
  "manifest_version": "1.0.0",
  "total_items": 200,
  "counts_by_category": {
    "SAFE_FOR_ALL": 100,
    "SAFE_14_PLUS": 100,
    "SAFE_18_PLUS": 0
  },
  "counts_by_type": {
    "image": 150,
    "reel": 50
  },
  "content_items": [
    {
      "content_id": "SAFEAD_SFA_IMG_001",
      "content_type": "image",
      "age_category": "SAFE_FOR_ALL",
      "minimum_age": 0,
      "title": "Everyday Consumer & Home Photo #01",
      "caption": "Wholesome everyday product, gadget, grocery, school, or domestic photo. Universal audience.",
      "media_path": "custom_ads/safe_ad_for_all/images/SAFEAD_SFA_IMG_001.jpg",
      "moderation_status": "APPROVED",
      "source_name": "Wikimedia Commons Open Photography",
      "source_url": "https://commons.wikimedia.org/",
      "license_status": "CC / Public Domain",
      "sha256": "1e69242b50f8b47dc8f74695ef4106c2fab46b5a4680a1aba34496994d67a128",
      "file_size_kb": 66.3,
      "resolution": "221x350"
    },
    {
      "content_id": "SAFEAD_SFA_VID_001",
      "content_type": "reel",
      "age_category": "SAFE_FOR_ALL",
      "minimum_age": 0,
      "title": "Kellogg Frosted Flakes Cereal TV Commercial (1976)",
      "caption": "Authentic television broadcast ad featuring Tony the Tiger, musical jingle with speech audio, and visible product cereal box packaging with slogan text. Universal audience.",
      "media_path": "custom_ads/safe_ad_for_all/videos/SAFEAD_SFA_VID_001.mp4",
      "moderation_status": "APPROVED",
      "source_name": "Internet Archive Classic TV Commercials",
      "source_url": "https://archive.org/download/KelloggsSugarFrostedFlakesCereal1976/Kellogg%27s%20Sugar%20Frosted%20Flakes%20Cereal%20%281976%29.mp4",
      "license_status": "Public Domain / Open TV Archive",
      "sha256": "1f6de8508227063563c1daabb60e10e4622c1ab11c40651187eb033447fae23f",
      "file_size_kb": 2984.1,
      "duration_seconds": 30.21,
      "has_audio": true,
      "contains_text": true
    }
  ]
}
```

---

## 🛠️ Verification Tools

1. **Rebuild Manifest**:
   ```bash
   python tools/build_content_manifest.py
   ```
2. **Validate Manifest**:
   ```bash
   python tools/validate_content_manifest.py
   ```
3. **Run Automated Test Suite**:
   ```bash
   python -m unittest discover tests
   ```

For complete integration instructions with `main_project_s7`, see [`../FRONTEND_INTEGRATION_GUIDE.md`](../FRONTEND_INTEGRATION_GUIDE.md).
