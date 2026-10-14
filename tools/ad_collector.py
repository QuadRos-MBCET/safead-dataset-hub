#!/usr/bin/env python3
"""SafeAd Dataset Hub - Collection & Manifest Management Tool

Supports:
- Importing permitted local images and videos into contributor category folders.
- Registering new advertisement records according to shared schema.
- Validating supported file formats (image: jpg, png, webp, bmp; video: mp4, avi, mov, mkv, webm).
- Computing SHA-256 checksums and detecting exact duplicates.
- Flagging possible near-duplicates (content similarity, identical source URLs).
- Checking missing or corrupted files on disk.
- Validating records against schema and flagging missing sources/licenses.
- Exporting/updating contributor manifests.
- Generating category-wise progress reports against assigned targets for Sourav and Juwel.
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

CATEGORY_PREFIX_MAP = {
    "SAFE_FOR_ALL": "SFA",
    "SAFE_14_PLUS": "S14P",
    "SAFE_18_PLUS": "S18P",
    "UNSAFE_FOR_ALL": "UFA",
}

CATEGORY_DIR_MAP = {
    "SAFE_FOR_ALL": "safe_for_all",
    "SAFE_14_PLUS": "safe_14_plus",
    "SAFE_18_PLUS": "safe_18_plus",
    "UNSAFE_FOR_ALL": "unsafe_for_all",
}

CONTRIBUTOR_CONFIGS = {
    "sourav": {
        "contributor_display": "sourav",
        "assigned_categories": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
        "branch": "feature/sourav-safe-for-all-14-plus",
        "target_counts": {
            "SAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
            "SAFE_14_PLUS": {"image": 75, "video": 25, "total": 100},
        },
    },
    "juwel": {
        "contributor_display": "Juwel",
        "assigned_categories": ["SAFE_18_PLUS", "UNSAFE_FOR_ALL"],
        "branch": "feature/juwel-18-plus-unsafe",
        "target_counts": {
            "SAFE_18_PLUS": {"image": 75, "video": 25, "total": 100},
            "UNSAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
        },
    },
}

# Default target counts for backward compatibility with existing tests
TARGET_COUNTS = {
    "SAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
    "SAFE_14_PLUS": {"image": 75, "video": 25, "total": 100},
    "SAFE_18_PLUS": {"image": 75, "video": 25, "total": 100},
    "UNSAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
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
        self.contributor = contributor.strip().lower()
        self.cfg = CONTRIBUTOR_CONFIGS.get(
            self.contributor,
            {
                "contributor_display": contributor,
                "assigned_categories": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
                "branch": f"feature/{self.contributor}-custom-ads",
                "target_counts": {
                    "SAFE_FOR_ALL": {"image": 75, "video": 25, "total": 100},
                    "SAFE_14_PLUS": {"image": 75, "video": 25, "total": 100},
                },
            },
        )
        self.storage_base = self.workspace_root / "SafeAd_Dataset" / "custom_ads" / self.contributor
        self.manifest_path = self.workspace_root / "manifests" / self.contributor / "contribution_manifest.json"
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
        """Saves contributor manifest with standard schema structure."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_data = {
            "contributor": self.cfg["contributor_display"],
            "assigned_categories": self.cfg["assigned_categories"],
            "branch": self.cfg["branch"],
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
        use_media_subdir: bool = False,
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
        category_prefix = CATEGORY_PREFIX_MAP.get(safead_label, "SAD")
        media_code = "IMG" if media_type == "image" else "VID"
        if not sample_id:
            count = sum(
                1 for r in self.records
                if r.get("safead_label") == safead_label and r.get("media_type") == media_type
            ) + 1
            sample_id = f"SAFEAD_{self.contributor.upper()}_{category_prefix}_{media_code}_{count:03d}"

        # Target subfolder relative path
        category_dir = CATEGORY_DIR_MAP.get(safead_label, "other")
        filename = f"{sample_id}{src_path.suffix.lower()}"
        if use_media_subdir:
            sub = "images" if media_type == "image" else "videos"
            rel_path = f"SafeAd_Dataset/custom_ads/{self.contributor}/{category_dir}/{sub}/{filename}"
        else:
            rel_path = f"SafeAd_Dataset/custom_ads/{self.contributor}/{category_dir}/{filename}"

        dest_path = self.workspace_root / rel_path

        if copy_file:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if dest_path.resolve() != src_path.resolve():
                shutil.copy2(src_path, dest_path)

        norm_rel_path = rel_path.replace("\\", "/")
        record = {
            "sample_id": sample_id,
            "file_path": norm_rel_path,
            "storage_uri": f"gdrive://{norm_rel_path}",
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

    def verify_files_on_disk(self) -> Dict[str, Any]:
        """Checks for missing or corrupted media files on disk and re-verifies hashes."""
        missing = []
        corrupted = []
        hash_mismatch = []
        verified_count = 0

        for rec in self.records:
            sid = rec.get("sample_id", "UNKNOWN")
            rel = rec.get("file_path", "")
            expected_hash = rec.get("sha256", "")
            mtype = rec.get("media_type", "image")
            local_path = self.workspace_root / rel

            if not local_path.is_file():
                missing.append({"sample_id": sid, "file_path": rel})
                continue

            # Check file corruption
            try:
                if mtype == "image":
                    from PIL import Image
                    with Image.open(local_path) as im:
                        im.verify()
                elif mtype == "video":
                    if local_path.stat().st_size < 100:
                        corrupted.append({"sample_id": sid, "reason": "Video file smaller than 100 bytes"})
                        continue
            except Exception as e:
                corrupted.append({"sample_id": sid, "file_path": rel, "error": str(e)})
                continue

            # Verify checksum
            actual_hash = compute_sha256(local_path)
            if actual_hash != expected_hash:
                hash_mismatch.append({
                    "sample_id": sid,
                    "expected": expected_hash,
                    "actual": actual_hash,
                })
            else:
                verified_count += 1

        return {
            "total_records": len(self.records),
            "verified_on_disk": verified_count,
            "missing_files": missing,
            "corrupted_files": corrupted,
            "hash_mismatches": hash_mismatch,
            "all_healthy": len(missing) == 0 and len(corrupted) == 0 and len(hash_mismatch) == 0,
        }

    def generate_progress_report(self) -> Dict[str, Any]:
        """Calculates category progress against contributor targets."""
        target_dict = self.cfg.get("target_counts", TARGET_COUNTS)
        counts = {}
        for cat in target_dict.keys():
            counts[cat] = {"image": 0, "video": 0, "total": 0}
        counts["OTHER"] = {"image": 0, "video": 0, "total": 0}

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
            "contributor": self.cfg["contributor_display"],
            "counts_by_category": counts,
            "review_status_counts": review_counts,
            "targets": target_dict,
            "total_collected": len(self.records),
        }
        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SafeAd Dataset Collector")
    parser.add_argument("--workspace", default=".", help="Path to repository workspace root")
    parser.add_argument("--contributor", default="sourav", choices=["sourav", "juwel"], help="Contributor name")
    parser.add_argument("--validate", action="store_true", help="Validate existing contribution manifest")
    parser.add_argument("--verify-disk", action="store_true", help="Verify media file presence and integrity on disk")
    parser.add_argument("--report", action="store_true", help="Display progress and category report")
    args = parser.parse_args()

    collector = SafeAdCollector(args.workspace, contributor=args.contributor)

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

    if args.verify_disk:
        disk_status = collector.verify_files_on_disk()
        print(f"Disk Integrity Status: {'HEALTHY' if disk_status['all_healthy'] else 'ISSUES FOUND'}")
        print(f"Verified on disk: {disk_status['verified_on_disk']} / {disk_status['total_records']}")
        if disk_status["missing_files"]:
            print(f"Missing: {len(disk_status['missing_files'])} files")
        if disk_status["corrupted_files"]:
            print(f"Corrupted: {len(disk_status['corrupted_files'])} files")
        if disk_status["hash_mismatches"]:
            print(f"Hash mismatches: {len(disk_status['hash_mismatches'])} files")

    if args.report:
        rep = collector.generate_progress_report()
        print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
