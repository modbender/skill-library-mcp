# Code Examples — Extract PDF Text

## Basic Extraction

```python
import fitz  # PyMuPDF

# Open and extract
doc = fitz.open("document.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text()
doc.close()
```

## With Context Manager

```python
import fitz

with fitz.open("document.pdf") as doc:
    for page in doc:
        print(page.get_text())
# Auto-closes when done
```

## Extract Specific Pages

```python
import fitz

doc = fitz.open("document.pdf")

# First 5 pages only
for page in doc[:5]:
    print(page.get_text())

# Specific page (0-indexed)
text = doc[2].get_text()  # Page 3

doc.close()
```

## Get Metadata

```python
import fitz

doc = fitz.open("document.pdf")
meta = doc.metadata

print(f"Title: {meta.get('title')}")
print(f"Author: {meta.get('author')}")
print(f"Pages: {doc.page_count}")

doc.close()
```

## Batch Processing

```python
import fitz
from pathlib import Path

def extract_all(folder):
    results = {}
    for pdf in Path(folder).glob("*.pdf"):
        try:
            doc = fitz.open(pdf)
            text = "".join(page.get_text() for page in doc)
            results[pdf.name] = {
                "text": text,
                "pages": doc.page_count,
                "words": len(text.split())
            }
            doc.close()
        except Exception as e:
            results[pdf.name] = {"error": str(e)}
    return results

# Usage
all_docs = extract_all("./pdfs/")
```

## Preserve Structure (Blocks)

```python
import fitz

doc = fitz.open("document.pdf")
page = doc[0]

# Get structured blocks
blocks = page.get_text("dict")["blocks"]

for block in blocks:
    if block["type"] == 0:  # Text block
        for line in block["lines"]:
            line_text = " ".join(span["text"] for span in line["spans"])
            print(line_text)

doc.close()
```

## Extract Tables (Basic)

```python
import fitz

doc = fitz.open("document.pdf")
page = doc[0]

# Find tables by looking for grid-like text
tables = page.find_tables()
for table in tables:
    for row in table.extract():
        print(row)

doc.close()
```

## Password Protected PDF

```python
import fitz

try:
    doc = fitz.open("protected.pdf")
except fitz.PasswordError:
    doc = fitz.open("protected.pdf", password="secret123")

# Or check first
doc = fitz.open("protected.pdf")
if doc.is_encrypted:
    doc.authenticate("secret123")
```

## Word Count Function

```python
import fitz

def count_words(pdf_path):
    doc = fitz.open(pdf_path)
    total = 0
    per_page = []
    
    for page in doc:
        words = len(page.get_text().split())
        per_page.append(words)
        total += words
    
    doc.close()
    return {
        "total": total,
        "per_page": per_page,
        "average": total / len(per_page) if per_page else 0
    }
```
