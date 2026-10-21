"""
test_content_manifest.py
------------------------
Automated test suite verifying the integrity, policy compliance,
and media accessibility of app_content/content_manifest.json.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "app_content" / "content_manifest.json"

class TestAppContentManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = MANIFEST_PATH
        cls.assertTrue(cls.manifest_path.exists(), f"Manifest file missing: {cls.manifest_path}")
        with open(cls.manifest_path, "r", encoding="utf-8") as f:
            cls.manifest_data = json.load(f)
        cls.items = cls.manifest_data.get("content_items", [])

    def test_manifest_metadata(self):
        """Manifest contains version, description, counts, and items."""
        self.assertIn("manifest_version", self.manifest_data)
        self.assertIn("content_items", self.manifest_data)
        self.assertGreater(len(self.items), 0)
        self.assertEqual(len(self.items), self.manifest_data.get("total_items"))

    def test_all_items_files_exist_on_disk(self):
        """Every single manifest item references a genuine file on disk."""
        missing = []
        for item in self.items:
            rel_path = item.get("media_path")
            full_path = REPO_ROOT / rel_path
            if not full_path.exists():
                missing.append((item.get("content_id"), rel_path))
        self.assertEqual(missing, [], f"Missing media files detected: {missing}")

    def test_no_duplicate_content_ids(self):
        """Every content item has a strictly unique ID."""
        seen = set()
        duplicates = []
        for item in self.items:
            cid = item.get("content_id")
            if cid in seen:
                duplicates.append(cid)
            seen.add(cid)
        self.assertEqual(duplicates, [], f"Duplicate content IDs found: {duplicates}")

    def test_valid_age_categories(self):
        """Only project-approved age categories are allowed in the manifest."""
        allowed = {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"}
        for item in self.items:
            cat = item.get("age_category")
            self.assertIn(cat, allowed, f"Invalid category '{cat}' in item {item.get('content_id')}")

    def test_strict_exclusion_of_unsafe_content(self):
        """UNSAFE_FOR_ALL and deceptive/scam media must NEVER be in app_content manifest."""
        for item in self.items:
            cat = item.get("age_category")
            mpath = item.get("media_path", "").lower()
            cid = item.get("content_id", "")
            self.assertNotEqual(cat, "UNSAFE_FOR_ALL", f"Item {cid} has prohibited category UNSAFE_FOR_ALL")
            self.assertNotIn("unsafe_for_all", mpath, f"Item {cid} references unsafe path: {mpath}")
            self.assertNotIn("scam", mpath, f"Item {cid} references scam path: {mpath}")

    def test_all_items_approved(self):
        """All published items must have moderation_status == 'APPROVED'."""
        for item in self.items:
            self.assertEqual(
                item.get("moderation_status"),
                "APPROVED",
                f"Item {item.get('content_id')} is not APPROVED"
            )

    def test_media_type_matches_extension(self):
        """Images must have image extensions; reels must have video extensions."""
        image_exts = {".jpg", ".jpeg", ".png", ".webp"}
        video_exts = {".mp4", ".mov", ".avi", ".webm"}
        for item in self.items:
            ctype = item.get("content_type")
            ext = Path(item.get("media_path")).suffix.lower()
            if ctype == "image":
                self.assertIn(ext, image_exts, f"Item {item.get('content_id')} type is image but extension is {ext}")
            elif ctype == "reel":
                self.assertIn(ext, video_exts, f"Item {item.get('content_id')} type is reel but extension is {ext}")
            else:
                self.fail(f"Item {item.get('content_id')} has unsupported type: {ctype}")

    def test_minimum_age_alignment(self):
        """Minimum age matches category definition exactly."""
        expected_min = {
            "SAFE_FOR_ALL": 0,
            "SAFE_14_PLUS": 14,
            "SAFE_18_PLUS": 18
        }
        for item in self.items:
            cat = item.get("age_category")
            min_age = item.get("minimum_age")
            self.assertEqual(
                min_age,
                expected_min[cat],
                f"Item {item.get('content_id')} min_age {min_age} mismatch for category {cat}"
            )

    def test_age_filtering_contract(self):
        """
        Verify the access rules:
        - Under 14: only SAFE_FOR_ALL
        - 14-17: SAFE_FOR_ALL and SAFE_14_PLUS
        - 18+: SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS
        """
        def filter_for_user(age: int, items: list):
            if age < 14:
                allowed_cats = {"SAFE_FOR_ALL"}
            elif 14 <= age <= 17:
                allowed_cats = {"SAFE_FOR_ALL", "SAFE_14_PLUS"}
            else:
                allowed_cats = {"SAFE_FOR_ALL", "SAFE_14_PLUS", "SAFE_18_PLUS"}
            return [it for it in items if it["age_category"] in allowed_cats]

        # Test user aged 10
        feed_child = filter_for_user(10, self.items)
        self.assertTrue(all(it["age_category"] == "SAFE_FOR_ALL" for it in feed_child))
        self.assertFalse(any(it["age_category"] == "SAFE_14_PLUS" for it in feed_child))
        self.assertFalse(any(it["age_category"] == "SAFE_18_PLUS" for it in feed_child))

        # Test user aged 15
        feed_teen = filter_for_user(15, self.items)
        teen_cats = set(it["age_category"] for it in feed_teen)
        self.assertEqual(teen_cats, {"SAFE_FOR_ALL", "SAFE_14_PLUS"})
        self.assertFalse(any(it["age_category"] == "SAFE_18_PLUS" for it in feed_teen))

        # Test user aged 25
        feed_adult = filter_for_user(25, self.items)
        adult_cats = set(it["age_category"] for it in feed_adult)
        self.assertIn("SAFE_FOR_ALL", adult_cats)
        self.assertIn("SAFE_14_PLUS", adult_cats)

if __name__ == "__main__":
    unittest.main()
