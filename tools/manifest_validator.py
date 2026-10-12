"""
Manifest Validation Tool for SafeAd AI.
Enforces compliance with the shared team schema across all contribution manifests.
"""

import csv
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "manifest_schema.json"

REQUIRED_FIELDS = [
    "sample_id",
    "file_path",
    "storage_uri",
    "media_type",
    "source_name",
    "source_url",
    "source_label",
    "safead_label",
    "license_status",
    "sha256",
    "review_status"
]

ALLOWED_SAFEAD_LABELS = {
    "SAFE_FOR_ALL",
    "SAFE_14_PLUS",
    "SAFE_18_PLUS",
    "UNSAFE_FOR_ALL",
    "UNASSIGNED",
    "",
    None
}

ALLOWED_MEDIA_TYPES = {"image", "video", "text", "audio", "multimodal"}
ALLOWED_REVIEW_STATUSES = {"pending", "verified", "flagged", "rejected"}
SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


def validate_manifest_record(record: Dict[str, Any], row_idx: int) -> List[str]:
    """Validates a single manifest record dictionary against schema rules."""
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"Row {row_idx}: Missing required column '{field}'.")

    # Sample ID
    sid = str(record.get("sample_id", "")).strip()
    if not sid:
        errors.append(f"Row {row_idx}: 'sample_id' must not be empty.")

    # Media type
    mtype = str(record.get("media_type", "")).strip().lower()
    if mtype not in ALLOWED_MEDIA_TYPES:
        errors.append(f"Row {row_idx}: Invalid 'media_type' '{mtype}'. Allowed: {ALLOWED_MEDIA_TYPES}")

    # SafeAd label
    s_label = record.get("safead_label")
    s_label_str = "" if s_label is None else str(s_label).strip()
    if s_label_str not in ALLOWED_SAFEAD_LABELS:
        errors.append(
            f"Row {row_idx}: Invalid 'safead_label' '{s_label_str}'. "
            f"Must be one of {sorted([str(x) for x in ALLOWED_SAFEAD_LABELS if x])} or empty/UNASSIGNED."
        )

    # Review status
    rstatus = str(record.get("review_status", "")).strip().lower()
    if rstatus not in ALLOWED_REVIEW_STATUSES:
        errors.append(f"Row {row_idx}: Invalid 'review_status' '{rstatus}'. Allowed: {ALLOWED_REVIEW_STATUSES}")

    # SHA256 checksum format
    checksum = str(record.get("sha256", "")).strip()
    if not SHA256_REGEX.match(checksum):
        errors.append(f"Row {row_idx}: 'sha256' is not a valid 64-character hexadecimal hash: '{checksum}'.")

    return errors


def validate_manifest_file(
    file_path: Union[str, Path],
    verify_on_disk: bool = False
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Validates a CSV or JSON manifest file.
    Returns:
        (is_valid, error_list, summary_stats)
    """
    path = Path(file_path)
    if not path.is_file():
        return False, [f"Manifest file not found: {file_path}"], {}

    records: List[Dict[str, Any]] = []
    if path.suffix.lower() == ".csv":
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                records.append(r)
    elif path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            records = data if isinstance(data, list) else data.get("samples", [])
    else:
        return False, [f"Unsupported manifest format '{path.suffix}'. Use CSV or JSON."], {}

    all_errors: List[str] = []
    seen_ids = set()
    duplicate_ids = []
    seen_hashes = {}
    duplicate_hashes = []

    for idx, rec in enumerate(records, start=1):
        errs = validate_manifest_record(rec, idx)
        all_errors.extend(errs)

        sid = str(rec.get("sample_id", "")).strip()
        if sid:
            if sid in seen_ids:
                duplicate_ids.append(sid)
            else:
                seen_ids.add(sid)

        h = str(rec.get("sha256", "")).strip().lower()
        if h and SHA256_REGEX.match(h):
            if h in seen_hashes:
                duplicate_hashes.append((sid, seen_hashes[h]))
            else:
                seen_hashes[h] = sid

    if duplicate_ids:
        all_errors.append(f"Duplicate sample_id values found: {list(set(duplicate_ids))}")

    stats = {
        "total_samples": len(records),
        "unique_sample_ids": len(seen_ids),
        "unique_sha256": len(seen_hashes),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_hash_count": len(duplicate_hashes),
        "media_types": {},
        "safead_labels": {},
        "source_labels": {}
    }

    for rec in records:
        mt = str(rec.get("media_type", "unknown"))
        stats["media_types"][mt] = stats["media_types"].get(mt, 0) + 1

        sl = str(rec.get("safead_label") or "UNASSIGNED")
        stats["safead_labels"][sl] = stats["safead_labels"].get(sl, 0) + 1

        src_lbl = str(rec.get("source_label", "unknown"))
        stats["source_labels"][src_lbl] = stats["source_labels"].get(src_lbl, 0) + 1

    is_valid = len(all_errors) == 0
    return is_valid, all_errors, stats


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        valid, errs, stats = validate_manifest_file(target)
        if valid:
            print(f"[SUCCESS] Manifest '{target.name}' is valid according to shared schema!")
            print(f"Total samples: {stats['total_samples']}")
            print(f"SafeAd label distribution: {stats['safead_labels']}")
        else:
            print(f"[FAIL] Manifest '{target.name}' failed validation with {len(errs)} errors:")
            for e in errs[:10]:
                print(f"  - {e}")
            if len(errs) > 10:
                print(f"  ... and {len(errs) - 10} more errors.")
    else:
        print("Usage: python tools/manifest_validator.py <path_to_manifest.csv>")
