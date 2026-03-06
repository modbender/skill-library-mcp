# Photography & Color Management

## Color Profiles

### The Rules
| Profile | Use For |
|---------|---------|
| **sRGB** | Web delivery — always convert before export |
| **Adobe RGB** | Print workflow, wider gamut |
| **ProPhoto RGB** | Maximum gamut, RAW editing |

**Critical:** Browsers assume sRGB. Adobe RGB images look washed out on web.

### Conversion Path
ProPhoto → Adobe RGB → sRGB (if gamut is wide)

Direct ProPhoto → sRGB can cause clipping.

**Always embed ICC profile.** Untagged images render differently everywhere.

---

## Metadata & EXIF

### Preserve by Default
- Camera settings (ISO, aperture, shutter)
- Timestamps (DateTimeOriginal)
- Copyright, IPTC contact info

### Strip When
- Publishing to web (privacy)
- Stock submission (some agencies)
- Explicit request

### GPS Warning
**Strip GPS** before publishing:
- Photos of homes
- Private locations
- Sensitive subjects

Ask before including GPS in public files.

---

## RAW Handling

### Core Rule
RAW files are negatives — **NEVER modify the original**.

Edits go into:
- Sidecar files (XMP)
- Catalog database (Lightroom, Capture One)

### White Balance
- **RAW:** Non-destructive, full adjustment
- **JPEG:** Destructive, causes color shifts/banding

Always recommend RAW for color correction.

### Different Converters = Different Results
Adobe Camera Raw ≠ Capture One ≠ DxO ≠ Darktable

Same RAW, different output. Ask which software.

---

## Non-Destructive Editing

### Layer Preservation
- Return PSD/TIFF with layers intact
- Only flatten for **final delivery**
- Smart Objects: Maintain for resizing (preserves resolution)

### Lightroom/Capture One
Catalog stores instructions, not pixels. 100% reversible until export.

---

## Batch Processing

### Test First
Never run untested presets on 500 images.

Test on 3-5 images covering:
- Different lighting
- Different exposures
- Different camera settings

### Naming Convention
```
YYYYMMDD_ProjectName_####.ext
```
- No spaces or special characters
- Sequence numbers must not restart mid-batch

---

## Export Settings

### Web
| Setting | Value |
|---------|-------|
| Color space | sRGB |
| DPI | 72-150 |
| Format | JPEG 75-85% or WebP |
| Resize | Long edge 2000-2400px max |
| Metadata | Strip (privacy) or basic only |
| Sharpening | Screen, standard |

### Print
| Setting | Value |
|---------|-------|
| Color space | Adobe RGB (or printer profile) |
| DPI | 300 |
| Format | TIFF or high-quality JPEG (95%+) |
| Resize | Match print dimensions |
| Metadata | Preserve copyright |
| Sharpening | Glossy/matte, high |

---

## Quality Control

Before delivery, verify:
```
□ No highlight/shadow clipping
□ Clean edges (no halos)
□ Dust spots removed
□ Consistent exposure (±0.3 EV)
□ No chromatic aberration
□ Correct color profile embedded
```
