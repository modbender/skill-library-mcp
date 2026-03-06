# Slide Patterns — PowerPoint PPTX

> **Reference patterns only.** Code examples are templates for developers to adapt.

## Title Slide

```python
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Presentation Title"

subtitle = slide.placeholders[1]
subtitle.text = "Subtitle or Author"
```

## Content Slide with Bullets

```python
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Key Points"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First point"

for point in ["Second point", "Third point"]:
    p = tf.add_paragraph()
    p.text = point
    p.level = 0
```

## Slide with Image

```python
from pptx.util import Inches

slide_layout = prs.slide_layouts[5]  # Title Only
slide = prs.slides.add_slide(slide_layout)

# Position image
left = Inches(1)
top = Inches(2)
width = Inches(4)

slide.shapes.add_picture('image.png', left, top, width=width)
```

## Two-Column Layout

```python
slide_layout = prs.slide_layouts[3]  # Two Content
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Comparison"

left_content = slide.placeholders[1]
left_content.text_frame.text = "Left column content"

right_content = slide.placeholders[2]
right_content.text_frame.text = "Right column content"
```

## Custom Shape Positioning

```python
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE

# Add rectangle
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(1), Inches(1),  # left, top
    Inches(3), Inches(1)   # width, height
)

# Style the shape
shape.fill.solid()
shape.fill.fore_color.rgb = RgbColor(0x1F, 0x77, 0xB4)
shape.line.color.rgb = RgbColor(0x00, 0x00, 0x00)
```

## Text Box with Formatting

```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# Add text box
txBox = slide.shapes.add_textbox(
    Inches(1), Inches(1),
    Inches(5), Inches(1)
)

tf = txBox.text_frame
p = tf.paragraphs[0]
p.text = "Formatted text"
p.font.size = Pt(24)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER
```

## Batch Slide Creation

```python
data = [
    {"title": "Slide 1", "content": ["Point A", "Point B"]},
    {"title": "Slide 2", "content": ["Point C", "Point D"]},
]

for item in data:
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = item["title"]
    
    body = slide.placeholders[1].text_frame
    body.text = item["content"][0]
    for point in item["content"][1:]:
        p = body.add_paragraph()
        p.text = point
```
