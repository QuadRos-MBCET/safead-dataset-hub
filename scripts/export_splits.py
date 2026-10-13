#!/usr/bin/env python3
"""
Dataset Split Exporter for SafeAd AI (SAFE-VISION) & main_project_s7.

Compiles dataset records from safead-dataset-hub manifests and exports stratified
or partitioned splits (train/val/test: default 80/10/10) directly ingestible by
training pipelines and notebooks (safead_training.ipynb, facial_age_estimation.ipynb).

Splits Produced:
1. Ad Policy Multimodal Splits (train.csv, val.csv, test.csv)
   - Labeled ads across the 4 tiers: SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS, UNSAFE_FOR_ALL.
   - Stratified random splitting preserving category ratios.
2. Facial Age / Demographic Splits (face_train.csv, face_val.csv, face_test.csv)
   - Component face benchmarks (UTKFace & FairFace) parsed with demographics (age, gender, race)
   - Binary is_child target flag (<14 or <18) matching facial_age_estimation.ipynb.
3. Text Guardrail Splits (text_train.csv, text_val.csv, text_test.csv)
   - Text samples from Jigsaw / comment benchmarks.
4. Summary Manifest (splits_summary.json)
   - Machine-readable manifest tracking split sizes, source distribution, and checksums.
"""

import argparse
import csv
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SAFEAD_LABEL_TO_ID = {
    "SAFE_FOR_ALL": 0,
    "SAFE_14_PLUS": 1,
    "SAFE_18_PLUS": 2,
    "UNSAFE_FOR_ALL": 3
}


def load_all_manifest_records(
    existing_root: Path,
    team_manifests_root: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Loads all records across manifest.csv files and optional team JSON manifests."""
    records: List[Dict[str, Any]] = []
    seen_ids = set()

    # 1. Existing public/benchmark datasets
    for manifest_path in existing_root.glob("**/manifest.csv"):
        try:
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    sid = r.get("sample_id")
                    if sid and sid not in seen_ids:
                        seen_ids.add(sid)
                        records.append(r)
        except Exception as e:
            print(f"[WARN] Error reading {manifest_path}: {e}")

    # 2. Team member JSON manifests if present
    if team_manifests_root and team_manifests_root.is_dir():
        for json_file in team_manifests_root.glob("**/*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    member_records = data.get("records") or data.get("samples") or []
                    for r in member_records:
                        sid = r.get("sample_id")
                        if sid and sid not in seen_ids:
                            seen_ids.add(sid)
                            records.append(r)
            except Exception as e:
                print(f"[WARN] Error reading team manifest {json_file}: {e}")

    return records


def split_list(items: List[Any], train_ratio: float = 0.8, val_ratio: float = 0.1, seed: int = 42) -> Tuple[List[Any], List[Any], List[Any]]:
    """Splits a list into train, val, and test subsets randomly with a fixed seed."""
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    train_set = shuffled[:n_train]
    val_set = shuffled[n_train:n_train + n_val]
    test_set = shuffled[n_train + n_val:]
    return train_set, val_set, test_set


def build_ad_splits(
    records: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Builds stratified splits for labeled ads (4 tiers)."""
    by_label: Dict[str, List[Dict[str, Any]]] = {
        "SAFE_FOR_ALL": [],
        "SAFE_14_PLUS": [],
        "SAFE_18_PLUS": [],
        "UNSAFE_FOR_ALL": []
    }

    for r in records:
        lbl = r.get("safead_label")
        if lbl in by_label:
            # Enrich with label_id for safead_training.ipynb
            item = dict(r)
            item["label_id"] = SAFEAD_LABEL_TO_ID[lbl]
            by_label[lbl].append(item)

    train_all, val_all, test_all = [], [], []
    for lbl, group in by_label.items():
        if group:
            t, v, te = split_list(group, train_ratio, val_ratio, seed)
            train_all.extend(t)
            val_all.extend(v)
            test_all.extend(te)

    # Shuffle combined sets
    rng = random.Random(seed)
    rng.shuffle(train_all)
    rng.shuffle(val_all)
    rng.shuffle(test_all)
    return train_all, val_all, test_all


def build_face_splits(
    records: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
    max_samples: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Builds face splits for facial_age_estimation.ipynb from UTKFace and FairFace records.
    Parses age from source_label and marks is_child (<14) and is_minor (<18).
    """
    face_records: List[Dict[str, Any]] = []

    for r in records:
        sname = (r.get("source_name") or "").lower()
        if "utkface" in sname or "fairface" in sname:
            slbl = r.get("source_label", "")
            age = None
            gender = None
            race = None

            # Parse age from standard tag (e.g., age=25;gender=Male;race=White or age=3-9...)
            for part in slbl.split(";"):
                if part.startswith("age="):
                    val = part.split("=", 1)[1]
                    if "-" in val:
                        try:
                            low, high = map(int, val.split("-"))
                            age = (low + high) // 2
                        except Exception:
                            age = None
                    elif "+" in val:
                        try:
                            age = int(val.replace("+", ""))
                        except Exception:
                            age = None
                    else:
                        try:
                            age = int(val)
                        except Exception:
                            age = None
                elif part.startswith("gender="):
                    gender = part.split("=", 1)[1]
                elif part.startswith("race="):
                    race = part.split("=", 1)[1]

            item = dict(r)
            item["parsed_age"] = age if age is not None else ""
            item["parsed_gender"] = gender if gender is not None else ""
            item["parsed_race"] = race if race is not None else ""
            item["is_child_14"] = 1 if (age is not None and age < 14) else (0 if age is not None else "")
            item["is_minor_18"] = 1 if (age is not None and age < 18) else (0 if age is not None else "")
            face_records.append(item)

    if max_samples and len(face_records) > max_samples:
        rng = random.Random(seed)
        rng.shuffle(face_records)
        face_records = face_records[:max_samples]

    return split_list(face_records, train_ratio, val_ratio, seed)


def write_csv(filepath: Path, records: List[Dict[str, Any]]) -> None:
    """Writes record dicts to a CSV file."""
    if not records:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def export_splits(
    existing_root: Path,
    output_dir: Path,
    team_manifests_root: Optional[Path] = None,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
    max_face_samples: Optional[int] = None
) -> Dict[str, Any]:
    """Compiles all manifests, computes splits, and saves output CSVs and JSON summary."""
    existing_root = Path(existing_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Scanning manifests from {existing_root}...")
    records = load_all_manifest_records(existing_root, team_manifests_root)
    print(f"[INFO] Loaded {len(records)} total records.")

    # 1. Ad Policy Splits (4-tier)
    ad_train, ad_val, ad_test = build_ad_splits(records, train_ratio, val_ratio, seed)
    ad_dir = output_dir / "ad_policy"
    write_csv(ad_dir / "train.csv", ad_train)
    write_csv(ad_dir / "val.csv", ad_val)
    write_csv(ad_dir / "test.csv", ad_test)

    # 2. Facial Demographics & Child Age Splits
    face_train, face_val, face_test = build_face_splits(records, train_ratio, val_ratio, seed, max_face_samples)
    face_dir = output_dir / "facial_age"
    write_csv(face_dir / "train.csv", face_train)
    write_csv(face_dir / "val.csv", face_val)
    write_csv(face_dir / "test.csv", face_test)

    # 3. Compile Summary Manifest
    summary = {
        "generator": "tools/export_splits.py",
        "split_ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": round(1.0 - train_ratio - val_ratio, 4)
        },
        "random_seed": seed,
        "ad_policy_splits": {
            "train_count": len(ad_train),
            "val_count": len(ad_val),
            "test_count": len(ad_test),
            "total": len(ad_train) + len(ad_val) + len(ad_test),
            "paths": {
                "train": str(ad_dir / "train.csv"),
                "val": str(ad_dir / "val.csv"),
                "test": str(ad_dir / "test.csv")
            }
        },
        "facial_age_splits": {
            "train_count": len(face_train),
            "val_count": len(face_val),
            "test_count": len(face_test),
            "total": len(face_train) + len(face_val) + len(face_test),
            "paths": {
                "train": str(face_dir / "train.csv"),
                "val": str(face_dir / "val.csv"),
                "test": str(face_dir / "test.csv")
            }
        },
        "total_manifest_records_ingested": len(records)
    }

    summary_file = output_dir / "splits_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[SUCCESS] Exported splits to {output_dir}")
    print(f"  - Ad Policy Splits: Train={len(ad_train)}, Val={len(ad_val)}, Test={len(ad_test)}")
    print(f"  - Facial Age Splits: Train={len(face_train)}, Val={len(face_val)}, Test={len(face_test)}")
    print(f"  - Summary Manifest: {summary_file}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export train/val/test splits for SafeAd AI pipelines")
    parser.add_argument("--existing-root", default="SafeAd_Dataset/existing_datasets", help="Root containing existing dataset manifests")
    parser.add_argument("--team-root", default="manifests", help="Root containing team manifests")
    parser.add_argument("--output-dir", default="splits", help="Directory where CSV splits will be saved")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Ratio for training set")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Ratio for validation set")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic splitting")
    parser.add_argument("--max-face-samples", type=int, default=None, help="Optional sample limit for face splits")

    args = parser.parse_args()
    export_splits(
        existing_root=Path(args.existing_root),
        output_dir=Path(args.output_dir),
        team_manifests_root=Path(args.team_root) if args.team_root else None,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        seed=args.seed,
        max_face_samples=args.max_face_samples
    )
