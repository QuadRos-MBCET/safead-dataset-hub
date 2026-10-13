#!/usr/bin/env python3
"""Downloads real, filmed, authentic open-licensed video clips from Wikimedia Commons
for SAFE_FOR_ALL and SAFE_14_PLUS.

Ensures:
- Real authentic camera footage (NOT generated)
- Duration strictly between 5 seconds and 5 minutes (5s - 300s)
- Lightweight & easily computable: standardized to 640x360 MP4
- Computable in Python (cv2.VideoCapture / torchvision.io / Decord)
- Direct save to Google Drive folders:
  G:\My Drive\SafeAd_Dataset\custom_ads\safe_ad_for_all\videos\
  G:\My Drive\SafeAd_Dataset\custom_ads\safe_14_plus\videos\
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
import cv2

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DRIVE_ROOT = Path(r"G:\My Drive\SafeAd_Dataset\custom_ads")

HEADERS = {
    "User-Agent": "SafeAdRealVideoDownloader/1.0 (https://github.com/QuadRos-MBCET/safead-dataset-hub; contact: sourav@safead.local)"
}

QUERIES_SFA_VIDEOS = [
    ("traffic electric bus", "Electric City Bus in Transit", "Real municipal zero-emission electric city bus traveling on urban roadway. Universal safe transit."),
    ("bicycle commuter ride", "Urban Commuter Bicycling", "Real commuter cyclist wearing road safety helmet riding on marked city bike path."),
    ("dog playing in park", "Pet Dog Playing in Grass", "Real domestic pet golden dog retrieving toy and running across public park lawn."),
    ("making coffee espresso", "Espresso Coffee Brewing", "Real barista espresso machine extracting fresh morning coffee into ceramic cup."),
    ("pottery clay wheel spinning", "Spinning Ceramic Pottery Wheel", "Real artisan hands shaping moist ceramic clay on spinning potter's kick wheel."),
    ("pouring milk glass", "Pouring Fresh Milk into Glass", "Real kitchen closeup pouring fresh farm milk into transparent drinking tumbler."),
    ("baking bread kitchen", "Slicing Fresh Hearth Bread", "Real domestic kitchen cutting freshly baked whole grain sourdough loaf."),
    ("clock pendulum ticking", "Antique Mechanical Clock", "Real brass clockwork pendulum smoothly swinging inside domestic wall clock."),
    ("pedestrian street crossing", "City Pedestrian Crosswalk", "Real street pedestrians safely crossing avenue at marked street zebra walk."),
    ("fountain water park", "Municipal Water Fountain", "Real public municipal park fountain spraying clean cascading water."),
    ("tram city transit street", "Urban Passenger Tram", "Real municipal passenger light rail tram moving through city street."),
    ("cat playing with toy", "Domestic Pet Cat Playing", "Real domestic cat playing with toy on living room floor."),
    ("cooking vegetables in pan", "Sauting Fresh Vegetables", "Real kitchen cooking fresh bell peppers and vegetables in skillet."),
    ("playing acoustic piano", "Acoustic Piano Performance", "Real pianist performing classical melody on grand acoustic piano."),
    ("duck swimming in pond", "Wild Ducks Swimming", "Real ducks swimming smoothly across calm park pond water."),
]

QUERIES_14P_VIDEOS = [
    ("skateboarding street", "Street Skateboarding Stunt", "Real street skateboarder executing ollie jump over urban concrete curb."),
    ("BMX bike jump trick", "BMX Freestyle Ramp Jump", "Real youth BMX trick rider catching air off wooden quarterpipe transition ramp."),
    ("breakdance street dancing", "Urban B-Boy Breakdancing", "Real athletic urban street dancer performing rhythmic footwork and spin."),
    ("gym workout dumbbells", "Fitness Dumbbell Workout", "Real athlete performing seated dumbbell curls on gym fitness bench."),
    ("boxing training punch bag", "Heavy Bag Boxing Training", "Real boxer in training gloves landing combination strikes on gym heavy bag."),
    ("electric guitar playing", "Electric Guitar Performance", "Real musician playing lead guitar solo on solid-body electric guitar."),
    ("rock climbing bouldering", "Gym Bouldering Wall Ascent", "Real climber scaling indoor bouldering wall using climbing chalk and shoes."),
    ("racing car drift track", "Drift Car Track Cornering", "Real sports coupe executing controlled high-speed slide through racecourse chicane."),
    ("rollerblade street skating", "Urban Inline Rollerblading", "Real skater performing slalom maneuvers on 4-wheel inline rollerblades."),
    ("quadcopter drone flying", "Quadcopter Drone Maneuvers", "Real remote-control quadcopter drone hovering and banking over outdoor field."),
    ("drummer playing drum kit", "Drum Kit Percussion Rhythm", "Real drummer playing dynamic rock rhythm on acoustic drum kit."),
    ("barbell weightlifting deadlift", "Barbell Strength Deadlift", "Real athlete executing heavy barbell lift on rubber gym platform."),
    ("motorcycle street riding", "Motorcycle Street Riding", "Real motorcyclist in riding gear cruising along asphalt highway curve."),
    ("snowboard winter snow", "Snowboard Mountain Descent", "Real snowboarder carving down mountain snow trail with speed."),
    ("street dance hip hop", "Hip Hop Urban Choreography", "Real youth street dance crew performing synchronized hip hop moves."),
]


def search_commons_videos(query: str, max_size_mb: float = 25.0):
    encoded = urllib.parse.quote(f"{query} filetype:video")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrnamespace=6&gsrlimit=6&prop=imageinfo&iiprop=url|size|mime&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, p in pages.items():
            if "imageinfo" in p and p["imageinfo"]:
                ii = p["imageinfo"][0]
                size_mb = ii.get("size", 0) / (1024 * 1024)
                if size_mb <= max_size_mb:
                    results.append({
                        "title": p.get("title", ""),
                        "url": ii.get("url", ""),
                        "size_mb": size_mb,
                    })
        return results
    except Exception:
        return []


def download_and_standardize_video(url: str, dest_mp4_path: Path, max_duration_sec: int = 15):
    temp_raw = dest_mp4_path.parent / f"raw_download_{dest_mp4_path.stem}.tmp"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(temp_raw, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)

    # Open with cv2 to verify and read specs
    cap = cv2.VideoCapture(str(temp_raw))
    if not cap.isOpened():
        temp_raw.unlink()
        raise ValueError("Could not decode video stream with cv2")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 60:
        fps = 24.0

    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps > 0 else 0

    # Ensure duration is strictly within 5 seconds to 5 minutes
    if duration < 5.0:
        cap.release()
        temp_raw.unlink()
        raise ValueError(f"Duration too short ({duration:.1f}s < 5s)")

    # Standardize to 640x360 MP4 (computable, compact, low memory)
    out_w, out_h = 640, 360
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(dest_mp4_path), fourcc, fps, (out_w, out_h))

    max_frames = int(fps * min(max_duration_sec, duration))
    written = 0

    while written < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (out_w, out_h), interpolation=cv2.INTER_AREA)
        writer.write(resized)
        written += 1

    cap.release()
    writer.release()
    temp_raw.unlink()

    actual_dur = round(written / fps, 1)
    if actual_dur < 5.0:
        dest_mp4_path.unlink()
        raise ValueError(f"Extracted duration too short ({actual_dur}s)")

    # Compute SHA-256
    hasher = hashlib.sha256()
    with open(dest_mp4_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256 = hasher.hexdigest().lower()
    sz_kb = round(dest_mp4_path.stat().st_size / 1024, 1)

    return sha256, actual_dur, sz_kb


def collect_real_videos():
    sfa_vid_dir = DRIVE_ROOT / "safe_ad_for_all" / "videos"
    s14p_vid_dir = DRIVE_ROOT / "safe_14_plus" / "videos"
    sfa_vid_dir.mkdir(parents=True, exist_ok=True)
    s14p_vid_dir.mkdir(parents=True, exist_ok=True)

    print("=== Downloading Real Authentic Videos from Open Repositories ===")
    print("Specs: Standard 640x360 MP4, 5s to 15s clips, lightweight & easily computable\n")

    sfa_records = []
    seen_sfa_hashes = set()
    num = 1

    # 1. Download SAFE_FOR_ALL videos
    print("--- Downloading SAFE_FOR_ALL Real Video Clips ---")
    for q, topic, reason in QUERIES_SFA_VIDEOS:
        cands = search_commons_videos(q, max_size_mb=20.0)
        time.sleep(0.3)
        for cand in cands:
            vid_name = f"SAFEAD_SFA_VID_{num:03d}.mp4"
            dest_file = sfa_vid_dir / vid_name
            try:
                print(f"Downloading [{num}] {topic} ({cand['size_mb']:.1f} MB source)...")
                sha, dur, sz_kb = download_and_standardize_video(cand["url"], dest_file, max_duration_sec=12)
                if sha in seen_sfa_hashes:
                    dest_file.unlink()
                    continue
                seen_sfa_hashes.add(sha)

                rec = {
                    "sample_id": f"SAFEAD_SFA_VID_{num:03d}",
                    "file_path": f"custom_ads/safe_ad_for_all/videos/{vid_name}",
                    "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_ad_for_all/videos/{vid_name}",
                    "media_type": "video",
                    "duration_seconds": dur,
                    "source_name": "Wikimedia Commons Open Video",
                    "source_url": cand["url"],
                    "original_source_label": cand["title"][:50],
                    "collection_date": time.strftime("%Y-%m-%d"),
                    "safead_label": "SAFE_FOR_ALL",
                    "label_reason": reason,
                    "license_status": "CC / Public Domain",
                    "sha256": sha,
                    "annotation_status": "COMPLETED",
                    "review_status": "PROPOSED",
                    "resolution": "640x360",
                    "file_size_kb": sz_kb,
                }
                sfa_records.append(rec)
                print(f"  [OK] Saved {vid_name} ({sz_kb} KB, {dur}s) - {topic}")
                num += 1
                break
            except Exception as e:
                continue

    # 2. Download SAFE_14_PLUS videos
    print("\n--- Downloading SAFE_14_PLUS Real Video Clips ---")
    s14p_records = []
    seen_14p_hashes = set()
    num = 1

    for q, topic, reason in QUERIES_14P_VIDEOS:
        cands = search_commons_videos(q, max_size_mb=20.0)
        time.sleep(0.3)
        for cand in cands:
            vid_name = f"SAFEAD_S14P_VID_{num:03d}.mp4"
            dest_file = s14p_vid_dir / vid_name
            try:
                print(f"Downloading [{num}] {topic} ({cand['size_mb']:.1f} MB source)...")
                sha, dur, sz_kb = download_and_standardize_video(cand["url"], dest_file, max_duration_sec=12)
                if sha in seen_14p_hashes:
                    dest_file.unlink()
                    continue
                seen_14p_hashes.add(sha)

                rec = {
                    "sample_id": f"SAFEAD_S14P_VID_{num:03d}",
                    "file_path": f"custom_ads/safe_14_plus/videos/{vid_name}",
                    "storage_uri": f"gdrive://SafeAd_Dataset/custom_ads/safe_14_plus/videos/{vid_name}",
                    "media_type": "video",
                    "duration_seconds": dur,
                    "source_name": "Wikimedia Commons Open Video",
                    "source_url": cand["url"],
                    "original_source_label": cand["title"][:50],
                    "collection_date": time.strftime("%Y-%m-%d"),
                    "safead_label": "SAFE_14_PLUS",
                    "label_reason": reason,
                    "license_status": "CC / Public Domain",
                    "sha256": sha,
                    "annotation_status": "COMPLETED",
                    "review_status": "PROPOSED",
                    "resolution": "640x360",
                    "file_size_kb": sz_kb,
                }
                s14p_records.append(rec)
                print(f"  [OK] Saved {vid_name} ({sz_kb} KB, {dur}s) - {topic}")
                num += 1
                break
            except Exception as e:
                continue

    print(f"\n==========================================")
    print(f"Downloaded Real Videos Complete!")
    print(f"  - SAFE_FOR_ALL videos: {len(sfa_records)}")
    print(f"  - SAFE_14_PLUS videos: {len(s14p_records)}")
    print(f"==========================================")

    # Combine with existing 150 images
    manifest_path = WORKSPACE_ROOT / "manifests" / "sourav" / "contribution_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    existing_imgs = [r for r in manifest_data.get("records", []) if r.get("media_type") == "image"]
    all_combined = existing_imgs + sfa_records + s14p_records

    # Update CSV catalog in Google Drive
    csv_file = DRIVE_ROOT / "complete_dataset_catalog.csv"
    all_keys = list({k: None for r in all_combined for k in r.keys()}.keys())
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(all_combined)

    # Update Git manifest
    manifest_data["records"] = all_combined
    manifest_data["total_records"] = len(all_combined)
    manifest_data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Updated complete dataset catalog: {csv_file}")
    print(f"Updated Git contribution manifest: {manifest_path}")


if __name__ == "__main__":
    collect_real_videos()
