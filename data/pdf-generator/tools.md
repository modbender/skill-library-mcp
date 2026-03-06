# PDF Tools - Selection Guide

## Quick Decision Tree

```
Need PDF? - What's the source?

- Markdown/Text - pandoc (with LaTeX for complex)
- HTML/CSS - weasyprint (best CSS)
- Data/Tables - reportlab (programmatic)
- Simple text - fpdf2 (lightweight)
- Existing PDF - pypdf (merge/split)
```

## Tool Comparison

| Tool | Best For | CSS Support | Complexity |
|------|----------|-------------|------------|
| weasyprint | HTML to PDF | Excellent | Low |
| pandoc | Markdown to PDF | Via LaTeX | Medium |
| reportlab | Data to PDF | None | High |
| fpdf2 | Simple text | None | Low |
| pypdf | Merge/split | N/A | Low |

## weasyprint (Recommended)

```python
from weasyprint import HTML, CSS

# From string
html = "<h1>Hello</h1><p>World</p>"
HTML(string=html).write_pdf("output.pdf")

# From file
HTML("document.html").write_pdf("output.pdf")

# With custom CSS
css = CSS(string="body { font-family: Arial; }")
HTML(string=html).write_pdf("output.pdf", stylesheets=[css])
```

## pandoc

```bash
# Basic conversion
pandoc document.md -o output.pdf

# With table of contents
pandoc document.md --toc -o output.pdf

# Custom margins
pandoc document.md -V geometry:margin=1in -o output.pdf
```

## reportlab (Programmatic)

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4

# Text
c.setFont("Helvetica-Bold", 24)
c.drawString(2*cm, height - 3*cm, "Report Title")

c.setFont("Helvetica", 12)
c.drawString(2*cm, height - 5*cm, "Body text here...")

c.save()
```

## fpdf2 (Lightweight)

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(200, 10, text="Hello World", align="C")

pdf.set_font("Helvetica", size=12)
pdf.multi_cell(0, 10, text="Long paragraph text...")

pdf.output("output.pdf")
```

## pypdf (Merge/Split)

```python
from pypdf import PdfWriter, PdfReader

# Merge PDFs
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)
writer.write("merged.pdf")

# Split PDF
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i+1}.pdf")
```
