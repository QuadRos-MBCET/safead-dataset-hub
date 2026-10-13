from pathlib import Path
import pytest

from tools.reporter import generate_manifest_summary, format_summary_markdown


def test_reporter_single_manifest_summary():
    manifest_path = (
        Path(__file__).resolve().parent.parent
        / "SafeAd_Dataset"
        / "existing_datasets"
        / "conpro_bad_ads"
        / "manifest.csv"
    )
    summary = generate_manifest_summary(manifest_path)
    assert summary["is_valid"] is True
    assert summary["source_id"] == "conpro_bad_ads"
    assert summary["total_samples"] >= 5
    assert "image" in summary["media_types"]


def test_reporter_markdown_formatting():
    mock_summaries = [
        {
            "manifest_path": "dummy/manifest.csv",
            "source_id": "mock_source",
            "source_name": "Mock Source Display",
            "source_url": "https://example.org",
            "license_status": "CC BY 4.0",
            "is_valid": True,
            "validation_errors": [],
            "total_samples": 10,
            "unique_samples": 10,
            "duplicate_hash_count": 0,
            "media_types": {"image": 10},
            "safead_labels": {"UNASSIGNED": 8, "SAFE_18_PLUS": 2},
            "source_labels": {"cat_a": 5, "cat_b": 5},
            "storage_size_bytes": 1024
        }
    ]

    md = format_summary_markdown(mock_summaries)
    assert "# SafeAd AI: Existing Dataset Collection Summary Report" in md
    assert "Mock Source Display" in md
    assert "[VALID]" in md
    assert "UNASSIGNED:8" in md or "`UNASSIGNED`: 8" in md
