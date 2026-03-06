# Renderer Spec

## Inputs

- `--spec`: JSON file with `{ "slides": [6 strings] }`
- `--out`: output directory for PNG slides
- `--font`: absolute `.ttf` path

## Render Contract

- Exactly 6 slides
- Canvas: `1024x1536` portrait
- PNG outputs named `slide_01.png` through `slide_06.png`
- Deterministic background and text layout
- Safe margins:
  - left/right: `90px`
  - top: `180px`
  - bottom reserved: `260px`

## Text Rules

- Word wrapping uses measured text widths (`textbbox`)
- Font scales down within bounded range to fit safe box
- White text with soft shadow for readability

## Failure Modes

- Missing Pillow dependency
- Invalid/missing spec JSON
- Slide count not equal to 6
- Missing or invalid font path
