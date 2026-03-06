# Advanced PDF Operations

## Merge PDFs

```python
from pypdf import PdfWriter, PdfReader

def merge_pdfs(input_files, output_file):
    writer = PdfWriter()
    
    for pdf_path in input_files:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
    
    with open(output_file, "wb") as f:
        writer.write(f)

# Usage
merge_pdfs(["doc1.pdf", "doc2.pdf"], "merged.pdf")
```

## Split PDF

```python
from pypdf import PdfReader, PdfWriter

def split_pdf(input_file, output_dir="."):
    reader = PdfReader(input_file)
    
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        with open(f"{output_dir}/page_{i+1}.pdf", "wb") as f:
            writer.write(f)

def split_by_range(input_file, ranges, output_file):
    """Extract specific pages. ranges = [(1,3), (5,7)]"""
    reader = PdfReader(input_file)
    writer = PdfWriter()
    
    for start, end in ranges:
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])
    
    with open(output_file, "wb") as f:
        writer.write(f)
```

## Fill PDF Forms

```python
from pypdf import PdfReader, PdfWriter

def fill_form(input_pdf, output_pdf, field_data):
    """
    field_data = {"field_name": "value"}
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    writer.append(reader)
    writer.update_page_form_field_values(writer.pages[0], field_data)
    
    with open(output_pdf, "wb") as f:
        writer.write(f)

# Get field names from PDF
def list_form_fields(pdf_path):
    reader = PdfReader(pdf_path)
    fields = reader.get_form_text_fields()
    for name, value in fields.items():
        print(f"{name}: {value}")
```

## Add Watermark

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

def create_watermark(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 50)
    c.rotate(45)
    c.drawString(200, 100, text)
    c.save()
    buffer.seek(0)
    return buffer

def add_watermark(input_pdf, output_pdf, watermark_text):
    watermark_buffer = create_watermark(watermark_text)
    watermark_reader = PdfReader(watermark_buffer)
    watermark_page = watermark_reader.pages[0]
    
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    
    with open(output_pdf, "wb") as f:
        writer.write(f)
```

## Batch Processing

```python
from pathlib import Path
from weasyprint import HTML

def batch_generate(template_html, data_list, output_dir):
    """Generate multiple PDFs from template + data."""
    Path(output_dir).mkdir(exist_ok=True)
    
    for item in data_list:
        html = template_html.format(**item['data'])
        output_path = f"{output_dir}/{item['filename']}.pdf"
        HTML(string=html).write_pdf(output_path)

# Usage
template = """
<html><body>
<h1>Invoice for {client}</h1>
<p>Amount: ${amount}</p>
</body></html>
"""

data = [
    {"filename": "invoice-001", "data": {"client": "Acme", "amount": 1000}},
    {"filename": "invoice-002", "data": {"client": "Beta", "amount": 2000}},
]

batch_generate(template, data, "./invoices")
```

## Add Bookmarks

```python
from pypdf import PdfWriter, PdfReader

def add_bookmarks(input_pdf, output_pdf, bookmarks):
    """
    bookmarks = [
        {"title": "Chapter 1", "page": 0},
        {"title": "Chapter 2", "page": 5},
    ]
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    for bm in bookmarks:
        writer.add_outline_item(bm["title"], bm["page"])
    
    with open(output_pdf, "wb") as f:
        writer.write(f)
```

## Rotate Pages

```python
from pypdf import PdfReader, PdfWriter

def rotate_pages(input_pdf, output_pdf, rotation=90, pages=None):
    """
    rotation: 90, 180, 270
    pages: list of page numbers (1-indexed) or None for all
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for i, page in enumerate(reader.pages):
        if pages is None or (i + 1) in pages:
            page.rotate(rotation)
        writer.add_page(page)
    
    with open(output_pdf, "wb") as f:
        writer.write(f)
```

## Extract Text

```python
from pypdf import PdfReader

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
```
