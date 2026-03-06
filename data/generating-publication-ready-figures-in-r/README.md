# Generating Publication-Ready Figures in R

A Claude Code skill and R package for transforming ggplot2 visualizations into publication-quality figures that meet the strict standards of top-tier scientific journals.

## Features

### Journal Themes
- `theme_nature()` - Nature journal style (single: 89mm, double: 183mm)
- `theme_science()` - Science journal style (single: 57mm, double: 114mm)
- `theme_cellpress()` - Cell Press journals style
- `theme_pnas()` - PNAS style
- `theme_colorblind()` - Colorblind-accessible theme

### Color Palettes
- `scale_color_nature()` - Nature-inspired color schemes
- `scale_fill_nature()` - Fill version for Nature colors
- `scale_color_okabe_ito()` - Okabe-Ito colorblind-safe palette

### Helper Functions
- `export_publication()` - Export figures with proper DPI and dimensions
- `journal_dims()` - Get standard dimensions for any journal
- `figure_publication()` - Create multi-panel figures with labels

## Quick Start

### Invoke the Skill

Simply ask Claude to create publication-ready figures:

```
Transform this ggplot to Nature journal style
Make this figure publication-ready for Science
Create a two-column figure matching Cell format
Export these plots at 600 DPI for submission
```

### Use in R

```r
# Source the themes
source("R/publication_themes.R")

# Create a basic plot
library(ggplot2)
p <- ggplot(mtcars, aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 2.5)

# Apply Nature theme
p_nature <- p +
  scale_color_nature() +
  theme_nature(base_size = 8) +
  labs(x = "Weight (tons)", y = "Fuel Efficiency (mpg)",
       color = "Cylinders")

# Export for Nature single column
export_publication(p_nature, "figure.pdf",
                   width = 3.5, height = 3, dpi = 300)
```

## Installation

```r
# Clone or download this repository

# Source the themes in your R script
source("R/publication_themes.R")

# Required packages
install.packages(c("ggplot2", "patchwork"))
```

## Examples

### Basic Scatter Plot

```r
library(ggplot2)
source("R/publication_themes.R")

p <- ggplot(mtcars, aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_nature() +
  labs(x = "Weight (tons)", y = "Fuel Efficiency (mpg)",
       color = "Cylinders") +
  theme_nature(base_size = 8)

export_publication(p, "figure.pdf", width = 3.5, height = 3)
```

### Multi-Panel Figure

```r
library(patchwork)

p1 <- ggplot(data, aes(x, y)) + geom_point() + theme_nature()
p2 <- ggplot(data, aes(x, y)) + geom_boxplot() + theme_nature()
p3 <- ggplot(data, aes(x)) + geom_histogram() + theme_nature()
p4 <- ggplot(data, aes(x, fill = group)) + geom_bar() + theme_nature()

fig <- figure_publication(p1, p2, p3, p4, ncol = 2)

export_publication(fig, "multipanel.pdf",
                   width = 7.2, height = 5)
```

### Colorblind-Safe Plot

```r
p <- ggplot(mtcars, aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 2.5) +
  scale_color_okabe_ito() +
  theme_colorblind(base_size = 10)

export_publication(p, "figure.pdf", width = 5, height = 4)
```

## Journal Dimensions

| Journal | Single Column | Double Column | Max Height | Min DPI |
|---------|---------------|---------------|------------|---------|
| Nature | 89 mm (3.5 in) | 183 mm (7.2 in) | 234 mm | 300 |
| Science | 57 mm (2.25 in) | 114 mm (4.5 in) | 229 mm | 300 |
| Cell | 85 mm (3.3 in) | 178 mm (7 in) | 229 mm | 300 |
| PNAS | 87 mm (3.4 in) | 178 mm (7 in) | 227 mm | 300 |
| PLOS ONE | 170 mm (6.7 in) | - | 230 mm | 300 |
| eLife | 183 mm (7.2 in) | - | 244 mm | 300 |

Use `journal_dims()` to get dimensions programmatically:

```r
journal_dims("nature", "single")
# $width: 3.5, $height_max: 9.2, $dpi: 300

journal_dims("science", "double")
# $width: 4.5, $height_max: 9, $dpi: 300
```

## Theme Comparison

| Feature | Nature | Science | Cell Press | Colorblind |
|---------|--------|---------|-----------|------------|
| Clean background | ✓ | ✓ | ✓ | ✓ |
| Minimal grid | ✓ | ✓ | ✓ | ✓ |
| Font family | Arial | Arial | Arial | sans |
| Optimized width | 89mm | 57mm | 85mm | flexible |
| Color palette | Default | N/A | N/A | Viridis/Okabe |

## Export Options

```r
export_publication(
  plot,                    # ggplot object
  "figure.pdf",            # filename
  width = 3.5,             # width in inches
  height = 3,              # height in inches
  dpi = 300,               # resolution
  units = "in",            # units
  device = "pdf",          # auto-detected from extension
  color_space = "RGB"      # color space
)
```

Supported formats: PDF, TIFF, PNG, EPS, SVG

## Color Palettes

### Nature Colors (Default)
```r
c("#3B4992", "#EE0000", "#008B45", "#631879",
  "#E69F00", "#009E73", "#56B4E9", "#D55E00")
```

### Okabe-Ito (Colorblind-Safe)
```r
c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
  "#0072B2", "#D55E00", "#CC79A7", "#999999", "#000000")
```

## Project Structure

```
generating-publication-ready-figures-in-r/
├── SKILL.md              # Skill definition for Claude Code
├── README.md             # This file
├── R/
│   └── publication_themes.R  # Main themes and functions
├── examples/
│   └── basic_example.R   # Usage examples
└── inst/
    └── themes/           # Additional theme files
```

## Run Examples

```r
# Set working directory to examples/
setwd("examples/")

# Run the example script
source("basic_example.R")
```

## Best Practices

1. **Vector formats first** - Use PDF/EPS when possible for scalability
2. **Check journal guidelines** - Always verify specific requirements
3. **Use consistent styling** - Apply same theme across all figures
4. **Test colorblind accessibility** - Use `colorblindr` package
5. **Keep labels concise** - Short, clear axis and legend labels
6. **Avoid chart junk** - Remove unnecessary grid lines, backgrounds

## Common Issues

### Fonts not rendering
```r
install.packages("extrafont")
extrafont::font_import()
extrafont::loadfonts()
```

### Legend overlaps plot
```r
p + theme(legend.position = "bottom")
# or
p + theme(legend.position = "outside")
```

### Text too small
```r
p + theme_nature(base_size = 10)  # increase from default 8
```

## Related Packages

- **ggplot2** - Base plotting system
- **patchwork** - Multi-panel figure composition
- **cowplot** - Alternative for combining plots
- **ggpubr** - Publication-ready plots with statistical tests
- **viridis** - Colorblind-safe color scales
- **colorblindr** - Test colorblind accessibility
- **extrafont** - Custom font support

## License

MIT

## Contributing

Contributions welcome! Feel free to submit issues or pull requests for additional journal themes, color palettes, or functionality improvements.

## Citation

If you use this skill/package in your work, please cite the repository and consider citing the ggplot2 package as well.

---

**Created as a Claude Code skill for automating publication-quality figure generation.**
