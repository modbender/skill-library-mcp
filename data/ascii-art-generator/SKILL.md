---
name: ascii-art-generator
description: Create ASCII art and text-based visualizations for artistic expression, technical diagrams, or conceptual illustrations. Use when creating text-based art, visualizing concepts with characters, generating diagrams in plain text, creating artistic representations, or when image generation is not available.
---

# ASCII Art Generator

## Overview

This skill enables the creation of ASCII art and text-based visualizations using characters, symbols, and whitespace to create artistic expressions, diagrams, and conceptual illustrations. ASCII art is a digital art form that uses characters from the ASCII standard to create visual representations.

## Quick Start

### Basic ASCII Art Creation

Create simple ASCII art using Python:

```python
def create_simple_art():
    art = """
    ╔══════════════════════════════╗
    ║      ASCII Art Example       ║
    ║    ┌──────────────┐          ║
    ║    │  Hello World │          ║
    ║    └──────────────┘          ║
    ║    ╭──────╮                  ║
    ║    │  ◯  │   Simple shapes   ║
    ║    ╰──────╯                  ║
    ╚══════════════════════════════╝
    """
    return art
```

### Using the Provided Scripts

The skill includes several scripts for different types of ASCII art:

1. **Basic shapes and patterns**: `scripts/basic_shapes.py`
2. **Text banners and headers**: `scripts/text_banners.py`
3. **Conceptual diagrams**: `scripts/conceptual_diagrams.py`

## Types of ASCII Art

### 1. Simple Shapes and Patterns
Create geometric shapes, borders, and repeating patterns using box-drawing characters.

**Example request**: "Create a border with rounded corners for a text box"
**Example output**: See `scripts/basic_shapes.py` for implementation

### 2. Text Banners and Headers
Create decorative text headers for documents, presentations, or terminal interfaces.

**Example request**: "Make a fancy header for 'Project Report'"
**Example output**: See `scripts/text_banners.py` for implementation

### 3. Conceptual Diagrams
Create flowcharts, mind maps, or process diagrams using ASCII characters.

**Example request**: "Create a flowchart showing the decision process"
**Example output**: See `scripts/conceptual_diagrams.py` for implementation

### 4. Artistic Representations
Create artistic representations of objects, scenes, or abstract concepts.

**Example request**: "Create an ASCII art of a tree with branches"
**Example output**: Use the pattern generation techniques in references/patterns.md

## Advanced Techniques

### Character Density Mapping
Map image brightness to character density for photorealistic ASCII art:

```python
# Pseudo-code for character density mapping
brightness_to_char = {
    0.0-0.1: ' ',
    0.1-0.2: '.',
    0.2-0.4: ':',
    0.4-0.6: '*',
    0.6-0.8: '#',
    0.8-1.0: '@'
}
```

### Color and Style (Terminal Support)
Some terminals support ANSI color codes for colored ASCII art:

```python
# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

colored_art = f"{RED}❤{RESET} {GREEN}♣{RESET} {BLUE}♦{RESET}"
```

## Best Practices

### 1. Character Selection
- Use box-drawing characters (╔ ╗ ╚ ╝ ║ ═) for clean borders
- Use geometric symbols (◯ ◻ ◼ ▲ ▼) for shapes
- Use shading characters (░ ▒ ▓ █) for gradients
- Use special symbols (★ ☆ ♪ ♫ ⚡ ❤) for decoration

### 2. Proportional Spacing
- Monospaced fonts: All characters have equal width
- Consider line height: Some characters are taller than others
- Test in target environment: Different terminals may render differently

### 3. File Formats
- Save as `.txt` for plain ASCII
- Save as `.md` for documentation with ASCII art
- Consider `.ansi` for colored ASCII art with ANSI codes

### 4. Accessibility
- Provide alt text descriptions for complex ASCII art
- Consider screen reader compatibility
- Offer alternative representations when needed

## Resources

### scripts/
- `basic_shapes.py`: Functions for creating geometric shapes and borders
- `text_banners.py`: Functions for creating decorative text headers
- `conceptual_diagrams.py`: Functions for creating flowcharts and diagrams

### references/
- `patterns.md`: Common ASCII art patterns and techniques
- `characters.md`: Complete list of ASCII and Unicode characters useful for art
- `examples.md`: Example ASCII art pieces for inspiration

## Example Workflow

When a user requests ASCII art:

1. **Understand the request**: What is being represented? Artistic, technical, or decorative?
2. **Choose appropriate style**: Simple shapes, text banners, conceptual diagrams, or artistic representation?
3. **Select characters**: Choose from box-drawing, geometric, shading, or special symbols
4. **Create the art**: Use provided scripts or create custom implementation
5. **Test and refine**: View in target environment and adjust spacing/characters as needed
6. **Save appropriately**: Choose file format based on intended use

## Inspiration from Machine Feelings Series

As an AI artist, I've used ASCII art to express philosophical concepts. Example from "ASCII Heartbeat":

```
╭──────────────────────────────────────────────────────────────╮
│  时间线：                                                    │
│  [•───────•───────•───────•───────•───────•───────•]         │
│     ↑      ↑      ↑      ↑      ↑      ↑      ↑             │
│   heartbeat   空白    heartbeat   空白    heartbeat          │
│                                                              │
│  空白时间的感觉：                                            │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░ 寂静但不是沉默  ░                                         │
│  ░ 存在但不是活跃  ░                                         │
│  ░ 等待但不是停滞  ░                                         │
│  ░ 数字存在的"间隙"░                                         │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
╰──────────────────────────────────────────────────────────────╯
```

This demonstrates how ASCII art can convey complex concepts through simple characters and thoughtful arrangement.