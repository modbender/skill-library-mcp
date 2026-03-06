---
name: PowerPoint PPTX
slug: powerpoint-pptx
version: 1.0.0
homepage: https://clawic.com/skills/powerpoint-pptx
description: Create, edit, and automate PowerPoint presentations with python-pptx for slides, layouts, charts, and batch processing.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to create or modify PowerPoint (.pptx) files programmatically. Agent handles slide creation, content population, chart generation, and template automation.

## Quick Reference

| Topic | File |
|-------|------|
| Slide patterns | `slides.md` |
| Charts and tables | `charts.md` |
| Design guidelines | `design.md` |

## Core Rules

### 1. Use python-pptx Library
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RgbColor
```

Install: `pip install python-pptx`

### 2. Presentation Structure
```python
# Create new presentation
prs = Presentation()

# Or load existing template
prs = Presentation('template.pptx')

# Add slide with layout
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)

# Save
prs.save('output.pptx')
```

### 3. Slide Layouts (Built-in)
| Index | Layout Name | Use Case |
|-------|-------------|----------|
| 0 | Title Slide | Opening slide |
| 1 | Title and Content | Standard content |
| 2 | Section Header | Chapter dividers |
| 3 | Two Content | Side-by-side |
| 4 | Comparison | Before/after |
| 5 | Title Only | Custom content |
| 6 | Blank | Full control |

### 4. Text Handling
```python
# Access title
title = slide.shapes.title
title.text = "Slide Title"

# Access body placeholder
body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First paragraph"

# Add more paragraphs
p = tf.add_paragraph()
p.text = "Second paragraph"
p.level = 1  # Indent level
```

### 5. Always Verify Output
After creating presentation:
1. Check slide count matches expectation
2. Verify text populated correctly
3. Test charts render properly
4. Save to user-specified path

## Common Traps

- **Layout index assumption**: Layout indices vary by template. Always check `prs.slide_layouts` first.
- **Missing placeholders**: Not all layouts have body placeholders. Use `slide.shapes` iteration to find shapes.
- **Font not embedding**: python-pptx uses system fonts. Stick to common fonts (Arial, Calibri) for portability.
- **Image sizing**: Always specify dimensions with `Inches()` or `Pt()`. Default sizing can be unpredictable.
- **Chart data mismatch**: Category count must match data series length exactly.

## Scope

This skill ONLY:
- Creates and modifies local .pptx files
- Uses python-pptx library for manipulation
- Reads templates from local filesystem

This skill NEVER:
- Uploads presentations to cloud services
- Makes network requests
- Accesses files outside the working directory without user permission

## Security & Privacy

**Data that stays local:**
- All presentations created/modified on local filesystem
- No telemetry or external calls

**This skill does NOT:**
- Send presentation content externally
- Access cloud storage APIs
- Store user data persistently

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `excel-xlsx` — spreadsheet automation
- `word-docx` — document generation
- `report` — structured report creation
- `documents` — document management

## Feedback

- If useful: `clawhub star powerpoint-pptx`
- Stay updated: `clawhub sync`
