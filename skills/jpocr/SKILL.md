---
name: jpocr
description: Japanese OCR via NDLOCR-Lite (National Diet Library). Trigger on 'OCR this image', '日文OCR', 'recognize Japanese text', or any request to extract text from Japanese documents, screenshots, or scanned pages. Best for printed Japanese and vertical text. Also works for English.
---

# jpocr — Japanese OCR Skill

Local Japanese OCR powered by NDLOCR-Lite from Japan's National Diet Library.
Runs on CPU (Apple Silicon / x86), no GPU or API key required.

## Capabilities

| Target | Quality |
|--------|---------|
| Printed Japanese (活字) | Excellent |
| Vertical text (縦書き) | Excellent |
| English text | Good |
| Handwritten Japanese (手書き) | Experimental |

## How to call

Run `scripts/ocr-cli.sh` from the skill root directory:

```bash
<SKILL_ROOT>/scripts/ocr-cli.sh <image_path>              # → plain text to stdout
<SKILL_ROOT>/scripts/ocr-cli.sh <image_path> --json        # → JSON with bounding boxes
<SKILL_ROOT>/scripts/ocr-cli.sh <image_path> --viz         # → also saves visualization
<SKILL_ROOT>/scripts/ocr-cli.sh <dir_path>                 # → batch all images in dir
```

## Output formats

**text** (default): one line per detected text region.

**json**:
```json
{
  "contents": [[
    {
      "boundingBox": [[x1,y1],[x1,y2],[x2,y1],[x2,y2]],
      "text": "recognized text",
      "confidence": 0.95,
      "isVertical": "true"
    }
  ]],
  "imginfo": { "img_width": 1920, "img_height": 1080 }
}
```

**viz**: saves `viz_<filename>` bounding-box overlay image to the output directory.

## Performance

- ~2-3 seconds per image on Apple Silicon (CPU)
- Formats: JPG, PNG, TIFF, JP2, BMP
- Charset: ~7000 characters (JIS kanji + kana + ASCII + Greek)

## Tech stack

- Layout detection: DEIMv2 (ONNX)
- Text recognition: PARSeq cascade (30/50/100 char models, ONNX)
- Reading order: xy-cut algorithm
