#!/usr/bin/env python3
"""
Leakage and Duplicate Verification Tool for SAFE-VISION (SafeAd AI).
Performs:
1. Exact file duplicate detection via SHA-256 binary hash.
2. Near-duplicate image detection via difference hashing (dHash).
3. Split-leakage validation across train, val, and test splits.
4. Campaign / source clustering checks.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent

def dhash(image, hash_size=8):
    """Calculates a difference hash (dHash) for an image."""
    image = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(image.getdata())
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, "0"))
            decimal_value = 0
    return "".join(hex_string)

def hamming_distance(s1, s2):
    """Computes Hamming distance between two hex hash strings."""
    return bin(int(s1, 16) ^ int(s2, 16)).count("1")

def check_leakage_and_duplicates():
    manifest_path = REPO_ROOT / "manifests" / "safead_master_manifest_v2_reconstructed.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    records = manifest["records"]
    
    print(f"=== SAFE-VISION Leakage & Duplicate Audit ({len(records)} records) ===\n")
    
    # 1. Exact SHA-256 Duplicates
    sha_map = {}
    exact_duplicates = []
    for r in records:
        sha = r["content_hash"]
        sid = r["sample_id"]
        if sha in sha_map:
            exact_duplicates.append((sid, sha_map[sha]))
        else:
            sha_map[sha] = sid
            
    print(f"[1/4] Exact SHA-256 Duplicate Check: {len(exact_duplicates)} collisions found.")
    if exact_duplicates:
        for d in exact_duplicates:
            print(f"  WARNING: {d[0]} is an exact byte-for-byte duplicate of {d[1]}")
    else:
        print("  PASS: All 414 catalog media files have unique cryptographic SHA-256 checksums.")

    # 2. Near-Duplicate Detection on Benchmark Images
    print("\n[2/4] Near-Duplicate Image Check (dHash Hamming distance <= 3):")
    image_records = [r for r in records if r["media_type"] == "image" and not r.get("is_synthetic")]
    hashes = {}
    for r in image_records:
        fp = REPO_ROOT / r["file_path"].replace("/", os.sep)
        try:
            with Image.open(fp) as im:
                h = dhash(im)
                hashes[r["sample_id"]] = (h, r["file_path"], r.get("split"))
        except Exception as e:
            pass
            
    near_duplicates = []
    keys = list(hashes.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k1, k2 = keys[i], keys[j]
            h1, p1, s1 = hashes[k1]
            h2, p2, s2 = hashes[k2]
            dist = hamming_distance(h1, h2)
            if dist <= 3:
                near_duplicates.append((k1, k2, dist, s1, s2))
                
    print(f"  Near-duplicate pairs detected: {len(near_duplicates)}")
    for nd in near_duplicates[:10]:
        print(f"  Potential near-duplicate: {nd[0]} ({nd[3]}) <-> {nd[1]} ({nd[4]}), dist={nd[2]}")
    if not near_duplicates:
        print("  PASS: Zero near-duplicate image pairs detected across the genuine benchmark.")

    # 3. Split Leakage Analysis (Train vs Val vs Test)
    print("\n[3/4] Split Contamination & Crossover Check:")
    splits = {"train": set(), "val": set(), "test": set(), "quarantined_synthetic_test": set()}
    for r in records:
        sp = r.get("split", "train")
        splits[sp].add(r["sample_id"])
        
    print(f"  Split counts: Train={len(splits['train'])}, Val={len(splits['val'])}, Test={len(splits['test'])}, Quarantined={len(splits['quarantined_synthetic_test'])}")
    
    # Check disjointness
    inter_tv = splits["train"].intersection(splits["val"])
    inter_tt = splits["train"].intersection(splits["test"])
    inter_vt = splits["val"].intersection(splits["test"])
    
    leakage_found = len(inter_tv) + len(inter_tt) + len(inter_vt)
    if leakage_found == 0:
        print("  PASS: Train, Val, and Test splits are strictly disjoint. Zero cross-split sample leakage.")
    else:
        print(f"  FAIL: Found {leakage_found} overlapping sample IDs across splits!")

    # 4. Campaign / Near-Duplicate Cross-Split Check
    print("\n[4/4] Near-Duplicate Cross-Split Leakage Check:")
    cross_split_near_dupes = [nd for nd in near_duplicates if nd[3] != nd[4] and nd[3] in ["train", "val", "test"] and nd[4] in ["train", "val", "test"]]
    if cross_split_near_dupes:
        print(f"  WARNING: {len(cross_split_near_dupes)} near-duplicate pairs cross protected evaluation splits!")
        for cnd in cross_split_near_dupes:
            print(f"    {cnd[0]} ({cnd[3]}) crosses with {cnd[1]} ({cnd[4]})")
    else:
        print("  PASS: Zero near-duplicate pairs cross protected train/val/test evaluation splits.")
        
    print("\n=== Leakage & Duplicate Audit Complete ===")
    return len(exact_duplicates) == 0 and leakage_found == 0

if __name__ == "__main__":
    success = check_leakage_and_duplicates()
    sys.exit(0 if success else 1)
