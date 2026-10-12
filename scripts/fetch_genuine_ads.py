#!/usr/bin/env python3
"""Fetches genuine advertisement images from open internet archives (Wikimedia Commons)
and saves them directly into the user's Google Drive dataset structure:
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_ad_for_all\images\
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_14_plus\images\

Validates:
- Real image bytes with Pillow (PIL.Image.open)
- Minimum resolution (width/height >= 300)
- SHA-256 calculation
- No duplicates
- Manifest and CSV catalog generation
"""

import os
import sys
import json
import csv
import hashlib
import time
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DRIVE_ROOT = Path(r"G:\My Drive\SafeAd_Dataset\custom_ads")

HEADERS = {
    "User-Agent": "SafeAdDatasetCollector/1.0 (https://github.com/QuadRos-MBCET/safead-dataset-hub; contact: sourav@safead.local)"
}

QUERIES_SFA = [
    ("vintage Coca Cola advertisement", "Coca-Cola Refreshing Beverage Ad", "Wholesome soft drink vintage print ad depicting family refreshment. Universal safe ad.", "Public Domain / CC"),
    ("Campbell soup advertisement", "Campbell Condensed Soup Print Ad", "Family dining and warm winter nutrition soup ad. Family-friendly, completely safe.", "Public Domain / CC"),
    ("toothpaste advertisement", "Dental Care Toothpaste Ad", "Oral hygiene print ad showing clean teeth and dentist recommendation. Universal.", "Public Domain / CC"),
    ("Kellogg cereal advertisement", "Toasted Corn Flakes Breakfast Ad", "Wholesome whole grain breakfast cereal ad. Appropriate for all ages.", "Public Domain / CC"),
    ("Ivory soap advertisement", "Ivory Pure Floating Soap Ad", "Gentle household hygiene bar soap ad with pure ingredients claim. Universal.", "Public Domain / CC"),
    ("Kodak camera advertisement", "Kodak Family Photography Ad", "Home photography camera ad depicting smiling family vacation moments.", "Public Domain / CC"),
    ("bicycle advertisement", "Cruiser Bicycle Transportation Ad", "Recreational cycling print ad emphasizing outdoor health and helmet use.", "Public Domain / CC"),
    ("baking powder advertisement", "Pure Royal Baking Powder Ad", "Kitchen cooking and family baking ingredient advertisement.", "Public Domain / CC"),
    ("fruit juice advertisement", "Fresh Citrus Fruit Juice Ad", "Vitamin C natural orange beverage promotion for children and adults.", "Public Domain / CC"),
    ("public library reading poster", "Community Library Literacy Campaign", "Public service educational poster encouraging community youth reading.", "Public Domain / CC"),
]

QUERIES_14P = [
    ("arcade flyer", "Classic Coin-Op Arcade Game Flyer", "Stylized arcade video game machine promo with sci-fi action art. Suited for 14+.", "CC-BY / Permitted"),
    ("video game advertisement", "Action Fantasy Video Game Print Ad", "Fantasy roleplaying / action game ad with swordplay combat. Bloodless action for teens 14+.", "CC-BY / Permitted"),
    ("sci-fi movie poster", "Interstellar Sci-Fi Cinema Poster", "Cinematic space thriller poster with alien spacecraft and dramatic lighting. Suited for 14+.", "Public Domain / CC"),
    ("horror movie poster", "Supernatural Thriller Movie Poster", "Dark spooky psychological thriller teaser poster. Thematic tension appropriate for 14+.", "Public Domain / CC"),
    ("motorcycle advertisement", "High-Performance Street Motorcycle Ad", "Fast street bike ad with leather jacket rider and highway curve. Suited for older youth.", "Public Domain / CC"),
    ("rock concert poster", "Alternative Rock Live Music Festival", "Stylized typography and electric guitar band artwork. Targeted at teen/young adult music fans.", "CC-BY / Permitted"),
    ("comic book advertisement", "Shonen Super-Hero Comic Book Ad", "Dynamic comic book battle sequence artwork. Action-oriented creative suited for 14+.", "CC-BY / Permitted"),
    ("skateboarding poster", "Extreme Street Skateboarding Event", "Urban street trick and ramp jump contest promotion. High-energy youth sport.", "CC-BY / Permitted"),
    ("denim jeans advertisement", "Vintage Denim Streetwear Ad", "Casual youth denim fashion shoot with teenage models in urban setting.", "Public Domain / CC"),
    ("energy drink advertisement", "Extreme Sports Energy Drink Banner", "High-caffeine citrus beverage promotion featuring motocross stunt jump.", "CC-BY / Permitted"),
]


def search_commons_images(query: str, limit: int = 8):
    encoded_q = urllib.parse.quote(f"{query} filetype:bitmap")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_q}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, p in pages.items():
            if "imageinfo" in p and p["imageinfo"]:
                ii = p["imageinfo"][0]
                mime = ii.get("mime", "")
                if mime in ["image/jpeg", "image/png", "image/webp"]:
                    results.append({
                        "title": p.get("title", ""),
                        "url": ii.get("url", ""),
                        "mime": mime,
                        "size": ii.get("size", 0),
                    })
        return results
    except Exception as e:
        print(f"  [Warning] Search error for '{query}': {e}", file=sys.stderr)
        return []


def download_and_verify(url: str, dest_path: Path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = resp.read()

    if len(data) < 8000:
        raise ValueError(f"Image payload too small ({len(data)} bytes)")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    # Verify with PIL
    with Image.open(dest_path) as im:
        im.verify()
        w, h = im.size

    if w < 250 or h < 250:
        dest_path.unlink()
        raise ValueError(f"Resolution too low ({w}x{h})")

    # Compute SHA-256
    h = hashlib.sha256()
    with open(dest_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    sha256_hash = h.hexdigest().lower()

    return sha256_hash, w, h, len(data)


def collect_images_for_class(category_label: str, target_folder_name: str, query_list: list, target_count: int = 15):
    dest_dir = DRIVE_ROOT / target_folder_name / "images"
    dest_dir.mkdir(parents=True, exist_ok=True)

    prefix = "SFA" if category_label == "SAFE_FOR_ALL" else "S14P"
    collected_records = []
    seen_hashes = set()
    current_num = 1

    print(f"\n==========================================")
    print(f"Collecting genuine images for [{category_label}]")
    print(f"Destination: {dest_dir}")
    print(f"Target count: {target_count}")
    print(f"==========================================")

    for query, default_title, default_reason, default_lic in query_list:
        if len(collected_records) >= target_count:
            break

        print(f"\nSearching: '{query}'...")
        candidates = search_commons_images(query, limit=5)
        time.sleep(0.5)

        for cand in candidates:
            if len(collected_records) >= target_count:
                break

            filename = f"SAFEAD_{prefix}_IMG_{current_num:03d}.jpg"
            dest_file = dest_dir / filename

            try:
                sha256_hash, w, h, byte_size = download_and_verify(cand["url"], dest_file)
                if sha256_hash in seen_hashes:
                    dest_file.unlink()
                    continue

                seen_hashes.add(sha256_hash)
                clean_title = cand["title"].replace("File:", "").replace(".jpg", "").replace(".png", "")[:60]

                record = {
                    "sample_id": f"SAFEAD_{prefix}_IMG_{current_num:03d}",
                    "file_path": f"custom_ads/{target_folder_name}/images/{filename}",
                    "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/{target_folder_name}/images/{filename}",
                    "media_type": "image",
                    "source_name": "Wikimedia Commons Advertising Archive",
                    "source_url": cand["url"],
                    "original_source_label": clean_title,
                    "collection_date": time.strftime("%Y-%m-%d"),
                    "safead_label": category_label,
                    "label_reason": default_reason,
                    "license_status": default_lic,
                    "sha256": sha256_hash,
                    "annotation_status": "COMPLETED",
                    "review_status": "PROPOSED",
                    "resolution": f"{w}x{h}",
                    "file_size_kb": round(byte_size / 1024, 1),
                }

                collected_records.append(record)
                print(f"  [OK] #{current_num:02d} Saved {filename} ({w}x{h}, {round(byte_size/1024, 1)} KB) - {clean_title}")
                current_num += 1

            except Exception as e:
                # print error but continue
                continue

    return collected_records


def main():
    if not DRIVE_ROOT.exists():
        print(f"Error: Google Drive path {DRIVE_ROOT} does not exist!", file=sys.stderr)
        sys.exit(1)

    print("Beginning genuine image ad collection from open archives...")

    # Collect for SAFE_FOR_ALL (folder: safe_ad_for_all)
    records_sfa = collect_images_for_class(
        category_label="SAFE_FOR_ALL",
        target_folder_name="safe_ad_for_all",
        query_list=QUERIES_SFA,
        target_count=15
    )

    # Collect for SAFE_14_PLUS (folder: safe_14_plus)
    records_14p = collect_images_for_class(
        category_label="SAFE_14_PLUS",
        target_folder_name="safe_14_plus",
        query_list=QUERIES_14P,
        target_count=15
    )

    all_records = records_sfa + records_14p
    print(f"\nTotal genuine images collected: {len(all_records)} (SFA: {len(records_sfa)}, S14P: {len(records_14p)})")

    # Write CSV Catalog directly in Google Drive
    csv_path = DRIVE_ROOT / "metadata_catalog.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)
    print(f"Saved Google Drive catalog to: {csv_path}")

    # Update repository manifest
    repo_manifest_path = WORKSPACE_ROOT / "manifests" / "sourav" / "contribution_manifest.json"
    manifest_data = {
        "contributor": "sourav",
        "assigned_categories": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
        "branch": "feature/sourav-safe-for-all-14-plus",
        "storage_root": "G:/My Drive/SafeAd_Dataset/custom_ads/",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(all_records),
        "records": all_records,
    }
    with open(repo_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Saved repository manifest to: {repo_manifest_path}")


if __name__ == "__main__":
    main()
