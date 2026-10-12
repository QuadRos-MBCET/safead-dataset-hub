"""
Dataset Summary and Audit Reporter for SafeAd AI.
Generates comprehensive reports covering sample counts, label distributions,
license compliance, integrity verification, and storage metrics.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from tools.manifest_validator import validate_manifest_file
from tools.registry import get_candidate_dataset


def generate_manifest_summary(manifest_path: Path) -> Dict[str, Any]:
    """Analyzes a manifest file and returns detailed statistics."""
    manifest_path = Path(manifest_path)
    is_valid, errors, stats = validate_manifest_file(manifest_path)

    source_id = "unknown"
    license_status = "Unknown"
    storage_size_bytes = 0

    # Read records to extract source_name and check local disk sizes
    if manifest_path.is_file():
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                source_id = r.get("source_name", source_id)
                license_status = r.get("license_status", license_status)
                fp = Path(r.get("file_path", ""))
                if fp.is_file():
                    storage_size_bytes += fp.stat().st_size

    ds_meta = get_candidate_dataset(source_id) or {}

    return {
        "manifest_path": str(manifest_path),
        "source_id": source_id,
        "source_name": ds_meta.get("name", source_id),
        "source_url": ds_meta.get("official_source_url", ""),
        "license_status": license_status,
        "is_valid": is_valid,
        "validation_errors": errors,
        "total_samples": stats.get("total_samples", 0),
        "unique_samples": stats.get("unique_sample_ids", 0),
        "duplicate_hash_count": stats.get("duplicate_hash_count", 0),
        "media_types": stats.get("media_types", {}),
        "safead_labels": stats.get("safead_labels", {}),
        "source_labels": stats.get("source_labels", {}),
        "storage_size_bytes": storage_size_bytes
    }


def format_summary_markdown(summaries: List[Dict[str, Any]]) -> str:
    """Formats multiple dataset summaries into a structured Markdown report."""
    total_samples = sum(s["total_samples"] for s in summaries)
    total_valid = sum(1 for s in summaries if s["is_valid"])

    md = []
    md.append("# SafeAd AI: Existing Dataset Collection Summary Report\n")
    md.append(f"- **Total Candidate Manifests Audited**: {len(summaries)}")
    md.append(f"- **Total Registered Samples**: {total_samples}")
    md.append(f"- **Schema Compliance Rate**: {total_valid} / {len(summaries)} ({(total_valid/len(summaries)*100 if summaries else 0):.1f}%)\n")

    md.append("## Dataset Breakdown Table\n")
    md.append("| Dataset ID | Display Name | Samples | Primary Modality | SafeAd Labels | License Status | Compliance |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for s in summaries:
        modality = ", ".join(s["media_types"].keys()) if s["media_types"] else "N/A"
        safead_summary = ", ".join(f"{k}:{v}" for k, v in s["safead_labels"].items()) if s["safead_labels"] else "None"
        status_badge = "[VALID]" if s["is_valid"] else "[INVALID]"
        md.append(
            f"| `{s['source_id']}` | {s['source_name']} | {s['total_samples']} | {modality} | {safead_summary} | {s['license_status']} | {status_badge} |"
        )

    md.append("\n---\n")
    md.append("## Detailed Dataset Statistics\n")

    for s in summaries:
        md.append(f"### {s['source_name']} (`{s['source_id']}`)")
        md.append(f"- **Manifest**: `{s['manifest_path']}`")
        md.append(f"- **Official URL**: {s['source_url']}")
        md.append(f"- **Verified License**: {s['license_status']}")
        md.append(f"- **Sample Count**: {s['total_samples']}")
        md.append(f"- **Duplicates Detected**: {s['duplicate_hash_count']}")

        md.append("\n**Media Type Distribution:**")
        for mt, cnt in s["media_types"].items():
            md.append(f"  - `{mt}`: {cnt}")

        md.append("\n**SafeAd 4-Tier Label Distribution:**")
        for sl, cnt in s["safead_labels"].items():
            pct = (cnt / s["total_samples"] * 100) if s["total_samples"] else 0
            md.append(f"  - `{sl}`: {cnt} ({pct:.1f}%)")

        md.append("\n**Source Annotations Sample:**")
        top_labels = list(s["source_labels"].items())[:5]
        for slbl, cnt in top_labels:
            md.append(f"  - `{slbl}`: {cnt}")
        if len(s["source_labels"]) > 5:
            md.append(f"  - *(and {len(s['source_labels']) - 5} more source labels)*")

        md.append("\n")

    return "\n".join(md)


def generate_all_reports(
    existing_root: Path,
    output_md_path: Optional[Path] = None
) -> str:
    """Finds all manifests under existing datasets root and creates the summary report."""
    manifest_files = list(existing_root.glob("**/manifest.csv"))
    summaries = [generate_manifest_summary(mf) for mf in manifest_files]
    report_text = format_summary_markdown(summaries)

    if output_md_path:
        out_path = Path(output_md_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_text)

    return report_text


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SafeAd AI Dataset Reporter")
    parser.add_argument("--manifest", type=str, help="Path to single manifest.csv")
    parser.add_argument("--root", default="SafeAd_Dataset/existing_datasets", help="Existing datasets root")
    parser.add_argument("--output-report", default=None, help="Output markdown report file")

    args = parser.parse_args()

    if args.manifest:
        summary = generate_manifest_summary(Path(args.manifest))
        print(json.dumps(summary, indent=2))
    else:
        root_dir = Path(args.root)
        report = generate_all_reports(root_dir, Path(args.output_report) if args.output_report else None)
        print(report)
