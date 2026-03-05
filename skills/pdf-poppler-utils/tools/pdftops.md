---
description: Convert PDF documents to PostScript.
---
# pdftops

Convert PDF documents to PostScript.

## Synopsis

```
pdftops [options] PDF-file [ps-file]
```

## Description

Pdftops converts PDF documents to PostScript for printing or further processing.

## When to Use

- To print PDF on PostScript printers
- To convert PDF for professional printing
- To create PostScript versions for archiving

## Common Options

### Level Options
| Option | Description |
|--------|-------------|
| `-level1` | Force Level 1 PostScript |
| `-level2` | Force Level 2 PostScript (default) |
| `-level3` | Force Level 3 PostScript |
| `-level1sep` | Level 1 separable PostScript |
| `-level2sep` | Level 2 separable PostScript |
| `-level3sep` | Level 3 separable PostScript |

### Output Options
| Option | Description |
|--------|-------------|
| `-eps` | Convert to EPS (Encapsulated PostScript) |
| `-form` | Generate PostScript form |
| `-singlefile` | Only convert first page |

### Paper Options
| Option | Description |
|--------|-------------|
| `-paper size` | Paper size (letter, legal, A4, A3, etc.) |
| `-paperw number` | Paper width in points |
| `-paperh number` | Paper height in points |
| `-origpagesizes` | Same as "-paper match" |
| `-nocrop` | Don't crop pages to CropBox |
| `-noshrink` | Don't scale pages to fit paper |
| `-nocenter` | Don't center pages on paper |
| `-expand` | Expand pages to paper size |

### Font Options
| Option | Description |
|--------|-------------|
| `-noembt1` | Don't embed Type 1 fonts |
| `-noembtt` | Don't embed TrueType fonts |
| `-noembcidps` | Don't embed CID PostScript fonts |
| `-noembcidtt` | Don't embed CID TrueType fonts |
| `-passfonts` | Pass through non-embedded fonts |

### Raster/Color Options
| Option | Description |
|--------|-------------|
| `-aaRaster yes\|no` | Raster anti-aliasing |
| `-rasterize always\|never\|whenneced` | Rasterization control |
| `-processcolorformat MONO8\|CMYK8\|RGB8` | Process color format |
| `-optimizecolorspace` | Optimize color space |
| `-overprint` | Enable overprint emulation |
| `-preload` | Preload images and forms |

### Other Options
| Option | Description |
|--------|-------------|
| `-duplex` | Set Duplex pagedevice |
| `-opi` | Generate OPI comments |
| `-binary` | Binary data in Level 1 PostScript |
| `-f number` | First page to convert |
| `-l number` | Last page to convert |
| `-q` | Quiet mode (no messages/errors) |
| `-v` | Print version information |
| `-opw password` | Owner password |
| `-upw password` | User password |

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
# Basic conversion
pdftops document.pdf output.ps

# Convert to EPS (single page)
pdftops -eps document.pdf page.eps

# Force Level 1 for older printers
pdftops -level1 document.pdf output.ps

# Custom paper size
pdftops -paper letter document.pdf output.ps

# Page range
pdftops -f 1 -l 5 document.pdf output.ps

# Using separable colors
pdftops -level2sep document.pdf output.ps
```
