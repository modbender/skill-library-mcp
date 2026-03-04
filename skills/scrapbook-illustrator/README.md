# Scrapbook-Style Illustration Inserter

Transform articles into richly illustrated markdown using **hand-crafted scrapbook-style images** — think torn paper edges, washi tape, hand-drawn arrows, layered textures, and high-saturation collage aesthetics generated via the [GLM-Image API](https://open.bigmodel.cn).

**Attribution:** Based on [glm-image](https://github.com/ViffyGwaanl/glm-image) by ViffyGwaanl (MIT License).

## What is Scrapbook Style?

Each generated image mimics a physical mixed-media scrapbook page:
- Torn and rough-edged paper layers
- Washi tape, paperclips, and push-pin textures
- Watercolor stains, newspaper clippings, grid paper backgrounds
- Hand-drawn marker circles, arrows, and decorative lines
- High-saturation, multi-color collisions

This style makes article illustrations feel handmade and visually distinctive — not stock photos.

## Prerequisites

- `GLM_API_KEY` set in TOOLS.md (get one at https://open.bigmodel.cn)
- Python 3 + `requests` library: `pip install requests`

No other skills required — GLM image generation is bundled.

## Usage

Provide an article and ask:
- "Illustrate this article"
- "Add images to my post"
- "Generate pictures for this content"
- "Illustrate in English" (for English text in images)

## Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `image_count` | 3 | Number of images to generate (2–5) |
| `orientation` | portrait | `portrait` (1088×1920) or `landscape` (1920×1088) |
| `language` | zh | `zh` (Chinese) or `en` (English) for text in images |

## How It Works

1. Validates article length (≥200 words recommended)
2. Generates scrapbook-style image descriptions as JSON using a specialized prompt
3. Creates each image via glm-image (failures logged inline, run continues)
4. Returns the full article with images inserted at logical break points

## Output

Complete markdown article with generated images embedded as `![caption](url)` links.

## License

MIT
