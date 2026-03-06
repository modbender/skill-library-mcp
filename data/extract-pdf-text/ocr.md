# OCR Setup — Extract PDF Text

## When to Use OCR

PyMuPDF extracts embedded text instantly. OCR is only needed for:
- Scanned documents (images of pages)
- PDFs where text is actually an image
- Very old PDFs with non-standard encoding

## Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**Python binding:**
```bash
pip install pytesseract
```

## OCR with PyMuPDF + Tesseract

```python
import fitz
import pytesseract
from PIL import Image
import io

def ocr_page(page, lang="eng"):
    """OCR a single page using Tesseract."""
    # Render page to image
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes()))
    
    # Run OCR
    text = pytesseract.image_to_string(img, lang=lang)
    return text

# Usage
doc = fitz.open("scanned.pdf")
for page in doc:
    text = ocr_page(page, lang="eng")
    print(text)
```

## Auto-Detect: Text vs Scanned

```python
def extract_smart(pdf_path, ocr_lang="eng"):
    """Extract text, using OCR only when needed."""
    doc = fitz.open(pdf_path)
    results = []
    
    for page in doc:
        text = page.get_text().strip()
        
        if len(text) > 50:
            # Has text, no OCR needed
            results.append({"text": text, "method": "native"})
        else:
            # Likely scanned, use OCR
            ocr_text = ocr_page(page, ocr_lang)
            results.append({"text": ocr_text, "method": "ocr"})
    
    doc.close()
    return results
```

## Language Codes

| Language | Code |
|----------|------|
| English | `eng` |
| Spanish | `spa` |
| French | `fra` |
| German | `deu` |
| Chinese | `chi_sim` |

**Multiple languages:**
```python
text = pytesseract.image_to_string(img, lang="eng+spa")
```

## Tips for Better OCR

1. **Use 300 DPI** — lower quality = worse accuracy
2. **Specify language** — don't rely on auto-detect
3. **Clean images** — remove noise before OCR
4. **Check results** — OCR isn't perfect
