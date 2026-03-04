---
name: mixtiles-it
description: Send a photo to Mixtiles for ordering wall tiles. Use when a user forwards/sends a photo and wants to order it as a Mixtile, add it to their Mixtiles cart, or says "mixtile this", "make this a tile", or similar. Also handles image URLs.
---

# Mixtiles It

Turn any photo into a Mixtiles order link. User sends a photo (or image URL) → get back a ready-to-order Mixtiles cart link.

## How It Works

1. User sends/forwards a photo or image URL
2. Run the upload script to get a public URL and Mixtiles cart link
3. Send the cart link back — user taps it to customize and order

## Usage

```bash
# Single photo
python3 scripts/mixtiles-cart.py <local-file-or-url> [--size SIZE]

# Multiple photos (one cart link with all photos)
python3 scripts/mixtiles-cart.py --batch <image1> <image2> ... [--size SIZE]
```

The script handles:
- **Local files**: Uploads to Cloudinary (the only host Mixtiles can display from)
- **URLs**: Downloads first, then uploads to Cloudinary
- **Batch mode**: Uploads all images and builds a single multi-photo cart URL
- **Output**: Prints the Mixtiles cart URL to stdout

### Size Options

Default is `RECTANGLE_12X16`. Other known sizes from Mixtiles:
- `SQUARE_8X8` — Classic square
- `RECTANGLE_12X16` — Portrait rectangle (default)
- `RECTANGLE_16X12` — Landscape rectangle

### Environment Variables (optional)

- `CLOUDINARY_CLOUD` — Cloudinary cloud name (default: `demo`)
- `CLOUDINARY_PRESET` — Cloudinary unsigned upload preset (default: `unsigned`)
- `MIXTILES_UPLOAD_URL` — Override the upload API endpoint (Railway fallback)
- `MIXTILES_UPLOAD_KEY` — Override the upload API key (Railway fallback)

## Workflow

When a user sends a photo with intent to mixtile it:

1. Identify the image file path (from media attachment) or URL
2. Run: `python3 <skill-dir>/scripts/mixtiles-cart.py <path-or-url>`
3. Send the resulting URL to the user with a brief message like "Here's your Mixtiles link! 🖼️ Tap to customize size, frame, and order."

If multiple photos are sent, use `--batch` to create a single cart link with all photos:
`python3 <skill-dir>/scripts/mixtiles-cart.py --batch <path1> <path2> ...`
