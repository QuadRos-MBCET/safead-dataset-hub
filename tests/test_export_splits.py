"""
Unit and integration tests for dataset split exporter (scripts/export_splits.py).
"""

import json
from pathlib import Path
import pytest

from scripts.export_splits import (
    split_list,
    build_ad_splits,
    build_face_splits,
    export_splits
)


def test_split_list_ratios_and_determinism():
    items = list(range(100))
    t1, v1, te1 = split_list(items, train_ratio=0.8, val_ratio=0.1, seed=42)
    t2, v2, te2 = split_list(items, train_ratio=0.8, val_ratio=0.1, seed=42)

    assert len(t1) == 80
    assert len(v1) == 10
    assert len(te1) == 10
    assert t1 == t2
    assert v1 == v2
    assert te1 == te2
    # Ensure no overlap
    assert set(t1).isdisjoint(set(v1))
    assert set(t1).isdisjoint(set(te1))
    assert set(v1).isdisjoint(set(te1))


def test_build_ad_splits_stratification():
    sample_records = [
        {"sample_id": f"S_{i}", "safead_label": "SAFE_18_PLUS"} for i in range(20)
    ] + [
        {"sample_id": f"U_{i}", "safead_label": "UNSAFE_FOR_ALL"} for i in range(10)
    ]

    train, val, test = build_ad_splits(sample_records, train_ratio=0.8, val_ratio=0.1, seed=42)
    assert len(train) == 24  # 16 + 8
    assert len(val) == 3    # 2 + 1
    assert len(test) == 3   # 2 + 1 (remaining: 20-16-2=2, 10-8-1=1)

    for item in train:
        assert "label_id" in item
        assert item["label_id"] in [2, 3]


def test_build_face_splits_demographic_parsing():
    sample_records = [
        {
            "sample_id": "FF_1",
            "source_name": "fairface",
            "source_label": "age=3-9;gender=Male;race=East Asian"
        },
        {
            "sample_id": "UTK_1",
            "source_name": "utkface",
            "source_label": "age=25;gender=Female;race=White"
        }
    ]

    train, val, test = build_face_splits(sample_records, train_ratio=0.5, val_ratio=0.5, seed=42)
    all_face = train + val + test
    assert len(all_face) == 2

    child_item = next(x for x in all_face if x["sample_id"] == "FF_1")
    assert child_item["parsed_age"] == 6
    assert child_item["parsed_gender"] == "Male"
    assert child_item["parsed_race"] == "East Asian"
    assert child_item["is_child_14"] == 1
    assert child_item["is_minor_18"] == 1

    adult_item = next(x for x in all_face if x["sample_id"] == "UTK_1")
    assert adult_item["parsed_age"] == 25
    assert adult_item["parsed_gender"] == "Female"
    assert adult_item["parsed_race"] == "White"
    assert adult_item["is_child_14"] == 0
    assert adult_item["is_minor_18"] == 0


def test_export_splits_end_to_end(tmp_path):
    existing_root = Path("SafeAd_Dataset/existing_datasets")
    out_dir = tmp_path / "splits_test"

    summary = export_splits(
        existing_root=existing_root,
        output_dir=out_dir,
        train_ratio=0.8,
        val_ratio=0.1,
        seed=42,
        max_face_samples=50
    )

    assert (out_dir / "ad_policy" / "train.csv").is_file()
    assert (out_dir / "facial_age" / "train.csv").is_file()
    assert (out_dir / "splits_summary.json").is_file()
    assert summary["facial_age_splits"]["total"] == 50
