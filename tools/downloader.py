"""
Authorized Dataset Downloader and Tracking Engine for SafeAd AI.

Enforces dataset access compliance, manages download status tracking,
supports dry-run execution, and explicitly handles restricted/gated sources
without attempting unauthorized bypasses.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.hasher import calculate_sha256
from tools.registry import get_candidate_dataset

TRACKER_FILE = Path(__file__).resolve().parent.parent / "configs" / "download_tracker.json"


def load_tracker(tracker_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads current download status tracker."""
    tpath = tracker_path or TRACKER_FILE
    if not tpath.is_file():
        return {"datasets": {}, "last_updated": None}
    with open(tpath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracker(tracker_data: Dict[str, Any], tracker_path: Optional[Path] = None) -> None:
    """Saves download status tracker."""
    tpath = tracker_path or TRACKER_FILE
    tpath.parent.mkdir(parents=True, exist_ok=True)
    tracker_data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump(tracker_data, f, indent=2)


def get_download_status(source_id: str, tracker_path: Optional[Path] = None) -> Dict[str, Any]:
    """Retrieves tracking info for a specific dataset source."""
    tracker = load_tracker(tracker_path)
    return tracker.get("datasets", {}).get(source_id, {
        "status": "not_started",
        "last_checked": None,
        "files_downloaded": []
    })


def update_source_status(
    source_id: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    tracker_path: Optional[Path] = None
) -> None:
    """Updates tracking state for a dataset source."""
    tracker = load_tracker(tracker_path)
    if "datasets" not in tracker:
        tracker["datasets"] = {}

    entry = tracker["datasets"].get(source_id, {})
    entry["status"] = status
    entry["last_updated"] = datetime.now(timezone.utc).isoformat()
    if details:
        entry.update(details)

    tracker["datasets"][source_id] = entry
    save_tracker(tracker, tracker_path)


def download_or_inspect_dataset(
    source_id: str,
    target_dir: Path,
    dry_run: bool = False,
    tracker_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Executes authorized acquisition or access validation for a candidate dataset.
    Strictly prohibits bypassing CAPTCHAs, competition terms, or gated access.
    """
    ds = get_candidate_dataset(source_id)
    if not ds:
        raise ValueError(f"Unknown dataset ID '{source_id}'. Must be registered in registry.")

    access_req = ds.get("access_requirements", "")
    target_dir = Path(target_dir)

    print(f"[{'DRY-RUN' if dry_run else 'EXECUTE'}] Checking source '{ds['name']}' (ID: {source_id})")

    # 1. Gated / Restricted Datasets
    if "Gated" in access_req or "DrivenData" in access_req or "Kaggle" in access_req:
        result = {
            "source_id": source_id,
            "status": "restricted_manual_action_required",
            "access_type": "Gated / Authentication Required",
            "message": f"Source '{source_id}' requires user account registration and license agreement.",
            "instructions": ds.get("download_import_instructions", ""),
            "dry_run": dry_run
        }
        if not dry_run:
            update_source_status(
                source_id,
                status="restricted_manual_action_required",
                details={
                    "access_type": "gated",
                    "manual_instructions": ds.get("download_import_instructions", "")
                },
                tracker_path=tracker_path
            )
        print(f"  -> RESTRICTED: Requires manual user credentials/terms agreement.")
        print(f"  -> Automated bypass is prohibited per policy.\n")
        return result

    # 2. Public datasets with Google Drive or external hosting
    if "Google Drive" in access_req or "author" in access_req.lower():
        result = {
            "source_id": source_id,
            "status": "manual_download_recommended",
            "access_type": "External Google Drive / Author Request",
            "message": f"Large media archives for '{source_id}' are hosted externally.",
            "instructions": ds.get("download_import_instructions", ""),
            "dry_run": dry_run
        }
        if not dry_run:
            update_source_status(
                source_id,
                status="manual_download_recommended",
                details={
                    "access_type": "external_drive",
                    "manual_instructions": ds.get("download_import_instructions", "")
                },
                tracker_path=tracker_path
            )
        print(f"  -> EXTERNAL HOSTING: Stored on verified external drive/repository.")
        print(f"  -> Manual download required into: {target_dir}\n")
        return result

    # 3. Public GitHub Metadata / Direct Files
    result = {
        "source_id": source_id,
        "status": "ready_for_import",
        "access_type": "Public Metadata",
        "dry_run": dry_run
    }
    if not dry_run:
        update_source_status(source_id, status="ready_for_import", tracker_path=tracker_path)
    return result


def initialize_all_candidate_tracking(tracker_path: Optional[Path] = None) -> None:
    """Initializes tracking records for all candidate datasets in registry."""
    from tools.registry import list_candidate_datasets
    candidates = list_candidate_datasets()
    for c in candidates:
        cid = c["id"]
        status = get_download_status(cid, tracker_path)
        if status.get("status") == "not_started":
            is_gated = "Gated" in c.get("access_requirements", "") or "Kaggle" in c.get("access_requirements", "")
            init_status = "restricted_manual_action_required" if is_gated else "pending_verification"
            update_source_status(
                cid,
                status=init_status,
                details={
                    "name": c["name"],
                    "access_requirements": c["access_requirements"],
                    "license_status": c["license_status"]
                },
                tracker_path=tracker_path
            )


def get_default_target_dir() -> Path:
    config_file = Path(__file__).resolve().parent.parent / "configs" / "storage_config.json"
    if config_file.is_file():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                custom_dir = cfg.get("existing_datasets_dir")
                if custom_dir:
                    p = Path(custom_dir)
                    if p.is_absolute() and Path(p.drive + "\\").exists():
                        return p
                    elif not p.is_absolute():
                        return Path(__file__).resolve().parent.parent / p
        except Exception:
            pass
    return Path(__file__).resolve().parent.parent / "SafeAd_Dataset" / "existing_datasets"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SafeAd AI Dataset Downloader & Tracker")
    parser.add_argument("--source", type=str, help="Dataset ID to check or download")
    parser.add_argument("--target-dir", default=str(get_default_target_dir()), help="Target local directory (defaults to external drive if configured)")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run without writing")
    parser.add_argument("--init-tracker", action="store_true", help="Initialize tracking for all candidates")
    parser.add_argument("--status", action="store_true", help="Print download tracking status table")

    args = parser.parse_args()

    if args.init_tracker:
        initialize_all_candidate_tracking()
        print("Initialized tracking for all registered candidate datasets.")

    elif args.status:
        trk = load_tracker()
        print("=" * 80)
        print(f"{'SAFEAD AI - DATASET DOWNLOAD TRACKING STATUS':^80}")
        print("=" * 80)
        for sid, info in trk.get("datasets", {}).items():
            print(f"[{sid:<16}] Status: {info.get('status', 'unknown'):<35} (Updated: {info.get('last_updated', 'N/A')[:19]})")
        print("=" * 80)

    elif args.source:
        tgt = Path(args.target_dir) / args.source
        res = download_or_inspect_dataset(args.source, tgt, dry_run=args.dry_run)
        print(json.dumps(res, indent=2))
    else:
        trk = load_tracker()
        print(f"Tracking {len(trk.get('datasets', {}))} datasets. Use --status to view.")
