#!/usr/bin/env python3
"""Build products.json by scanning the Label AKS category image folders."""
from pathlib import Path
import json
import re

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


def natural_key(value):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", value)
    ]


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

    OUTPUT.write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        f"Generated {OUTPUT} with "
        f"{sum(len(v['images']) for v in catalogue['categories'].values())} image entries."
    )


if __name__ == "__main__":
    main()
