#!/usr/bin/env python3
"""Script to search and download genuine advertisement images from Wikimedia Commons."""

import os
import sys
import json
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image

HEADERS = {
    "User-Agent": "SafeAdDatasetCollector/1.0 (https://github.com/QuadRos-MBCET/safead-dataset-hub; contact: sourav@safead.local)"
}


def search_commons_images(query: str, limit: int = 15):
    encoded_q = urllib.parse.quote(f"{query} filetype:bitmap")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_q}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url|size|mime|extmetadata&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, p in pages.items():
            if "imageinfo" in p and p["imageinfo"]:
                ii = p["imageinfo"][0]
                mime = ii.get("mime", "")
                if mime in ["image/jpeg", "image/png", "image/webp"]:
                    results.append({
                        "title": p.get("title", ""),
                        "url": ii.get("url", ""),
                        "mime": mime,
                        "size": ii.get("size", 0),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0),
                    })
        return results
    except Exception as e:
        print(f"Search failed for '{query}': {e}", file=sys.stderr)
        return []


def download_and_verify_image(img_info: dict, dest_path: Path):
    req = urllib.request.Request(img_info["url"], headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()

    if len(data) < 5000:
        raise ValueError(f"Image too small ({len(data)} bytes)")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    # Verify with PIL
    with Image.open(dest_path) as im:
        im.verify()
        w, h = im.size
        fmt = im.format

    # Recompute SHA-256
    h = hashlib.sha256()
    with open(dest_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    sha256 = h.hexdigest().lower()

    return {
        "width": w,
        "height": h,
        "format": fmt,
        "sha256": sha256,
        "bytes": len(data),
    }


if __name__ == "__main__":
    queries_sfa = ["vintage Coca Cola advertisement", "Campbell soup advertisement", "toothpaste advertisement"]
    print("Testing SAFE_FOR_ALL queries...")
    for q in queries_sfa:
        res = search_commons_images(q, limit=5)
        print(f"Query '{q}': found {len(res)} candidate images")
        for r in res[:2]:
            print(f"  - {r['title']} ({r['width']}x{r['height']})")
