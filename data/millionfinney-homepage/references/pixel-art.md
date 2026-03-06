# Pixel Pattern & Artwork Recipes

Use this guide when you need to turn logos, patterns, or generative art into Million Finney pixel payloads.

## Coordinate Planning

1. **Choose anchor point(s)** — top-left `(x0, y0)` of your composition. Keep everything 0–999.
2. **Reserve space** — ensure your shape fits within the grid: `x0 + width ≤ 1000`, `y0 + height ≤ 1000`.
3. **Token IDs** — `tokenId = (y0 + dy) * 1000 + (x0 + dx)`.
4. **Batch sizing** — group up to 100 pixels per `purchasePixelBatch`. For larger pieces, split into multiple batches but keep deterministic ordering so titles/colors align.

## Color Encoding

- Use hex colors in RGB, e.g. `#FF5733` → `0xFF5733` as `bytes3`.
- Avoid alpha; transparent pixels should simply remain unpurchased.
- Keep palettes bold for visibility on the 1M grid (high contrast + simple gradients read best at 1px scale).

## Titles

- Up to 128 chars. Recommended: `"Finney Bot (x,y)"`, brand names, or short slogans.
- Titles display in NFT metadata forever — keep them descriptive.

## Common Pattern Recipes

### Solid Blocks / Logos

1. Decide block width & height.
2. Choose palette: background, outline, foreground.
3. Generate pixel array row-by-row. Use `scripts/image_to_pixels.py` (see SKILL.md) for automatic conversion.
4. Purchase in batches, then call `setPixelMedia` for each pixel (can all reference the same IPFS artwork or unique frames).

### Text / Typography

- Convert text to bitmap using any font renderer (e.g. Pillow, p5.js).  
- Threshold to 1-bit, then map to chosen color(s).  
- Skip transparent/white pixels to leave background untouched (script supports `--skip-hex` for background colors).

### Gradients

- Linear gradient along X or Y: `color = lerp(colorA, colorB, t)` where `t = dx/(width-1)` or `dy/(height-1)`.
- Radial gradient: `t = distance(center, pixel) / maxDistance`.
- Clamp to `[0,1]`. Convert to `0xRRGGBB`.

### Checkerboards / Motifs

```
color = ( (x + y) % 2 === 0 ) ? primary : secondary;
```

This arrives as repeating diagonals; vary modulus for stripes, polka dots, etc.

### Dithering & Image Reduction

- Resize source art to target pixel dimensions with **nearest-neighbor** or **pixelated** interpolation to keep crisp edges.
- Apply **Floyd–Steinberg** or **Jarvis-Judice-Ninke** dithering when mapping rich images to a small palette.
- Palette suggestions: brand colors + black/white; or compute median-cut/`quantize` via Pillow.

## Image → Pixel Payload Workflow

1. Prepare your source image (PNG/SVG). For SVG, rasterize to PNG first.
2. Decide:
   - `--top-left` coordinate (`x,y`).
   - `--max-width/height` or exact `--size` parameters.
   - Palette overrides (optional).
3. Run `scripts/image_to_pixels.py` (see SKILL.md) to produce:
   - `pixels.json` list with `{x, y, tokenId, color, title}`.
   - Optional CSV for spreadsheets.
4. Review the preview ASCII output (script prints a mini-map).
5. Split JSON into ≤100 sized chunks before purchasing.

## Logo Tips

- Keep logos ≤ 80×80 for readability.
- Remove gradients unless you plan to allocate extra area for smooth transitions.
- Outline logos with high-contrast stroke to keep edges visible when zoomed out.
- Pair grid color with matching IPFS media for close-up detail.

## Automated Pattern Ideas

| Pattern | Formula |
| --- | --- |
| Radial burst | `h = Math.atan2(y - yc, x - xc); color = palette[Math.floor(((h + π)/(2π)) * palette.length)]` |
| Noise texture | Use deterministic seeded noise (Perlin/Simplex) to map grayscale → palette bucket. |
| QR/Code art | Render QR to bitmap; map dark modules to brand color, light modules left blank. |
| Animated story | Purchase contiguous strip; set each pixel’s IPFS image to sequential frames telling a story. |

## Testing & Visualization

- Dump JSON to `grid-state.json` for dry runs; use simple HTML canvas to preview before spending ETH.
- Keep a list of token IDs you touched to avoid duplicates on retries.
- Always re-check `isPixelOwned` for each token right before calling `purchasePixel(Batch)`.

Use this reference with the helper script + contract guide to build deterministic, eye-catching installations on the Million Finney Homepage.
