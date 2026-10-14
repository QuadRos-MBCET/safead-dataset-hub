#!/usr/bin/env python3
"""
Beer-Tv-Ads Video Commercial Downloader & Manifest Generator.

Downloads real broadcast television beer / alcohol commercials from the Beer-Tv-Ads
dataset (hosted on high-speed CDN / CloudFront) to external storage on D:\SafeAd_Dataset,
calculates streaming SHA-256 hashes, and registers them in manifest.csv as SAFE_18_PLUS
(Adult / Age-Gated Ad Policy).
"""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_METADATA_PATH = Path(r"D:\SafeAd_Dataset\existing_datasets\video_ads\beer_ads_metadata.json")
DEFAULT_OUTPUT_DIR = Path(r"D:\SafeAd_Dataset\existing_datasets\video_ads")


def compute_sha256(filepath: Path) -> str:
    """Computes streaming SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def download_stream(url: str, dest_path: Path, timeout: int = 30) -> Optional[str]:
    """Downloads a file via streaming HTTP GET and computes SHA-256 on the fly."""
    temp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    h = hashlib.sha256()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SafeAd-Dataset-Hub/1.0 (Multimodal Ad Policy Ingest)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            with open(temp_path, "wb") as out_file:
                while True:
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    h.update(chunk)
        if temp_path.exists() and temp_path.stat().st_size > 0:
            if dest_path.exists():
                dest_path.unlink()
            temp_path.rename(dest_path)
            return h.hexdigest()
        else:
            if temp_path.exists():
                temp_path.unlink()
            return None
    except Exception as e:
        print(f"    [ERROR] Download failed for {url}: {e}")
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        return None


def main():
    parser = argparse.ArgumentParser(description="Download Beer TV Ads for SAFE_18_PLUS category.")
    parser.add_argument("--metadata", type=str, default=str(DEFAULT_METADATA_PATH), help="Path to beer_ads_metadata.json")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory on D: drive")
    parser.add_argument("--limit", type=int, default=75, help="Number of commercial videos to download (default: 75)")
    args = parser.parse_args()

    meta_path = Path(args.metadata)
    out_dir = Path(args.output_dir)
    videos_dir = out_dir / "videos"
    manifest_path = out_dir / "manifest.csv"

    if not meta_path.exists():
        print(f"[FATAL] Metadata file not found at {meta_path}")
        sys.exit(1)

    videos_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Loading metadata from {meta_path}...")
    with open(meta_path, "r", encoding="utf-8") as f:
        records: List[Dict[str, str]] = json.load(f)

    print(f"[INFO] Found {len(records)} commercial records. Target limit: {args.limit}")

    # Check existing manifest if present to resume or append
    existing_manifest_rows = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_manifest_rows[row["sample_id"]] = row

    downloaded_records = []
    success_count = 0

    manifest_fields = [
        "sample_id", "file_path", "storage_uri", "media_type",
        "source_name", "source_url", "source_label", "safead_label",
        "license_status", "sha256", "review_status", "notes"
    ]

    for idx, item in enumerate(records[:args.limit], start=1):
        sample_id = f"VAD_18P_{idx:05d}"
        url = item.get("video_link", "").strip()
        brand = item.get("brand_name", "").strip()
        product = item.get("spot_products", "").strip()
        desc = item.get("spot_description", "").strip().replace("\n", " ")

        if not url:
            continue

        filename = f"{sample_id}.mp4"
        dest_video = videos_dir / filename
        rel_path = f"SafeAd_Dataset/existing_datasets/video_ads/videos/{filename}"
        storage_uri = f"gdrive://safead-storage/SafeAd_Dataset/existing_datasets/video_ads/videos/{filename}"

        print(f"[{idx}/{args.limit}] {sample_id} ({brand}): Downloading...")

        sha256_hash = None
        if dest_video.exists() and dest_video.stat().st_size > 10000:
            print(f"    Already exists ({dest_video.stat().st_size / 1024 / 1024:.2f} MB), computing hash...")
            sha256_hash = compute_sha256(dest_video)
        else:
            t0 = time.time()
            sha256_hash = download_stream(url, dest_video)
            t1 = time.time()
            if sha256_hash:
                sz_mb = dest_video.stat().st_size / 1024 / 1024
                print(f"    Success: {sz_mb:.2f} MB in {t1 - t0:.2f}s ({sz_mb / (t1 - t0):.2f} MB/s)")

        if sha256_hash:
            success_count += 1
            row = {
                "sample_id": sample_id,
                "file_path": rel_path,
                "storage_uri": storage_uri,
                "media_type": "video",
                "source_name": "Beer-Tv-Ads",
                "source_url": url,
                "source_label": "Alcohol / Beer Commercial",
                "safead_label": "SAFE_18_PLUS",
                "license_status": "Research / Open Broadcast",
                "sha256": sha256_hash,
                "review_status": "VERIFIED",
                "notes": f"Brand: {brand} | Product: {product} | Desc: {desc[:200]}"
            }
            downloaded_records.append(row)
        else:
            print(f"    Failed to acquire video for {sample_id}")

    print(f"\n[INFO] Writing {len(downloaded_records)} verified records to {manifest_path}...")
    with open(manifest_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_fields)
        writer.writeheader()
        writer.writerows(downloaded_records)

    print(f"[SUCCESS] Download completed! Total verified: {success_count}/{args.limit}")
    print(f"Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
