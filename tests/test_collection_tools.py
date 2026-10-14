#!/usr/bin/env python3
"""Unit tests for SafeAd dataset collection and validation tools."""

import unittest
import tempfile
import shutil
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.ad_collector import SafeAdCollector, compute_sha256, detect_media_type
from tools.validate_manifest import validate_manifest_file


class TestSafeAdTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir)
        (self.workspace / "manifests" / "sourav").mkdir(parents=True)
        (self.workspace / "manifests" / "juwel").mkdir(parents=True)
        (self.workspace / "SafeAd_Dataset" / "custom_ads" / "sourav").mkdir(parents=True)
        (self.workspace / "SafeAd_Dataset" / "custom_ads" / "juwel").mkdir(parents=True)

        # Create dummy sample media
        self.dummy_img = self.workspace / "test_ad.jpg"
        self.dummy_img.write_bytes(b"sample image raw bytes 12345")

        self.dummy_vid = self.workspace / "test_ad.mp4"
        self.dummy_vid.write_bytes(b"sample video stream payload 67890" * 10)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_detect_media_type(self):
        self.assertEqual(detect_media_type("sample.jpg"), "image")
        self.assertEqual(detect_media_type("sample.PNG"), "image")
        self.assertEqual(detect_media_type("video.mp4"), "video")
        self.assertEqual(detect_media_type("clip.mov"), "video")
        self.assertIsNone(detect_media_type("doc.pdf"))

    def test_compute_sha256(self):
        h1 = compute_sha256(self.dummy_img)
        h2 = compute_sha256(self.dummy_img)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_import_and_register_record(self):
        collector = SafeAdCollector(self.workspace, contributor="sourav")
        rec = collector.import_and_register_sample(
            src_file=self.dummy_img,
            safead_label="SAFE_FOR_ALL",
            source_name="Wikimedia Commons Ad Archive",
            source_url="https://commons.wikimedia.org/wiki/File:Example_Ad.jpg",
            label_reason="Family-friendly fruit juice advert without any age-restricted elements.",
            license_status="CC-BY-4.0",
        )
        self.assertEqual(rec["safead_label"], "SAFE_FOR_ALL")
        self.assertEqual(rec["media_type"], "image")
        self.assertTrue(rec["file_path"].startswith("SafeAd_Dataset/custom_ads/sourav/safe_for_all/"))
        self.assertNotIn("C:\\", rec["file_path"])
        collector.save_manifest()

        # Validate saved manifest
        val = collector.validate_records()
        self.assertTrue(val["is_valid"])
        self.assertEqual(val["total_records"], 1)

    def test_duplicate_detection(self):
        collector = SafeAdCollector(self.workspace, contributor="sourav")
        collector.import_and_register_sample(
            src_file=self.dummy_img,
            safead_label="SAFE_FOR_ALL",
            source_name="Test Source",
            source_url="https://example.com/ad1",
            label_reason="Wholesome family ad",
            license_status="CC0",
        )
        # Attempt registering same file
        with self.assertRaises(ValueError) as ctx:
            collector.import_and_register_sample(
                src_file=self.dummy_img,
                safead_label="SAFE_FOR_ALL",
                source_name="Test Source Duplicate",
                source_url="https://example.com/ad2",
                label_reason="Same ad content",
                license_status="CC0",
            )
        self.assertIn("Duplicate media detected", str(ctx.exception))

    def test_progress_reporting(self):
        collector = SafeAdCollector(self.workspace, contributor="sourav")
        collector.import_and_register_sample(
            src_file=self.dummy_img,
            safead_label="SAFE_FOR_ALL",
            source_name="Test Source",
            source_url="https://example.com/ad1",
            label_reason="Wholesome family ad",
            license_status="CC0",
        )
        collector.import_and_register_sample(
            src_file=self.dummy_vid,
            safead_label="SAFE_14_PLUS",
            source_name="Video Source",
            source_url="https://example.com/ad2",
            label_reason="Teen sci-fi game ad with mild animated action",
            license_status="CC-BY-3.0",
        )
        rep = collector.generate_progress_report()
        self.assertEqual(rep["counts_by_category"]["SAFE_FOR_ALL"]["image"], 1)
        self.assertEqual(rep["counts_by_category"]["SAFE_14_PLUS"]["video"], 1)
        self.assertEqual(rep["total_collected"], 2)

    def test_juwel_collector_workflow(self):
        collector = SafeAdCollector(self.workspace, contributor="juwel")
        img_18 = self.workspace / "sample_beer.jpg"
        img_18.write_bytes(b"sample adult beverage photo bytes")

        rec18 = collector.import_and_register_sample(
            src_file=img_18,
            safead_label="SAFE_18_PLUS",
            source_name="Alcohol Ad Archive",
            source_url="https://commons.wikimedia.org/wiki/File:Vintage_Ale.jpg",
            label_reason="Regulated craft beer commercial advert with statutory 18+ drinking age notice.",
            license_status="Public Domain",
        )
        self.assertEqual(rec18["safead_label"], "SAFE_18_PLUS")
        self.assertTrue(rec18["file_path"].startswith("SafeAd_Dataset/custom_ads/juwel/safe_18_plus/"))
        self.assertNotIn("C:\\", rec18["file_path"])

        img_unsafe = self.workspace / "sample_scam.png"
        img_unsafe.write_bytes(b"sample deceptive phishing alert screenshot bytes")

        rec_u = collector.import_and_register_sample(
            src_file=img_unsafe,
            safead_label="UNSAFE_FOR_ALL",
            source_name="FTC Consumer Protection Archive",
            source_url="https://www.consumer.ftc.gov/scam-ad.png",
            label_reason="Deceptive virus warning banner urging users to call fake tech support hotline.",
            license_status="US Gov Public Domain",
            review_status="PROPOSED",
        )
        self.assertEqual(rec_u["safead_label"], "UNSAFE_FOR_ALL")
        self.assertTrue(rec_u["file_path"].startswith("SafeAd_Dataset/custom_ads/juwel/unsafe_for_all/"))

        collector.save_manifest()
        self.assertTrue(collector.manifest_path.exists())

        with open(collector.manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["contributor"], "Juwel")
        self.assertEqual(data["assigned_categories"], ["SAFE_18_PLUS", "UNSAFE_FOR_ALL"])
        self.assertEqual(data["branch"], "feature/juwel-18-plus-unsafe")
        self.assertEqual(len(data["records"]), 2)

        # Validate with tools/validate_manifest.py validator
        val_ok = validate_manifest_file(collector.manifest_path)
        self.assertTrue(val_ok)

        # Report check
        rep = collector.generate_progress_report()
        self.assertEqual(rep["counts_by_category"]["SAFE_18_PLUS"]["image"], 1)
        self.assertEqual(rep["counts_by_category"]["UNSAFE_FOR_ALL"]["image"], 1)

    def test_disk_verification(self):
        from PIL import Image
        collector = SafeAdCollector(self.workspace, contributor="juwel")
        test_file = self.workspace / "verified_test.jpg"
        im = Image.new("RGB", (20, 20), color="blue")
        im.save(test_file, "JPEG")

        collector.import_and_register_sample(
            src_file=test_file,
            safead_label="SAFE_18_PLUS",
            source_name="Test Pub",
            source_url="https://example.com/pub1",
            label_reason="Adult pub night advertisement",
            license_status="CC0",
        )

        disk_status = collector.verify_files_on_disk()
        self.assertTrue(disk_status["all_healthy"])
        self.assertEqual(disk_status["verified_on_disk"], 1)

        # Delete file from disk to test missing detection
        target_path = self.workspace / collector.records[0]["file_path"]
        target_path.unlink()

        disk_status_missing = collector.verify_files_on_disk()
        self.assertFalse(disk_status_missing["all_healthy"])
        self.assertEqual(len(disk_status_missing["missing_files"]), 1)

    def test_near_duplicate_and_needs_review(self):
        collector = SafeAdCollector(self.workspace, contributor="juwel")
        f1 = self.workspace / "ad1.png"
        f1.write_bytes(b"content 1")
        f2 = self.workspace / "ad2.png"
        f2.write_bytes(b"content 2")

        shared_url = "https://example.com/same-campaign"
        collector.import_and_register_sample(
            src_file=f1,
            safead_label="SAFE_18_PLUS",
            source_name="Campaign",
            source_url=shared_url,
            label_reason="Nightclub party banner #1",
            license_status="CC-BY-4.0",
        )
        collector.import_and_register_sample(
            src_file=f2,
            safead_label="SAFE_18_PLUS",
            source_name="Campaign",
            source_url=shared_url,
            label_reason="Nightclub party banner #2 with dual-meaning claim",
            license_status="CC-BY-4.0",
            review_status="NEEDS_REVIEW",
        )

        val = collector.validate_records()
        self.assertTrue(val["is_valid"])
        self.assertTrue(any("Near-duplicate" in w for w in val["warnings"]))

        rep = collector.generate_progress_report()
        self.assertEqual(rep["review_status_counts"]["PROPOSED"], 1)
        self.assertEqual(rep["review_status_counts"]["NEEDS_REVIEW"], 1)


if __name__ == "__main__":
    unittest.main()
