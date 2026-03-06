---
name: instagram-photo-text-overlay
description: Overlay text on photos for Instagram posts. Generates portrait (4:5) images with gradient overlays, titles, and optional numbered lists. Use when creating Instagram content that needs text on top of a photo — destination itineraries, top-5 lists, travel highlights, or any branded social image with text overlay.
---

# Instagram Photo Text Overlay

Overlay text onto photos for Instagram-ready images. Two styles: **list** (title + numbered items) and **clean** (title only).

## Quick Start

```bash
python3 scripts/overlay.py \
  --input photo.jpg \
  --output result.jpg \
  --title "TAORMINA" \
  --subtitle "3-Day Trip Itinerary" \
  --items '["Teatro Greco|Ancient theatre with Etna views", "Isola Bella|Crystal-clear beach"]' \
  --style list
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Source photo path |
| `--output` | (required) | Output image path |
| `--title` | (required) | Main title (auto-uppercased) |
| `--subtitle` | `"3-Day Trip Itinerary"` | Subtitle below title |
| `--items` | `[]` | JSON array of `"Name\|Reason"` strings (list style) |
| `--watermark` | `"tabiji.ai"` | Top-left watermark (empty string to disable) |
| `--accent` | `255,220,150` | Accent color for numbers/tags (R,G,B) |
| `--quote` | `""` | Quote text (for quote style) |
| `--style` | `list` | `list` / `clean` / `quote` |
| `--quality` | `95` | JPEG output quality |

## Styles

- **clean**: Cover slide. Big title = destination + category + count (e.g. "7 unique cheap eats in barcelona spain"). Subtitle = credibility/source line (e.g. "Insider takes from r/barcelona"). Best as carousel first slide.
- **list**: Content slides. Title + subtitle + divider + numbered items with reasons. Best for top-5 / itinerary posts.
- **quote**: Title with accent bar on the left + blockquote text below. No subtitle or divider. Best for travel quotes, testimonials, or key takeaways.

## Workflow

1. Receive photo + destination/topic + list of items from user
2. Run `scripts/overlay.py` with appropriate args
3. Output is auto-cropped to 4:5 portrait (Instagram optimal)
4. Review output and adjust if needed (font sizes scale with image width)

## Requirements

- Python 3 + Pillow (`pip install Pillow`)
- Works on macOS (Helvetica) and Linux (DejaVu/Liberation fallback)

## Tips

- Items format: `"Name|Short reason"` — the pipe separates bold name from description
- For destinations, pull top picks from existing itineraries when available
- Gradient + white text ensures readability on any photo
- All font sizes are proportional to image width — works at any resolution
