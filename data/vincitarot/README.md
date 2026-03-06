# tarot-skill

OpenClaw Tarot Skill with **professional reader mode**: multiple spreads, spread selection by question, energy guidance, and interpretation.

- **Install for OpenClaw**: See [INSTALL.md](./INSTALL.md) for directory layout, requirements, card data and image setup, and verification.
- **Entry points and behavior**: See [SKILL.md](./SKILL.md) for frontmatter, spread list, **reader guidelines** (before draw / during interpretation / after), **spread image** usage, and API.
- **Implementation**: Python package `tarot_skill/` provides `perform_reading`, `interpret_card`, `suggest_spread`; layouts in `spread_layouts.py`; card data from `data/cards.json` (see export below). Dependencies: `pip install -r requirements.txt` (Pillow).
- **Spread image**: After a reading, generate and send the image with:
  - `python -m tarot_skill.scripts.generate_spread_image --input reading.json [--output out/spread.png] [--images-dir ./cards]`
  - On **first run**, the script will try to download 78 card images into `cards/` (same source as tarot_game); on 403, missing cards use placeholders but the image still generates. Later runs reuse existing `cards/`.
  - Card image URL matches **tarot_game/constants/tarotCards.ts** `IMG_ROOT`. If auto-download fails, run manually when network allows:  
    `python -m tarot_skill.scripts.download_card_images [--output-dir ./cards]`  
    or save 78 images as `{id}.jpg` into `cards/` from tarot_game or elsewhere.
- **Card data**: Export 78 cards from **tarot_game** into `data/cards.json` first:
  - From `tarot_skill` run: `npm run export-cards` or `npx tsx scripts/export_cards_from_tarot_game.ts` (requires `tarot_skill` and `tarot_game` under the same parent; `npm install` for tsx).
