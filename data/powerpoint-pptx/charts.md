# Charts and Tables — PowerPoint PPTX

> **Reference patterns only.** Code examples are templates for developers to adapt.

## Bar Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

# Prepare data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Sales', (19.2, 21.4, 16.7, 28.0))
chart_data.add_series('Costs', (12.1, 14.3, 11.2, 18.5))

# Add chart to slide
x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

# Optional: add title
chart.has_title = True
chart.chart_title.text_frame.text = "Quarterly Performance"
```

## Line Chart

```python
chart_data = CategoryChartData()
chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
chart_data.add_series('Trend', (4.3, 2.5, 3.5, 4.5, 5.2))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE, Inches(1), Inches(2), Inches(8), Inches(4), chart_data
).chart
```

## Pie Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ['Product A', 'Product B', 'Product C']
chart_data.add_series('Market Share', (35, 45, 20))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE, Inches(2), Inches(2), Inches(6), Inches(4), chart_data
).chart

# Show percentages
plot = chart.plots[0]
plot.has_data_labels = True
data_labels = plot.data_labels
data_labels.show_percentage = True
data_labels.show_value = False
```

## Table Creation

```python
from pptx.util import Inches, Pt

rows, cols = 4, 3
left, top = Inches(1), Inches(2)
width, height = Inches(8), Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(2)
table.columns[1].width = Inches(3)
table.columns[2].width = Inches(3)

# Header row
headers = ['Name', 'Department', 'Revenue']
for i, header in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True

# Data rows
data = [
    ['Alice', 'Sales', '125000'],
    ['Bob', 'Marketing', '98000'],
    ['Carol', 'Engineering', '156000'],
]

for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = value
```

## Table Styling

```python
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

# Style header row
for cell in table.rows[0].cells:
    cell.fill.solid()
    cell.fill.fore_color.rgb = RgbColor(0x1F, 0x77, 0xB4)
    para = cell.text_frame.paragraphs[0]
    para.font.color.rgb = RgbColor(0xFF, 0xFF, 0xFF)
    para.alignment = PP_ALIGN.CENTER

# Alternate row colors
for i, row in enumerate(table.rows[1:], start=1):
    for cell in row.cells:
        if i % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RgbColor(0xF0, 0xF0, 0xF0)
```

## Chart Types Reference

| Type | Constant | Use Case |
|------|----------|----------|
| Column | `XL_CHART_TYPE.COLUMN_CLUSTERED` | Compare categories |
| Bar | `XL_CHART_TYPE.BAR_CLUSTERED` | Horizontal comparison |
| Line | `XL_CHART_TYPE.LINE` | Trends over time |
| Pie | `XL_CHART_TYPE.PIE` | Part of whole |
| Area | `XL_CHART_TYPE.AREA` | Volume over time |
| Scatter | `XL_CHART_TYPE.XY_SCATTER` | Correlation |
| Doughnut | `XL_CHART_TYPE.DOUGHNUT` | Pie with center hole |
