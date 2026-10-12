"""
Streaming SHA-256 hashing and duplicate detection utility for SafeAd AI.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Union


def calculate_sha256(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Computes streaming SHA-256 hexadecimal hash for a given file.
    Does not load large media files entirely into memory.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for hashing: {file_path}")

    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def verify_file_checksum(file_path: Union[str, Path], expected_sha256: str) -> bool:
    """Verifies whether a file matches the expected SHA-256 checksum."""
    computed = calculate_sha256(file_path)
    return computed == expected_sha256.strip().lower()


def detect_duplicates_by_hash(
    file_paths: List[Union[str, Path]]
) -> Tuple[Dict[str, List[Path]], List[Path]]:
    """
    Groups file paths by their SHA-256 hash.
    Returns:
        hash_to_files: mapping of hash -> list of file paths with that hash.
        duplicates: list of secondary paths that share a hash with an earlier file.
    """
    hash_to_files: Dict[str, List[Path]] = {}
    duplicates: List[Path] = []

    for item in file_paths:
        p = Path(item)
        if not p.is_file():
            continue
        h = calculate_sha256(p)
        if h in hash_to_files:
            hash_to_files[h].append(p)
            duplicates.append(p)
        else:
            hash_to_files[h] = [p]

    return hash_to_files, duplicates


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if target.is_file():
            print(f"File: {target.name}")
            print(f"SHA-256: {calculate_sha256(target)}")
        elif target.is_dir():
            files = [p for p in target.glob("**/*") if p.is_file()]
            _, dups = detect_duplicates_by_hash(files)
            print(f"Scanned {len(files)} files in {target}. Found {len(dups)} duplicates.")
    else:
        print("Usage: python tools/hasher.py <file_or_directory>")
