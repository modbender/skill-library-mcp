---
name: Extract PDF Text
slug: extract-pdf-text
version: 1.0.2
homepage: https://clawic.com/skills/extract-pdf-text
description: Extract text from PDF files using PyMuPDF. Parse tables, forms, and complex layouts. Supports OCR for scanned documents.
changelog: Remove internal build file that was accidentally included
metadata: {"clawdbot":{"emoji":"📄","requires":{"bins":["python3"],"pip":["pymupdf"]},"os":["linux","darwin","win32"],"install":[{"id":"pymupdf","kind":"pip","package":"PyMuPDF","label":"Install PyMuPDF"}]}}
---

## When to Use

Agent needs to extract text from PDFs. Use PyMuPDF (fitz) for fast local extraction. Works with text-based documents, scanned pages with OCR, forms, and complex layouts.

## Quick Reference

| Topic | File |
|-------|------|
| Code examples | `examples.md` |
| OCR setup | `ocr.md` |
| Troubleshooting | `troubleshooting.md` |

## Core Rules

### 1. Install PyMuPDF First

```bash
pip install PyMuPDF
```

Import as `fitz` (historical name):
```python
import fitz  # PyMuPDF
```

### 2. Basic Text Extraction

```python
import fitz

doc = fitz.open("document.pdf")
text = ""
for page in doc:
    text += page.get_text()
doc.close()
```

### 3. Pick the Right Method

| PDF Type | Method |
|----------|--------|
| Text-based | `page.get_text()` — fast, accurate |
| Scanned | OCR with pytesseract — slower |
| Mixed | Check each page, use OCR when needed |

### 4. Check for Text Before OCR

```python
def needs_ocr(page):
    text = page.get_text().strip()
    return len(text) < 50  # Likely scanned if very little text
```

### 5. Handle Errors Gracefully

```python
try:
    doc = fitz.open(path)
except fitz.FileDataError:
    print("Invalid or corrupted PDF")
except fitz.PasswordError:
    doc = fitz.open(path, password="secret")
```

## Extraction Traps

| Trap | What Happens | Fix |
|------|--------------|-----|
| OCR on text PDF | Slow + worse accuracy | Check `get_text()` first |
| Forget to close doc | Memory leak | Use `with` or `doc.close()` |
| Assume page order | Wrong reading flow | Use `sort=True` in get_text() |
| Ignore encoding | Garbled characters | PyMuPDF handles UTF-8 |

## Scope

This skill provides instructions for using PyMuPDF to extract PDF text.

This skill ONLY:
- Gives code examples for PyMuPDF
- Explains OCR setup when needed
- Troubleshoots common issues

This skill NEVER:
- Accesses files without user request
- Sends data externally
- Modifies original PDFs

## Security & Privacy

**All processing is local:**
- PyMuPDF runs entirely on your machine
- No external API calls
- No data leaves your system

## Output Formats

### Plain Text
```python
text = page.get_text()
```

### Structured (dict)
```python
blocks = page.get_text("dict")["blocks"]
for b in blocks:
    if b["type"] == 0:  # text block
        for line in b["lines"]:
            for span in line["spans"]:
                print(span["text"], span["size"])
```

### JSON
```python
import json
data = page.get_text("json")
parsed = json.loads(data)
```

## Full Example

```python
import fitz

def extract_pdf(path):
    """Extract text from PDF, with OCR fallback for scanned pages."""
    doc = fitz.open(path)
    results = []
    
    for i, page in enumerate(doc):
        text = page.get_text()
        method = "text"
        
        # If very little text, might be scanned
        if len(text.strip()) < 50:
            # OCR would go here (see ocr.md)
            method = "needs_ocr"
        
        results.append({
            "page": i + 1,
            "text": text,
            "method": method
        })
    
    doc.close()
    return {
        "pages": len(results),
        "content": results,
        "word_count": sum(len(r["text"].split()) for r in results)
    }

# Usage
result = extract_pdf("document.pdf")
print(f"Extracted {result['word_count']} words from {result['pages']} pages")
```

## Feedback

- Useful? `clawhub star extract-pdf-text`
- Stay updated: `clawhub sync`
