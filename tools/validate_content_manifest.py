"""
validate_content_manifest.py
----------------------------
Automated validation tool for app_content/content_manifest.json.

Verification Rules:
1. Every approved entry points to a physical file that exists on disk.
2. No duplicate content IDs.
3. Every age category is valid (SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS).
4. Media types match file extensions (image vs reel).
5. Every public content item has moderation_status == 'APPROVED'.
6. Unsafe and unreviewed content is strictly prohibited.
7. Minimum age matches the age category (0, 14, 18).
"""

import json
import os
import sys
from pathlib import Path

VALID_CATEGORIES = {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"}
CATEGORY_MIN_AGE = {
    "SAFE_FOR_ALL": 0,
    "SAFE_14_PLUS": 14,
    "SAFE_18_PLUS": 18
}

VALID_TYPES = {"image", "reel"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}

def validate_manifest(manifest_path: Path, repo_root: Path) -> bool:
    if not manifest_path.exists():
        print(f"[FAIL] Manifest file does not exist: {manifest_path}")
        return False

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FAIL] JSON parsing error in {manifest_path}: {e}")
        return False

    items = data.get("content_items", [])
    if not items:
        print("[FAIL] Manifest contains no content_items.")
        return False

    errors = []
    seen_ids = set()
    category_counts = {}
    type_counts = {}

    for idx, item in enumerate(items):
        cid = item.get("content_id")
        ctype = item.get("content_type")
        cat = item.get("age_category")
        min_age = item.get("minimum_age")
        mpath = item.get("media_path")
        mod_status = item.get("moderation_status")

        # 1. Unique ID
        if not cid:
            errors.append(f"Item #{idx}: Missing 'content_id'.")
        elif cid in seen_ids:
            errors.append(f"Item #{idx}: Duplicate content_id '{cid}'.")
        else:
            seen_ids.add(cid)

        # 2. Valid Category & Strict Exclusion of Unsafe
        if cat not in VALID_CATEGORIES:
            errors.append(f"Item {cid}: Invalid age_category '{cat}'. Allowed: {VALID_CATEGORIES}.")
        category_counts[cat] = category_counts.get(cat, 0) + 1

        # 3. Minimum age alignment
        expected_min = CATEGORY_MIN_AGE.get(cat)
        if expected_min is not None and min_age != expected_min:
            errors.append(f"Item {cid}: minimum_age {min_age} does not match expected {expected_min} for category '{cat}'.")

        # 4. Content Type
        if ctype not in VALID_TYPES:
            errors.append(f"Item {cid}: Invalid content_type '{ctype}'. Allowed: {VALID_TYPES}.")
        type_counts[ctype] = type_counts.get(ctype, 0) + 1

        # 5. Moderation Status
        if mod_status != "APPROVED":
            errors.append(f"Item {cid}: moderation_status must be 'APPROVED' (got '{mod_status}'). Unapproved content prohibited.")

        # 6. Media path existence & file extension check
        if not mpath:
            errors.append(f"Item {cid}: Missing 'media_path'.")
        else:
            full_path = repo_root / mpath
            if not full_path.exists():
                errors.append(f"Item {cid}: Referenced media file not found: {mpath}")
            else:
                ext = full_path.suffix.lower()
                if ctype == "image" and ext not in IMAGE_EXTENSIONS:
                    errors.append(f"Item {cid}: Content type is 'image' but file extension is '{ext}'.")
                elif ctype == "reel" and ext not in VIDEO_EXTENSIONS:
                    errors.append(f"Item {cid}: Content type is 'reel' but file extension is '{ext}'.")

    if errors:
        print(f"[FAIL] Found {len(errors)} validation error(s) in {manifest_path.name}:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        return False

    print(f"[PASS] Content manifest validation passed ({len(items)} items).")
    print(f"       Categories: {category_counts}")
    print(f"       Types:      {type_counts}")
    return True

def main():
    repo_root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = repo_root / "app_content" / "content_manifest.json"

    success = validate_manifest(target, repo_root)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
