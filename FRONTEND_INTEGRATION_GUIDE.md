# SAFE-VISION / SafeAd AI — Frontend & Backend Integration Guide

**Document Version**: 2.0.0  
**Target Repository**: `https://github.com/QuadRos-MBCET/main_project_s7`  
**Dataset & Media Repository**: `https://github.com/QuadRos-MBCET/safead-dataset-hub`  
**Effective Date**: October 2026  

---

## 1. Architectural Overview & Boundary Separation

SAFE-VISION couples an AI multimodal moderation pipeline with an age-adaptive social media feed (Instagram-like UI featuring facial authentication, age estimation, and dynamic reels/image playback).

### Critical Boundary Principles:
1. **Catalog vs. Benchmark Separation**:
   - The approved content catalog (`app_content/content_manifest.json`) contains **strictly human-reviewed, age-safe commercial media** approved for frontend user feeds.
   - The evaluation benchmark (`manifests/safead_master_manifest_v2_reconstructed.json`) contains model testing sets, adversarial controls, and quarantined synthetic cards. **The evaluation benchmark must never be exposed to frontend feeds.**
2. **Backend Age Enforcement**:
   - The frontend UI must **not** perform client-side filtering of unauthenticated content.
   - **The backend application service is solely responsible for enforcing age-based access boundaries** based on verified user profile age or facial age estimation outputs before dispatching feed payloads.
3. **Universal Prohibition Exclusion**:
   - `UNSAFE_FOR_ALL` media (scams, phishing, malicious promotions, hazardous content) is **100% excluded** from the approved catalog and must **never** be served in any public feed.

---

## 2. Age-Safety Access Matrix (The Serving Contract)

| User Age Group | Verified Age Range | Permitted Content Categories | Blocked Content Categories |
| :--- | :--- | :--- | :--- |
| **Child User** | Under 14 years old (`age < 14`) | `SAFE_FOR_ALL` (Minimum Age: 0) | `SAFE_14_PLUS`, `SAFE_18_PLUS`, `UNSAFE_FOR_ALL` |
| **Adolescent / Teen** | 14 to 17 years old (`14 <= age < 18`) | `SAFE_FOR_ALL` (0+) + `SAFE_14_PLUS` (14+) | `SAFE_18_PLUS`, `UNSAFE_FOR_ALL` |
| **Adult User** | 18 years and older (`age >= 18`) | `SAFE_FOR_ALL` (0+) + `SAFE_14_PLUS` (14+) + `SAFE_18_PLUS` (18+) | `UNSAFE_FOR_ALL` |
| **Universal Blacklist** | Any audience | **None** | `UNSAFE_FOR_ALL` is permanently blocked |

---

## 3. Approved Content Catalog Schema (`app_content/content_manifest.json`)

The manifest is located at `app_content/content_manifest.json`.

### 3.1. Top-Level Structure
```json
{
  "manifest_version": "2.0.0",
  "repository": "https://github.com/QuadRos-MBCET/safead-dataset-hub",
  "description": "SafeAd AI / SAFE-VISION approved age-categorized social media images and reels catalog",
  "generated_at": "2026-10-22T07:30:00Z",
  "policy_contract": {
    "under_14": ["SAFE_FOR_ALL"],
    "age_14_to_17": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
    "age_18_plus": ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"],
    "prohibited": []
  },
  "total_items": 249,
  "counts_by_category": {
    "SAFE_FOR_ALL": 170,
    "SAFE_14_PLUS": 30,
    "SAFE_18_PLUS": 49
  },
  "counts_by_type": {
    "image": 174,
    "reel": 75
  },
  "content_items": [ ... ]
}
```

### 3.2. Content Item Fields
```json
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
}
```

For video reels (`content_type == "reel"`), additional fields are provided:
- `duration_seconds`: Video duration (e.g., `30.0`).
- `has_audio`: `true`.
- `contains_text`: `true`.
- `reel_thumbnail`: Relative path to preview thumbnail image.

---

## 4. Backend Implementation Guide (Python / FastAPI Example)

The main application backend service should load the manifest once on startup and expose an authenticated, age-gated `/api/feed` endpoint.

```python
import json
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="SAFE-VISION Feed Service")

DATASET_HUB_PATH = Path("/path/to/safead-dataset-hub")
MANIFEST_PATH = DATASET_HUB_PATH / "app_content" / "content_manifest.json"

# Load catalog into memory
with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    CATALOG = json.load(f)["content_items"]

def get_permitted_categories(user_age: int) -> List[str]:
    """Applies the SAFE-VISION age-safety contract."""
    if user_age < 14:
        return ["SAFE_FOR_ALL"]
    elif user_age < 18:
        return ["SAFE_FOR_ALL", "SAFE_14_PLUS"]
    else:
        return ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"]

@app.get("/api/feed")
def get_user_feed(
    user_age: int = Query(..., description="Verified age from face estimation or user profile"),
    media_type: Optional[str] = Query(None, regex="^(image|reel)$"),
    limit: int = Query(20, le=100)
):
    """
    Returns an age-appropriate advertisement and social media feed.
    Strictly gates content by minimum_age and approved categories.
    """
    if user_age < 0:
        raise HTTPException(status_code=400, detail="Invalid user age")
        
    permitted_categories = get_permitted_categories(user_age)
    
    # Filter catalog
    feed = [
        item for item in CATALOG
        if item["age_category"] in permitted_categories
        and item["minimum_age"] <= user_age
        and (media_type is None or item["content_type"] == media_type)
    ]
    
    # Format absolute static URL for frontend image/video player
    formatted_feed = []
    for item in feed[:limit]:
        entry = dict(item)
        entry["media_url"] = f"/static/media/{item['media_path']}"
        formatted_feed.append(entry)
        
    return {
        "user_age": user_age,
        "permitted_categories": permitted_categories,
        "feed_count": len(formatted_feed),
        "feed": formatted_feed
    }
```

---

## 5. Authenticated & Authorized Media Delivery (Strict Security Contract)

> **CRITICAL SECURITY REQUIREMENT**: 
> **Never expose raw media directories through an unrestricted public static web folder.** Serving `custom_ads/` via an open public directory bypasses age verification, allowing underage clients or web scrapers to download `SAFE_18_PLUS` adult content directly by URL tampering.

### Required Architecture:
Media delivery must be gated by the backend authorization layer using either **Authorized Streaming** or **Signed Short-Lived Tokens**:

#### Option A: Authenticated Backend Streaming Route (Local & Server Deployments)
The backend streams media only after validating user identity and age against the content's `minimum_age`:

```python
import hmac
import hashlib
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse

# Index catalog by content_id for fast lookup
CATALOG_BY_ID = {item["content_id"]: item for item in CATALOG}

def get_current_user_age(authorization: str = Header(...)) -> int:
    """Validates session JWT/token and returns verified user age from authentication service."""
    # Verification logic against main_project_s7 auth/face recognition pipeline
    verified_age = verify_session_token_and_get_age(authorization)
    return verified_age

@app.get("/api/media/{content_id}")
def stream_authorized_media(
    content_id: str,
    user_age: int = Depends(get_current_user_age)
):
    """
    Streams media content only if user's verified age satisfies the item's minimum_age.
    Returns HTTP 403 if the user is underage.
    """
    if content_id not in CATALOG_BY_ID:
        raise HTTPException(status_code=404, detail="Content asset not found")
        
    item = CATALOG_BY_ID[content_id]
    
    # Enforce age gate at the media byte level
    if user_age < item["minimum_age"]:
        raise HTTPException(
            status_code=403, 
            detail=f"Age restriction policy: User age {user_age} is below required minimum age {item['minimum_age']} for this creative."
        )
        
    media_file_path = DATASET_HUB_PATH / item["media_path"]
    if not media_file_path.is_file():
        raise HTTPException(status_code=404, detail="Underlying media file missing")
        
    media_type = "video/mp4" if item["content_type"] == "reel" else "image/jpeg"
    return FileResponse(media_file_path, media_type=media_type)
```

#### Option B: Signed Ephemeral URLs (Cloud CDN / S3 Deployments)
When offloading media delivery to cloud storage (e.g. AWS S3, Google Cloud Storage, Cloudflare):
- The backend generates **short-lived signed URLs** (10–15 minute expiry) only for items permitted for the requesting user's age.
- Direct bucket access is strictly private (`private` ACL / Block Public Access enabled).
- URLs expire rapidly, preventing link sharing across age demographics.

---

## 6. Reel Playback Recommendations for Frontend UI

- **Aspect Ratio**: Recomended container is `9:16` vertical reel container or `4:5` feed container with centered fit and background blur.
- **Audio Autoplay**: Autoplay muted with user tap-to-unmute control.
- **Looping**: Infinite loop for short promotional reels.
- **Caption Overlay**: Display `title` and `caption` over a subtle dark gradient at the bottom 25% of the video container.
