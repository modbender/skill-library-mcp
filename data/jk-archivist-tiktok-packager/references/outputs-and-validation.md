# Outputs and Validation

## Output Layout

```text
outbox/tiktok/intro/YYYY-MM-DD/
  _slide_spec.json
  slides/slide_01.png ... slide_06.png
  caption.txt
  review/review.md
  review/contact_sheet.png
  postiz_response.json (optional, when --postiz is used)
```

## Verifier

Run:

```bash
python3 scripts/verify_slides.py --dir outbox/tiktok/intro/YYYY-MM-DD/slides
```

Checks:

- exact filenames `slide_01.png` ... `slide_06.png`
- each image is `1024x1536`

## Local Test Suite

```bash
npm test
```

- Node tests validate caption + slide contract constants
- Python tests validate spec loader and verification constants

## Dry-run behavior

`--dry-run` writes spec and review metadata, then skips render/upload steps.
