# Design Guidelines — PowerPoint PPTX

> **Reference patterns only.** Guidelines for creating professional presentations.

## Slide Dimensions

```python
from pptx.util import Inches

# Standard 16:9 (default)
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Standard 4:3
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)
```

## Font Sizing Guidelines

| Element | Size Range | Recommended |
|---------|------------|-------------|
| Title | 36-44 pt | 40 pt |
| Subtitle | 24-32 pt | 28 pt |
| Body text | 18-24 pt | 20 pt |
| Bullets | 16-20 pt | 18 pt |
| Captions | 12-14 pt | 12 pt |

```python
from pptx.util import Pt

paragraph.font.size = Pt(20)
```

## Color Palettes

### Professional Blue
```python
primary = RgbColor(0x1F, 0x77, 0xB4)    # Main blue
secondary = RgbColor(0xAE, 0xC7, 0xE8)  # Light blue
accent = RgbColor(0xFF, 0x7F, 0x0E)     # Orange accent
text = RgbColor(0x33, 0x33, 0x33)       # Dark gray
```

### Corporate Gray
```python
primary = RgbColor(0x4A, 0x4A, 0x4A)    # Charcoal
secondary = RgbColor(0x9B, 0x9B, 0x9B)  # Medium gray
accent = RgbColor(0x00, 0x7A, 0xCC)     # Blue accent
background = RgbColor(0xF5, 0xF5, 0xF5) # Light gray
```

## Margin and Spacing

```python
# Safe margins from slide edges
MARGIN_LEFT = Inches(0.5)
MARGIN_TOP = Inches(0.5)
MARGIN_RIGHT = Inches(0.5)
MARGIN_BOTTOM = Inches(0.5)

# Content area
content_width = prs.slide_width - Inches(1)
content_height = prs.slide_height - Inches(1.5)  # Account for title
```

## Text Frame Settings

```python
from pptx.enum.text import MSO_ANCHOR

tf = shape.text_frame

# Remove auto-fit (keeps font size consistent)
tf.auto_size = None

# Margins inside text frame
tf.margin_left = Inches(0.1)
tf.margin_right = Inches(0.1)
tf.margin_top = Inches(0.05)
tf.margin_bottom = Inches(0.05)

# Vertical alignment
tf.anchor = MSO_ANCHOR.MIDDLE
```

## Bullet Formatting

```python
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

for level in range(3):
    p = tf.add_paragraph()
    p.level = level
    p.text = f"Level {level} bullet"
    
    # Indent increases with level
    p.font.size = Pt(18 - level * 2)
```

## Image Best Practices

```python
# Maintain aspect ratio
pic = slide.shapes.add_picture(
    'image.png',
    left=Inches(1),
    top=Inches(2),
    width=Inches(4)  # Height auto-calculated
)

# Center image horizontally
slide_width = prs.slide_width
img_width = Inches(4)
left = (slide_width - img_width) / 2
```

## Consistency Patterns

### Reusable Title Function
```python
def add_titled_slide(prs, title_text, layout_idx=1):
    slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
    slide.shapes.title.text = title_text
    return slide
```

### Consistent Styling
```python
def style_title(title_shape):
    title_shape.text_frame.paragraphs[0].font.size = Pt(40)
    title_shape.text_frame.paragraphs[0].font.bold = True
    title_shape.text_frame.paragraphs[0].font.color.rgb = RgbColor(0x1F, 0x77, 0xB4)
```

## Common Presentation Structures

### Business Presentation
1. Title slide
2. Agenda/Overview
3. Problem statement
4. Solution
5. Benefits/Features (2-3 slides)
6. Implementation/Timeline
7. Call to action
8. Q&A/Contact

### Technical Presentation
1. Title slide
2. Context/Background
3. Architecture overview
4. Deep dive sections
5. Demo/Examples
6. Summary
7. Questions
