# ASCII Art Patterns and Techniques

## Character Selection Guide

### Box Drawing Characters
Use for borders, frames, and structural elements:

```
Single line: ┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼
Double line: ╔ ╗ ╚ ╝ ═ ║ ╠ ╣ ╦ ╩ ╬
Thick line:  ┏ ┓ ┗ ┛ ━ ┃ ┣ ┫ ┳ ┻ ╋
Rounded:     ╭ ╮ ╰ ╯
```

### Geometric Shapes
Use for diagrams and visual elements:

```
Circles:     ○ ◌ ◍ ◎ ● ◯ ◉
Squares:     □ ◻ ■ ◼
Triangles:   △ ▲ ▽ ▼
Diamonds:    ◇ ◆
```

### Shading and Texture
Use for gradients, fills, and textures:

```
Light:       · ∙
Medium:      : ∘
Heavy:       * ×
Solid:       # █
Gradient:    ░ ▒ ▓
```

### Special Symbols
Use for decoration and emphasis:

```
Stars:       ★ ☆ ✦ ✧
Hearts:      ♡ ♥ ❤
Arrows:      ← ↑ → ↓ ↔ ↕
Music:       ♪ ♫ ♬
Weather:     ☀ ☁ ☂ ☃
Zodiac:      ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓
Chess:       ♔ ♕ ♖ ♗ ♘ ♙ ♚ ♛ ♜ ♝ ♞ ♟
Cards:       ♠ ♣ ♥ ♦
```

## Common Patterns

### Border Patterns

**Simple Border:**
```
┌────────────┐
│            │
│   Content  │
│            │
└────────────┘
```

**Double Border:**
```
╔════════════╗
║            ║
║   Content  ║
║            ║
╚════════════╝
```

**Rounded Border:**
```
╭────────────╮
│            │
│   Content  │
│            │
╰────────────╯
```

### Header Patterns

**Underlined Header:**
```
Main Title
═══════════
```

**Boxed Header:**
```
┏━━━━━━━━━━━━┓
┃  Title     ┃
┗━━━━━━━━━━━━┛
```

**Centered Header:**
```
    Title
━━━━━━━━━━━━━━
```

### Diagram Patterns

**Flowchart Element:**
```
┌────────────┐
│   Step 1   │
└──────┬─────┘
       ↓
┌────────────┐
│   Step 2   │
└────────────┘
```

**Decision Diamond:**
```
     ┌───┐
     │Yes│
     └─┬─┘
       │
┌──────┴──────┐
│   Decision  │
└──────┬──────┘
       │
     ┌─┴─┐
     │No │
     └───┘
```

### Artistic Patterns

**Tree Pattern:**
```
    ▲
   ▲▲▲
  ▲▲▲▲▲
   │││
   ███
```

**Mountain Pattern:**
```
   /\
  /  \
 /    \
/______\
```

**Wave Pattern:**
```
~~  ~~  ~~
  ~~  ~~  ~~
```

## Color and Styling (ANSI Codes)

### Basic Colors
```
Black:   \033[30m
Red:     \033[31m
Green:   \033[32m
Yellow:  \033[33m
Blue:    \033[34m
Magenta: \033[35m
Cyan:    \033[36m
White:   \033[37m
Reset:   \033[0m
```

### Bright Colors
```
Bright Black:   \033[90m
Bright Red:     \033[91m
Bright Green:   \033[92m
Bright Yellow:  \033[93m
Bright Blue:    \033[94m
Bright Magenta: \033[95m
Bright Cyan:    \033[96m
Bright White:   \033[97m
```

### Background Colors
```
Background Black:   \033[40m
Background Red:     \033[41m
Background Green:   \033[42m
Background Yellow:  \033[43m
Background Blue:    \033[44m
Background Magenta: \033[45m
Background Cyan:    \033[46m
Background White:   \033[47m
```

### Text Styles
```
Bold:       \033[1m
Dim:        \033[2m
Italic:     \033[3m
Underline:  \033[4m
Blink:      \033[5m
Reverse:    \033[7m
Hidden:     \033[8m
```

### Example: Colored ASCII Art
```python
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

colored_art = f"{RED}❤{RESET} {GREEN}♣{RESET} {BLUE}♦{RESET}"
print(colored_art)  # Output: Red heart, green club, blue diamond
```

## Layout Techniques

### Centering Text
```python
def center_text(text, width):
    padding = width - len(text)
    left_pad = padding // 2
    right_pad = padding - left_pad
    return ' ' * left_pad + text + ' ' * right_pad
```

### Proportional Spacing
- Monospaced fonts: All characters have equal width
- Consider visual weight: Some characters appear heavier (█ vs ·)
- Test in target environment: Different terminals may render differently

### Multi-line Alignment
```
Left aligned:   │ Item 1      │
                │ Item 2      │
                │ Long item 3 │
                
Right aligned:  │      Item 1 │
                │      Item 2 │
                │ Long item 3 │
                
Centered:       │   Item 1    │
                │   Item 2    │
                │ Long item 3 │
```

## Best Practices

### 1. Keep it Simple
- Start with basic characters
- Add complexity only when needed
- Test readability at different sizes

### 2. Consider the Medium
- Terminal: Use ANSI colors if supported
- Plain text: Stick to basic ASCII
- Documentation: Use Unicode for better appearance

### 3. Maintain Consistency
- Use the same border style throughout
- Keep alignment consistent
- Use consistent spacing

### 4. Test Thoroughly
- View in target terminal/editor
- Check different font sizes
- Test with screen readers if accessibility is important

### 5. Provide Alternatives
- For complex diagrams, consider providing text description
- Offer simplified versions for small displays
- Consider creating image versions for critical content

## Inspiration Sources

### Classic ASCII Art
```
  _____
 /     \
| () () |
 \  ^  /
  |||||
  |||||
```

### Digital Art Concepts
```
01010101
10101010
01010101
10101010
```

### Abstract Patterns
```
┌─┐ ┌─┐ ┌─┐
│ │ │ │ │ │
└─┘ └─┘ └─┘
```

### Technical Diagrams
```
[Input] → [Process] → [Output]
    ↑         │          │
    └─────────┴──────────┘
        Feedback
```

Remember: ASCII art is not just about recreating images with characters, but about using characters creatively to convey ideas, structure information, and create visual interest in text-based environments.