---
description: Convert PDF to Cairo graphics library formats (PNG, JPEG, TIFF, SVG, PS).
---
# pdftocairo

Convert PDF to Cairo graphics library formats.

## Synopsis

```
pdftocairo [options] PDF-file [output]
```

## Description

Pdftocairo converts PDF to Cairo graphics library formats. The output format is determined by the file extension:
- `.png` - PNG image
- `.jpeg` / `.jpg` - JPEG image
- `.tiff` / `.tif` - TIFF image
- `.pdf` - PDF output
- `.svg` - SVG vector graphics
- `.ps` - PostScript
- `.eps` - Encapsulated PostScript

For image formats, one file is produced per page (with page number appended). For vector formats, the output-file is used as the full filename.

## When to Use

- To convert PDF to high-quality images
- To create SVG from PDF
- To generate PDF from PDF (with transformations)
- For more advanced image conversion than pdftoppm

## Common Options

### Output Options
| Option | Description |
|--------|-------------|
| `-png` | Force PNG output |
| `-jpeg` | Force JPEG output |
| `-tiff` | Force TIFF output |
| `-svg` | Force SVG output |
| `-pdf` | Force PDF output |
| `-ps` | Force PostScript output |
| `-eps` | Generate EPS file |

### Page Range
| Option | Description |
|--------|-------------|
| `-f number` | First page to convert |
| `-l number` | Last page to convert |

### Resolution & Scaling
| Option | Description |
|--------|-------------|
| `-r number` | Resolution in DPI (default: 150) |
| `-rx number` | X resolution |
| `-ry number` | Y resolution |
| `-scale-to number` | Scale to fit within specified pixels |
| `-scale-to-x number` | Scale to width |
| `-scale-to-y number` | Scale to height |

### Cropping
| Option | Description |
|--------|-------------|
| `-x number` | x-coordinate of crop area |
| `-y number` | y-coordinate of crop area |
| `-W number` | Width of crop area |
| `-H number` | Height of crop area |
| `-sz number` | Square crop size |
| `-cropbox` | Use crop box instead of media box |

### Color Options
| Option | Description |
|--------|-------------|
| `-mono` | Monochrome output |
| `-gray` | Grayscale output |
| `-antialias` | Antialiasing settings |
| `-transp` | Transparent background |
| `-icc` | ICC profile for PNG |
| `-jpegopt` | JPEG compression options |

### Paper & Layout
| Option | Description |
|--------|-------------|
| `-paper size` | Paper size (letter, legal, A4, etc.) |
| `-paperw number` | Paper width in points |
| `-paperh number` | Paper height in points |
| `-origpagesizes` | Same as "-paper match" |
| `-nocrop` | Don't crop pages to CropBox |
| `-expand` | Expand pages to paper |
| `-noshrink` | Don't scale pages to fit paper |
| `-nocenter` | Don't center pages on paper |

### Other Options
| Option | Description |
|--------|-------------|
| `-singlefile` | Only convert first page |
| `-o` | Convert only odd pages |
| `-e` | Convert only even pages |
| `-struct` | PDF structural info |
| `-duplex` | Set Duplex pagedevice |
| `-preload` | Preload images and forms |
| `-q` | Quiet mode |
| `-v` | Print version information |
| `-opw password` | Owner password |
| `-upw password` | User password |

## JPEG Options

When outputting JPEG, use `-jpegopt` with:
- `quality=N` (0-100, default: 95)
- `progressive`
- `optimize`

Example: `-jpegopt quality=90,progressive`

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Error opening PDF file |
| 2 | Error opening output file |
| 3 | PDF permissions error |
| 99 | Other error |

## Notes

- EPS requires single page (use `-f` and `-l`)
- Cropping uses pixels for images, points for vector formats

## Examples

```bash
# Convert to PNG
pdftocairo -png document.pdf output

# Convert to SVG (vector)
pdftocairo -svg document.pdf output

# High resolution PNG
pdftocairo -r 300 -png document.pdf output

# Grayscale output
pdftocairo -gray -png document.pdf output

# Crop specific area
pdftocairo -x 0 -y 0 -W 500 -H 700 -png document.pdf output
```
