# Troubleshooting — Extract PDF Text

## Empty Output

**Cause:** PDF is scanned (images, not text).

```python
# Check if page has text
text = page.get_text()
if len(text.strip()) < 50:
    print("Likely scanned — use OCR")
```

**Fix:** See `ocr.md` for OCR setup.

## Import Error

**Cause:** PyMuPDF not installed.

```bash
pip install PyMuPDF
```

**Note:** Import as `fitz`, not `pymupdf`:
```python
import fitz  # Correct
```

## Password Required

```python
import fitz

doc = fitz.open("protected.pdf")
if doc.is_encrypted:
    success = doc.authenticate("password")
    if not success:
        print("Wrong password")
```

## Corrupted PDF

```python
import fitz

try:
    doc = fitz.open("file.pdf")
except fitz.FileDataError:
    print("PDF is corrupted or invalid")
```

## Memory Issues (Large PDFs)

**Cause:** Loading entire PDF at once.

**Fix:** Process page by page:
```python
doc = fitz.open("huge.pdf")
for i, page in enumerate(doc):
    text = page.get_text()
    process(text)  # Handle immediately
    # Don't accumulate in memory
doc.close()
```

## Wrong Character Encoding

**Cause:** Usually not PyMuPDF's fault — PDF has bad encoding.

PyMuPDF handles UTF-8 automatically. If you see garbled text:
1. Try `page.get_text("text")` explicitly
2. Check if PDF is actually scanned (use OCR)
3. PDF may have custom fonts — text may be images

## Text in Wrong Order

**Cause:** PDF has complex layout.

**Fix:** Use sort parameter:
```python
text = page.get_text(sort=True)  # Sort by position
```

## Tables Not Extracted Properly

**Cause:** Tables are just positioned text.

**Fix:** Use table extraction:
```python
tables = page.find_tables()
for table in tables:
    for row in table.extract():
        print(row)
```

## Slow Extraction

| Cause | Fix |
|-------|-----|
| OCR on text PDF | Check `get_text()` first |
| High DPI for OCR | Use 300, not higher |
| Processing in loop | Batch if possible |
