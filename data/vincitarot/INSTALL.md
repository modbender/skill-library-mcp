# Install for OpenClaw

After installing this skill into OpenClaw, the agent can use the Python implementation for draws, spread image generation, and interpretation.

## 1. What to copy

Place the whole **tarot_skill** directory in OpenClaw’s skill directory (see OpenClaw docs for the path), or ensure OpenClaw can load it. Keep this structure:

```
tarot_skill/
├── SKILL.md              # Skill description and OpenClaw metadata (required)
├── README.md
├── INSTALL.md            # This install guide
├── requirements.txt     # Python dependencies
├── package.json         # Optional, only for exporting card data
├── data/
│   └── cards.json       # 78 cards (required; export from tarot_game if missing)
├── tarot_skill/         # Python package (required)
│   ├── __init__.py
│   ├── types.py
│   ├── spreads.py
│   ├── spread_layouts.py
│   ├── cards_loader.py
│   └── scripts/
│       ├── generate_spread_image.py
│       └── download_card_images.py
├── scripts/             # Optional, only for exporting cards.json
│   └── export_cards_from_tarot_game.ts
└── cards/               # Optional, 78 card images; auto-download or run script
```

- **Required**: `SKILL.md`, `tarot_skill/` package, `data/cards.json`, `requirements.txt`
- **Optional**: `cards/` (images), `package.json` + `scripts/` (only when re-exporting from tarot_game)

## 2. Requirements

- **Python**: 3.8+ (on PATH; OpenClaw checks for `python3`)
- **Dependencies**: From `tarot_skill` or a directory where Python can find it:
  ```bash
  pip install -r requirements.txt
  ```
  Currently: `Pillow>=10.0.0`

## 3. Card data (data/cards.json)

- If the repo already has `data/cards.json`, no extra step.
- If not (e.g. you only copied part of the repo), export from **tarot_game**:
  1. Put `tarot_skill` and `tarot_game` under the same parent directory.
  2. From `tarot_skill` run: `npm install`, then `npm run export-cards` (or `npx tsx scripts/export_cards_from_tarot_game.ts`).
  3. This produces `data/cards.json`.

## 4. Card images (cards/) — optional

- When generating a spread image, if you pass `--images-dir ./cards` and `cards/` has 78 `{id}.jpg` files, those are used; otherwise the script tries the network and falls back to placeholders.
- On **first** run without `--images-dir`, if the default `cards/` is missing or has fewer than 78 images, the script will try to run the download script (may fail with 403).
- To rely on local images, run the download once when the network is good:
  ```bash
  cd /path/to/tarot_skill
  PYTHONPATH=. python3 -m tarot_skill.scripts.download_card_images --output-dir ./cards
  ```
  Ensure Python can import `tarot_skill` (e.g. set `PYTHONPATH` to the repo root).

## 5. How the agent runs it

- **Working directory**: When running `generate_spread_image`, the current working directory or `PYTHONPATH` must include the root that contains the `tarot_skill` package and `data/`.
- **Example** (from the parent of `tarot_skill`):
  ```bash
  PYTHONPATH=/path/to/tarot_skill python3 -m tarot_skill.scripts.generate_spread_image \
    --input /path/to/reading.json \
    --output /path/to/out/spread.png \
    --images-dir /path/to/tarot_skill/cards
  ```
- **Flow**: Agent calls `perform_reading()` → saves result as JSON → runs the command above → sends the image first, then the interpretation.

## 6. Verify installation

From `tarot_skill` or its parent (with `PYTHONPATH` including that root):

```bash
python3 -c "
from tarot_skill import perform_reading, suggest_spread
r = perform_reading({'spreadType': 'daily'})
print('ok' if r.get('ok') and r.get('spread') else 'fail')
"
```

If you see `ok`, the package and `data/cards.json` are fine. Then test image generation (with a reading.json):

```bash
python3 -m tarot_skill.scripts.generate_spread_image --input /path/to/reading.json --output /tmp/spread.png
```

If `/tmp/spread.png` is created without errors, the install is complete.
