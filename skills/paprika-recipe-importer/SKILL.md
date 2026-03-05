---
name: paprika-recipe-importer
description: >
  Convert recipe text (pasted text, video transcript, image description, or any raw content)
  into a .paprikarecipes file that can be imported directly into the Paprika Recipe Manager app.
  Use when the user shares a recipe in any format (text, transcript, image) and wants a Paprika
  import file. Triggers on phrases like "create a Paprika file", "import into Paprika",
  "save this recipe to Paprika", or when a recipe is shared and export to Paprika is implied.
---

# Paprika Recipe Importer

Convert recipe content (any format/language) into a `.paprikarecipes` file for Paprika 3.

## Workflow

1. **Extract** recipe fields from the input (text, image, transcript, URL content).
2. **Build** a JSON recipe object — only include fields actually present in the source; do NOT invent values.
3. **Run** the packaging script to produce the `.paprikarecipes` file.
4. **Deliver** the file to the user.

## Step 1 — Extract Fields

Parse the input and populate only the fields that exist in the source:

| JSON field        | Notes |
|-------------------|-------|
| `name`            | Recipe title. Required. |
| `ingredients`     | Newline-separated list. Format: `quantity unit ingredient`. |
| `directions`      | Newline-separated steps. |
| `description`     | Intro/summary paragraph, if present. |
| `notes`           | Tips, variations, author notes. |
| `servings`        | e.g. `"4 porções"` or `"serves 6"` |
| `prep_time`       | e.g. `"15 min"` |
| `cook_time`       | e.g. `"30 min"` |
| `total_time`      | e.g. `"45 min"` |
| `source`          | Author name, site name, person. |
| `source_url`      | Original URL, if available. |
| `categories`      | JSON array of strings, e.g. `["Jantar", "Massas"]` |
| `difficulty`      | `"Easy"`, `"Medium"`, or `"Hard"` — only if explicitly stated. |
| `rating`          | Integer 1–5 — only if explicitly stated. |
| `nutritional_info`| Any nutritional data present. |

**Rules:**
- Never fabricate values not present in the source.
- Keep the original language (Portuguese, English, mixed — whatever the source uses).
- Ingredients: one per line, preserve quantities and units exactly.
- Directions: one step per line; numbered steps → strip the number (Paprika handles display).

## Step 2 — Build JSON

Write the recipe as a JSON file to a temp path, e.g. `/tmp/<recipe-name>.json`.

## Step 3 — Run the Script

```bash
python3 ~/.openclaw/skills/paprika-recipe-importer/scripts/build_paprikarecipes.py \
  /tmp/<recipe-name>.json \
  /tmp/<recipe-name>.paprikarecipes
```

The script accepts a single JSON object or a JSON array (for multiple recipes).

## Step 4 — Deliver

Send the `.paprikarecipes` file to the user. Mention:
- How to import: **File → Import** in Paprika (or double-click the file on macOS/iOS).
- Which fields were found and which were absent from the source.
