---
name: office-docs
description: "Generate and manipulate office documents (PDF, DOCX, XLSX, PPTX)
  for professional reports, presentations, and data exports. Use when: (1)
  Creating PDFs from text/images, (2) Generating Word documents, (3) Creating
  Excel spreadsheets with formulas, (4) Building PowerPoint presentations, (5)
  Extracting content from office documents."
---


# Office Docs - Professional Document Generation

Comprehensive skill for creating and manipulating office documents. Handles PDF, DOCX, XLSX, and PPTX formats.

## Quick Reference

| Format | Create | Read | Edit |
|--------|--------|------|------|
| PDF | `fpdf`, `reportlab` | `pdfplumber`, `pymupdf` | `pypdf` |
| DOCX | `python-docx` | `python-docx` | `python-docx` |
| XLSX | `openpyxl`, `pandas` | `openpyxl`, `pandas` | `openpyxl` |
| PPTX | `python-pptx` | `python-pptx` | `python-pptx` |

---

## PDF Operations

### Install

```bash
pip install fpdf reportlab pdfplumber pymupdf pypdf
```

### Create PDF

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(0, 10, "Hello World", ln=True)
pdf.output("document.pdf")
```

### Create PDF with Images

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.image("photo.jpg", x=10, y=10, w=100)
pdf.output("with_image.pdf")
```

### Extract Text from PDF

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
```

### Merge PDFs

```python
from pypdf import PdfMerger

merger = PdfMerger()
merger.append("file1.pdf")
merger.append("file2.pdf")
merger.write("merged.pdf")
merger.close()
```

### Split PDF

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for i in range(0, 5):  # First 5 pages
    writer.add_page(reader.pages[i])

with open("split.pdf", "wb") as f:
    writer.write(f)
```

---

## DOCX (Word) Operations

### Install

```bash
pip install python-docx
```

### Create Document

```python
from docx import Document

doc = Document()
doc.add_heading("Report Title", level=0)
doc.add_paragraph("This is a paragraph.")
doc.add_paragraph("Bold text", style="Intense Quote")
doc.save("report.docx")
```

### Add Table

```python
from docx import Document

doc = Document()
table = doc.add_table(rows=3, cols=2)
table.style = "Table Grid"

# Header row
hdr_cells = table.rows[0].cells
hdr_cells[0].text = "Name"
hdr_cells[1].text = "Value"

# Data rows
row = table.rows[1].cells
row[0].text = "Revenue"
row[1].text = "$1,000,000"

doc.save("table.docx")
```

### Add Image

```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_picture("chart.png", width=Inches(5))
doc.save("with_image.docx")
```

### Read Document

```python
from docx import Document

doc = Document("report.docx")
for para in doc.paragraphs:
    print(para.text)

for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

### Add Bullet List

```python
from docx import Document

doc = Document()
doc.add_paragraph("Items:", style="List Bullet")
doc.add_paragraph("First item", style="List Bullet")
doc.add_paragraph("Second item", style="List Bullet")
doc.save("bullets.docx")
```

---

## XLSX (Excel) Operations

### Install

```bash
pip install openpyxl pandas xlsxwriter
```

### Create Workbook

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

# Headers
ws["A1"] = "Name"
ws["B1"] = "Value"

# Data
ws["A2"] = "Revenue"
ws["B2"] = 1000000

# Formula
ws["A3"] = "Total"
ws["B3"] = "=SUM(B2:B2)"

wb.save("data.xlsx")
```

### Create with Pandas

```python
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Score": [85, 92, 78]
})

df.to_excel("scores.xlsx", index=False)
```

### Add Charts

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active

# Data
ws["A1"] = "Month"
ws["B1"] = "Sales"
data = [("Jan", 100), ("Feb", 150), ("Mar", 200)]
for i, (month, sales) in enumerate(data, 2):
    ws[f"A{i}"] = month
    ws[f"B{i}"] = sales

# Chart
chart = BarChart()
chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=4))
chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=4))
chart.title = "Monthly Sales"
ws.add_chart(chart, "D1")

wb.save("chart.xlsx")
```

### Read Workbook

```python
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active

for row in ws.iter_rows(values_only=True):
    print(row)
```

### Format Cells

```python
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl import Workbook

wb = Workbook()
ws = wb.active

# Bold header
ws["A1"] = "Header"
ws["A1"].font = Font(bold=True, size=14)

# Background color
ws["A1"].fill = PatternFill(start_color="4472C4", fill_type="solid")
ws["A1"].font = Font(color="FFFFFF", bold=True)

# Center align
ws["A1"].alignment = Alignment(horizontal="center")

wb.save("formatted.xlsx")
```

---

## PPTX (PowerPoint) Operations

### Install

```bash
pip install python-pptx
```

### Create Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Title slide
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Presentation Title"
subtitle.text = "Subtitle here"

prs.save("presentation.pptx")
```

### Add Bullet Slide

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Key Points"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First point"

p = tf.add_paragraph()
p.text = "Second point"
p.level = 1  # Indent

prs.save("bullets.pptx")
```

### Add Image

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide_layout = prs.slide_layouts[5]  # Blank
slide = prs.slides.add_slide(slide_layout)

slide.shapes.add_picture("chart.png", Inches(1), Inches(1), width=Inches(8))

prs.save("with_image.pptx")
```

### Add Table

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
slide_layout = prs.slide_layouts[5]  # Blank
slide = prs.slides.add_slide(slide_layout)

rows, cols = 4, 3
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(1), Inches(8), Inches(3)).table

# Set headers
table.cell(0, 0).text = "Name"
table.cell(0, 1).text = "Q1"
table.cell(0, 2).text = "Q2"

# Set data
table.cell(1, 0).text = "Alice"
table.cell(1, 1).text = "100"
table.cell(1, 2).text = "150"

prs.save("table.pptx")
```

---

## Common Workflows

### Report Generation

```python
from docx import Document
from docx.shared import Inches

doc = Document()
doc.add_heading("Monthly Report", level=0)
doc.add_paragraph("Generated automatically by agent.")

# Add summary table
table = doc.add_table(rows=3, cols=2)
table.style = "Table Grid"
table.rows[0].cells[0].text = "Metric"
table.rows[0].cells[1].text = "Value"
table.rows[1].cells[0].text = "Revenue"
table.rows[1].cells[1].text = "$1,000,000"
table.rows[2].cells[0].text = "Users"
table.rows[2].cells[1].text = "5,000"

doc.save("report.docx")
```

### Data Export to Excel

```python
import pandas as pd
from openpyxl.chart import BarChart, Reference
from openpyxl import load_workbook

# Create data
df = pd.DataFrame({
    "Date": pd.date_range("2026-01-01", periods=30),
    "Revenue": [1000 + i * 50 for i in range(30)]
})

# Save with formatting
df.to_excel("daily_revenue.xlsx", index=False)

# Add chart
wb = load_workbook("daily_revenue.xlsx")
ws = wb.active

chart = BarChart()
chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=31))
chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=31))
chart.title = "Daily Revenue"
ws.add_chart(chart, "D1")

wb.save("daily_revenue.xlsx")
```

### PDF Report with Charts

```python
from fpdf import FPDF
import matplotlib.pyplot as plt

# Create chart image
plt.figure(figsize=(10, 6))
plt.bar(["Jan", "Feb", "Mar"], [100, 150, 200])
plt.title("Monthly Sales")
plt.savefig("chart.png")
plt.close()

# Create PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=16)
pdf.cell(0, 10, "Monthly Sales Report", ln=True, align="C")
pdf.image("chart.png", x=10, y=30, w=190)
pdf.output("report.pdf")
```
