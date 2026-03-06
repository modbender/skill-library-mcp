---
name: generating-publication-ready-figures-in-r
description: Transform standard ggplot2 figures into publication-quality visualizations matching Nature, Science, and other top journal styles with proper themes, colors, fonts, and export settings.
---

# Generating Publication-Ready Figures in R

This skill specializes in transforming ordinary ggplot2 plots into professional, publication-ready figures that meet the strict standards of top-tier journals like Nature, Science, Cell, and others.

Use this skill when the user wants to:
- Convert ggplot plots to journal-style figures
- Apply Nature/Science publication themes to existing plots
- Create multi-panel figures with consistent styling
- Export figures with proper DPI, dimensions, and formats
- Match specific journal submission guidelines
- Create colorblind-safe and publication-quality color schemes

---

## What This Skill Does

When activated, this skill will:

1. **Analyze existing ggplot code** - Read and understand the current plot structure

2. **Apply journal themes** - Add publication-quality themes including:
   - Proper font sizes and families
   - Clean axis lines and backgrounds
   - Journal-specific color palettes
   - Legend positioning and styling

3. **Optimize for submission** - Ensure figures meet:
   - DPI requirements (typically 300-600 DPI)
   - Width/height specifications (single vs double column)
   - File format requirements (TIFF, PDF, EPS)
   - Color space requirements (CMYK vs RGB)

4. **Create multi-panel figures** - Combine plots using:
   - `patchwork` for simple layouts
   - `cowplot` for complex compositions
   - Custom annotation and labeling

5. **Export properly** - Save with correct:
   - Resolution (DPI)
   - Dimensions (inches/cm)
   - File format
   - Color profile

---

## Example User Requests That Should Trigger This Skill

- "Transform this ggplot to Nature journal style"
- "Make this figure publication-ready for Science"
- "Create a two-column figure matching Cell format"
- "Export these plots at 600 DPI for submission"
- "Apply a colorblind-safe palette to my plots"
- "Combine these four plots into one publication figure"
- "Format my scatter plot for PNAS submission"

---

## Journal Style Guidelines

### Nature Style
- Font: Arial or Helvetica
- Font sizes: Axis titles 7-9 pt, axis labels 6-8 pt
- Single column: 89 mm (3.5 in) width
- Double column: 183 mm (7.2 in) width
- Max height: 234 mm (9.2 in)
- Resolution: 300-600 DPI
- Formats: TIFF, PDF, EPS (vector preferred)

### Science Style
- Font: Arial
- Font sizes: Title 9 pt, labels 7 pt
- Single column: 57 mm (2.25 in) width
- Double column: 114 mm (4.5 in) width
- Resolution: 300-600 DPI
- Formats: TIFF, PDF, EPS

### Cell Press Style
- Font: Arial or Helvetica
- Single column: 85 mm (3.3 in) width
- Double column: 178 mm (7 in) width
- Resolution: 300 DPI minimum
- Formats: TIFF, EPS, PDF

---

## Theme Templates Available

### `theme_nature()`
Clean, minimalist theme matching Nature journals:
- No gray backgrounds
- Minimal grid lines
- Arial font family
- Proper axis sizing

### `theme_science()`
Theme for Science journal submissions:
- Compact layout
- Clean typography
- Optimized for smaller widths

### `theme_cellpress()`
Cell Press journal theme:
- Professional appearance
- Flexible legend placement
- Publication-ready defaults

### `theme_colorblind()`
Colorblind-safe palette with:
- Viridis/Colorbrewer schemes
- High contrast ratios
- Print-friendly colors

---

## Color Palettes

### Nature-Approved Colors
```r
# Primary colors
nature_colors <- c(
  blue = "#3B4992",
  red = "#EE0000",
  green = "#008B45",
  purple = "#631879"
)
```

### Colorblind-Safe Scales
- `scale_fill_viridis()`
- `scale_color_okabe_ito()` (Okabe-Ito palette)
- `scale_color_viridis()`

---

## Example Workflow

**User:** Here's my ggplot code, make it Nature-style.

```r
# Original plot
p <- ggplot(mtcars, aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 3)
```

**Skill transforms to:**

```r
# Publication-ready version
p <- ggplot(mtcars, aes(x = "Weight (tons)", y = "Fuel Efficiency (mpg)",
                        color = "Cylinders")) +
  geom_point(size = 2.5, shape = 16, alpha = 0.8) +
  scale_color_nature() +
  theme_nature(base_size = 8) +
  labs(title = NULL)

# Export at correct size
ggsave("figure1.pdf", p, width = 3.5, height = 3, dpi = 300,
       device = "pdf")
```

---

## Multi-Panel Figures

```r
# Combine plots with patchwork
library(patchwork)

figure1 <- (panel_a | panel_b) / (panel_c | panel_d)

# Add panel labels
figure1 <- figure1 +
  plot_annotation(tag_levels = "A",
                  tag_suffix = ")")

# Export
ggsave("figure1.pdf", figure1, width = 7, height = 6, dpi = 300)
```

---

## Tools & Packages Commonly Used

| Purpose | R Packages |
|--------|------------|
| Base plotting | ggplot2 |
| Themes | ggplot2, cowplot, hrbrthemes |
| Color palettes | viridis, RColorBrewer, scales, ggsci |
| Multi-panel | patchwork, cowplot, ggpubr |
| Export | ggplot2, ragg |
| Fonts | extrafont, showtext |
| Annotations | ggrepel, ggpp |

---

## Common Journal Requirements

| Journal | Width (single) | Width (double) | Max Height | Min DPI |
|---------|---------------|----------------|------------|---------|
| Nature | 89 mm | 183 mm | 234 mm | 300 |
| Science | 57 mm | 114 mm | 229 mm | 300 |
| Cell | 85 mm | 178 mm | 229 mm | 300 |
| PNAS | 87 mm | 178 mm | 227 mm | 300 |
| PLOS ONE | 170 mm | - | 230 mm | 300 |
| eLife | 183 mm | - | 244 mm | 300 |

---

## Quick Reference

### Applying a theme
```r
p + theme_nature()           # Nature style
p + theme_science()          # Science style
p + theme_cellpress()        # Cell Press style
p + theme_colorblind()       # Colorblind-safe
```

### Export formats
```r
# Vector (preferred)
ggsave("figure.pdf", ... device = "pdf")
ggsave("figure.eps", ... device = "eps")

# Raster (high DPI)
ggsave("figure.tiff", ... device = "tiff", dpi = 600)
ggsave("figure.png", ... device = "png", dpi = 300)
```

### Common fixes
- **Text too small**: Increase `base_size` in theme
- **Legend overlap**: Use `theme(legend.position = "bottom")`
- **Colors not distinct**: Use `scale_fill_viridis()`
- **Fonts not rendering**: Use `extrafont::font_import()`

---

## Notes

- Always check specific journal guidelines before submission
- Vector formats (PDF/EPS) are preferred over raster
- Use consistent styling across all figures in a paper
- Test colorblind accessibility with `colorblindr` package
- Keep axis labels clear and concise
- Avoid redundant chart junk (backgrounds, grid lines)
