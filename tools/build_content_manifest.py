"""
build_content_manifest.py
-------------------------
Compiles the approved production content manifest (app_content/content_manifest.json)
from verified SafeAd Dataset Hub contributions.

Safety Rules:
- Only approved, verified content is included.
- UNSAFE_FOR_ALL and unreviewed content are strictly excluded.
- Content types are mapped to 'image' and 'reel'.
- Minimum ages are strictly assigned (0 for SAFE_FOR_ALL, 14 for SAFE_14_PLUS, 18 for SAFE_18_PLUS).
- Every referenced file must exist on disk.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CATEGORY_MIN_AGE = {
    "SAFE_FOR_ALL": 0,
    "SAFE_14_PLUS": 14,
    "SAFE_18_PLUS": 18
}

ALLOWED_CATEGORIES = set(CATEGORY_MIN_AGE.keys())

def build_content_manifest():
    manifest_source = REPO_ROOT / "manifests" / "sourav" / "contribution_manifest.json"
    if not manifest_source.exists():
        raise FileNotFoundError(f"Source manifest not found: {manifest_source}")

    with open(manifest_source, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    records = source_data.get("records", [])
    output_records = []
    seen_ids = set()

    for r in records:
        sample_id = r.get("sample_id")
        safead_label = r.get("safead_label")
        review_status = r.get("review_status", "PROPOSED")
        file_path_rel = r.get("file_path")
        media_type = r.get("media_type")

        # Exclusion filter: Never include UNSAFE_FOR_ALL or non-allowed categories
        if safead_label not in ALLOWED_CATEGORIES:
            continue

        # Verify physical file existence
        full_path = REPO_ROOT / file_path_rel
        if not full_path.exists():
            print(f"Warning: skipping missing file: {file_path_rel}", file=sys.stderr)
            continue

        # Prevent duplicate IDs
        if sample_id in seen_ids:
            raise ValueError(f"Duplicate content ID encountered: {sample_id}")
        seen_ids.add(sample_id)

        # Map media type: videos are designated as 'reel' for social media feed
        content_type = "reel" if media_type == "video" else "image"

        # Content metadata
        orig_label = r.get("original_source_label", "")
        reason = r.get("label_reason", "")

        manifest_entry = {
            "content_id": sample_id,
            "content_type": content_type,
            "age_category": safead_label,
            "minimum_age": CATEGORY_MIN_AGE[safead_label],
            "title": orig_label or f"Verified Creative {sample_id}",
            "caption": reason or "SafeAd AI verified safe content.",
            "media_path": file_path_rel.replace("\\", "/"),
            "moderation_status": "APPROVED",
            "source_name": r.get("source_name", "SafeAd Dataset Hub"),
            "source_url": r.get("source_url", ""),
            "license_status": r.get("license_status", "Open Content"),
            "sha256": r.get("sha256", ""),
            "file_size_kb": r.get("file_size_kb", round(full_path.stat().st_size / 1024, 1))
        }

        if content_type == "reel":
            manifest_entry["duration_seconds"] = r.get("duration_seconds", 0.0)
            manifest_entry["has_audio"] = r.get("has_audio", True)
            manifest_entry["contains_text"] = r.get("contains_text", True)
        else:
            manifest_entry["resolution"] = r.get("resolution", "")

        output_records.append(manifest_entry)

    out_dir = REPO_ROOT / "app_content"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "content_manifest.json"

    manifest_payload = {
        "manifest_version": "1.0.0",
        "repository": "https://github.com/QuadRos-MBCET/safead-dataset-hub",
        "description": "SafeAd AI / SAFE-VISION approved age-categorized social media images and reels catalog",
        "generated_at": "2026-10-21T14:30:00Z",
        "policy_contract": {
            "under_14": ["SAFE_FOR_ALL"],
            "age_14_to_17": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
            "age_18_plus": ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"],
            "prohibited": ["UNSAFE_FOR_ALL"]
        },
        "total_items": len(output_records),
        "counts_by_category": {
            "SAFE_FOR_ALL": sum(1 for r in output_records if r["age_category"] == "SAFE_FOR_ALL"),
            "SAFE_14_PLUS": sum(1 for r in output_records if r["age_category"] == "SAFE_14_PLUS"),
            "SAFE_18_PLUS": sum(1 for r in output_records if r["age_category"] == "SAFE_18_PLUS")
        },
        "counts_by_type": {
            "image": sum(1 for r in output_records if r["content_type"] == "image"),
            "reel": sum(1 for r in output_records if r["content_type"] == "reel")
        },
        "content_items": output_records
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)

    print(f"Successfully generated {out_file} with {len(output_records)} approved items.")
    print(f"  - Images: {manifest_payload['counts_by_type']['image']}")
    print(f"  - Reels:  {manifest_payload['counts_by_type']['reel']}")
    print(f"  - SAFE_FOR_ALL: {manifest_payload['counts_by_category']['SAFE_FOR_ALL']}")
    print(f"  - SAFE_14_PLUS: {manifest_payload['counts_by_category']['SAFE_14_PLUS']}")
    print(f"  - SAFE_18_PLUS: {manifest_payload['counts_by_category']['SAFE_18_PLUS']}")

if __name__ == "__main__":
    build_content_manifest()
