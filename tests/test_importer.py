import tempfile
from pathlib import Path
import pytest

from tools.importer import (
    import_dataset_directory,
    import_from_metadata_table,
    map_source_label_to_safead,
    parse_utkface_filename,
)


def test_parse_utkface_filename():
    fn = "25_0_0_20170116174525125.chip.jpg"
    age, gender, race = parse_utkface_filename(fn)
    assert age == 25
    assert gender == "Male"
    assert race == "White"

    fn_female = "14_1_3_20170109204215280.chip.jpg"
    age2, gender2, race2 = parse_utkface_filename(fn_female)
    assert age2 == 14
    assert gender2 == "Female"
    assert race2 == "Indian"


def test_map_source_label_to_safead_rules():
    # ConPro bad ads
    s_label, _ = map_source_label_to_safead("conpro_bad_ads", "Potentially Unwanted Software")
    assert s_label == "UNSAFE_FOR_ALL"

    s_label2, _ = map_source_label_to_safead("conpro_bad_ads", "Investing")
    assert s_label2 == "SAFE_18_PLUS"

    s_label3, _ = map_source_label_to_safead("conpro_bad_ads", "Supplements")
    assert s_label3 == "UNASSIGNED"

    # UTKFace and FairFace: must always remain UNASSIGNED
    s_label_utk, _ = map_source_label_to_safead("utkface", "age=25;gender=Male;race=White")
    assert s_label_utk == "UNASSIGNED"

    s_label_ff, _ = map_source_label_to_safead("fairface", "age=20-29;gender=Male;race=East Asian")
    assert s_label_ff == "UNASSIGNED"


def test_import_dataset_directory_synthetic_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        mock_data = tdir / "raw_data"
        mock_data.mkdir()

        # Create mock synthetic files
        (mock_data / "sample1.png").write_bytes(b"Synthetic PNG Image 1")
        (mock_data / "sample2.png").write_bytes(b"Synthetic PNG Image 2")
        (mock_data / "sample3_dup.png").write_bytes(b"Synthetic PNG Image 1")  # Duplicate of 1

        out_csv = tdir / "output_manifest.csv"

        records, summary = import_dataset_directory(
            source_id="conpro_bad_ads",
            data_dir=mock_data,
            output_manifest_csv=out_csv,
            dry_run=False
        )

        assert len(records) == 3
        assert summary["duplicate_count"] == 1
        assert out_csv.is_file()

        # Verify duplicate flag on 3rd sample
        dup_record = [r for r in records if "sample3_dup" in r["file_path"]][0]
        assert dup_record["review_status"] == "flagged"


def test_import_from_metadata_table_synthetic():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        mock_csv = tdir / "source_meta.csv"
        mock_csv.write_text(
            "ad_id,name,ad_screenshot\n"
            "1001,Potentially Unwanted Software,screenshots/rogue.png\n"
            "1002,Investing,screenshots/crypto.png\n"
            "1003,Supplements,screenshots/vitamins.png\n",
            encoding="utf-8"
        )

        out_csv = tdir / "out_manifest.csv"
        records, summary = import_from_metadata_table(
            source_id="conpro_bad_ads",
            metadata_table_path=mock_csv,
            output_manifest_csv=out_csv,
            dry_run=False
        )

        assert len(records) == 3
        assert summary["total_records_processed"] == 3
        assert records[0]["safead_label"] == "UNSAFE_FOR_ALL"
        assert records[1]["safead_label"] == "SAFE_18_PLUS"
        assert records[2]["safead_label"] == "UNASSIGNED"
        assert out_csv.is_file()
