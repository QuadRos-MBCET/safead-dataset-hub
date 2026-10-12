from pathlib import Path
import pytest

from tools.manifest_validator import (
    validate_manifest_file,
    validate_manifest_record,
)


def test_validate_record_valid():
    valid_record = {
        "sample_id": "TEST_00001",
        "file_path": "SafeAd_Dataset/existing_datasets/test/sample.jpg",
        "storage_uri": "gdrive://safead-storage/SafeAd_Dataset/existing_datasets/test/sample.jpg",
        "media_type": "image",
        "source_name": "test_source",
        "source_url": "https://example.org/test",
        "source_label": "sample_label",
        "safead_label": "SAFE_FOR_ALL",
        "license_status": "CC0",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "review_status": "verified"
    }
    errors = validate_manifest_record(valid_record, 1)
    assert len(errors) == 0


def test_validate_record_invalid_safead_label():
    invalid_record = {
        "sample_id": "TEST_00002",
        "file_path": "test/path.png",
        "storage_uri": "gdrive://test/path.png",
        "media_type": "image",
        "source_name": "test",
        "source_url": "https://test.com",
        "source_label": "test",
        "safead_label": "COMPLETELY_SAFE_UNVERIFIED",  # Invalid SafeAd label
        "license_status": "CC0",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "review_status": "verified"
    }
    errors = validate_manifest_record(invalid_record, 1)
    assert any("safead_label" in e for e in errors)


def test_validate_record_invalid_sha256():
    invalid_record = {
        "sample_id": "TEST_00003",
        "file_path": "test/path.png",
        "storage_uri": "gdrive://test/path.png",
        "media_type": "image",
        "source_name": "test",
        "source_url": "https://test.com",
        "source_label": "test",
        "safead_label": "UNASSIGNED",
        "license_status": "CC0",
        "sha256": "bad-hash-short",  # Invalid sha256
        "review_status": "verified"
    }
    errors = validate_manifest_record(invalid_record, 1)
    assert any("sha256" in e for e in errors)


def test_all_existing_manifests_are_valid():
    existing_root = Path(__file__).resolve().parent.parent / "SafeAd_Dataset" / "existing_datasets"
    manifests = list(existing_root.glob("**/manifest.csv"))
    assert len(manifests) == 6

    for mf in manifests:
        is_valid, errors, stats = validate_manifest_file(mf)
        assert is_valid is True, f"Manifest {mf} failed validation with errors: {errors}"
        assert stats["total_samples"] > 0
        assert stats["duplicate_id_count"] == 0


def test_contribution_manifest_is_valid():
    contrib_manifest = (
        Path(__file__).resolve().parent.parent
        / "contributions"
        / "existing_datasets"
        / "existing_datasets_manifest.csv"
    )
    is_valid, errors, stats = validate_manifest_file(contrib_manifest)
    assert is_valid is True, f"Contribution manifest failed with errors: {errors}"
    assert stats["total_samples"] == 22
    assert stats["duplicate_id_count"] == 0
