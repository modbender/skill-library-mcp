# Extraction Pipeline Guide

The Research Library extraction pipeline converts documents, images, and code files into searchable text with confidence scores for quality assessment.

## How Extraction Works

### Three-Phase Process

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   DETECT    │───▶│   EXTRACT   │───▶│    SCORE    │
│  File Type  │    │    Text     │    │  Confidence │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### Phase 1: Detect
- Identifies file type by extension (primary) and MIME type (fallback)
- Routes to appropriate extractor
- Handles unknown types gracefully

#### Phase 2: Extract
- Pulls text content using type-specific methods
- Extracts metadata (EXIF, PDF info, code structure)
- Falls back to simpler methods if primary fails

#### Phase 3: Score
- Assigns confidence based on extraction quality
- Considers OCR clarity, text coherence, parsing success
- Enables downstream filtering and ranking

---

## Supported File Types

### PDF Documents (`.pdf`)

**Extraction Method:** pdfplumber (text) → OCR fallback (scanned)

| Content Type | Confidence | Method |
|-------------|------------|--------|
| Born-digital text | 1.0 | Direct text extraction |
| Scanned (clear) | 0.85 | OCR with pytesseract |
| Scanned (poor) | 0.4 | OCR with quality penalty |

**Metadata Extracted:**
- Page count
- PDF info (title, author, creation date)
- Image count per page
- Character count

**Example Output:**
```
[Page 1]
Servo Motor Control Systems

A servo motor is a rotary actuator...

[Page 2]
PID Control Implementation...
```

### Images (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`)

**Extraction Method:** EXIF metadata → OCR (if available)

| Content Type | Confidence | Method |
|-------------|------------|--------|
| Clear text | 0.8 | OCR |
| Handwriting | 0.3 | OCR with quality penalty |
| No text / EXIF only | 0.2 | Metadata extraction |

**Metadata Extracted:**
- Dimensions (width × height)
- EXIF data (camera, date, GPS, etc.)
- Color mode

**Note:** OCR requires `pytesseract` and system `tesseract-ocr`. Falls back to filename + EXIF if unavailable.

### Code Files

#### Python (`.py`, `.pyw`)

**Extraction Method:** AST parsing → regex fallback

| Scenario | Confidence |
|----------|------------|
| Valid syntax | 1.0 |
| Syntax errors | 0.7 |

**Extracted Structure:**
- Module docstring
- Imports list
- Classes with docstrings and methods
- Functions with signatures and docstrings
- Comments

**Example Output:**
```
[Python File: servo_controller.py]

[Module Docstring]
Servo Motor Controller Module...

[Classes]
class PIDController
  """PID controller for servo position control."""
  def __init__(self, kp: float, ki: float, kd: float)
  def update(self, setpoint: float, measured: float) -> float
  def reset(self)

[Functions]
def calculate_trajectory(start, end, steps=100)
  """Calculate smooth trajectory between two points."""
```

#### C/C++/Arduino (`.c`, `.cpp`, `.h`, `.hpp`, `.ino`)

**Extraction Method:** Regex-based parsing

**Extracted Structure:**
- `#include` directives
- `#define` macros
- Class/struct declarations
- Function signatures
- Comments

**Arduino-specific:**
- Detects `setup()` and `loop()` presence
- Flags as Arduino-standard or non-standard

#### G-code (`.gcode`, `.gnd`, `.nc`, `.ngc`, `.tap`)

**Extraction Method:** Command parsing with descriptions

**Extracted Structure:**
- Commands used with counts (G0, G1, M3, etc.)
- Human-readable descriptions
- Work envelope (X/Y/Z min/max)
- Feed rate range
- Spindle speed range
- Comments

**Example Output:**
```
[G-Code File: bracket.gcode]

[Commands Used]
  G0: Rapid positioning (×12)
  G1: Linear interpolation (×45)
  G2: Circular interpolation CW (×4)
  M3: Spindle on CW (×1)

[Work Envelope]
  X: 10.000 to 60.000
  Y: 10.000 to 60.000
  Z: -5.000 to 10.000

[Feed Rates]
  Range: 200.0 - 1000.0

[Comments]
  G-code for servo bracket milling
  Material: Aluminum 6061
```

#### Other Languages

Supported with regex-based extraction:
- JavaScript/TypeScript (`.js`, `.ts`)
- Java (`.java`)
- Rust (`.rs`)
- Go (`.go`)
- Ruby (`.rb`)
- Shell (`.sh`, `.bash`)
- SQL (`.sql`)
- Markup (`.json`, `.yaml`, `.xml`, `.html`, `.css`, `.md`)
- OpenSCAD (`.scad`)
- KiCad (`.kicad_pcb`, `.kicad_sch`)

---

## Confidence Scoring

### Score Meanings

| Score | Interpretation | Use Case |
|-------|---------------|----------|
| 1.0 | Perfect extraction | Full-text search, exact matching |
| 0.85 | Very good OCR | Search with minor tolerance |
| 0.7-0.8 | Good extraction | Search with fuzzy matching |
| 0.4-0.6 | Partial extraction | Keyword search only |
| 0.1-0.3 | Minimal extraction | Metadata/filename only |
| <0.1 | Failed | Skip or manual review |

### What Affects Confidence

**PDF:**
- Text layer presence (born-digital vs scanned)
- OCR quality (character recognition rate)
- Text coherence (word patterns)

**Images:**
- OCR clarity (Tesseract confidence scores)
- Text vs noise ratio
- Character patterns (gibberish detection)

**Code:**
- Syntax validity (AST success)
- Language detection certainty
- Structure extraction completeness

---

## Performance Targets

| File Type | Target | Typical |
|-----------|--------|---------|
| Text PDF (3 pages) | <100ms | 40-60ms |
| Scanned PDF (3 pages) | <3000ms | 500-2000ms |
| Image (OCR) | <500ms | 200-400ms |
| Python code | <50ms | 5-20ms |
| C++/Arduino | <50ms | 5-15ms |
| G-code | <30ms | 5-10ms |

**Note:** OCR times vary significantly with image quality and size.

---

## Usage Examples

### Basic Extraction

```python
from reslib import DocumentExtractor, extract_file

# Single file
result = extract_file("/path/to/document.pdf")
print(f"Text: {result.text[:500]}")
print(f"Confidence: {result.confidence}")
print(f"Time: {result.extraction_time_ms}ms")

# With extractor instance
extractor = DocumentExtractor()
result = extractor.extract("/path/to/code.py")
```

### Batch Processing

```python
from reslib import BatchExtractor

batch = BatchExtractor()

# With progress callback
def progress(current, total, filename):
    print(f"[{current}/{total}] Processing {filename}")

results = batch.extract_directory(
    "/path/to/documents",
    recursive=True,
    progress_callback=progress
)

# Filter by confidence
good_results = [r for r in results if r.confidence >= 0.7]
```

### Accessing Metadata

```python
result = extract_file("servo_controller.py")

# Python-specific metadata
if result.language == 'python':
    print(f"Classes: {result.metadata.get('classes', [])}")
    print(f"Functions: {result.metadata.get('functions', [])}")
    print(f"Imports: {result.metadata.get('imports', [])}")

# G-code specific
if result.language == 'gcode':
    print(f"Commands: {result.metadata.get('commands', {})}")
    print(f"X range: {result.metadata.get('x_min')} to {result.metadata.get('x_max')}")
```

---

## Error Handling

### Timeout Protection

All extractions have a 5-minute timeout (configurable):

```python
extractor = DocumentExtractor(timeout_seconds=120)  # 2 minute timeout
```

### Graceful Degradation

The pipeline never crashes. Fallback chain:

1. **Primary method fails** → Try alternative method
2. **Alternative fails** → Extract filename + basic metadata
3. **Complete failure** → Return error result with low confidence

```python
result = extractor.extract("/path/to/broken.pdf")

if result.error:
    print(f"Extraction failed: {result.error}")
    print(f"Fallback text: {result.text}")  # At least filename
```

### Logging

Enable debug logging for troubleshooting:

```python
import logging
logging.getLogger('reslib.extractor').setLevel(logging.DEBUG)
```

---

## Known Limitations

### Current Limitations

1. **OCR Quality**
   - Handwriting recognition is poor
   - Rotated/skewed text needs preprocessing
   - Multi-language documents may have issues

2. **Complex PDFs**
   - Multi-column layouts may interleave text
   - Tables extract as plain text (no structure)
   - Forms with checkboxes not detected

3. **Code Parsing**
   - Only Python uses full AST parsing
   - C++/Java use regex (may miss complex patterns)
   - Template metaprogramming not handled

### Deferred Features

- **CAD files** (DXF, STEP, STL) - Requires specialized libraries
- **Office documents** (DOCX, XLSX) - Use python-docx/openpyxl
- **Audio/Video transcription** - Requires speech-to-text
- **Table structure extraction** - Requires camelot/tabula

---

## Dependencies

### Required
- `pdfplumber` - PDF text extraction
- `Pillow` (PIL) - Image handling

### Optional (Recommended)
- `pytesseract` - OCR for scanned documents/images
- `tesseract-ocr` - System package for OCR engine
- `reportlab` - Creating synthetic PDFs (testing only)

### Install All
```bash
pip install pdfplumber pillow pytesseract
sudo apt install tesseract-ocr  # Debian/Ubuntu
```
