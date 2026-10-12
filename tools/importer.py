"""
Authorized Dataset Importer and Local Folder Ingestion Engine for SafeAd AI.

Imports local raw data directories and pre-annotated datasets into standardized
SafeAd manifest files adhering strictly to the shared schema.
Preserves original source annotations and maintains UNASSIGNED SafeAd labels
where no 1:1 policy mapping exists.
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.hasher import calculate_sha256, detect_duplicates_by_hash
from tools.manifest_validator import (
    REQUIRED_FIELDS,
    validate_manifest_file,
    validate_manifest_record,
)
from tools.registry import get_candidate_dataset

MEDIA_EXT_MAP = {
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
    ".bmp": "image",
    ".gif": "image",
    ".mp4": "video",
    ".avi": "video",
    ".mov": "video",
    ".mkv": "video",
    ".webm": "video",
    ".txt": "text",
    ".json": "text",
    ".jsonl": "text",
    ".csv": "text",
    ".wav": "audio",
    ".mp3": "audio",
    ".flac": "audio",
    ".aac": "audio",
}

SOURCE_PREFIXES = {
    "conpro_bad_ads": "CP",
    "hateful_memes": "FHM",
    "dehate": "DH",
    "jigsaw_toxic": "JIG",
    "utkface": "UTK",
    "fairface": "FF",
    "generic": "SMP"
}


def infer_media_type(path: Path) -> str:
    """Infers media type from file suffix."""
    return MEDIA_EXT_MAP.get(path.suffix.lower(), "multimodal")


def parse_utkface_filename(filename: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Parses UTKFace filename format: [age]_[gender]_[race]_[date&time].jpg
    Gender: 0: Male, 1: Female
    Race: 0: White, 1: Black, 2: Asian, 3: Indian, 4: Others
    """
    parts = Path(filename).stem.split("_")
    if len(parts) >= 3:
        try:
            age = int(parts[0])
            gender = "Male" if parts[1] == "0" else "Female"
            race_map = {"0": "White", "1": "Black", "2": "Asian", "3": "Indian", "4": "Others"}
            race = race_map.get(parts[2], "Others")
            return age, gender, race
        except ValueError:
            pass
    return None, None, None


def map_source_label_to_safead(source_id: str, raw_label: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    """
    Conservative mapping from source label to SafeAd 4-tier categories:
    - SAFE_FOR_ALL
    - SAFE_14_PLUS
    - SAFE_18_PLUS
    - UNSAFE_FOR_ALL
    - UNASSIGNED (if no defensible direct mapping exists)
    Returns:
        (safead_label, mapping_rationale)
    """
    source_lower = str(source_id).lower()
    raw_str = str(raw_label).strip()

    if source_lower == "conpro_bad_ads":
        if raw_str == "Potentially Unwanted Software":
            return "UNSAFE_FOR_ALL", "Malvertising / unwanted software violates basic ad safety"
        elif raw_str in {"Investing", "Mortgage"}:
            return "SAFE_18_PLUS", "High-risk financial advertorial restricted to adults"
        else:
            return "UNASSIGNED", "Non-violating or ambiguous ad category retained for component study"

    elif source_lower == "hateful_memes":
        if raw_str in {"1", "hateful"}:
            return "UNSAFE_FOR_ALL", "Hateful multimodal content rejected under hate speech policy"
        else:
            return "UNASSIGNED", "Benign meme cannot be presumed a compliant commercial ad"

    elif source_lower == "dehate":
        if "explicit" in raw_str.lower():
            return "UNSAFE_FOR_ALL", "Explicit hateful video content violates baseline safety policy"
        elif "implicit" in raw_str.lower():
            return "UNSAFE_FOR_ALL", "Implicit hate violates hate speech policy upon review"
        else:
            return "UNASSIGNED", "Non-hate video clip retained for video guardrail benchmarking"

    elif source_lower == "jigsaw_toxic":
        meta = metadata or {}
        if meta.get("severe_toxic") or meta.get("threat") or meta.get("identity_hate"):
            return "UNSAFE_FOR_ALL", "Severe toxicity/threat/identity hate rejected"
        elif meta.get("obscene"):
            return "SAFE_18_PLUS", "Profane/obscene language age-gated to adults"
        elif meta.get("toxic") or meta.get("insult"):
            return "SAFE_18_PLUS", "Mild toxic language age-gated"
        else:
            return "UNASSIGNED", "Non-toxic text alone cannot guarantee visual ad safety"

    elif source_lower in {"utkface", "fairface"}:
        # Crucial: Face images are demographic calibration crops, NOT commercial ads.
        return "UNASSIGNED", "Face crop dataset strictly reserved for face-age estimation training"

    return "UNASSIGNED", "No defensible 1:1 policy mapping available; sample retained for component research"


def import_dataset_directory(
    source_id: str,
    data_dir: Path,
    output_manifest_csv: Path,
    storage_root_uri: str = "gdrive://safead-storage/SafeAd_Dataset",
    dry_run: bool = False,
    metadata_table_path: Optional[Path] = None,
    default_review_status: str = "verified"
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Scans a local dataset folder, hashes files, builds records according to the shared schema,
    and writes out the validated manifest CSV and JSON.
    """
    data_dir = Path(data_dir)
    source_meta = get_candidate_dataset(source_id) or {
        "id": source_id,
        "name": source_id,
        "official_source_url": "https://unknown.source",
        "license_status": "Unknown License"
    }

    prefix = SOURCE_PREFIXES.get(source_id, "SMP")
    source_name = source_meta.get("id", source_id)
    source_url = source_meta.get("official_source_url", "")
    license_status = source_meta.get("license_status", "Research Only")

    # Discover media files
    media_files = []
    for root, _, files in os.walk(data_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in MEDIA_EXT_MAP and not f.startswith("."):
                media_files.append(p)

    media_files.sort()

    # Pre-load optional metadata lookup
    metadata_lookup: Dict[str, Dict[str, Any]] = {}
    if metadata_table_path and metadata_table_path.is_file():
        if metadata_table_path.suffix.lower() == ".csv":
            with open(metadata_table_path, "r", encoding="utf-8-sig") as mf:
                reader = csv.DictReader(mf)
                for row in reader:
                    key = row.get("filename") or row.get("id") or row.get("ad_id") or row.get("img")
                    if key:
                        metadata_lookup[Path(key).name] = row

    records: List[Dict[str, Any]] = []
    seen_hashes: Dict[str, Path] = {}
    duplicate_paths: List[Path] = []

    for idx, fpath in enumerate(media_files, start=1):
        rel_path = fpath.relative_to(data_dir).as_posix()
        storage_uri = f"{storage_root_uri}/existing_datasets/{source_id}/{rel_path}"
        mtype = infer_media_type(fpath)

        # Hashing
        file_hash = calculate_sha256(fpath)
        if file_hash in seen_hashes:
            duplicate_paths.append(fpath)
            review = "flagged"
            dup_note = f"Duplicate of {seen_hashes[file_hash].name}; "
        else:
            seen_hashes[file_hash] = fpath
            review = default_review_status
            dup_note = ""

        # Extract label & SafeAd mapping
        raw_label = "unlabeled"
        notes_extra = ""
        meta_row = metadata_lookup.get(fpath.name)

        if source_id == "utkface":
            age, gender, race = parse_utkface_filename(fpath.name)
            if age is not None:
                raw_label = f"age={age};gender={gender};race={race}"
                notes_extra = f"Demographics: Age {age}, {gender}, {race}"
        elif meta_row:
            raw_label = (
                meta_row.get("name")
                or meta_row.get("label")
                or meta_row.get("toxic")
                or meta_row.get("ground_truth")
                or "labeled"
            )
        elif "labels" in rel_path.lower():
            raw_label = Path(rel_path).parent.name

        safead_label, rationale = map_source_label_to_safead(source_id, raw_label, meta_row)
        final_notes = f"{dup_note}{rationale}" if not notes_extra else f"{dup_note}{notes_extra} | {rationale}"

        sample_id = f"{prefix}_{idx:05d}"

        record = {
            "sample_id": sample_id,
            "file_path": f"SafeAd_Dataset/existing_datasets/{source_id}/{rel_path}",
            "storage_uri": storage_uri,
            "media_type": mtype,
            "source_name": source_name,
            "source_url": source_url,
            "source_label": raw_label,
            "safead_label": safead_label,
            "license_status": license_status,
            "sha256": file_hash,
            "review_status": review,
            "notes": final_notes.strip()
        }
        records.append(record)

    summary = {
        "source_id": source_id,
        "total_files": len(media_files),
        "total_samples": len(records),
        "duplicate_count": len(duplicate_paths),
        "dry_run": dry_run
    }

    if dry_run:
        print(f"[DRY RUN] Ingested {len(records)} samples from {data_dir}. No manifest written.")
        return records, summary

    # Write manifest CSV
    output_manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_manifest_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS + ["notes"])
        writer.writeheader()
        writer.writerows(records)

    # Write companion manifest JSON
    output_manifest_json = output_manifest_csv.with_suffix(".json")
    with open(output_manifest_json, "w", encoding="utf-8") as f:
        json.dump({"dataset": source_id, "samples": records}, f, indent=2)

    # Validate output manifest against shared schema
    is_valid, errors, _ = validate_manifest_file(output_manifest_csv)
    if not is_valid:
        raise ValueError(f"Generated manifest failed schema validation: {errors}")

    return records, summary


def import_from_metadata_table(
    source_id: str,
    metadata_table_path: Path,
    output_manifest_csv: Path,
    storage_root_uri: str = "gdrive://safead-storage/SafeAd_Dataset",
    base_media_dir: Optional[Path] = None,
    dry_run: bool = False,
    limit: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses a source metadata table (e.g., ConPro dataset.csv) into the shared manifest schema.
    If media files are present locally, computes SHA-256; otherwise marks review_status='pending'
    and computes a deterministic content hash.
    """
    import hashlib
    metadata_table_path = Path(metadata_table_path)
    if not metadata_table_path.is_file():
        raise FileNotFoundError(f"Metadata table not found: {metadata_table_path}")

    source_meta = get_candidate_dataset(source_id) or {
        "id": source_id,
        "name": source_id,
        "official_source_url": "https://unknown.source",
        "license_status": "Academic Research Only"
    }

    prefix = SOURCE_PREFIXES.get(source_id, "SMP")
    source_name = source_meta.get("id", source_id)
    source_url = source_meta.get("official_source_url", "")
    license_status = source_meta.get("license_status", "Academic Research Only")

    records: List[Dict[str, Any]] = []

    with open(metadata_table_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if limit and idx > limit:
                break

            # Find media relative path
            raw_media_path = (
                row.get("ad_screenshot")
                or row.get("file_path")
                or row.get("img")
                or row.get("image")
                or row.get("screenshot")
                or f"samples/{idx:05d}.jpg"
            )

            # Determine label
            raw_label = (
                row.get("name")
                or row.get("label")
                or row.get("source_label")
                or "unlabeled"
            )

            safead_label, rationale = map_source_label_to_safead(source_id, raw_label, row)

            sample_id = f"{prefix}_{idx:05d}"
            rel_file_path = f"SafeAd_Dataset/existing_datasets/{source_id}/{raw_media_path}"
            storage_uri = f"{storage_root_uri}/existing_datasets/{source_id}/{raw_media_path}"
            mtype = infer_media_type(Path(raw_media_path))

            # Compute hash
            local_target = (base_media_dir / raw_media_path) if base_media_dir else None
            if not (local_target and local_target.is_file()):
                ext_path = Path("D:/SafeAd_Dataset/existing_datasets") / source_id / raw_media_path
                if ext_path.is_file():
                    local_target = ext_path

            if local_target and local_target.is_file():
                sha256_val = calculate_sha256(local_target)
                review_status = "verified"
            else:
                # Deterministic hash representing the pending cloud sample record
                rec_str = f"{source_id}:{sample_id}:{raw_media_path}:{raw_label}"
                sha256_val = hashlib.sha256(rec_str.encode("utf-8")).hexdigest()
                review_status = "pending"

            notes = f"Imported from {metadata_table_path.name}; {rationale}"

            records.append({
                "sample_id": sample_id,
                "file_path": rel_file_path,
                "storage_uri": storage_uri,
                "media_type": mtype,
                "source_name": source_name,
                "source_url": source_url,
                "source_label": raw_label,
                "safead_label": safead_label,
                "license_status": license_status,
                "sha256": sha256_val,
                "review_status": review_status,
                "notes": notes.strip()
            })

    summary = {
        "source_id": source_id,
        "total_records_processed": len(records),
        "dry_run": dry_run
    }

    if dry_run:
        print(f"[DRY RUN] Processed {len(records)} records from {metadata_table_path}.")
        return records, summary

    output_manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_manifest_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS + ["notes"])
        writer.writeheader()
        writer.writerows(records)

    output_manifest_json = output_manifest_csv.with_suffix(".json")
    with open(output_manifest_json, "w", encoding="utf-8") as f:
        json.dump({"dataset": source_id, "samples": records}, f, indent=2)

    is_valid, errors, _ = validate_manifest_file(output_manifest_csv)
    if not is_valid:
        raise ValueError(f"Generated manifest failed schema validation: {errors}")

    return records, summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SafeAd AI Dataset Importer")
    parser.add_argument("--source", required=True, help="Registered dataset ID (e.g., conpro_bad_ads, utkface)")
    parser.add_argument("--data-dir", default=None, help="Local directory containing media files")
    parser.add_argument("--metadata-table", default=None, help="Source metadata table to ingest directly")
    parser.add_argument("--output-csv", default=None, help="Path to write manifest.csv")
    parser.add_argument("--metadata-csv", default=None, help="Path to raw source metadata table for folder import")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without writing output")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of processed records")

    args = parser.parse_args()

    if args.metadata_table:
        m_table = Path(args.metadata_table)
        out_csv = Path(args.output_csv) if args.output_csv else m_table.parent / "manifest.csv"
        recs, sumry = import_from_metadata_table(
            source_id=args.source,
            metadata_table_path=m_table,
            output_manifest_csv=out_csv,
            dry_run=args.dry_run,
            limit=args.limit
        )
        print(f"Table Ingestion: Imported {len(recs)} records for '{args.source}'. Manifest: {out_csv}")
    elif args.data_dir:
        s_dir = Path(args.data_dir)
        out_csv = Path(args.output_csv) if args.output_csv else s_dir / "manifest.csv"
        meta_table = Path(args.metadata_csv) if args.metadata_csv else None

        recs, sumry = import_dataset_directory(
            source_id=args.source,
            data_dir=s_dir,
            output_manifest_csv=out_csv,
            dry_run=args.dry_run,
            metadata_table_path=meta_table
        )
        print(f"Directory Ingestion: Imported {len(recs)} records for '{args.source}'. Manifest: {out_csv}")
    else:
        print("Please provide either --data-dir or --metadata-table.")
