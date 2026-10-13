"""
External Storage Setup and Diagnostic Tool for SafeAd AI.
Ensures large dataset media is routed to external drive D: (JB Passport)
without consuming limited space on C: drive.
"""

import os
import shutil
import sys
from pathlib import Path

EXTERNAL_ROOT = Path("D:/SafeAd_Dataset")

DATASET_DIRECTORIES = [
    EXTERNAL_ROOT / "existing_datasets" / "conpro_bad_ads" / "screenshots",
    EXTERNAL_ROOT / "existing_datasets" / "utkface" / "faces",
    EXTERNAL_ROOT / "existing_datasets" / "fairface" / "val",
    EXTERNAL_ROOT / "existing_datasets" / "dehate" / "videos",
    EXTERNAL_ROOT / "existing_datasets" / "jigsaw_toxic",
    EXTERNAL_ROOT / "existing_datasets" / "hateful_memes" / "img",
    EXTERNAL_ROOT / "custom_ads" / "sourav",
    EXTERNAL_ROOT / "custom_ads" / "juwel",
]

DOWNLOAD_GUIDE = {
    "conpro_bad_ads": {
        "name": "Bad News / ConPro Ads Screenshots",
        "url": "https://drive.google.com/file/d/12sCuxv38RPlrRKUs-hjl-JrTDQ4J_HcR/view?usp=sharing",
        "target": EXTERNAL_ROOT / "existing_datasets" / "conpro_bad_ads" / "screenshots",
        "action": "Download screenshots.tar.gz and extract images here."
    },
    "utkface": {
        "name": "UTKFace Aligned & Cropped Faces (107 MB)",
        "url": "https://huggingface.co/datasets/py97/UTKFace-Cropped or https://www.kaggle.com/datasets/jangedoo/utkface-new",
        "target": EXTERNAL_ROOT / "existing_datasets" / "utkface" / "faces",
        "action": "Download UTKFace.tar.gz from Hugging Face or crop_part1 from Kaggle and extract images here."
    },
    "fairface": {
        "name": "FairFace Images Margin 1.25",
        "url": "https://github.com/dchen236/FairFace",
        "target": EXTERNAL_ROOT / "existing_datasets" / "fairface",
        "action": "Download fairface-img-margin125-trainval.zip and label CSVs from Google Drive link."
    },
    "dehate": {
        "name": "DeHate Video Metadata",
        "url": "https://github.com/Multimodal-Intelligence-Lab-MIL/DeHate",
        "target": EXTERNAL_ROOT / "existing_datasets" / "dehate",
        "action": "DeHate.xlsx already verified. Video clips fetched per research protocol into videos/."
    }
}


def check_and_initialize_external_storage():
    print("=" * 80)
    print("           SAFEAD AI - EXTERNAL STORAGE VERIFICATION TOOL           ")
    print("=" * 80)

    # Check Drive D:
    d_drive = Path("D:/")
    if not d_drive.exists():
        print("[ERROR] Drive D: (External Hard Drive) is not detected!")
        print("Please plug in your external hard drive and re-run this tool.")
        return False

    usage = shutil.disk_usage(d_drive)
    total_gb = usage.total / (1024 ** 3)
    free_gb = usage.free / (1024 ** 3)
    used_gb = usage.used / (1024 ** 3)

    print(f"External Drive D: Detected ('JB Passport')")
    print(f"Total Capacity: {total_gb:.2f} GB | Used: {used_gb:.2f} GB | Free: {free_gb:.2f} GB\n")

    # Create directories
    created_count = 0
    for d in DATASET_DIRECTORIES:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created_count += 1

    print(f"[OK] External storage root is ready at: {EXTERNAL_ROOT}")
    print(f"Directories verified: {len(DATASET_DIRECTORIES)} (Created {created_count} new folders)\n")

    print("-" * 80)
    print("CANDIDATE DATASET DOWNLOAD & EXTRACTION INSTRUCTIONS")
    print("-" * 80)
    for ds_id, info in DOWNLOAD_GUIDE.items():
        print(f"- {info['name']}:")
        print(f"  Source URL : {info['url']}")
        print(f"  Target Path: {info['target']}")
        print(f"  Action     : {info['action']}\n")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = check_and_initialize_external_storage()
    sys.exit(0 if success else 1)
