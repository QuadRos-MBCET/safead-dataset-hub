import pytest
from tools.registry import list_candidate_datasets, get_candidate_dataset


def test_registry_contains_all_six_candidates():
    datasets = list_candidate_datasets()
    assert len(datasets) >= 6

    expected_ids = {
        "conpro_bad_ads",
        "hateful_memes",
        "dehate",
        "jigsaw_toxic",
        "utkface",
        "fairface"
    }
    registered_ids = {d["id"] for d in datasets}
    assert expected_ids.issubset(registered_ids)


def test_registry_fields_complete():
    required_keys = [
        "id",
        "name",
        "official_source_url",
        "paper_title",
        "modality",
        "media_types",
        "purpose",
        "actual_label_types",
        "potential_safead_use",
        "access_requirements",
        "license_status",
        "commercial_restrictions",
        "attribution_requirements",
        "download_import_instructions",
        "known_limitations",
        "verification_status"
    ]

    for ds in list_candidate_datasets():
        for key in required_keys:
            assert key in ds, f"Dataset {ds['id']} missing required key '{key}'"
            assert ds[key], f"Dataset {ds['id']} has empty value for key '{key}'"


def test_get_candidate_dataset_existing_and_nonexistent():
    cp = get_candidate_dataset("conpro_bad_ads")
    assert cp is not None
    assert cp["name"] == "Bad News / ConPro Online Ads Dataset"

    missing = get_candidate_dataset("non_existent_dataset")
    assert missing is None
