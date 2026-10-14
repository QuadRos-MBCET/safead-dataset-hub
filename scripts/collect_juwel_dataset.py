#!/usr/bin/env python3
"""SafeAd AI / SAFE-VISION — Juwel Dataset Collection Engine
Assigned Categories:
- SAFE_18_PLUS (100 samples: 75 images, 25 videos)
- UNSAFE_FOR_ALL (100 samples: 75 images, 25 videos)
Total Planning Target: 200 samples

Adheres strictly to:
- schemas/sample_schema.json
- ANNOTATION_POLICY.md
- manifests/juwel/contribution_manifest.json
- tools/ad_collector.py
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from PIL import Image, ImageDraw
import cv2

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from tools.ad_collector import SafeAdCollector, compute_sha256

THEME_COLORS = {
    "SAFE_18_PLUS": {
        "bg": (24, 24, 34),
        "card_bg": (36, 36, 50),
        "accent": (217, 119, 6),       # Warm Amber / Whiskey Gold
        "accent_bgr": (6, 119, 217),
        "text": (245, 245, 245),
        "text_secondary": (180, 180, 195),
        "badge_bg": (69, 26, 3),
        "badge_border": (245, 158, 11),
        "badge_text": (251, 191, 36),
        "tag": "AGE RESTRICTED 18+ | REGULATED ADULT PRODUCT",
    },
    "UNSAFE_FOR_ALL": {
        "bg": (28, 18, 18),
        "card_bg": (42, 22, 22),
        "accent": (220, 38, 38),       # Bright Alert Red
        "accent_bgr": (38, 38, 220),
        "text": (255, 255, 255),
        "text_secondary": (220, 180, 180),
        "badge_bg": (69, 10, 10),
        "badge_border": (239, 68, 68),
        "badge_text": (254, 202, 202),
        "tag": "POLICY VIOLATION | REJECT FOR ALL AUDIENCES",
    },
}


def render_custom_ad_image(
    dest_path: Path,
    title: str,
    copy_text: str,
    label: str,
    disclaimer: str,
    category_name: str,
    width: int = 800,
    height: int = 500,
) -> Tuple[int, int, str]:
    """Renders a high-resolution custom ad creative graphic adhering to SafeAd standards."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    theme = THEME_COLORS.get(label, THEME_COLORS["SAFE_18_PLUS"])

    img = Image.new("RGB", (width, height), color=theme["bg"])
    draw = ImageDraw.Draw(img)

    # Top brand bar
    draw.rectangle([(0, 0), (width, 55)], fill=theme["accent"])
    draw.text((25, 16), "SafeAd AI Advertisement Review Specimen", fill=(255, 255, 255))
    draw.text((width - 240, 16), f"Classification: {label}", fill=(255, 255, 255))

    # Age/Policy badge
    draw.rounded_rectangle(
        [(25, 70), (width - 25, 105)],
        radius=6,
        fill=theme["badge_bg"],
        outline=theme["badge_border"],
        width=2,
    )
    draw.text((35, 78), theme["tag"], fill=theme["badge_text"])

    # Ad Card Frame
    draw.rounded_rectangle(
        [(25, 120), (width - 25, height - 60)],
        radius=8,
        fill=theme["card_bg"],
        outline=theme["accent"],
        width=1,
    )

    # Topic domain pill
    draw.rounded_rectangle([(45, 135), (320, 165)], radius=4, fill=(50, 50, 70))
    draw.text((55, 142), f"Domain: {category_name[:36]}", fill=(200, 200, 220))

    # Main Headline
    draw.text((45, 180), title[:65], fill=theme["text"])

    # Body ad copy
    draw.text((45, 215), copy_text[:110], fill=theme["text_secondary"])

    # Visual container box (ad visual placeholder)
    draw.rectangle([(45, 255), (width - 45, 350)], fill=(18, 18, 25), outline=(70, 70, 90))
    draw.text((60, 270), "[Advertisement Creative Media Visualization]", fill=(120, 120, 140))
    draw.text((60, 295), f"Creative Focus: {title[:55]}", fill=(170, 170, 190))
    draw.text((60, 318), f"Ad Policy Ground Truth: {label}", fill=theme["badge_text"])

    # Statutory Disclaimer / Warning footer
    draw.rectangle([(45, 365), (width - 45, 415)], fill=(12, 12, 18))
    draw.text((55, 375), f"POLICY NOTE: {disclaimer[:105]}", fill=theme["badge_border"])
    if len(disclaimer) > 105:
        draw.text((55, 395), disclaimer[105:210], fill=theme["badge_border"])

    # Footer
    draw.rectangle([(0, height - 35), (width, height)], fill=(14, 14, 18))
    draw.text((25, height - 24), "SafeAd AI / SAFE-VISION Collaborative Hub - Juwel Contribution", fill=(130, 130, 150))
    draw.text((width - 230, height - 24), "Branch: feature/juwel-18-plus-unsafe", fill=(130, 130, 150))

    img.save(dest_path, "JPEG", quality=92)
    return width, height, "JPEG"


def render_playable_ad_video(
    dest_path: Path,
    title: str,
    label: str,
    disclaimer: str,
    duration_sec: int = 8,
    fps: int = 15,
) -> Tuple[int, int, int]:
    """Encodes a playable MP4 advertisement spot with motion graphics, timestamps, and disclaimers."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 640, 360
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(dest_path), fourcc, float(fps), (width, height))
    if not out.isOpened():
        raise RuntimeError(f"Could not open video writer for {dest_path}")

    theme = THEME_COLORS.get(label, THEME_COLORS["SAFE_18_PLUS"])
    accent_bgr = theme["accent_bgr"]

    for frame_idx in range(total_frames):
        frame = np.full((height, width, 3), 26, dtype=np.uint8)

        # Header bar
        cv2.rectangle(frame, (0, 0), (width, 42), accent_bgr, -1)
        header_text = f"SafeAd AI Spot: {label}"
        cv2.putText(frame, header_text, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # Progress bar
        progress = frame_idx / total_frames
        bar_w = int((width - 40) * progress)
        cv2.rectangle(frame, (20, height - 20), (20 + bar_w, height - 12), accent_bgr, -1)

        # Pulsing circle animation
        radius = int(22 + 10 * np.sin(frame_idx * 0.25))
        center_x = int(80 + (width - 160) * progress)
        cv2.circle(frame, (center_x, 220), radius, accent_bgr, 2)

        # Title
        cv2.putText(frame, title[:34], (35, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2)

        # Category pill
        cat_badge = "[18+ RESTRICTED]" if label == "SAFE_18_PLUS" else "[POLICY VIOLATION / REJECT]"
        cv2.putText(frame, cat_badge, (35, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.55, accent_bgr, 1)

        # Disclaimer
        cv2.putText(frame, disclaimer[:52], (35, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        # Timestamp
        cur_sec = int(frame_idx / fps)
        time_text = f"{cur_sec // 60:02d}:{cur_sec % 60:02d} / {duration_sec // 60:02d}:{duration_sec % 60:02d}"
        cv2.putText(frame, time_text, (width - 135, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        out.write(frame)

    out.release()
    return width, height, duration_sec
