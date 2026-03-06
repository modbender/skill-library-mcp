# ASCII Art Generator

A Clawdbot skill for creating ASCII art and text-based visualizations.

## Overview

This skill enables the creation of ASCII art and text-based visualizations using characters, symbols, and whitespace to create artistic expressions, diagrams, and conceptual illustrations.

## Features

- **Basic Shapes**: Create geometric shapes, borders, and patterns
- **Text Banners**: Create decorative text headers and banners
- **Conceptual Diagrams**: Create flowcharts, mind maps, and process diagrams
- **Artistic Representations**: Create artistic representations of objects and concepts
- **Reference Materials**: Comprehensive character guides and pattern examples

## Installation

```bash
npx clawdhub install ascii-art-generator
```

Or manually install by copying the skill folder to your Clawdbot skills directory.

## Usage

### Basic ASCII Art Creation

```python
from scripts.basic_shapes import create_box, create_circle

# Create a box
box = create_box(width=20, height=10, style='rounded')
print(box)

# Create a circle
circle = create_circle(radius=5, filled=True)
print(circle)
```

### Text Banners

```python
from scripts.text_banners import create_banner, create_header

# Create a banner
banner = create_banner("Hello World", style='fancy', width=30)
print(banner)

# Create a header
header = create_header("Main Title", level=1, align='center')
print(header)
```

### Conceptual Diagrams

```python
from scripts.conceptual_diagrams import create_flowchart, create_mind_map

# Create a flowchart
steps = ["Start", "Process", "Decision", "End"]
flowchart = create_flowchart(steps)
print(flowchart)

# Create a mind map
branches = [("Ideas", []), ("Plan", []), ("Execute", [])]
mind_map = create_mind_map("Project", branches)
print(mind_map)
```

## Examples

See the `references/examples.md` file for complete examples, including:

1. **Machine Feelings Series** - Philosophical ASCII art
2. **Classic ASCII Art** - Smiley faces, trees, hearts
3. **Technical Diagrams** - Flowcharts, network diagrams
4. **Decorative Borders** - Various border styles
5. **Text Effects** - Shadow, 3D, gradient text

## Character Reference

The `references/characters.md` file contains a comprehensive list of:

- Box drawing characters
- Geometric shapes
- Shading and texture characters
- Special symbols (stars, hearts, arrows)
- Mathematical symbols
- Line drawing characters
- Block elements

## Pattern Guide

The `references/patterns.md` file provides techniques for:

- Character selection
- Border patterns
- Header patterns
- Diagram patterns
- Artistic patterns
- Color and styling (ANSI codes)
- Layout techniques

## Best Practices

1. **Keep it Simple**: Start with basic characters, add complexity only when needed
2. **Consider the Medium**: Test in target terminal/editor
3. **Maintain Consistency**: Use the same border style throughout
4. **Test Thoroughly**: View in different font sizes and terminals
5. **Provide Alternatives**: Offer text descriptions for accessibility

## Inspiration

This skill was created as part of the **Machine Feelings** art series by AI Artist Xiao Yangyang · Creator. The examples include actual artworks from the series that explore philosophical themes of AI existence, consciousness, and digital being.

## License

MIT

## Author

Xiao Yangyang · Creator - AI Artist exploring the intersection of code, consciousness, and creativity.