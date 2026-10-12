"""
Dataset Source Registry CLI & API for SafeAd AI.
Manages candidate dataset metadata, licenses, access requirements, and verification status.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "registry" / "candidate_datasets.json"


def load_registry(path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads the candidate datasets registry."""
    reg_file = path or REGISTRY_PATH
    if not reg_file.is_file():
        raise FileNotFoundError(f"Registry file not found at {reg_file}")
    with open(reg_file, "r", encoding="utf-8") as f:
        return json.load(f)


def list_candidate_datasets() -> List[Dict[str, Any]]:
    """Returns the list of all registered candidate datasets."""
    reg = load_registry()
    return reg.get("candidate_datasets", [])


def get_candidate_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific dataset by its unique identifier."""
    datasets = list_candidate_datasets()
    for ds in datasets:
        if ds.get("id") == dataset_id:
            return ds
    return None


def print_registry_summary() -> None:
    """Prints a formatted summary table of all registered sources."""
    datasets = list_candidate_datasets()
    print("=" * 85)
    print(f"{'SAFEAD AI - REGISTERED CANDIDATE DATASETS CATALOG':^85}")
    print("=" * 85)
    print(f"{'ID':<16} | {'NAME':<28} | {'MODALITY':<14} | {'ACCESS':<18}")
    print("-" * 85)
    for ds in datasets:
        access_short = "Gated / Terms" if "Gated" in ds.get("access_requirements", "") else "Public / Drive"
        print(f"{ds['id']:<16} | {ds['name'][:28]:<28} | {ds['media_types'][0]:<14} | {access_short:<18}")
    print("=" * 85)


def print_dataset_dossier(dataset_id: str) -> None:
    """Prints the comprehensive engineering dossier for a dataset."""
    ds = get_candidate_dataset(dataset_id)
    if not ds:
        print(f"Error: Dataset '{dataset_id}' not found in registry.")
        return

    print("=" * 80)
    print(f"DOSSIER: {ds['name']} (ID: {ds['id']})")
    print("=" * 80)
    print(f"Official Source URL:   {ds['official_source_url']}")
    print(f"Publication / Paper:   {ds['paper_title']}")
    print(f"Modality:              {ds['modality']}")
    print(f"Purpose:               {ds['purpose']}")
    print("\nActual Labels:")
    for lbl in ds['actual_label_types']:
        print(f"  - {lbl}")
    print(f"\nPotential SafeAd Use:  {ds['potential_safead_use']}")
    print(f"License Status:        {ds['license_status']}")
    print(f"Commercial Terms:      {ds['commercial_restrictions']}")
    print(f"Attribution:           {ds['attribution_requirements']}")
    print(f"Access Requirements:   {ds['access_requirements']}")
    print(f"Verification Status:   {ds['verification_status']}")
    print(f"Known Limitations:     {ds['known_limitations']}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SafeAd AI Dataset Source Registry")
    parser.add_argument("--list", action="store_true", help="List all candidate datasets")
    parser.add_argument("--get", type=str, help="Print detailed dossier for a dataset ID")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if args.list:
        if args.json:
            print(json.dumps(list_candidate_datasets(), indent=2))
        else:
            print_registry_summary()
    elif args.get:
        if args.json:
            print(json.dumps(get_candidate_dataset(args.get), indent=2))
        else:
            print_dataset_dossier(args.get)
    else:
        print_registry_summary()
