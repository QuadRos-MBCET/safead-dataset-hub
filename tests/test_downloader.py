import tempfile
from pathlib import Path
import pytest

from tools.downloader import (
    download_or_inspect_dataset,
    get_download_status,
    load_tracker,
    update_source_status,
)


def test_downloader_refuses_bypassing_gated_dataset():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        trk_file = tdir / "test_tracker.json"

        # hateful_memes is gated (DrivenData / Meta research license)
        res = download_or_inspect_dataset(
            source_id="hateful_memes",
            target_dir=tdir,
            dry_run=True,
            tracker_path=trk_file
        )

        assert res["status"] == "restricted_manual_action_required"
        assert "DrivenData" in res["instructions"] or "Hugging Face" in res["instructions"]


def test_downloader_dry_run_does_not_mutate_disk():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        trk_file = tdir / "test_tracker.json"

        res = download_or_inspect_dataset(
            source_id="conpro_bad_ads",
            target_dir=tdir,
            dry_run=True,
            tracker_path=trk_file
        )

        assert res["dry_run"] is True
        assert not trk_file.is_file()  # Tracker file not written on dry run


def test_tracker_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        trk_file = tdir / "test_tracker.json"

        update_source_status("utkface", "completed", {"test_key": 42}, tracker_path=trk_file)
        stat = get_download_status("utkface", tracker_path=trk_file)
        assert stat["status"] == "completed"
        assert stat["test_key"] == 42
