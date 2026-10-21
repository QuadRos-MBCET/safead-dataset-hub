import os
import sys
import json
import hashlib
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parent.parent
CUSTOM_ADS = REPO_ROOT / "custom_ads"
GDRIVE_ROOT = Path(r"G:\My Drive\SafeAd_Dataset\custom_ads")

# 1. Load real UFA video metadata
with open(REPO_ROOT / "scripts" / "real_ufa_videos_metadata.json", "r", encoding="utf-8") as f:
    real_vids_meta = json.load(f)

# Also ensure SAFEAD_UFA_VID_001 to 004 and 006 are included
existing_cat = pd.read_csv(CUSTOM_ADS / "complete_dataset_catalog.csv")

# Filter out any old synthetic UFA records (005, 007 to 025)
ufa_keep_ids = {"SAFEAD_UFA_VID_001", "SAFEAD_UFA_VID_002", "SAFEAD_UFA_VID_003", "SAFEAD_UFA_VID_004", "SAFEAD_UFA_VID_006"}
preserved_df = existing_cat[
    (existing_cat["safead_label"] != "UNSAFE_FOR_ALL") |
    (existing_cat["media_type"] == "image") |
    (existing_cat["sample_id"].isin(ufa_keep_ids))
]

# Convert real_vids_meta into dataframe
new_vids_df = pd.DataFrame(real_vids_meta)

# Combine and sort
combined_df = pd.concat([preserved_df, new_vids_df], ignore_index=True)

# Drop any accidental duplicates
combined_df = combined_df.drop_duplicates(subset=["sample_id"])

# Sort order: SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS, UNSAFE_FOR_ALL
tier_sort = {"SAFE_FOR_ALL": 1, "SAFE_14_PLUS": 2, "SAFE_18_PLUS": 3, "UNSAFE_FOR_ALL": 4}
combined_df["_sort"] = combined_df["safead_label"].map(tier_sort)
combined_df = combined_df.sort_values(by=["_sort", "media_type", "sample_id"]).drop(columns=["_sort"]).reset_index(drop=True)

print("Master dataset counts:")
print(combined_df.groupby(["safead_label", "media_type"]).size())
print("Total rows:", len(combined_df))

# Save updated complete_dataset_catalog.csv
cat_csv_path = CUSTOM_ADS / "complete_dataset_catalog.csv"
combined_df.to_csv(cat_csv_path, index=False)
combined_df.to_csv(CUSTOM_ADS / "SafeAd_Master_Dataset_Combined.csv", index=False)
print(f"Saved master CSV to {cat_csv_path}")

# Update Juwel manifest
with open(REPO_ROOT / "manifests" / "juwel" / "contribution_manifest.json", "r", encoding="utf-8") as f:
    juwel_data = json.load(f)

juwel_records = combined_df[combined_df["safead_label"].isin(["SAFE_18_PLUS", "UNSAFE_FOR_ALL"])].to_dict(orient="records")
juwel_data["records"] = juwel_records
juwel_data["total_records"] = len(juwel_records)
juwel_data["counts_by_tier"] = {
    "SAFE_18_PLUS": int((combined_df["safead_label"] == "SAFE_18_PLUS").sum()),
    "UNSAFE_FOR_ALL": int((combined_df["safead_label"] == "UNSAFE_FOR_ALL").sum())
}
juwel_data["counts_by_type"] = {
    "image": int((combined_df["media_type"] == "image").sum() // 2),
    "video": int((combined_df["media_type"] == "video").sum() // 2)
}
with open(REPO_ROOT / "manifests" / "juwel" / "contribution_manifest.json", "w", encoding="utf-8") as f:
    json.dump(juwel_data, f, indent=2)
print("Updated Juwel manifest to 200 records.")

# Update ocr_accuracy_ground_truth.csv
ocr_path = CUSTOM_ADS / "ocr_accuracy_ground_truth.csv"
existing_ocr = pd.read_csv(ocr_path)
# Keep SFA, S14P, and preserve non-synthetic UFA
ocr_clean = existing_ocr[~existing_ocr["sample_id"].isin([r["sample_id"] for r in real_vids_meta])]

new_ocr_rows = []
for r in real_vids_meta:
    new_ocr_rows.append({
        "sample_id": r["sample_id"],
        "media_type": "video",
        "category": "UNSAFE_FOR_ALL",
        "file_path": r["file_path"],
        "contains_text": True,
        "ocr_ground_truth_text": r["ocr_ground_truth_text"],
        "key_brand_tokens": r["key_brand_tokens"],
        "ocr_text_type": r["ocr_text_type"],
        "evaluation_metric_recommended": "Token-Recall & Levenshtein-Similarity",
        "instructions_for_testing": "Extract keyframes, run OCR model, calculate case-insensitive token recall."
    })
updated_ocr_df = pd.concat([ocr_clean, pd.DataFrame(new_ocr_rows)], ignore_index=True)
updated_ocr_df.to_csv(ocr_path, index=False)
print(f"Updated OCR ground truth to {len(updated_ocr_df)} rows.")

# 2. Build High-Quality Master Excel Workbook
COLUMN_WIDTHS = {
    "sample_id": 24,
    "file_path": 58,
    "storage_uri": 75,
    "media_type": 14,
    "source_name": 44,
    "source_url": 60,
    "original_source_label": 48,
    "collection_date": 16,
    "safead_label": 18,
    "label_reason": 68,
    "license_status": 36,
    "sha256": 68,
    "annotation_status": 20,
    "review_status": 16,
    "resolution": 16,
    "file_size_kb": 16,
    "duration_seconds": 18,
    "has_audio": 14,
    "contains_text": 15,
    "ocr_ground_truth_text": 68,
    "key_brand_tokens": 42,
    "ocr_text_type": 36
}

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove empty default sheet

# Professional Styles
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
fill_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_crimson = PatternFill(start_color="881337", end_color="881337", fill_type="solid")
fill_emerald = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
fill_amber = PatternFill(start_color="92400E", end_color="92400E", fill_type="solid")
fill_slate = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
fill_alt_row = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

font_body = Font(name="Segoe UI", size=10)
font_bold_id = Font(name="Segoe UI", size=10, bold=True)

border_cell = Border(
    left=Side(style='thin', color='E2E8F0'),
    right=Side(style='thin', color='E2E8F0'),
    top=Side(style='thin', color='E2E8F0'),
    bottom=Side(style='thin', color='E2E8F0')
)

CENTER_COLS = {"sample_id", "media_type", "collection_date", "safead_label", "annotation_status", "review_status", "resolution", "has_audio", "contains_text"}
RIGHT_COLS = {"file_size_kb", "duration_seconds"}

def write_catalog_sheet(wb, title, df, header_fill):
    ws = wb.create_sheet(title=title)
    ws.views.sheetView[0].showGridLines = True
    
    headers = list(df.columns)
    ws.append(headers)
    ws.row_dimensions[1].height = 28
    
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=c_idx)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
        cell.border = border_cell
        
    for r_idx, row in df.iterrows():
        row_num = r_idx + 2
        ws.row_dimensions[row_num].height = 22
        is_even = (r_idx % 2 == 1)
        
        row_data = []
        for val in row:
            if pd.isna(val):
                row_data.append("")
            elif isinstance(val, bool):
                row_data.append("TRUE" if val else "FALSE")
            else:
                row_data.append(val)
        ws.append(row_data)
        
        for c_idx, col_name in enumerate(headers, 1):
            c = ws.cell(row=row_num, column=c_idx)
            c.border = border_cell
            if is_even:
                c.fill = fill_alt_row
                
            if col_name == "sample_id":
                c.font = font_bold_id
            else:
                c.font = font_body
                
            if col_name in CENTER_COLS:
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_name in RIGHT_COLS:
                c.alignment = Alignment(horizontal="right", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")
                
    # Apply column widths
    for c_idx, col_name in enumerate(headers, 1):
        col_letter = get_column_letter(c_idx)
        w = COLUMN_WIDTHS.get(col_name, 25)
        ws.column_dimensions[col_letter].width = w
        
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws

# 1. Primary Sheet: Complete_Dataset (ALL 400 Records)
write_catalog_sheet(wb, "Complete_Dataset", combined_df, fill_navy)

# 2. Category Sheet: Unsafe_For_All (100 Records)
ufa_df = combined_df[combined_df["safead_label"] == "UNSAFE_FOR_ALL"].copy()
write_catalog_sheet(wb, "UNSAFE_FOR_ALL", ufa_df, fill_crimson)

# 3. Category Sheet: Safe_For_All (100 Records)
sfa_df = combined_df[combined_df["safead_label"] == "SAFE_FOR_ALL"].copy()
write_catalog_sheet(wb, "SAFE_FOR_ALL", sfa_df, fill_emerald)

# 4. Category Sheet: Safe_14_Plus (100 Records)
s14p_df = combined_df[combined_df["safead_label"] == "SAFE_14_PLUS"].copy()
write_catalog_sheet(wb, "SAFE_14_PLUS", s14p_df, fill_amber)

# 5. Category Sheet: Safe_18_Plus (100 Records)
s18p_df = combined_df[combined_df["safead_label"] == "SAFE_18_PLUS"].copy()
write_catalog_sheet(wb, "SAFE_18_PLUS", s18p_df, fill_slate)

# 6. Sheet: OCR_Ground_Truth
write_catalog_sheet(wb, "OCR_Ground_Truth", updated_ocr_df, fill_navy)

# Save Excel files
excel_main = CUSTOM_ADS / "SafeAd_Consolidated_Dataset_Hub.xlsx"
excel_catalog = CUSTOM_ADS / "complete_dataset_catalog.xlsx"
excel_root = REPO_ROOT / "SafeAd_Consolidated_Dataset_Hub.xlsx"

wb.save(str(excel_main))
wb.save(str(excel_catalog))
wb.save(str(excel_root))
print(f"Generated clean Excel workbook: {excel_main} ({excel_main.stat().st_size} bytes)")

# Mirror to Google Drive
if GDRIVE_ROOT.exists():
    import shutil
    wb.save(str(GDRIVE_ROOT / "SafeAd_Consolidated_Dataset_Hub.xlsx"))
    wb.save(str(GDRIVE_ROOT / "complete_dataset_catalog.xlsx"))
    combined_df.to_csv(GDRIVE_ROOT / "complete_dataset_catalog.csv", index=False)
    updated_ocr_df.to_csv(GDRIVE_ROOT / "ocr_accuracy_ground_truth.csv", index=False)
    print("Synchronized Excel and CSV catalogs to Google Drive.")

print("All catalogs and Excel workbooks updated properly!")
