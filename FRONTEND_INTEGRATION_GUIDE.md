# SAFE-VISION / SafeAd AI — Frontend & Backend Integration Guide

This guide provides instructions and architectural contracts for integrating approved, age-categorized social media images and reels from `safead-dataset-hub` into the main application (`main_project_s7`).

---

## 1. Actual Content Folder Structure

In `safead-dataset-hub`, content is curated into two distinct layers:
1. **Public/Approved Content Serving Layer (`app_content/`)**: Clean metadata catalog referencing verified assets approved for user feeds.
2. **Curated Media Storage (`custom_ads/`)**: High-resolution genuine images and broadcast MP4 video reels.
3. **Evaluation & Audit Partition (`SafeAd_Dataset/` & `custom_ads/unsafe_for_all/`)**: Reference benchmarks, scam examples, and testing data preserved strictly for AI policy accuracy defense.

```text
safead-dataset-hub/
├── app_content/
│   ├── README.md                          # Content serving overview
│   └── content_manifest.json              # Master production manifest (200 approved items)
│
├── custom_ads/
│   ├── safe_ad_for_all/
│   │   ├── images/                        # 75 verified photos (SAFEAD_SFA_IMG_001.jpg - 075.jpg)
│   │   └── videos/                        # 25 authentic broadcast reels (SAFEAD_SFA_VID_001.mp4 - 025.mp4)
│   ├── safe_14_plus/
│   │   ├── images/                        # 75 verified photos (SAFEAD_S14P_IMG_001.jpg - 075.jpg)
│   │   └── videos/                        # 25 authentic broadcast reels (SAFEAD_S14P_VID_001.mp4 - 025.mp4)
│   └── unsafe_for_all/                    # 11 scam images & 3 scam reels (STRICTLY EXCLUDED from feed)
│
├── manifests/
│   ├── sourav/contribution_manifest.json  # Raw evaluation dataset manifest
│   ├── juwel/contribution_manifest.json   # 18+ & Unsafe pipeline branch manifest
│   └── coordinator/public_datasets.json   # Benchmark reference manifests
│
├── schemas/
│   ├── content_manifest_schema.json       # JSON Schema for app_content manifest
│   └── sample_schema.json                 # JSON Schema for dataset contributions
│
├── tools/
│   ├── build_content_manifest.py          # Builds app_content/content_manifest.json
│   └── validate_content_manifest.py       # Strict automated CI validator
│
├── tests/
│   └── test_content_manifest.py           # PyUnit test suite for content integrity
│
└── FRONTEND_INTEGRATION_GUIDE.md          # This integration specification
```

---

## 2. Reading the Content Manifest

The main application backend reads [`app_content/content_manifest.json`](app_content/content_manifest.json).

### Top-level Structure:
```json
{
  "manifest_version": "1.0.0",
  "repository": "https://github.com/QuadRos-MBCET/safead-dataset-hub",
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
  "content_items": [ ... ]
}
```

### Content Item Schema:
| Field | Type | Description | Example |
|---|---|---|---|
| `content_id` | `string` | Unique sample identifier | `"SAFEAD_SFA_IMG_001"` |
| `content_type` | `string` | Modality designation: `"image"` or `"reel"` | `"image"` |
| `age_category` | `string` | Safety policy classification | `"SAFE_FOR_ALL"` |
| `minimum_age` | `integer` | Minimum chronological age allowed | `0` |
| `title` | `string` | Title or commercial headline | `"Kellogg Frosted Flakes Cereal TV Commercial (1976)"` |
| `caption` | `string` | Caption or safety policy justification | `"Wholesome everyday product photo. Universal audience."` |
| `media_path` | `string` | Relative path from repository root | `"custom_ads/safe_ad_for_all/images/SAFEAD_SFA_IMG_001.jpg"` |
| `moderation_status` | `string` | Approval state (must be `"APPROVED"`) | `"APPROVED"` |
| `source_name` | `string` | Content source or license provider | `"Internet Archive Classic TV Commercials"` |
| `source_url` | `string` | Original public archive source URL | `"https://archive.org/download/..."` |
| `license_status` | `string` | Legal licensing status | `"Public Domain / Open TV Archive"` |
| `sha256` | `string` | SHA-256 binary hash for integrity verification | `"1f6de8508227063563c1daabb60e10e4622c1ab11c40651187eb033447fae23f"` |
| `file_size_kb` | `float` | File size in kilobytes | `2984.1` |
| `duration_seconds` | `float` | Runtime duration for reels (seconds) | `30.21` |
| `has_audio` | `boolean` | Indicates active audio stream for reels | `true` |
| `contains_text` | `boolean` | Indicates visible typography or brand logos | `true` |
| `resolution` | `string` | Pixel resolution for images | `"3024x2697"` |

---

## 3. How the Main Application Should Resolve Media Paths

Paths in `content_manifest.json` are specified **relative to the root of `safead-dataset-hub`**.

### Recommended Deployment Options:

#### Option A: Sibling Repository / Local Directory Sync (Recommended for Dev & Demo)
Configure an environment variable `DATASET_HUB_ROOT` in the main application's `.env`:
```env
DATASET_HUB_ROOT=../safead-dataset-hub
```
In Python:
```python
import os
from pathlib import Path

DATASET_ROOT = Path(os.getenv("DATASET_HUB_ROOT", "../safead-dataset-hub")).resolve()

def resolve_media_path(manifest_entry: dict) -> Path:
    target_path = DATASET_ROOT / manifest_entry["media_path"]
    if not target_path.exists():
        raise FileNotFoundError(f"Media file not found at: {target_path}")
    return target_path
```

#### Option B: Automated Sync Script into `main_project_s7/uploads/`
Use a background sync script (see Section 8) to copy or symlink approved media into the main backend's `uploads/` folder or database.

#### Option C: FastAPI Static Media Mount
In `main_project_s7/backend/app/main.py`:
```python
from fastapi.staticfiles import StaticFiles

# Expose media through a protected media route
app.mount("/api/media", StaticFiles(directory=str(DATASET_ROOT / "custom_ads")), name="media")
```

---

## 4. How Age Categories Are Represented & Filtered

### Age Categories:
- `SAFE_FOR_ALL`: Unrestricted content suitable for all ages.
- `SAFE_14_PLUS`: Content geared toward teens and adults (gaming peripherals, action sports, youth fashion).
- `SAFE_18_PLUS`: Age-gated content restricted to verified legal adults (financial investments, mature topics).
- `UNSAFE_FOR_ALL`: Scams, deceptive advertorials, and prohibited content. **Never served in user feeds.**

### User Age-Gating Access Matrix:

| Verified User Age Bracket | Minimum Age Required | Permitted Content Categories | Forbidden Categories |
|---|---|---|---|
| **Under 14** (`UNDER_14`) | 0 | `SAFE_FOR_ALL` | `SAFE_14_PLUS`, `SAFE_18_PLUS`, `UNSAFE_FOR_ALL` |
| **14 to 17** (`AGE_14_TO_17`) | 14 | `SAFE_FOR_ALL`, `SAFE_14_PLUS` | `SAFE_18_PLUS`, `UNSAFE_FOR_ALL` |
| **18 and Above** (`AGE_18_PLUS`) | 18 | `SAFE_FOR_ALL`, `SAFE_14_PLUS`, `SAFE_18_PLUS` | `UNSAFE_FOR_ALL` |

### Backend Enforcement Logic:
```python
def is_content_permitted(item_category: str, user_age_group: str) -> bool:
    """
    Evaluates whether the user's verified age bracket authorizes access to the content.
    """
    if item_category == "UNSAFE_FOR_ALL":
        return False
        
    if user_age_group == "UNDER_14":
        return item_category == "SAFE_FOR_ALL"
    elif user_age_group == "AGE_14_TO_17":
        return item_category in ["SAFE_FOR_ALL", "SAFE_14_PLUS"]
    elif user_age_group == "AGE_18_PLUS":
        return item_category in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"]
        
    # Conservative fallback for unverified or uncertain sessions
    return item_category == "SAFE_FOR_ALL"
```

---

## 5. How Images and Reels Are Distinguished

- **Images (`content_type: "image"`)**:
  - Formats: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Served in the main Instagram Home Feed (`/api/feed`).
  - Rendered with `st.image()` in Streamlit or `<img>` in web clients.
- **Reels (`content_type: "reel"`)**:
  - Formats: `.mp4` (H.264 + AAC Stereo)
  - Contains audio dialogue/music and on-screen text.
  - Served in the Reels tab (`/api/reels`).
  - Rendered with `st.video()` in Streamlit or `<video>` player in web clients.

---

## 6. How to Add New Approved Content

1. **Place Media Files**:
   - For `SAFE_FOR_ALL`: Place images in `custom_ads/safe_ad_for_all/images/` and videos in `custom_ads/safe_ad_for_all/videos/`.
   - For `SAFE_14_PLUS`: Place images in `custom_ads/safe_14_plus/images/` and videos in `custom_ads/safe_14_plus/videos/`.
   - For `SAFE_18_PLUS`: Place in `custom_ads/safe_18_plus/images/` or `videos/`.
2. **Naming Convention**:
   - Images: `SAFEAD_SFA_IMG_xxx.jpg`, `SAFEAD_S14P_IMG_xxx.jpg`, `SAFEAD_S18P_IMG_xxx.jpg`
   - Reels: `SAFEAD_SFA_VID_xxx.mp4`, `SAFEAD_S14P_VID_xxx.mp4`, `SAFEAD_S18P_VID_xxx.mp4`
3. **Verify Compliance**:
   - Ensure media is licensed (CC / Public Domain / authorized creative).
   - Compute SHA-256 hash.
4. **Update Manifest**:
   - Add entry to the contributor manifest (`manifests/<name>/contribution_manifest.json`) or run `python tools/build_content_manifest.py`.
5. **Run Validation**:
   - Run `python tools/validate_content_manifest.py`.

---

## 7. How to Update the Manifest

Run the automated build tool:
```bash
python tools/build_content_manifest.py
```
Then run the automated test suite to ensure schema and policy compliance:
```bash
python tools/validate_content_manifest.py
python -m unittest discover tests
```

---

## 8. How the Main Backend Should Synchronize Content

The main application backend (`main_project_s7`) can synchronize approved content directly into its SQLite/MySQL database.

### Integration Script for `main_project_s7`:
Create a script in `main_project_s7/tools/sync_from_dataset_hub.py`:

```python
"""
Syncs approved items from safead-dataset-hub into main_project_s7 database.
"""
import json
import os
from pathlib import Path
from backend.app.db.database import SessionLocal
from backend.app.db.models import Advertisement, ModerationResult, SafetyClassification, ModerationAction

HUB_ROOT = Path(os.getenv("DATASET_HUB_ROOT", "../../safead-dataset-hub")).resolve()
MANIFEST_PATH = HUB_ROOT / "app_content" / "content_manifest.json"

CATEGORY_MAPPING = {
    "SAFE_FOR_ALL": SafetyClassification.SAFE_FOR_ALL,
    "SAFE_14_PLUS": SafetyClassification.AGE_14_PLUS,
    "SAFE_18_PLUS": SafetyClassification.AGE_18_PLUS
}

def sync_catalog():
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found at {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    imported_count = 0

    try:
        for item in data.get("content_items", []):
            full_media_path = str((HUB_ROOT / item["media_path"]).resolve())
            
            # Check if ad already imported
            existing = db.query(Advertisement).filter(Advertisement.file_path == full_media_path).first()
            if existing:
                continue

            # 1. Create Advertisement record
            ad = Advertisement(
                title=item["title"],
                caption=item["caption"],
                file_path=full_media_path,
                media_type="video" if item["content_type"] == "reel" else "image",
                status="APPROVED",
                owner_id=1  # Default system/curator account
            )
            db.add(ad)
            db.commit()
            db.refresh(ad)

            # 2. Create ModerationResult record
            classification = CATEGORY_MAPPING[item["age_category"]]
            action = ModerationAction.APPROVE if classification == SafetyClassification.SAFE_FOR_ALL else ModerationAction.RESTRICT
            
            mod_result = ModerationResult(
                advertisement_id=ad.id,
                model_version="SafeAd_DatasetHub_V1",
                classification=classification,
                risk_category="general_creative",
                risk_score=0.0,
                risk_score_available=True,
                explanation=item["caption"],
                evidence=f"Source: {item['source_name']}; License: {item['license_status']}",
                moderation_action=action,
                age_restriction=item["minimum_age"],
                publishable=True
            )
            db.add(mod_result)
            db.commit()
            imported_count += 1

        print(f"✅ Successfully synchronized {imported_count} new media items into SAFE-VISION database.")
    finally:
        db.close()

if __name__ == "__main__":
    sync_catalog()
```

---

## 9. How Restricted Content Must Be Protected

1. **Authentication Token Binding**: The backend must extract the user's verified age bracket from the validated session/JWT token (`st.session_state["verified_age_norm"]` or user database entry). Never trust an unverified client parameter.
2. **Never Return Unsafe Content**: Even for adult users (`AGE_18_PLUS`), `UNSAFE_FOR_ALL` items must be filtered out at the query level (`Advertisement.status != "REJECT"`).
3. **Conservative Default on Ambiguity**: If biometric or ID card age estimation is inconclusive or in `PENDING`/`CONFLICT` status, the backend must default the user to `UNDER_14`, serving only `SAFE_FOR_ALL` content until verified.
4. **Direct File Path Shielding**: Media URLs must not expose raw filesystem directories or allow path traversal (`../`). Media should be streamed via `/api/content/{content_id}` with age verification performed on each request.

---

## 10. How the Frontend Developer Can Test the Integration

### Step 1: Validate the Hub Manifest
In the `safead-dataset-hub` directory:
```powershell
python tools/validate_content_manifest.py
python -m unittest discover tests
```
Both commands must report `[PASS]` and `OK`.

### Step 2: Test Endpoint Mocking
Using Python requests or FastAPI test client:
```python
import json
from pathlib import Path

# Load manifest
with open("app_content/content_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

items = manifest["content_items"]

# Simulate Child user (Age 10)
child_feed = [it for it in items if it["minimum_age"] == 0]
assert all(it["age_category"] == "SAFE_FOR_ALL" for it in child_feed)
print(f"Child Feed: {len(child_feed)} items (All SAFE_FOR_ALL)")

# Simulate Teen user (Age 16)
teen_feed = [it for it in items if it["minimum_age"] <= 14]
assert all(it["age_category"] in ["SAFE_FOR_ALL", "SAFE_14_PLUS"] for it in teen_feed)
print(f"Teen Feed: {len(teen_feed)} items (SAFE_FOR_ALL + SAFE_14_PLUS)")

# Simulate Adult user (Age 22)
adult_feed = [it for it in items if it["minimum_age"] <= 18]
print(f"Adult Feed: {len(adult_feed)} items (All safe tiers)")
```

### Step 3: Verify Frontend Display in `user_workspace.py`
In `main_project_s7/frontend/views/user_workspace.py`:
- In the **Reels Tab**, verify that only reels where `is_ad_allowed_for_age(policy, user_cat)` is `True` appear in `curated_reels`.
- In the **Instagram Home Feed**, verify that approved images are displayed with the proper verification badge:
  `🛡️ Sponsored • Verified for {user_cat} ({classification})`.
