#!/usr/bin/env python3
"""SafeAd Dataset Hub - Collection & Manifest Management Tool

Supports:
- Importing permitted local images and videos into category folders.
- Registering new advertisement records.
- Validating supported file formats.
- Computing SHA-256 checksums and detecting exact duplicates.
- Flagging possible near-duplicates (content similarity / duplicate sources or hashes).
- Validating records against schema and flagging missing sources/licenses.
- Exporting/updating contributor manifests.
- Generating category-wise progress reports against targets.
"""

import os
import sys
import json
import hashlib
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
VALID_LABELS = {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"}
VALID_REVIEW_STATUSES = {"PROPOSED", "ACCEPTED", "REJECTED", "NEEDS_REVIEW"}
VALID_ANNOTATION_STATUSES = {"COMPLETED", "IN_PROGRESS", "PENDING"}

TARGET_COUNTS = {
    "SAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
    "SAFE_14_PLUS": {"image": 75, "video": 25, "total": 100},
}


def compute_sha256(filepath: str | Path) -> str:
    """Computes SHA-256 checksum of a file in streaming chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


def detect_media_type(filename_or_path: str | Path) -> Optional[str]:
    """Detects media type (image or video) based on extension."""
    ext = Path(filename_or_path).suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTS:
        return "image"
    if ext in SUPPORTED_VIDEO_EXTS:
        return "video"
    return None


class SafeAdCollector:
    def __init__(self, workspace_root: str | Path, contributor: str = "sourav"):
        self.workspace_root = Path(workspace_root).resolve()
        self.contributor = contributor
        self.storage_base = self.workspace_root / "SafeAd_Dataset" / "custom_ads" / contributor
        self.manifest_path = self.workspace_root / "manifests" / contributor / "contribution_manifest.json"
        self.records: List[Dict[str, Any]] = []
        self._load_manifest()

    def _load_manifest(self) -> None:
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
            except Exception as e:
                print(f"[Warning] Failed to load existing manifest: {e}", file=sys.stderr)
                self.records = []
        else:
            self.records = []

    def save_manifest(self) -> None:
        """Saves contributor manifest with standard structure."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_data = {
            "contributor": self.contributor,
            "assigned_categories": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
            "branch": f"feature/{self.contributor}-safe-for-all-14-plus",
            "storage_root": f"SafeAd_Dataset/custom_ads/{self.contributor}/",
            "generated_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "records": self.records,
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

    def import_and_register_sample(
        self,
        src_file: str | Path,
        safead_label: str,
        source_name: str,
        source_url: str,
        label_reason: str,
        license_status: str,
        sample_id: Optional[str] = None,
        original_source_label: Optional[str] = None,
        review_status: str = "PROPOSED",
        copy_file: bool = True,
    ) -> Dict[str, Any]:
        """Imports local media file, validates format, calculates SHA256, and registers record."""
        src_path = Path(src_file)
        if not src_path.exists():
            raise FileNotFoundError(f"Source media file not found: {src_file}")

        media_type = detect_media_type(src_path)
        if not media_type:
            raise ValueError(f"Unsupported media extension: {src_path.suffix}")

        if safead_label not in VALID_LABELS:
            raise ValueError(f"Invalid SafeAd label: {safead_label}")

        sha256_hash = compute_sha256(src_path)

        # Check exact duplicate within existing records
        for r in self.records:
            if r.get("sha256") == sha256_hash:
                raise ValueError(
                    f"Duplicate media detected: hash {sha256_hash} matches existing sample {r.get('sample_id')}"
                )

        # Generate sample_id if not provided
        category_prefix = "SFA" if safead_label == "SAFE_FOR_ALL" else "S14P" if safead_label == "SAFE_14_PLUS" else "SAD"
        media_code = "IMG" if media_type == "image" else "VID"
        if not sample_id:
            count = sum(1 for r in self.records if r.get("safead_label") == safead_label and r.get("media_type") == media_type) + 1
            sample_id = f"SAFEAD_{self.contributor.upper()}_{category_prefix}_{media_code}_{count:03d}"

        # Target subfolder relative path
        category_dir = "safe_for_all" if safead_label == "SAFE_FOR_ALL" else "safe_14_plus"
        filename = f"{sample_id}{src_path.suffix.lower()}"
        rel_path = f"SafeAd_Dataset/custom_ads/{self.contributor}/{category_dir}/{filename}"
        dest_path = self.workspace_root / rel_path

        if copy_file:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)

        record = {
            "sample_id": sample_id,
            "file_path": rel_path.replace("\\", "/"),
            "storage_uri": f"gdrive://{rel_path.replace('\\', '/')}",
            "media_type": media_type,
            "source_name": source_name,
            "source_url": source_url,
            "original_source_label": original_source_label or "Unlabeled Ad",
            "collection_date": datetime.now().strftime("%Y-%m-%d"),
            "safead_label": safead_label,
            "label_reason": label_reason,
            "license_status": license_status,
            "sha256": sha256_hash,
            "annotation_status": "COMPLETED",
            "review_status": review_status,
        }

        self.records.append(record)
        return record

    def validate_records(self) -> Dict[str, Any]:
        """Validates all records in the manifest for completeness, errors, and duplicates."""
        errors = []
        warnings = []
        seen_ids = set()
        seen_hashes = {}
        seen_sources = {}

        for idx, rec in enumerate(self.records):
            sid = rec.get("sample_id")
            if not sid:
                errors.append(f"Record #{idx} missing sample_id.")
            elif sid in seen_ids:
                errors.append(f"Duplicate sample_id found: {sid}")
            else:
                seen_ids.add(sid)

            # Check absolute paths leak
            fpath = rec.get("file_path", "")
            if ":\\" in fpath or fpath.startswith("/Users/"):
                errors.append(f"Record {sid} contains absolute path in file_path: {fpath}")

            # Validate fields
            for req in [
                "sample_id", "file_path", "storage_uri", "media_type", "source_name",
                "source_url", "safead_label", "label_reason", "license_status",
                "sha256", "annotation_status", "review_status"
            ]:
                val = rec.get(req)
                if val is None or (isinstance(val, str) and not val.strip()):
                    errors.append(f"Record {sid} missing required field: {req}")

            # Validate label
            lbl = rec.get("safead_label")
            if lbl not in VALID_LABELS:
                errors.append(f"Record {sid} invalid safead_label: {lbl}")

            # Validate review status
            rev = rec.get("review_status")
            if rev not in VALID_REVIEW_STATUSES:
                errors.append(f"Record {sid} invalid review_status: {rev}")

            # Exact duplicate check via hash
            sha = rec.get("sha256")
            if sha:
                if sha in seen_hashes:
                    errors.append(f"Exact duplicate detected: {sid} matches {seen_hashes[sha]} (hash: {sha})")
                else:
                    seen_hashes[sha] = sid

            # Near-duplicate check: identical source_url with same label
            src_url = rec.get("source_url")
            if src_url and src_url != "N/A":
                if src_url in seen_sources and seen_sources[src_url] != sid:
                    warnings.append(
                        f"Near-duplicate check: {sid} shares identical source_url with {seen_sources[src_url]}: {src_url}"
                    )
                else:
                    seen_sources[src_url] = sid

            # Missing license or source warning
            lic = rec.get("license_status", "").lower()
            if lic in {"unknown", "none", "unspecified", ""}:
                warnings.append(f"Record {sid} has unverified or missing license: '{rec.get('license_status')}'")

        return {
            "total_records": len(self.records),
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0,
        }

    def generate_progress_report(self) -> Dict[str, Any]:
        """Calculates category progress against targets."""
        counts = {
            "SAFE_FOR_ALL": {"image": 0, "video": 0, "total": 0},
            "SAFE_14_PLUS": {"image": 0, "video": 0, "total": 0},
            "OTHER": {"image": 0, "video": 0, "total": 0},
        }
        review_counts = {
            "PROPOSED": 0,
            "ACCEPTED": 0,
            "REJECTED": 0,
            "NEEDS_REVIEW": 0,
        }

        for r in self.records:
            lbl = r.get("safead_label", "OTHER")
            mtype = r.get("media_type", "image")
            rstatus = r.get("review_status", "PROPOSED")

            bucket = counts.get(lbl, counts["OTHER"])
            if mtype in bucket:
                bucket[mtype] += 1
            bucket["total"] += 1

            if rstatus in review_counts:
                review_counts[rstatus] += 1

        report = {
            "counts_by_category": counts,
            "review_status_counts": review_counts,
            "targets": TARGET_COUNTS,
            "total_collected": len(self.records),
        }
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SafeAd Dataset Collector")
    parser.add_argument("--workspace", default=".", help="Path to repository workspace root")
    parser.add_argument("--validate", action="store_true", help="Validate existing contribution manifest")
    parser.add_argument("--report", action="store_true", help="Display progress and category report")
    args = parser.parse_args()

    collector = SafeAdCollector(args.workspace)

    if args.validate:
        val = collector.validate_records()
        print(f"Validation Status: {'PASS' if val['is_valid'] else 'FAIL'}")
        print(f"Total Records: {val['total_records']}")
        if val["errors"]:
            print("Errors:")
            for err in val["errors"]:
                print(f" - {err}")
        if val["warnings"]:
            print("Warnings:")
            for w in val["warnings"]:
                print(f" - {w}")
        sys.exit(0 if val["is_valid"] else 1)

    if args.report:
        rep = collector.generate_progress_report()
        print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
