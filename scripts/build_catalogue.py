#!/usr/bin/env python3
"""Build products.json by scanning Label AKS category folders.

New Arrivals is generated automatically from the 25 most recently changed
product photos across all catalogue categories, using Git commit timestamps.
"""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "images"
OUTPUT = ROOT / "products.json"

CATEGORIES = {
    "western-wear": {
        "folders": ["Westernwear"],
        "legacy": [],
    },
    "cord-sets": {
        "folders": ["cordsets", "co-ord-sets"],
        "legacy": [],
    },
    "indo-western": {
        "folders": ["indowestern"],
        "legacy": [],
    },
    "designer-suits": {
        "folders": ["designer-suits"],
        "legacy": [],
    },
    "suit-sets": {
        "folders": ["suit-sets"],
        "legacy": [
            "Suit 1.jpeg", "Suit2.jpeg", "Suit4.jpeg", "suit 1a.jpeg",
            "suit3.jpeg", "suit5.jpeg", "suit6.jpeg",
        ],
    },
    "lehengas": {
        "folders": ["lehengas"],
        "legacy": ["Lehenga 1.jpeg"],
    },
    "daily-wear": {
        "folders": ["daily-wear"],
        "legacy": ["suit 1a.jpeg", "Suit 1.jpeg", "Suit2.jpeg", "suit3.jpeg"],
    },
    "festive-wear": {
        "folders": ["festive-wear"],
        "legacy": ["Suit2.jpeg", "Suit4.jpeg", "Lehenga 1.jpeg", "suit5.jpeg"],
    },
    "party-wear": {
        "folders": ["party-wear"],
        "legacy": ["Suit4.jpeg", "Lehenga 1.jpeg", "suit5.jpeg", "suit6.jpeg"],
    },
    "new-arrivals": {
        "folders": ["new-arrivals"],
        "legacy": ["cod.jpeg", "Cod2.jpeg", "Suit 1.jpeg", "Lehenga 1.jpeg", "Suit2.jpeg"],
    },
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
NEW_ARRIVALS_LIMIT = 25


def natural_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


def latest_image_timestamps():
    """Return each image's latest Git commit timestamp (newest change wins)."""
    timestamps = {}
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ct", "--name-only", "--", "images"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        current_timestamp = None
        for line in result.stdout.splitlines():
            value = line.strip()
            if not value:
                continue
            if value.isdigit():
                current_timestamp = int(value)
            elif current_timestamp is not None and value not in timestamps:
                timestamps[value] = current_timestamp
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Allows local/manual runs even when Git history is unavailable.
        pass
    return timestamps


def main():
    catalogue = {"version": 1, "categories": {}}

    for slug, config in CATEGORIES.items():
        paths = []

        for filename in config["legacy"]:
            path = IMAGE_ROOT / filename
            if path.is_file():
                paths.append("/images/" + filename)

        for folder_name in config["folders"]:
            folder = IMAGE_ROOT / folder_name
            if not folder.is_dir():
                continue

            files = sorted(
                (
                    p for p in folder.iterdir()
                    if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
                ),
                key=lambda p: natural_key(p.name),
            )

            for path in files:
                web_path = "/" + path.relative_to(ROOT).as_posix()
                if web_path not in paths:
                    paths.append(web_path)

        catalogue["categories"][slug] = {"images": paths}

    # Build New Arrivals from every category, without duplicating image paths.
    all_images = {
        image_path
        for category in catalogue["categories"].values()
        for image_path in category["images"]
    }

    timestamps = latest_image_timestamps()

    def recency_key(web_path):
        relative_path = web_path.lstrip("/")
        file_path = ROOT / relative_path
        timestamp = timestamps.get(relative_path)
        if timestamp is None and file_path.is_file():
            timestamp = int(file_path.stat().st_mtime)
        return (-(timestamp or 0), web_path.casefold())

    catalogue["categories"]["new-arrivals"]["images"] = sorted(
        all_images, key=recency_key
    )[:NEW_ARRIVALS_LIMIT]

    OUTPUT.write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Generated {OUTPUT} with "
        f"{sum(len(v['images']) for v in catalogue['categories'].values())} "
        f"image entries; New Arrivals contains "
        f"{len(catalogue['categories']['new-arrivals']['images'])} photos."
    )


if __name__ == "__main__":
    main()
