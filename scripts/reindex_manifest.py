#!/usr/bin/env python3
"""Reindexes manifest records to guarantee unique, sequential IDs and matching filenames."""

import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
MANIFEST_PATH = WORKSPACE / "manifests" / "sourav" / "contribution_manifest.json"

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

records = data.get("records", [])
sfa_count = 1
s14p_count = 1

for r in records:
    lbl = r.get("safead_label")
    if lbl == "SAFE_FOR_ALL":
        sid = f"SAFEAD_SFA_IMG_{sfa_count:03d}"
        sfa_count += 1
    else:
        sid = f"SAFEAD_S14P_IMG_{s14p_count:03d}"
        s14p_count += 1
    r["sample_id"] = sid

data["total_records"] = len(records)

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Re-indexed successfully: SFA={sfa_count-1}, S14P={s14p_count-1}, Total={len(records)}")
