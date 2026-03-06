---
name: visual-prompt-engine
description: "Generate diverse, non-repetitive image prompts powered by real visual references from Dribbble and design platforms. USE WHEN: user wants an image prompt, needs creative visual inspiration, asks for design-informed prompts, wants to avoid repetitive AI image generation, or says 'generate a prompt for an image', 'give me a creative image idea', 'make me a unique visual prompt'. DON'T USE WHEN: user wants to generate the image itself (use an image generation tool), wants to edit an existing image, or needs text-only content. EDGE CASES: 'make me an image' → use image generation tool, then optionally this skill for the prompt. 'improve this image prompt' → this skill. 'I keep getting similar AI images' → this skill (solves repetition)."
---

# Visual Prompt Engine

Generate high-quality, diverse image prompts by feeding real visual references into a structured prompt pipeline.

## Problem

AI agents reuse the same visual patterns and clichés when writing image prompts. This skill breaks that cycle by grounding prompts in real, trending design work.

## Architecture

```
Dribbble Scraper → Style Cards → Prompt Generator → Quality Reviewer → Final Prompt
```

## Quick Start

### 1. Collect Visual References

**Recommended: Browser-based collection** (Dribbble blocks automated requests)

Browse `https://dribbble.com/shots/popular` with a browser tool (Camofox, Playwright, etc.), collect shot URLs, titles, and image URLs, then save as JSON:

```bash
python3 scripts/scrape_dribbble.py --method import --import-file manual_shots.json --output data/references.json
```

**Alternative: RSS/HTML** (may be blocked by WAF)

```bash
python3 scripts/scrape_dribbble.py --output data/references.json --count 20
```

The import JSON format: `[{"title": "...", "url": "https://dribbble.com/shots/...", "image_url": "..."}]`

### 2. Build Style Cards

Convert raw references into style cards:

```bash
python3 scripts/style_card.py build --input data/references.json --output data/style_cards.json
```

### 3. Generate Prompts

When the user requests an image prompt:

1. Read `data/style_cards.json` for available visual references
2. Select 1-3 cards relevant to the user's goal
3. Read `references/prompt-patterns.md` for diverse prompt structures
4. Read `references/visual-vocabulary.md` for precise design terminology
5. Compose a prompt combining: user goal + style card elements + varied pattern
6. Check against recent prompts in `data/prompt_history.json` to prevent repetition
7. Append the new prompt to history

### 4. Review and Deliver

Before delivering, verify the prompt:
- Uses specific visual language (not generic adjectives)
- References concrete design elements from the style card
- Follows a pattern different from the last 5 prompts
- Includes composition, lighting, color palette, and mood

## Style Card Schema

See `references/style-card-schema.md` for the full schema. A style card contains:

| Field | Description |
|-------|-------------|
| `palette` | Hex colors extracted from the design |
| `composition` | Layout structure (grid, asymmetric, centered, etc.) |
| `typography` | Font style and weight characteristics |
| `mood` | Emotional tone (bold, minimal, playful, etc.) |
| `textures` | Surface qualities (glass, grain, matte, etc.) |
| `lighting` | Light direction and quality |
| `source_url` | Original Dribbble shot URL |
| `tags` | Design categories |

## Prompt Patterns

See `references/prompt-patterns.md` for 12+ distinct prompt structures that prevent repetition. Rotate through patterns to keep outputs fresh.

## Visual Vocabulary

See `references/visual-vocabulary.md` for precise design terminology covering color, composition, lighting, texture, and typography. Use these terms instead of generic words like "beautiful" or "nice".

## Automation (Optional)

Set up a daily cron to refresh visual references:

```bash
# Run daily to keep references current
python3 scripts/scrape_dribbble.py --output data/references.json --count 20
python3 scripts/style_card.py build --input data/references.json --output data/style_cards.json
```

## Data Directory

The skill stores working data in `data/`:

```
data/
├── references.json      # Raw Dribbble scrape results
├── style_cards.json     # Processed style cards
└── prompt_history.json  # Generated prompts (for deduplication)
```

Create the `data/` directory on first run if it does not exist.

## Dependencies

Python 3.9+ with standard library only. Optional: `requests`, `beautifulsoup4` for live scraping (falls back to Dribbble RSS if not installed).

Install optional dependencies:

```bash
pip install requests beautifulsoup4
```
