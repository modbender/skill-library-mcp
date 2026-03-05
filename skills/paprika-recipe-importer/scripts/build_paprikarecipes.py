#!/usr/bin/env python3
"""
Convert a JSON recipe dict to a .paprikarecipes file.

Usage:
    python3 build_paprikarecipes.py recipe.json [output.paprikarecipes]

The JSON file should contain a single object (or list of objects) with any
subset of the supported Paprika recipe fields.
"""

import gzip
import json
import os
import sys
import uuid
import zipfile
from pathlib import Path


SUPPORTED_FIELDS = [
    "name", "ingredients", "directions", "description", "notes",
    "servings", "prep_time", "cook_time", "total_time",
    "source", "source_url", "categories", "rating", "difficulty",
    "nutritional_info", "on_favorites", "photo_data",
]


def make_paprikarecipe(recipe: dict) -> bytes:
    """Serialize a recipe dict as a gzipped JSON .paprikarecipe blob."""
    # Ensure required uid field
    if "uid" not in recipe:
        recipe["uid"] = str(uuid.uuid4()).upper()
    # Keep only known fields + uid
    clean = {k: v for k, v in recipe.items() if k in SUPPORTED_FIELDS + ["uid"]}
    raw = json.dumps(clean, ensure_ascii=False, indent=2).encode("utf-8")
    return gzip.compress(raw)


def build_paprikarecipes(recipes: list[dict], output_path: str):
    """Package one or more recipes into a .paprikarecipes zip file."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for recipe in recipes:
            blob = make_paprikarecipe(recipe)
            name = recipe.get("name", "recipe").replace("/", "-")
            entry_name = f"{name}.paprikarecipe"
            zf.writestr(entry_name, blob)
    print(f"Written: {output_path}  ({len(recipes)} recipe(s))")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    recipes = data if isinstance(data, list) else [data]

    output_path = sys.argv[2] if len(sys.argv) > 2 else Path(input_path).stem + ".paprikarecipes"
    build_paprikarecipes(recipes, output_path)
