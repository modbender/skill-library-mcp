# MechanicsSketches API Reference

Condensed reference for all public functions. For full documentation, see [docs.md](../../../docs.md).

---

## Sketch Management (`base.py`)

```python
create_sketch(name="", parameters={})
# Returns: dict with keys "name", "objects", "parameters"

add_to_sketch(sketch, obj)
# Adds a primitive or group to sketch["objects"]

make_group(objects, name="")
# Returns: group dict with type="group"

save_sketch(sketch, filename)
# Saves sketch to JSON file

load_sketch(filename)
# Returns: sketch dict from JSON file
```

---

## Primitives (`base.py`)

```python
make_line(x0, y0, x1, y1, linewidth=1.0, layer=5, edgecolor="black")
# Returns: line dict

make_circle(x, y, r, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# Returns: circle dict

make_arc(x, y, width, height, theta1, theta2, angle=0, linewidth=1.0, layer=5, edgecolor="black")
# Returns: arc dict

make_polygon(points, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# points: list of (x, y) tuples
# Returns: polygon dict

make_rectangle(x0, y0, x1, y1, linewidth=1.0, layer=5, facecolor="white", edgecolor="black")
# Returns: polygon dict (rectangle is a special case of polygon)

make_text(x, y, text, fontsize=20, layer=10, color="black", ha="center", va="center", rotation=0, render_mode="latex")
# Returns: text dict. Use render_mode="plain" to disable LaTeX.
```

---

## Transformations (`base.py`)

```python
translate(obj_or_list, dx, dy)
# Returns: new translated object(s)

rotate(obj_or_list, cx, cy, angle_deg, ignore_text=False)
# Returns: new rotated object(s). Rotates around (cx, cy).

scale(obj_or_list, cx, cy, factor, scale_linewidth=False)
# Returns: new scaled object(s). Scales from center (cx, cy).
```

All transformations are non-destructive (return new objects).

---

## Mechanical Elements (`elements.py`)

All `add_*` functions take `sketch` as first argument and call `add_to_sketch` internally.
All `make_*` functions return a list of primitives without adding to a sketch.

### Supports

```python
add_pinned_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Pinned support (Festlager). angle_deg=0 → triangle points upward.

add_roller_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Roller support (Loslager). angle_deg=0 → points upward with sliding gap.

add_fixed_support(sketch, cx, cy, angle_deg=0, scale_factor=1.0, name="")
# Fixed/clamped support (Einspannung). angle_deg=0 → vertical wall, hatching left.

add_hinge(sketch, cx, cy, scale_factor=1.0, name="")
# Hinge joint (Gelenk). Simple circle, no angle parameter.
```

### Structural Elements

```python
add_beam(sketch, ax, ay, bx, by, scale_factor=1.0, name="")
# Rectangular beam from (ax, ay) to (bx, by).

add_truss(sketch, ax, ay, bx, by, scale_factor=1.0, name="")
# Truss member (line) from (ax, ay) to (bx, by).
```

### Loads

```python
add_force(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
          annotation="", fontsize_scale=1.0, offsetx=0, offsety=0,
          rotate_annotation=False, name="")
# Force arrow. angle_deg=0 → points upward (+y).
# Arrow tip is at (cx, cy), arrow extends away from that point.

add_moment(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
           annotation="", fontsize_scale=1.0, offsetx=0, offsety=0,
           rotate_annotation=False, name="")
# Curved moment arrow. angle_deg=0 → counterclockwise.
```

### Dimensions

```python
add_dimension_arrow(sketch, cx, cy, length, angle_deg=0, scale_factor=1.0,
                    annotation="", fontsize_scale=1.0, offsetx=0, offsety=0,
                    rotate_annotation=False, name="")
# Double-headed dimension arrow centered at (cx, cy).
# length is in coordinate space (not scaled). angle_deg=0 → horizontal.

add_dimension_thickness(sketch, cx, cy, thickness, angle_deg=0, scale_factor=1.0,
                        annotation="", fontsize_scale=1.0, offsetx=0, offsety=0,
                        rotate_annotation=False, name="")
# Thickness dimension with inward-pointing arrows. angle_deg=0 → horizontal.
```

### Coordinate Systems

```python
add_coordinate_system(sketch, cx, cy, angle_deg=0, scale_factor=1.0,
                      ax1="$x$", ax2="$y$", ax3="$z$",
                      last_axis_out_of_image=True,
                      fontsize_scale=1.0, rotate_annotation=False, name="")
# angle_deg=0 → ax1 points right, ax2 points up.
# last_axis_out_of_image=True → dot (⊙), False → cross (⊗).
```

### Text

```python
add_text(sketch, x, y, text, fontsize=10, name="", rotation=0)
# Adds a text annotation at (x, y).
```

---

## Rendering

```python
# Qt renderer (default, recommended)
from MechanicsSketches.qt_renderer import render
render(sketch, filename="output.pdf", dpi=300, margin=0.05)
# Formats: .pdf, .png, .jpg, .svg

# Matplotlib renderer (fallback)
from MechanicsSketches.renderer import mpl_render
mpl_render(sketch, figsize=(5, 5), filename="output.pdf", dpi=300)
```

---

## JSON Sketch Format

```json
{
    "name": "Sketch Name",
    "parameters": {},
    "objects": [
        {"type": "line", "x": [0, 5], "y": [0, 0], "lw": 1.0, "l": 5, "edgecolor": "black"},
        {"type": "group", "name": "Support", "c_type": "pinned_support",
         "c_params": {"cx": 0, "cy": 0, "angle_deg": 0, "scale_factor": 30},
         "objects": [...]}
    ]
}
```
