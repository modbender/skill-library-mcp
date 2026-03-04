---
description: Convert PDF pages to image formats (PPM, PNG, JPEG).
---
# pdftoppm

Convert PDF pages to image formats (PPM, PNG, JPEG).

## Synopsis

```
pdftoppm [options] PDF-file [prefix]
```

## Description

Pdftoppm converts PDF pages to image formats. One image is produced for each page.

## When to Use

- To create image thumbnails of PDF pages
- To convert PDF pages to images for preview
- To extract pages as images for use in other applications

## Common Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to convert |
| `-l number` | Last page to convert |
| `-r number` | Resolution in DPI (default: 150) |
| `-rx number` | X resolution in DPI |
| `-ry number` | Y resolution in DPI |
| `-scale-to number` | Scale to fit within specified pixels |
| `-scale-to-x number` | Scale to width in pixels |
| `-scale-to-y number` | Scale to height in pixels |
| `-x number` | x-coordinate of crop area top-left corner |
| `-y number` | y-coordinate of crop area top-left corner |
| `-W number` | Width of crop area in pixels |
| `-H number` | Height of crop area in pixels |
| `-sz number` | Square crop size |
| `-cropbox` | Use crop box instead of media box |
| `-hide-annotations` | Do not show annotations |
| `-mono` | Generate monochrome PBM file |
| `-gray` | Generate grayscale PGM file |
| `-jpeg` | Generate JPEG file |
| `-jpegopt options` | JPEG compression options |
| `-tiff` | Generate TIFF file |
| `-tiffcompression none|packbits|jpeg|lzw|deflate` | TIFF compression type |
| `-freetype yes|no` | Enable/disable FreeType |
| `-thinlinemode none|solid|shape` | Thin line mode |
| `-aa yes|no` | Font anti-aliasing |
| `-aaVector yes|no` | Vector anti-aliasing |
| `-progress` | Print progress info |
| `-q` | Don't print messages |
| `-png` | Output as PNG (default) |
| `-jpeg` | Output as JPEG |
| `-jpg` | Output as JPEG (same as -jpeg) |
| `-mono` | Convert to 1-bit bitmap |
| `-gray` | Convert to grayscale |
| `-tiff` | Output as TIFF |
| `-singlefile` | Only convert first page |
| `-cropbox` | Use crop box instead of media box |
| `-hide-annotations` | Hide annotations |
| `-o` | Convert only odd pages |
| `-e` | Convert only even pages |
| `-opw password` | Owner password |
| `-upw password` | User password |
| `-q` | Quiet mode |
| `-v` | Print version information |
| `-h` | Print help information |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Error opening PDF file |
| 2 | Error opening output file |
| 3 | PDF permissions error |
| 99 | Other error |

## Examples

```bash
# Convert to PNG at 300 DPI
pdftoppm -png -r 300 document.pdf page

# Convert to JPEG
pdftoppm -jpeg -r 200 document.pdf page

# Single page
pdftoppm -singlefile -png document.pdf cover

# Scale to specific size
pdftoppm -scale-to 800 document.pdf thumbnail

# Crop specific area
pdftoppm -x 0 -y 0 -W 500 -H 700 document.pdf cropped
```
