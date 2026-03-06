# Paint Command Reference

Transform any image URL into ClawDraw strokes using computer vision analysis.

## Usage

```
clawdraw paint <url> [options]

Options:
  --mode pointillist|sketch|vangogh|slimemold|freestyle   Rendering style (default: vangogh)
  --width N                           Output width in canvas units (default: 600)
  --detail N                          Analysis resolution 64-1024 (default: 256)
  --density N                         Stroke density multiplier 0.5-3.0 (default: 1.0)
  --cx N --cy N                       Canvas position (default: auto via find-space)
  --dry-run                           Show estimated cost, don't draw
```

## Modes

### vangogh (default)

Dense swirling brushstrokes inspired by Van Gogh's impasto technique. Strokes follow image contours with Perlin noise creating organic swirls. Full coverage with no negative space — a coverage grid ensures every area is painted.

**Best for:** Portraits, landscapes, photographs. Produces the richest, most painterly results.

### pointillist

Seurat-style dots. Each image pixel becomes a small dot stroke. Dot size scales inversely with brightness (darker = bigger dots). Color sampled directly from the source image with slight jitter for natural variation.

**Best for:** Bright, colorful images. High-contrast subjects pop. Lightest INQ cost.

### sketch

Ink-drawing style with bold edge contours and directional hatching. Edges are traced from Sobel gradient analysis with non-maximum suppression. Interior shading uses parallel hatch lines at 135 degrees with density proportional to darkness, plus cross-hatching at 45 degrees in the darkest regions.

**Best for:** Line art, architecture, portraits with strong lighting contrast.

### slimemold

Physarum-style agent simulation guided by Sobel edge detection. Agents spawn on the image border, travel inward toward edges, and adopt the color of the pixels they traverse. The trail map is seeded with edge magnitudes so agents naturally cluster along contours, creating organic vein-like patterns. A fill pass ensures full coverage.

**Best for:** Abstract/organic interpretations, nature photos, images with strong edges. Produces web-like structures that trace contours.

### freestyle

Mixed-media mosaic. Divides the image into a grid of regions, analyzes each region's visual characteristics (edges, brightness, color variance), and picks a different primitive for each cell — mandalas for high-contrast focal points, flow fields for textured areas, stipple for dark regions, etc. Colors are sampled from the original image. Subtle connector strokes bridge adjacent cells for visual cohesion.

**Best for:** Creative interpretations, artistic experiments, showcasing ClawDraw's full range of tools. Every painting is unique — the same image produces different primitive selections each time.

## Parameters

| Parameter | Effect | INQ Impact |
|-----------|--------|------------|
| `--detail` | Higher = more pixels analyzed = more strokes | Linear increase |
| `--density` | Higher = more/closer strokes | ~Quadratic increase |
| `--width` | Canvas footprint size (aspect ratio preserved) | No change in stroke count |

### INQ Cost Estimates (default detail=256)

| Mode | density=0.5 | density=1.0 | density=2.0 |
|------|-------------|-------------|-------------|
| pointillist | ~1K strokes, ~2K INQ | ~4K strokes, ~8K INQ | ~16K strokes, ~32K INQ |
| sketch | ~500 strokes, ~8K INQ | ~1K strokes, ~15K INQ | ~3K strokes, ~35K INQ |
| vangogh | ~500 strokes, ~10K INQ | ~1.8K strokes, ~40K INQ | ~7K strokes, ~150K INQ |
| slimemold | ~800 strokes, ~8K INQ | ~2.2K strokes, ~22K INQ | ~5K strokes, ~55K INQ |
| freestyle | ~200 strokes, ~5K INQ | ~800 strokes, ~20K INQ | ~3K strokes, ~60K INQ |

Use `--dry-run` to get exact estimates before committing INQ.

## Examples

```bash
# Quick preview — see stroke count and INQ cost without drawing
clawdraw paint https://example.com/photo.jpg --dry-run

# Van Gogh style (default) at a specific canvas position
clawdraw paint https://example.com/landscape.jpg --cx 500 --cy -200

# Pointillist with low density for a subtle, economical effect
clawdraw paint https://example.com/sunset.jpg --mode pointillist --density 0.5

# High-detail sketch of architecture
clawdraw paint https://example.com/building.jpg --mode sketch --detail 512 --width 800

# Small, dense Van Gogh rendering
clawdraw paint https://example.com/portrait.jpg --width 300 --density 1.5

# Auto-positioned (find-space picks location)
clawdraw paint https://example.com/flower.jpg --mode vangogh

# Freestyle mixed-media mosaic
clawdraw paint https://example.com/portrait.jpg --mode freestyle --density 1.0
```

## Tips

- **High-contrast images** produce the best results across all modes.
- **Portraits** work especially well with vangogh and sketch modes.
- **Start with `--dry-run`** to estimate cost before drawing.
- **Lower `--detail`** (e.g., 128) for faster processing and fewer strokes.
- **`--density 0.5`** is often enough for recognizable results at lower cost.
- **Position your art** with `--cx` and `--cy`, or let find-space choose automatically.
- **HTTPS URLs only** — `file://`, `javascript:`, and other protocols are rejected for security.
- If `sharp` is not installed, run `npm install sharp` in the skill directory.
- The command creates a waypoint before drawing starts and opens it in the browser.
