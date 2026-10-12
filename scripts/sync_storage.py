#!/usr/bin/env python3
"""SafeAd Dataset Storage Sync Tool

Facilitates syncing local media from `SafeAd_Dataset/` to team cloud storage (Google Drive / S3 / Rclone)
without committing any media binaries into Git.
"""

import sys
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
LOCAL_STORAGE = WORKSPACE_ROOT / "SafeAd_Dataset" / "custom_ads" / "sourav"


def inspect_storage_footprint():
    if not LOCAL_STORAGE.exists():
        print(f"No local storage directory found at {LOCAL_STORAGE}")
        return

    total_bytes = 0
    file_count = 0
    categories = {}

    for p in LOCAL_STORAGE.rglob("*"):
        if p.is_file():
            size = p.stat().st_size
            total_bytes += size
            file_count += 1
            cat = p.parent.name
            categories[cat] = categories.get(cat, 0) + 1

    print(f"=== SafeAd Local Media Storage Summary ===")
    print(f"Path: {LOCAL_STORAGE}")
    print(f"Total Media Files: {file_count}")
    print(f"Total Size on Disk: {total_bytes / 1024:.2f} KB ({total_bytes} bytes)")
    print(f"Category breakdown:")
    for cat, count in categories.items():
        print(f"  - {cat}: {count} files")
    print("===========================================")
    print("\nTo sync to Google Drive using Rclone or Google Drive Desktop:")
    print(f"  rclone sync \"{LOCAL_STORAGE}\" \"gdrive:SafeAd_Dataset/custom_ads/sourav/\" -P")


if __name__ == "__main__":
    inspect_storage_footprint()
