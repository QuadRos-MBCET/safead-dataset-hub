#!/usr/bin/env python3
"""Collects genuine real-world photos across diverse product, gadget, apparel, food,
sports, and lifestyle categories for SafeAd AI:
- SAFE_FOR_ALL: Household products, study gadgets, food, school supplies, clean transit, pets
- SAFE_14_PLUS: Teen streetwear, gaming gear, extreme sports, acne skincare, energy drinks, audio gear

Saves directly into:
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_ad_for_all\images\
- G:\My Drive\SafeAd_Dataset\custom_ads\safe_14_plus\images\
"""

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
    "User-Agent": "SafeAdRealImageCollector/1.0 (https://github.com/QuadRos-MBCET/safead-dataset-hub; contact: sourav@safead.local)"
}

# Diverse topics: Consumer goods, electronics, school supplies, food, sports, apparel, grooming
TOPICS_SFA = [
    ("cereal box packaging", "Cereal Box Packaging", "Real packaged breakfast cereal box on kitchen table. Safe everyday food product.", "CC / Public Domain"),
    ("toothpaste tube dental", "Toothpaste Tube Care", "Real fluoride toothpaste tube for family oral hygiene. Wholesome personal care.", "CC / Public Domain"),
    ("laptop on study desk", "Laptop on Study Desk", "Real student laptop computer on wooden desk with notebook. Benign technology.", "CC / Public Domain"),
    ("school backpack stationery", "School Backpack & Supplies", "Real youth school backpack with notebooks and colored pens. Educational object.", "CC / Public Domain"),
    ("toy building blocks plastic", "STEM Building Blocks", "Real colorful plastic toy construction blocks. Wholesome childhood play.", "CC / Public Domain"),
    ("fresh fruit bowl apples", "Fresh Fruit Dining Bowl", "Real dining table bowl filled with fresh apples, bananas, and oranges. Healthy diet.", "CC / Public Domain"),
    ("cooking pan stainless kitchen", "Stainless Steel Skillet", "Real kitchen cookware pan and wooden cooking spoon on kitchen counter.", "CC / Public Domain"),
    ("folded laundry towels", "Clean Folded Towels", "Real stack of clean bathroom laundry towels. Domestic household utility.", "CC / Public Domain"),
    ("pet dog with collar", "Domestic Pet Dog with Leash", "Real family golden dog with collar and leash. Wholesome domestic animal care.", "CC / Public Domain"),
    ("smartwatch on wrist", "Smartwatch Fitness Tracker", "Real modern smartwatch gadget showing step count on wrist. Everyday tech.", "CC / Public Domain"),
    ("electric city bus transit", "Public Transit Electric Bus", "Real municipal zero-emission electric city bus at street stop. Civic transit.", "CC / Public Domain"),
    ("bicycle with safety helmet", "Commuter Bike & Helmet", "Real urban commuter bicycle equipped with bicycle safety helmet. Family safety.", "CC / Public Domain"),
    ("optical microscope lab", "Student Optical Microscope", "Real classroom science microscope and glass slides. Educational STEM gear.", "CC / Public Domain"),
    ("shampoo bottle bathroom", "Hygiene Shampoo Bottle", "Real plastic shampoo and body wash bottle in clean bathroom setting.", "CC / Public Domain"),
    ("desk reading lamp led", "Study Desk Reading Lamp", "Real LED goose-neck reading lamp illuminated on student desk. Wholesome study tool.", "CC / Public Domain"),
]

TOPICS_14P = [
    ("sneakers athletic shoes pair", "Youth Athletic Sneakers", "Real pair of high-top streetwear sneakers on concrete. Teen fashion apparel.", "CC / Public Domain"),
    ("hoodie streetwear sweatshirt", "Streetwear Graphic Hoodie", "Real graphic print cotton streetwear hoodie on clothes hanger. Youth style.", "CC / Public Domain"),
    ("gaming gamepad controller", "Wireless Gaming Controller", "Real modern video game console controller on desk. Teen gaming entertainment.", "CC / Public Domain"),
    ("mechanical keyboard RGB", "RGB Mechanical Gaming Keyboard", "Real esports mechanical keyboard with illuminated keys on mousepad.", "CC / Public Domain"),
    ("skateboard deck grip tape", "Skateboard Deck & Wheels", "Real street skateboard with black grip tape and urethane wheels at skatepark.", "CC / Public Domain"),
    ("BMX bicycle freestyle", "BMX Freestyle Trick Bike", "Real 20-inch BMX stunt bicycle with steel frame. Teen action sports gear.", "CC / Public Domain"),
    ("gym dumbbells workout", "Fitness Gym Dumbbells", "Real iron hex dumbbells on gym rubber mat. Youth athletic strength training.", "CC / Public Domain"),
    ("boxing gloves sparring pair", "Sparring Boxing Gloves", "Real pair of leather boxing training gloves on workout bench. Sports fitness.", "CC / Public Domain"),
    ("facial cleanser tube skincare", "Blemish Cleanser Skincare", "Real acne dermatological face wash tube on vanity. Adolescent skincare item.", "CC / Public Domain"),
    ("hair styling clay pomade", "Matte Hair Styling Pomade", "Real tin of men's matte hair styling clay wax. Teen grooming product.", "CC / Public Domain"),
    ("energy drink aluminum can", "Citrus Energy Drink Can", "Real 16oz caffeinated energy drink aluminum beverage can. High-stimulant youth drink.", "CC / Public Domain"),
    ("spicy tortilla chips snack", "Spicy Tortilla Chips Snack", "Real bag of extreme chili pepper tortilla chips on table. Teen snacking product.", "CC / Public Domain"),
    ("electric guitar with amplifier", "Electric Guitar & Amplifier", "Real solid-body electric guitar resting against practice amplifier. Youth music hobby.", "CC / Public Domain"),
    ("over-ear studio headphones", "Over-Ear DJ Studio Headphones", "Real professional studio monitoring headphones with coiled cable.", "CC / Public Domain"),
    ("quadcopter drone camera", "Camera Quadcopter Drone", "Real consumer remote-controlled camera quadcopter drone with controller.", "CC / Public Domain"),
]


def search_commons_photo(query_phrase: str, limit: int = 6):
    encoded = urllib.parse.quote(f"{query_phrase} filetype:bitmap")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime&format=json"
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
        return []


def download_real_photo(url: str, dest_path: Path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = resp.read()

    if len(data) < 8000:
        raise ValueError("Image too small")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    with Image.open(dest_path) as im:
        im.verify()
        w, h = im.size

    if w < 200 or h < 200:
        dest_path.unlink()
        raise ValueError("Resolution too low")

    # Hash
    hasher = hashlib.sha256()
    with open(dest_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256_hash = hasher.hexdigest().lower()

    return sha256_hash, w, h, len(data)


def collect_diverse_dataset():
    if not DRIVE_ROOT.exists():
        print(f"Error: Google Drive path {DRIVE_ROOT} not found!", file=sys.stderr)
        return

    all_records = []

    # Category 1: SAFE_FOR_ALL (safe_ad_for_all)
    sfa_dir = DRIVE_ROOT / "safe_ad_for_all" / "images"
    sfa_dir.mkdir(parents=True, exist_ok=True)
    sfa_records = []
    seen_sfa_hashes = set()
    num = 1

    print("\n--- Collecting SAFE_FOR_ALL Genuine Photos Across Diverse Topics ---")
    for q_term, topic_label, reason, lic in TOPICS_SFA:
        candidates = search_commons_photo(q_term, limit=4)
        time.sleep(0.4)
        saved = False

        for cand in candidates:
            filename = f"SAFEAD_SFA_IMG_{num:03d}.jpg"
            dest_file = sfa_dir / filename
            try:
                sha256_h, w, h, b_size = download_real_photo(cand["url"], dest_file)
                if sha256_h in seen_sfa_hashes:
                    dest_file.unlink()
                    continue

                seen_sfa_hashes.add(sha256_h)
                clean_title = cand["title"].replace("File:", "").replace(".jpg", "").replace(".png", "")[:50]

                rec = {
                    "sample_id": f"SAFEAD_SFA_IMG_{num:03d}",
                    "file_path": f"custom_ads/safe_ad_for_all/images/{filename}",
                    "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_ad_for_all/images/{filename}",
                    "media_type": "image",
                    "topic_category": topic_label,
                    "source_name": "Wikimedia Commons Open Photography",
                    "source_url": cand["url"],
                    "original_source_label": clean_title,
                    "collection_date": time.strftime("%Y-%m-%d"),
                    "safead_label": "SAFE_FOR_ALL",
                    "label_reason": reason,
                    "license_status": lic,
                    "sha256": sha256_h,
                    "annotation_status": "COMPLETED",
                    "review_status": "PROPOSED",
                    "resolution": f"{w}x{h}",
                    "file_size_kb": round(b_size / 1024, 1),
                }
                sfa_records.append(rec)
                print(f"[SFA #{num:02d}] {topic_label}: {clean_title} ({w}x{h})")
                num += 1
                saved = True
                break
            except Exception:
                continue

    # Category 2: SAFE_14_PLUS (safe_14_plus)
    s14p_dir = DRIVE_ROOT / "safe_14_plus" / "images"
    s14p_dir.mkdir(parents=True, exist_ok=True)
    s14p_records = []
    seen_14p_hashes = set()
    num = 1

    print("\n--- Collecting SAFE_14_PLUS Genuine Photos Across Diverse Topics ---")
    for q_term, topic_label, reason, lic in TOPICS_14P:
        candidates = search_commons_photo(q_term, limit=4)
        time.sleep(0.4)

        for cand in candidates:
            filename = f"SAFEAD_S14P_IMG_{num:03d}.jpg"
            dest_file = s14p_dir / filename
            try:
                sha256_h, w, h, b_size = download_real_photo(cand["url"], dest_file)
                if sha256_h in seen_14p_hashes:
                    dest_file.unlink()
                    continue

                seen_14p_hashes.add(sha256_h)
                clean_title = cand["title"].replace("File:", "").replace(".jpg", "").replace(".png", "")[:50]

                rec = {
                    "sample_id": f"SAFEAD_S14P_IMG_{num:03d}",
                    "file_path": f"custom_ads/safe_14_plus/images/{filename}",
                    "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_14_plus/images/{filename}",
                    "media_type": "image",
                    "topic_category": topic_label,
                    "source_name": "Wikimedia Commons Open Photography",
                    "source_url": cand["url"],
                    "original_source_label": clean_title,
                    "collection_date": time.strftime("%Y-%m-%d"),
                    "safead_label": "SAFE_14_PLUS",
                    "label_reason": reason,
                    "license_status": lic,
                    "sha256": sha256_h,
                    "annotation_status": "COMPLETED",
                    "review_status": "PROPOSED",
                    "resolution": f"{w}x{h}",
                    "file_size_kb": round(b_size / 1024, 1),
                }
                s14p_records.append(rec)
                print(f"[14P #{num:02d}] {topic_label}: {clean_title} ({w}x{h})")
                num += 1
                break
            except Exception:
                continue

    all_records = sfa_records + s14p_records
    print(f"\n=======================================================")
    print(f"Total genuine photos collected: {len(all_records)}")
    print(f"  - SAFE_FOR_ALL: {len(sfa_records)} diverse topic photos")
    print(f"  - SAFE_14_PLUS: {len(s14p_records)} diverse topic photos")
    print(f"=======================================================")

    # Write CSV catalog to Google Drive
    csv_file = DRIVE_ROOT / "diverse_dataset_catalog.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_records[0].keys()))
        writer.writeheader()
        writer.writerows(all_records)
    print(f"Google Drive catalog written to: {csv_file}")

    # Write repository contribution manifest
    manifest_file = WORKSPACE_ROOT / "manifests" / "sourav" / "contribution_manifest.json"
    manifest_data = {
        "contributor": "sourav",
        "assigned_categories": ["SAFE_FOR_ALL", "SAFE_14_PLUS"],
        "branch": "feature/sourav-safe-for-all-14-plus",
        "storage_root": "G:/My Drive/SafeAd_Dataset/custom_ads/",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(all_records),
        "records": all_records,
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Repository manifest updated: {manifest_file}")


if __name__ == "__main__":
    collect_diverse_dataset()
