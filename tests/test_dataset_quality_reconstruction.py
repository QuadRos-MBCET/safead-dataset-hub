#!/usr/bin/env python3
"""
Pytest test suite verifying dataset quality, reconstruction integrity,
synthetic card isolation, and leakage protection.
"""

import json
from pathlib import Path
from tools.validate_dataset_quality import DatasetQualityValidator
from tools.check_leakage_and_duplicates import check_leakage_and_duplicates

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_full_dataset_quality_suite():
    validator = DatasetQualityValidator()
    assert validator.run_all_checks() is True

def test_leakage_and_duplicate_integrity():
    assert check_leakage_and_duplicates() is True

def test_synthetic_quarantine_integrity():
    syn_path = REPO_ROOT / "manifests" / "synthetic_benchmark_manifest.json"
    assert syn_path.is_file()
    with open(syn_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_quarantined_cards"] == 118
    assert len(data["samples"]) == 118
    for item in data["samples"]:
        assert item["is_synthetic"] is True
        assert item["resolution"] == "800x520"

def test_frontend_manifest_purged_of_synthetics_and_prohibited():
    app_manifest_path = REPO_ROOT / "app_content" / "content_manifest.json"
    assert app_manifest_path.is_file()
    with open(app_manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_items"] == len(data["content_items"])
    assert data["total_items"] == 99
    for item in data["content_items"]:
        assert item["age_category"] in ["SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"]
        assert item["age_category"] != "UNSAFE_FOR_ALL"
        assert "SAFEAD_SCAM_" not in item["content_id"]
        # Ensure none of the 118 synthetic cards are present
        assert item.get("resolution") != "800x520" or "S18P_IMG_003" not in item["content_id"]
