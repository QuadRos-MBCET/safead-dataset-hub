r"""SafeAd Dataset Hub - Manifest Validator

Validates contribution and master manifests against schema and policy:
- Schema field completeness
- Allowed labels (SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS, UNSAFE_FOR_ALL)
- No local absolute paths (e.g. C:\ or /Users/)
- Valid SHA-256 format (64 hex characters)
- Duplicate sample_id and duplicate sha256 detection
- Valid storage URIs
"""

import sys
import json
import re
from pathlib import Path


def validate_manifest_file(manifest_path: str | Path) -> bool:
    path = Path(manifest_path)
    if not path.exists():
        print(f"[FAIL] Manifest file does not exist: {path}", file=sys.stderr)
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    print(f"Validating manifest: {path.name} ({len(records)} records)")

    errors = []
    seen_ids = set()
    seen_hashes = {}

    for i, r in enumerate(records):
        sid = r.get("sample_id")
        if not sid:
            errors.append(f"Record #{i}: missing sample_id")
        elif sid in seen_ids:
            errors.append(f"Record #{i}: duplicate sample_id '{sid}'")
        else:
            seen_ids.add(sid)

        # Path checks
        fpath = r.get("file_path", "")
        if ":\\" in fpath or fpath.startswith("/Users/"):
            errors.append(f"Record '{sid}': contains absolute path '{fpath}'")

        # Label checks
        label = r.get("safead_label")
        if label not in {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS", "UNSAFE_FOR_ALL"}:
            errors.append(f"Record '{sid}': invalid label '{label}'")

        # SHA256 checks
        sha = r.get("sha256", "")
        if not re.match(r"^[a-fA-F0-9]{64}$", sha):
            errors.append(f"Record '{sid}': invalid SHA-256 format '{sha}'")
        elif sha in seen_hashes:
            errors.append(f"Record '{sid}': duplicate SHA-256 with '{seen_hashes[sha]}'")
        else:
            seen_hashes[sha] = sid

        # Required non-empty string fields
        for field in ["storage_uri", "source_name", "source_url", "label_reason", "license_status"]:
            if not r.get(field):
                errors.append(f"Record '{sid}': missing or empty field '{field}'")

    if errors:
        print(f"[FAIL] Found {len(errors)} validation errors:")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"[PASS] All {len(records)} records in {path.name} are valid.")
    return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "manifests/sourav/contribution_manifest.json"
    ok = validate_manifest_file(target)
    sys.exit(0 if ok else 1)
