import tempfile
from pathlib import Path
import pytest

from tools.hasher import (
    calculate_sha256,
    verify_file_checksum,
    detect_duplicates_by_hash,
)


def test_calculate_sha256_known_hash():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"")
        tmp_path = Path(tmp.name)

    try:
        # Known SHA-256 for empty file
        expected_empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert calculate_sha256(tmp_path) == expected_empty
    finally:
        tmp_path.unlink()


def test_verify_file_checksum():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"SafeAd AI project test buffer")
        tmp_path = Path(tmp.name)

    try:
        h = calculate_sha256(tmp_path)
        assert verify_file_checksum(tmp_path, h) is True
        assert verify_file_checksum(tmp_path, "0" * 64) is False
    finally:
        tmp_path.unlink()


def test_detect_duplicates_by_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        tdir = Path(tmpdir)
        f1 = tdir / "sample_1.txt"
        f2 = tdir / "sample_2.txt"  # Duplicate of f1
        f3 = tdir / "sample_3.txt"  # Distinct

        f1.write_bytes(b"Duplicate payload data 12345")
        f2.write_bytes(b"Duplicate payload data 12345")
        f3.write_bytes(b"Unique distinct payload data 99999")

        hash_map, duplicates = detect_duplicates_by_hash([f1, f2, f3])
        assert len(hash_map) == 2
        assert len(duplicates) == 1
        assert duplicates[0] == f2
