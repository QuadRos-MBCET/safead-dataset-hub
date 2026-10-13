#!/usr/bin/env python3
"""SafeAd Model Training Export Adapter

Exports valid and accepted ad records from manifests into clean tabular formats (CSV, JSON Lines)
for immediate consumption by the SafeAd / SAFE-VISION training pipelines in `QuadRos-MBCET/main_project_s7`.
"""

import sys
import json
import csv
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

LABEL_TO_ID = {
    "SAFE_FOR_ALL": 0,
    "SAFE_14_PLUS": 1,
    "SAFE_18_PLUS": 2,
    "UNSAFE_FOR_ALL": 3,
}


def export_dataset(output_format: str = "csv", include_needs_review: bool = False):
    manifests_dir = WORKSPACE_ROOT / "manifests"
    all_records = []

    for manifest_path in manifests_dir.rglob("*.json"):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data.get("records", [])
                for r in records:
                    r["_origin_manifest"] = manifest_path.name
                    all_records.append(r)
        except Exception as e:
            print(f"[Warning] Failed to parse {manifest_path}: {e}", file=sys.stderr)

    # Filter records
    training_samples = []
    skipped_count = 0

    for r in all_records:
        rev = r.get("review_status", "")
        if not include_needs_review and rev == "NEEDS_REVIEW":
            skipped_count += 1
            continue

        label_name = r.get("safead_label")
        if label_name not in LABEL_TO_ID:
            continue

        training_samples.append({
            "sample_id": r.get("sample_id"),
            "file_path": r.get("file_path"),
            "storage_uri": r.get("storage_uri"),
            "media_type": r.get("media_type"),
            "label_name": label_name,
            "label_id": LABEL_TO_ID[label_name],
            "label_reason": r.get("label_reason"),
            "review_status": rev,
            "license": r.get("license_status"),
            "sha256": r.get("sha256"),
        })

    out_dir = WORKSPACE_ROOT / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)

    if output_format == "csv":
        out_file = out_dir / "safead_training_manifest.csv"
        with open(out_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(training_samples[0].keys()))
            writer.writeheader()
            writer.writerows(training_samples)
        print(f"Exported {len(training_samples)} training rows to {out_file}")
    else:
        out_file = out_dir / "safead_training_manifest.jsonl"
        with open(out_file, "w", encoding="utf-8") as f:
            for item in training_samples:
                f.write(json.dumps(item) + "\n")
        print(f"Exported {len(training_samples)} training rows to {out_file}")

    print(f"Total processed: {len(all_records)} (Included: {len(training_samples)}, Skipped pending review: {skipped_count})")


if __name__ == "__main__":
    fmt = sys.argv[1] if len(sys.argv) > 1 else "csv"
    export_dataset(output_format=fmt)
