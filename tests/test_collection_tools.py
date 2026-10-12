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
        (self.workspace / "SafeAd_Dataset" / "custom_ads" / "sourav").mkdir(parents=True)

        # Create dummy sample media
        self.dummy_img = self.workspace / "test_ad.jpg"
        self.dummy_img.write_bytes(b"sample image raw bytes 12345")

        self.dummy_vid = self.workspace / "test_ad.mp4"
        self.dummy_vid.write_bytes(b"sample video stream payload 67890")

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


if __name__ == "__main__":
    unittest.main()
