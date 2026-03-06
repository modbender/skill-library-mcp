---
name: mechanics-sketches
description: >
  Generate technical engineering mechanics sketches (beams, supports, forces,
  moments, dimensions, coordinate systems) as PDF/PNG/SVG using the
  MechanicsSketches Python library. Use this skill when asked to create
  free-body diagrams, structural sketches, or mechanical engineering figures.
license: MIT
homepage: https://github.com/MatthiasHBusch/MechanicsSketches
metadata: {"author": "MatthiasHBusch", "version": "1.0.0"}
files: ["scripts/*", "references/*"]
---

# MechanicsSketches Skill

You can generate engineering mechanics sketches programmatically using the **MechanicsSketches** Python library.

## Setup

Install the library via pip:

```bash
pip install git+https://github.com/MatthiasHBusch/MechanicsSketches.git
```

Or install dependencies manually and add to `PYTHONPATH`:

```bash
pip install matplotlib PyQt5
export PYTHONPATH="/path/to/parent/of/MechanicsSketches:$PYTHONPATH"
```

## Quick Start — Writing a Script

Create a Python script that builds a sketch and renders it:

```python
from MechanicsSketches import *
import os

sketch = create_sketch("My Sketch")
S = 30.0  # Scale factor (recommended: 20-40)

# Add components
add_beam(sketch, ax=0, ay=0, bx=10*S, by=0, scale_factor=S)
add_pinned_support(sketch, cx=0, cy=0, angle_deg=0, scale_factor=S)
add_roller_support(sketch, cx=10*S, cy=0, angle_deg=0, scale_factor=S)
add_force(sketch, cx=5*S, cy=0, angle_deg=0, scale_factor=S, annotation=r"$F$")

# Render
script_dir = os.path.dirname(os.path.abspath(__file__))
render(sketch, filename=os.path.join(script_dir, "output.pdf"), dpi=300)
```

Then run: `python my_sketch.py`

## Quick Start — Using the Helper Script

Alternatively, use the bundled helper to render from JSON:

```bash
python scripts/generate_sketch.py input.json output.pdf
```

## Key Concepts

### Scale Factor (`S`)

All positions and sizes should be multiples of `S` (typically 30.0). This keeps proportions consistent across components.

### Angle Convention

- `angle_deg=0` → default orientation (upward for supports/forces, horizontal for dimensions)
- Angles rotate counterclockwise in degrees

### Available Components

| Function | Description | Key Parameters |
|----------|-------------|----------------|
| `add_beam(sketch, ax, ay, bx, by, scale_factor)` | Rectangular beam A→B | Endpoints, scale |
| `add_truss(sketch, ax, ay, bx, by, scale_factor)` | Line member A→B | Endpoints, scale |
| `add_pinned_support(sketch, cx, cy, angle_deg, scale_factor)` | Fixed-position support (triangle) | Center, angle, scale |
| `add_roller_support(sketch, cx, cy, angle_deg, scale_factor)` | Sliding support | Center, angle, scale |
| `add_fixed_support(sketch, cx, cy, angle_deg, scale_factor)` | Clamped wall support | Center, angle, scale |
| `add_hinge(sketch, cx, cy, scale_factor)` | Joint circle | Center, scale |
| `add_force(sketch, cx, cy, angle_deg, scale_factor, annotation, ...)` | Force arrow | Center, angle, scale, label |
| `add_moment(sketch, cx, cy, angle_deg, scale_factor, annotation, ...)` | Curved moment arrow | Center, angle, scale, label |
| `add_dimension_arrow(sketch, cx, cy, length, angle_deg, scale_factor, annotation, ...)` | Double-headed dimension | Center, length, angle, scale, label |
| `add_dimension_thickness(sketch, cx, cy, thickness, angle_deg, scale_factor, annotation, ...)` | Inward dimension arrows | Center, thickness, angle, scale, label |
| `add_coordinate_system(sketch, cx, cy, angle_deg, scale_factor, ax1, ax2, ax3, ...)` | x-y-z axes | Center, angle, scale, axis labels |
| `add_text(sketch, x, y, text, fontsize, name, rotation)` | Text annotation | Position, text, font size |

### Annotation Parameters

Force, moment, and dimension functions accept:
- `annotation` — LaTeX string (e.g., `r"$F$"`, `r"$M_A$"`)
- `fontsize_scale` — relative font size (default 1.0)
- `offsetx`, `offsety` — label position offset
- `rotate_annotation` — rotate label with component (default False)

### Primitives

For custom shapes, use:
- `make_line(x0, y0, x1, y1, linewidth, layer, edgecolor)`
- `make_circle(x, y, r, linewidth, layer, facecolor, edgecolor)`
- `make_polygon(points, linewidth, layer, facecolor, edgecolor)`
- `make_arc(x, y, width, height, theta1, theta2, angle, linewidth, layer)`
- `make_text(x, y, text, fontsize, layer, color, ha, va, rotation)`
- `make_rectangle(x0, y0, x1, y1, ...)`

Add to sketch via `add_to_sketch(sketch, primitive)`.

### Transformations

- `translate(obj, dx, dy)` — move by offset
- `rotate(obj, cx, cy, angle_deg)` — rotate around point
- `scale(obj, cx, cy, factor)` — scale from center

All return new objects (non-destructive). Can be chained.

### Rendering

```python
render(sketch, filename="output.pdf", dpi=300)  # Qt renderer (default, recommended)
mpl_render(sketch, filename="output.pdf")        # Matplotlib fallback (deprecated, text scaling issues)
```

Supported formats: `.pdf`, `.png`, `.jpg`, `.svg`

## Tips for the Agent

1. Always define `S = 30.0` as the scale factor
2. Place beams first, then supports at endpoints, then loads
3. Use LaTeX for annotations: `r"$F$"`, `r"$M_0$"`, `r"$\ell$"`
4. For detailed API signatures, see `references/api_reference.md`
5. The `render()` function requires a filename — it does not display interactively
6. Do **not** use `mpl_render()` — it is deprecated due to text scaling issues. Always use `render()`.

## External Endpoints

This skill makes **no network requests**. All processing is done locally.

## Security & Privacy

- **No data leaves your machine.** The skill only reads local JSON files and writes local image/PDF output.
- No API keys or credentials are required.
- No telemetry or analytics.
- The helper script (`scripts/generate_sketch.py`) only reads the input file specified by the user and writes to the specified output path.

## Trust Statement

This skill is developed and maintained by [MatthiasHBusch](https://github.com/MatthiasHBusch). The source code is fully open under the MIT license. All functionality runs locally with no external dependencies beyond standard Python packages (matplotlib, PyQt5).
