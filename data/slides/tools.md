# Programmatic Slide Tools

## Tool Selection Matrix

| Output Needed | Best Tool | Alternatives |
|---------------|-----------|--------------|
| .pptx (PowerPoint) | python-pptx | officegen (Node.js) |
| Google Slides | Google Slides API | — |
| Web presentation | reveal.js | Slidev, Marp |
| PDF from markdown | Marp | reveal.js + decktape |
| Code-heavy talks | Slidev | reveal.js |

## python-pptx (Python → PowerPoint)

### Basic Structure
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()
# Or from template: Presentation('template.pptx')

slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)

title = slide.shapes.title
title.text = "Slide Title"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First bullet"
p = tf.add_paragraph()
p.text = "Second bullet"
p.level = 1  # Indented

prs.save('output.pptx')
```

### Common Patterns
```python
# Add image
slide.shapes.add_picture('image.png', Inches(1), Inches(2), width=Inches(4))

# Add table
rows, cols = 3, 4
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(2)).table
table.cell(0, 0).text = "Header"

# Add chart (requires python-pptx-chart or manual XML)
from pptx.chart.data import CategoryChartData
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3']
chart_data.add_series('Sales', (100, 200, 150))
```

### Critical: Always Use Units
```python
# ❌ WRONG
shape.left = 100

# ✅ CORRECT
from pptx.util import Inches, Pt, Emu
shape.left = Inches(1)
shape.width = Inches(4)
font.size = Pt(24)
```

### Slide Layouts (Standard)
| Index | Name | Use |
|-------|------|-----|
| 0 | Title Slide | Opening |
| 1 | Title and Content | Most slides |
| 2 | Section Header | Dividers |
| 3 | Two Content | Comparisons |
| 4 | Comparison | Side by side |
| 5 | Title Only | Custom content |
| 6 | Blank | Full control |

## Google Slides API

### Authentication
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/presentations']
creds = service_account.Credentials.from_service_account_file('creds.json', scopes=SCOPES)
service = build('slides', 'v1', credentials=creds)
```

### Create Presentation
```python
presentation = service.presentations().create(body={'title': 'My Deck'}).execute()
presentation_id = presentation['presentationId']
```

### Add Slide
```python
requests = [{
    'createSlide': {
        'objectId': 'slide_001',
        'slideLayoutReference': {'predefinedLayout': 'TITLE_AND_BODY'}
    }
}]
service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()
```

### Insert Text
```python
requests = [{
    'insertText': {
        'objectId': 'title_placeholder_id',
        'text': 'My Title'
    }
}]
```

### Batch Updates (Required for Efficiency)
```python
# Combine multiple operations
requests = [
    {'createSlide': {...}},
    {'insertText': {...}},
    {'updateTextStyle': {...}}
]
service.presentations().batchUpdate(presentationId=id, body={'requests': requests}).execute()
```

## reveal.js (Markdown → Web)

### Basic HTML
```html
<div class="reveal">
  <div class="slides">
    <section>Slide 1</section>
    <section>Slide 2</section>
  </div>
</div>
```

### Markdown Mode
```markdown
---
title: My Talk
---

# Slide 1
Content here

---

# Slide 2
More content

--

## Vertical Slide
Use -- for vertical navigation
```

### Code Highlighting
```markdown
```python
def hello():
    return "world"
```⁣
```

### Speaker Notes
```html
<section>
  <p>Slide content</p>
  <aside class="notes">
    These are speaker notes
  </aside>
</section>
```

## Slidev (Vue + Markdown)

### Frontmatter
```yaml
---
theme: seriph
background: https://source.unsplash.com/random
class: text-center
---
```

### Slides
```markdown
---

# Slide Title

Content with **markdown**

---
layout: two-cols
---

# Left Column

::right::

# Right Column
```

### Code Blocks
```markdown
```ts {2-3|5}
function hello() {
  // highlighted first
  const a = 1
  
  return a // highlighted second
}
```⁣
```

### Run
```bash
npx slidev slides.md
npx slidev build  # Export to static
npx slidev export # Export to PDF
```

## Marp (Markdown → PDF/PPTX)

### Frontmatter (Required)
```yaml
---
marp: true
theme: default
paginate: true
---
```

### Slides
```markdown
# First Slide

---

# Second Slide

![bg right](image.png)

Content with background image
```

### Directives
```markdown
<!-- _class: lead -->    # This slide only
<!-- class: centered --> # All following slides
<!-- _backgroundColor: #123 -->
```

### CLI
```bash
# Install
npm install -g @marp-team/marp-cli

# Convert
marp slides.md -o output.pdf
marp slides.md -o output.pptx
marp slides.md -o output.html
```

## Export Tools

### decktape (Any HTML → PDF)
```bash
npm install -g decktape
decktape reveal http://localhost:8000 output.pdf
decktape generic http://localhost:8000 output.pdf
```

### Playwright (Screenshots)
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8000')
    page.screenshot(path='slide.png', full_page=True)
```
