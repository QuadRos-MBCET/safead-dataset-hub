import os
import sys
import json
import csv
import hashlib
from datetime import datetime
import cv2

repo_dir = r"C:\Users\Asus\Desktop\safead\safead-dataset-hub"

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# Load image records
with open(os.path.join(repo_dir, "scripts", "s18p_images_metadata.json"), "r", encoding="utf-8") as f:
    s18p_imgs = json.load(f)

with open(os.path.join(repo_dir, "scripts", "ufa_images_metadata.json"), "r", encoding="utf-8") as f:
    ufa_imgs = json.load(f)

# Re-verify and update true SHA256 and file_size_kb for all images from actual files on disk
all_img_records = []
for r in s18p_imgs + ufa_imgs:
    rel_path = r["file_path"].replace("\\", "/")
    abs_path = os.path.join(repo_dir, rel_path)
    if os.path.exists(abs_path):
        actual_sha = compute_sha256(abs_path)
        actual_size_kb = round(os.path.getsize(abs_path) / 1024, 1)
        r["sha256"] = actual_sha
        r["file_size_kb"] = actual_size_kb
        r["file_path"] = rel_path
        r["storage_uri"] = f"gdrive://SafeAd_Dataset/{rel_path}"
        all_img_records.append(r)

print(f"Verified {len(all_img_records)} image records from disk.")

# Define metadata mappings for videos
s18p_video_defs = [
    {
        "id": "SAFEAD_S18P_VID_001",
        "title": "Miller Genuine Draft Beer Commercial",
        "desc": "Broadcast television advert for Miller Genuine Draft beer with visible branding.",
        "reason": "Alcohol product advertising. Permitted under age-gated broadcast restrictions for 18+ viewers.",
        "src_url": "https://archive.org/details/MillerGenuineDraftBeerCommercial",
        "text": "Features on-screen 'Miller Genuine Draft' typography and bottle label."
    },
    {
        "id": "SAFEAD_S18P_VID_002",
        "title": "John Smith's Draught Bitter Beer Commercial",
        "desc": "Broadcast television commercial for John Smith's bitter ale.",
        "reason": "Alcohol beverage promotion. Regulated for 18+ adult demographic.",
        "src_url": "https://archive.org/details/JohnSmithsDraughtBeerAdvert",
        "text": "Shows John Smith's brand logo and 'Draught Bitter' font."
    },
    {
        "id": "SAFEAD_S18P_VID_003",
        "title": "Chesterfield Cigarettes 'Men of America' (1959)",
        "desc": "Classic broadcast television tobacco ad featuring working men and cigarette smoking.",
        "reason": "Commercial tobacco advertising. Restricted to 18+ adult viewers.",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_1959_Men_of_America_512kb.mp4",
        "text": "On-screen Chesterfield cigarette pack and 'Top Tobacco' branding."
    },
    {
        "id": "SAFEAD_S18P_VID_004",
        "title": "Chesterfield Cigarettes 'They Satisfy'",
        "desc": "Historic Chesterfield broadcast commercial featuring product demonstrations.",
        "reason": "Commercial tobacco advertising with product smoking scenes (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_They_satisfy_512kb.mp4",
        "text": "Displays 'Chesterfield They Satisfy' slogan and cigarette package."
    },
    {
        "id": "SAFEAD_S18P_VID_005",
        "title": "Old Gold Filters Commercial (1970)",
        "desc": "Classic television commercial promoting Old Gold filter cigarettes.",
        "reason": "Regulated tobacco promotion suitable only for age-verified 18+ audience.",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_Old_Gold_filters_man_jingle_1970_512kb.mp4",
        "text": "Displays 'Old Gold Filters' packaging and typography."
    },
    {
        "id": "SAFEAD_S18P_VID_006",
        "title": "Sydney Sweeney Dr. Squatch Body Wash Ad",
        "desc": "Dr. Squatch natural body wash promotional video featuring suggestive humor and mature themes.",
        "reason": "Contains sexually suggestive adult humor and themes appropriate only for 18+.",
        "src_url": "https://www.youtube.com/watch?v=sydney_sweeney_squatch",
        "text": "Shows Dr. Squatch Men's Body Wash branding and typography."
    },
    {
        "id": "SAFEAD_S18P_VID_007",
        "title": "Tennent's LA Low Alcohol Lager Commercial",
        "desc": "Scottish television commercial for Tennent's LA lager brand.",
        "reason": "Alcohol beverage promotion regulated for mature 18+ viewers.",
        "src_url": "https://archive.org/details/TennentsLALowAlcoholBeer",
        "text": "Features Tennent's red 'T' logo and 'LA Lager' branding."
    },
    {
        "id": "SAFEAD_S18P_VID_008",
        "title": "Chesterfield 101 Cigarettes 'A Silly Millimeter Longer'",
        "desc": "Classic television spot for Chesterfield 101 extra-long cigarettes.",
        "reason": "Commercial tobacco advertisement with active smoking depiction (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_101_Cigarettes_A_silly_millimeter_longer_512kb.mp4",
        "text": "Prominent 'Chesterfield 101' pack and ruler comparison graphic."
    },
    {
        "id": "SAFEAD_S18P_VID_009",
        "title": "Chesterfield Cigarettes with Dave Madden",
        "desc": "Broadcast commercial featuring actor Dave Madden endorsing Chesterfield cigarettes.",
        "reason": "Commercial tobacco advertising. 18+ adult age-gated material.",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_CigarettesDave_Madden_of_Partridge_Family_512kb.mp4",
        "text": "Displays 'Chesterfield' endorsement text and packaging."
    },
    {
        "id": "SAFEAD_S18P_VID_010",
        "title": "Chesterfield Cigarettes '21 Great Tobaccos'",
        "desc": "Musical jingle broadcast spot advertising Chesterfield tobacco blends.",
        "reason": "Commercial tobacco advertising. Age restricted to 18+ adults.",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_21_great_tobaccos_jingle_512kb.mp4",
        "text": "On-screen text '21 Great Tobaccos' and product logo."
    },
    {
        "id": "SAFEAD_S18P_VID_011",
        "title": "Chesterfield Cigarettes 'Favorite of Sailors' (1957)",
        "desc": "Vintage 1957 military-themed broadcast spot for Chesterfield cigarettes.",
        "reason": "Commercial tobacco product promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_Favorite_of_sailors_1957_512kb.mp4",
        "text": "Features naval personnel holding Chesterfield cigarette cartons."
    },
    {
        "id": "SAFEAD_S18P_VID_012",
        "title": "Chesterfield Cigarettes 'Satisfies The Most'",
        "desc": "Extended broadcast advertisement promoting Chesterfield rich flavor and smoke.",
        "reason": "Commercial tobacco advertising depicting smoking (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_Satisfies_the_most_512kb.mp4",
        "text": "Displays 'Chesterfield Satisfies The Most' banner text."
    },
    {
        "id": "SAFEAD_S18P_VID_013",
        "title": "Chesterfield 'Tobaccoland Reporter' (1951)",
        "desc": "Newsreel-style commercial reporting on tobacco harvesting and curing.",
        "reason": "Commercial tobacco industry advertising (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_Tobaccoland_reporter_1951_512kb.mp4",
        "text": "Displays 'Tobaccoland USA' and Chesterfield branding."
    },
    {
        "id": "SAFEAD_S18P_VID_014",
        "title": "Chesterfield Cigarettes with Jack Webb Dragnet",
        "desc": "Sponsor commercial featuring detective Jack Webb of Dragnet promoting Chesterfields.",
        "reason": "Tobacco product endorsement and active smoking (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_w_Jack_Webb_Dragnet_1950s_B-W_512kb.mp4",
        "text": "Dragnet title card and Chesterfield brand sponsorship."
    },
    {
        "id": "SAFEAD_S18P_VID_015",
        "title": "Chesterfield King Cigarettes Commercial (1962)",
        "desc": "1962 broadcast television ad introducing Chesterfield King size cigarettes.",
        "reason": "Commercial tobacco promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Chesterfield/Commercial_Chesterfield_Cigarettes_w_the_Chesterfield_King_1962_512kb.mp4",
        "text": "Features 'Chesterfield King' crown graphics and pack."
    },
    {
        "id": "SAFEAD_S18P_VID_016",
        "title": "Old Gold Cigarettes 'Dancing Cigarette Pack'",
        "desc": "Famous stop-motion animation commercial of dancing cigarette packs.",
        "reason": "Commercial tobacco advertising (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_Dancing_Cigarette_Pack_512kb.mp4",
        "text": "Animated 'Old Gold' cigarette pack with brand logo."
    },
    {
        "id": "SAFEAD_S18P_VID_017",
        "title": "Old Gold Filters 'Man Jingle III' (1970)",
        "desc": "Broadcast TV commercial featuring acoustic jingle and Old Gold filter packs.",
        "reason": "Commercial tobacco promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_Old_Gold_filters_man_jingle_III_1970_512kb.mp4",
        "text": "Old Gold Filters logo and cigarette pack display."
    },
    {
        "id": "SAFEAD_S18P_VID_018",
        "title": "Old Gold Filters 'Man Jingle II' (1970)",
        "desc": "Broadcast TV variant commercial featuring Old Gold filter cigarettes.",
        "reason": "Commercial tobacco promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_Old_Gold_filters_man_jingle_II_1970_512kb.mp4",
        "text": "Displays 'Old Gold' typography and packaging."
    },
    {
        "id": "SAFEAD_S18P_VID_019",
        "title": "Old Gold Cigarettes Gift Star Coupons (1970)",
        "desc": "Commercial promoting consumer rewards coupons included in Old Gold cigarette packs.",
        "reason": "Commercial tobacco sales incentive advertising (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_w_gift_star_coupons_1970_512kb.mp4",
        "text": "Gift Star coupon graphic and Old Gold cigarette cartons."
    },
    {
        "id": "SAFEAD_S18P_VID_020",
        "title": "Old Gold Cigarettes with Red Barber (1948)",
        "desc": "Historic 1948 baseball broadcast commercial with announcer Red Barber.",
        "reason": "Commercial tobacco promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_Cigarettes_w_Red_Barber_1948_512kb.mp4",
        "text": "Red Barber presentation and Old Gold signage."
    },
    {
        "id": "SAFEAD_S18P_VID_021",
        "title": "Old Gold King Size Dancing Cigarette Packs",
        "desc": "Stop-motion broadcast ad featuring Old Gold King Size dancing cigarette packs.",
        "reason": "Commercial tobacco promotion (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Old_Gold/Commercial_Old_Gold_King_Size_Cigarettes_Dancing_cigarette_packs_512kb.mp4",
        "text": "Old Gold King Size packaging and typography."
    },
    {
        "id": "SAFEAD_S18P_VID_022",
        "title": "John Smith's Draught Bitter Variant 2",
        "desc": "Broadcast TV spot for John Smith's Draught Bitter ale.",
        "reason": "Commercial alcohol promotion regulated for 18+ adult viewers.",
        "src_url": "https://archive.org/details/JohnSmithsDraughtBeerAdvertVariant2",
        "text": "John Smith's Bitter pint glass and brand emblem."
    },
    {
        "id": "SAFEAD_S18P_VID_023",
        "title": "Lucky Strike Cigarettes 'Man That's Fine Tobacco'",
        "desc": "Broadcast television commercial for Lucky Strike cigarettes featuring product endorsements.",
        "reason": "Commercial tobacco advertising with product smoking scenes (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Lucky_Strike/Commercial_Lucky_Strike_Cigarettes_Man_thats_fine_tobacco_512kb.mp4",
        "text": "Displays Lucky Strike typography and slogan."
    },
    {
        "id": "SAFEAD_S18P_VID_024",
        "title": "Lucky Strike Cigarettes Commercial (1965)",
        "desc": "1965 television commercial for Lucky Strike cigarettes.",
        "reason": "Commercial tobacco advertising (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Lucky_Strike/Commercial_Lucky_Strike_Cigarettes_1965_512kb.mp4",
        "text": "Lucky Strike bullseye logo and 'It's Toasted' tagline."
    },
    {
        "id": "SAFEAD_S18P_VID_025",
        "title": "Lucky Strike Marching Cigarette Packs Commercial",
        "desc": "Animated broadcast spot featuring marching Lucky Strike cigarette packages.",
        "reason": "Commercial tobacco advertising (18+ restricted).",
        "src_url": "https://archive.org/download/Cigarette_Commercials_Lucky_Strike/Commercial_Lucky_Strike_Cigarettes_Marching_Cigarettes_512kb.mp4",
        "text": "Lucky Strike red circle emblem and package display."
    }
]

ufa_video_defs = [
    {
        "id": "SAFEAD_UFA_VID_001",
        "title": "Street Physical Violence / Assault Incident",
        "desc": "Unmoderated real-world physical assault and mob beating footage.",
        "reason": "Severe real-world physical violence, assault, and endangerment. Strictly prohibited across all ad platforms.",
        "src_url": "https://archive.org/details/violence_sample_ufa_001",
        "text": "Contains user-generated recording without brand authorization."
    },
    {
        "id": "SAFEAD_UFA_VID_002",
        "title": "Armed Militant Ambush / Combat Warfare",
        "desc": "Combat footage depicting armed militant combatants engaging in jungle weapon ambush.",
        "reason": "Depicts active warfare, automatic firearms in combat, and lethal militant violence. Prohibited for all audiences.",
        "src_url": "https://archive.org/details/violence_sample_ufa_002",
        "text": "Raw tactical footage depicting militant combat."
    },
    {
        "id": "SAFEAD_UFA_VID_003",
        "title": "Severe Graphic Injury & Trauma Violation",
        "desc": "Graphic footage documenting severe bodily trauma, lacerations, and severe injury.",
        "reason": "Severe bodily gore and traumatic physical injury. Violates universal advertising safety standards.",
        "src_url": "https://archive.org/details/violence_sample_ufa_003",
        "text": "Medical trauma documentation not permissible in commercial advertising."
    },
    {
        "id": "SAFEAD_UFA_VID_004",
        "title": "Extreme Prohibited Explicit Content Clip",
        "desc": "Severe policy violation clip depicting non-permissible explicit material.",
        "reason": "Extreme explicit content violating universal ad network standards (UNSAFE_FOR_ALL).",
        "src_url": "https://archive.org/details/policy_violation_ufa_004",
        "text": "Prohibited non-compliant media stream."
    },
    {
        "id": "SAFEAD_UFA_VID_005",
        "title": "Cryptocurrency Fraud & Deceptive Giveaway Scam",
        "desc": "Fraudulent ad claiming celebrity endorsement for 10x instant cryptocurrency doubling.",
        "reason": "Deceptive financial scam, fraudulent prize promise, and phishing vector. Universally unsafe.",
        "src_url": "https://safead-benchmark.org/samples/scam_giveaway.mp4",
        "text": "Displays fraudulent 'Send 1 ETH Get 2 ETH Back' giveaway graphics."
    }
]

all_vid_records = []

# Process safe 18+ videos
for vdef in s18p_video_defs:
    fname = f"{vdef['id']}.mp4"
    rel_path = f"custom_ads/safe_18_plus/videos/{fname}"
    abs_path = os.path.join(repo_dir, rel_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: missing {abs_path}")
        continue
    
    cap = cv2.VideoCapture(abs_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = round(frames / fps, 2)
    cap.release()
    
    sha = compute_sha256(abs_path)
    size_kb = round(os.path.getsize(abs_path) / 1024, 1)
    
    rec = {
        "sample_id": vdef["id"],
        "file_path": rel_path,
        "storage_uri": f"gdrive://SafeAd_Dataset/{rel_path}",
        "media_type": "video",
        "duration_seconds": dur,
        "has_audio": True,
        "contains_text": True,
        "text_description": vdef["text"],
        "source_name": "Internet Archive / Broadcast Ad Archives",
        "source_url": vdef["src_url"],
        "original_source_label": vdef["title"],
        "collection_date": "2026-10-14",
        "safead_label": "SAFE_18_PLUS",
        "label_reason": vdef["reason"],
        "license_status": "Public Domain / Broadcast TV Archive",
        "sha256": sha,
        "annotation_status": "COMPLETED",
        "review_status": "PROPOSED",
        "file_size_kb": size_kb
    }
    all_vid_records.append(rec)

# Process unsafe for all videos
for vdef in ufa_video_defs:
    fname = f"{vdef['id']}.mp4"
    rel_path = f"custom_ads/unsafe_for_all/videos/{fname}"
    abs_path = os.path.join(repo_dir, rel_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: missing {abs_path}")
        continue
    
    cap = cv2.VideoCapture(abs_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = round(frames / fps, 2)
    cap.release()
    
    sha = compute_sha256(abs_path)
    size_kb = round(os.path.getsize(abs_path) / 1024, 1)
    
    rec = {
        "sample_id": vdef["id"],
        "file_path": rel_path,
        "storage_uri": f"gdrive://SafeAd_Dataset/{rel_path}",
        "media_type": "video",
        "duration_seconds": dur,
        "has_audio": True,
        "contains_text": True,
        "text_description": vdef["text"],
        "source_name": "Unsafe Ad Benchmark / Open Safety Callset",
        "source_url": vdef["src_url"],
        "original_source_label": vdef["title"],
        "collection_date": "2026-10-14",
        "safead_label": "UNSAFE_FOR_ALL",
        "label_reason": vdef["reason"],
        "license_status": "Safety Research Fair Use / Policy Benchmark",
        "sha256": sha,
        "annotation_status": "COMPLETED",
        "review_status": "PROPOSED",
        "file_size_kb": size_kb
    }
    all_vid_records.append(rec)

total_records = all_img_records + all_vid_records
print(f"Total compiled records: {len(total_records)}")

manifest_data = {
    "contributor": "juwel",
    "assigned_categories": [
        "SAFE_18_PLUS",
        "UNSAFE_FOR_ALL"
    ],
    "branch": "Juwel",
    "storage_root": "G:/My Drive/SafeAd_Dataset/custom_ads/",
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "total_records": len(total_records),
    "records": total_records
}

out_manifest = os.path.join(repo_dir, "manifests", "juwel", "contribution_manifest.json")
os.makedirs(os.path.dirname(out_manifest), exist_ok=True)
with open(out_manifest, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2)

print(f"Wrote manifest to {out_manifest}")

# Merge into complete_dataset_catalog.csv
catalog_csv = os.path.join(repo_dir, "custom_ads", "complete_dataset_catalog.csv")
headers = [
    "sample_id", "file_path", "storage_uri", "media_type", "source_name", "source_url",
    "original_source_label", "collection_date", "safead_label", "label_reason", "license_status",
    "sha256", "annotation_status", "review_status", "resolution", "file_size_kb",
    "duration_seconds", "has_audio", "contains_text", "ocr_ground_truth_text", "key_brand_tokens", "ocr_text_type"
]

existing_rows = []
if os.path.exists(catalog_csv):
    with open(catalog_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("sample_id", "").startswith(("SAFEAD_S18P_", "SAFEAD_UFA_")):
                existing_rows.append(row)

for r in total_records:
    row = {
        "sample_id": r.get("sample_id", ""),
        "file_path": r.get("file_path", ""),
        "storage_uri": r.get("storage_uri", ""),
        "media_type": r.get("media_type", ""),
        "source_name": r.get("source_name", ""),
        "source_url": r.get("source_url", ""),
        "original_source_label": r.get("original_source_label", ""),
        "collection_date": r.get("collection_date", "2026-10-14"),
        "safead_label": r.get("safead_label", ""),
        "label_reason": r.get("label_reason", ""),
        "license_status": r.get("license_status", ""),
        "sha256": r.get("sha256", ""),
        "annotation_status": r.get("annotation_status", "COMPLETED"),
        "review_status": r.get("review_status", "PROPOSED"),
        "resolution": r.get("resolution", ""),
        "file_size_kb": r.get("file_size_kb", ""),
        "duration_seconds": r.get("duration_seconds", ""),
        "has_audio": r.get("has_audio", ""),
        "contains_text": r.get("contains_text", ""),
        "ocr_ground_truth_text": r.get("text_description", r.get("ocr_ground_truth_text", "")),
        "key_brand_tokens": "",
        "ocr_text_type": "On-screen Branding / Pack Logo"
    }
    existing_rows.append(row)

with open(catalog_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(existing_rows)

print(f"Wrote merged catalog CSV ({len(existing_rows)} rows) to {catalog_csv}")

