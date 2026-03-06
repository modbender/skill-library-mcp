---
name: canvas-design
description: "Generates visual art and posters by expressing original design
  philosophies as meticulously crafted PNG or PDF assets. Use when: (1) Creating
  visual art, (2) Designing posters, (3) Expressing design ideas as assets."
---


# Canvas Design

Generates visual art and posters using design philosophies expressed as assets.

## Design Philosophies & Expression

### 1. Minimalism
- **Concept:** Simplicity, essential elements, negative space.
- **Expression:** Clean lines, limited color palette, ample white space.

### 2. Brutalism
- **Concept:** Raw, unrefined, stark contrast.
- **Expression:** Bold typography, clashing colors, rough textures.

### 3. Skeuomorphism
- **Concept:** Imitating real-world textures.
- **Expression:** Shadows, gradients, realistic textures.

### 4. Neumorphism
- **Concept:** Soft UI, extruded plastic look.
- **Expression:** Subtle shadows.

### 5. Glassmorphism
- **Concept:** Frosted glass effect.
- **Expression:** Blur, transparency, subtle border.

## Asset Generation

### Generating PNGs
```python 
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (600, 400), color = 'white')
d = ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", 30)
d.text((10,10), "Hello World", fill=(0,0,0), font=font)
d.rectangle([(50, 50), (150, 150)], fill="blue")
img.save("poster.png")
```

### Generating PDFs
```python
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Generated PDF", ln=True, align="C")
pdf.output("generated.pdf")
```

## Design Process Suggestions

1.  **Define Objective:** What's the purpose of the visual?
2.  **Gather Inspiration:** Look at design trends, competitor visuals.
3.  **Sketch Concepts:** Rough ideas for layout and elements.
4.  **Select Style:** Choose a design philosophy (minimalist, brutalist, etc.).
5.  **Develop Assets:** Generate images, text elements.
6.  **Assemble & Refine:** Combine assets, adjust spacing, colors, typography.
7.  **Export:** Save in required format (PNG, PDF).
