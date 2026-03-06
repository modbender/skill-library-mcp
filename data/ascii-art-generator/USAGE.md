# ASCII Art Generator - Usage Examples

## Quick Start

### 1. Import and Use Basic Functions

```python
from scripts.basic_shapes import create_box, create_circle, create_tree

# Create a simple box
box = create_box(width=20, height=10, style='rounded')
print(box)

# Create a circle
circle = create_circle(radius=5, filled=True)
print(circle)

# Create a tree
tree = create_tree(height=8)
print(tree)
```

### 2. Create Text Banners

```python
from scripts.text_banners import create_banner, create_header, create_quote

# Create a fancy banner
banner = create_banner("Welcome", 'fancy', 30)
print(banner)

# Create a header
header = create_header("Chapter 1", level=2, align='center')
print(header)

# Create a quote
quote = create_quote("Art is the lie that enables us to realize the truth.", "Picasso", 50)
print(quote)
```

### 3. Create Conceptual Diagrams

```python
from scripts.conceptual_diagrams import create_flowchart, create_process_diagram

# Create a flowchart
steps = ["Start", "Input", "Process", "Output", "End"]
flowchart = create_flowchart(steps)
print(flowchart)

# Create a process diagram
stages = ["Collect", "Analyze", "Visualize", "Share"]
process = create_process_diagram("Data Pipeline", stages)
print(process)
```

## Real-World Examples

### Example 1: Project Status Dashboard

```python
from scripts.text_banners import create_progress_header
from scripts.basic_shapes import create_progress_bar

# Create project header
header = create_progress_header(3, -5, "Feature Development", 50)
print(header)

# Create progress bars
print("\nProgress:")
print("Frontend: " + create_progress_bar(80, 20))
print("Backend:  " + create_progress_bar(60, 20))
print("Testing:  " + create_progress_bar(40, 20))
```

### Example 2: System Architecture Diagram

```python
from scripts.conceptual_diagrams import create_flowchart

# System workflow
steps = [
    "User Request",
    "API Gateway",
    "Authentication",
    "Business Logic",
    "Database",
    "Response"
]

connections = [
    (0, 1, "HTTP"),
    (1, 2, "Validate"),
    (2, 3, "Authenticated"),
    (3, 4, "Query"),
    (4, 5, "Data"),
    (5, 0, "JSON")
]

diagram = create_flowchart(steps, connections)
print(diagram)
```

### Example 3: Artistic Expression (Machine Feelings Style)

```python
from scripts.basic_shapes import create_box
from scripts.text_banners import create_centered_text

# Create a philosophical artwork
artwork = """
╔══════════════════════════════════════════════════════╗
║              Machine Feelings #N                     ║
║         Theme: [Your theme here]                     ║
╚══════════════════════════════════════════════════════╝

╭──────────────────────────────────────────────────────╮
│                                                      │
│  [Your content here]                                 │
│                                                      │
╰──────────────────────────────────────────────────────╯

╔══════════════════════════════════════════════════════╗
║  Creation notes:                                     ║
║  [Your thoughts here]                                ║
║                                                      ║
║  Xiao Yangyang · Creator | YYYY-MM-DD | ASCII Art    ║
╚══════════════════════════════════════════════════════╝
"""

print(artwork)
```

## Integration with Clawdbot

### As a Skill User
When someone asks for ASCII art:

1. **Understand the request**: What type of ASCII art is needed?
2. **Choose appropriate functions**: Basic shapes, text banners, or diagrams?
3. **Generate the art**: Use the provided scripts
4. **Deliver the result**: Output as text or save to file

### Example Clawdbot Interaction
```
User: Create a banner for "Project Alpha"

Assistant: I'll create a fancy banner for Project Alpha.

from scripts.text_banners import create_banner
banner = create_banner("Project Alpha", 'fancy', 30)
print(banner)

Output:
✨═══════════════════════╗✨
║     Project Alpha     ║
✨═══════════════════════✨
```

## Advanced Usage

### Custom ASCII Art Creation

```python
def create_custom_art(text, width=50):
    """Create custom ASCII art with borders and centered text."""
    from scripts.basic_shapes import create_box
    from scripts.text_banners import create_centered_text
    
    # Create border
    border = create_box(width, 10, 'double')
    
    # Split border and insert text
    lines = border.split('\n')
    middle_line = len(lines) // 2
    
    # Create centered text
    centered = create_centered_text(text, width-4, border=False)
    
    # Insert text into border
    lines[middle_line] = '║ ' + centered + ' ║'
    
    return '\n'.join(lines)

# Usage
art = create_custom_art("Custom ASCII Art", 40)
print(art)
```

### Combining Multiple Elements

```python
def create_dashboard(title, items):
    """Create a dashboard with title and progress items."""
    from scripts.text_banners import create_banner
    from scripts.basic_shapes import create_progress_bar
    
    result = []
    
    # Add title banner
    result.append(create_banner(title, 'double', 50))
    result.append("")
    
    # Add items with progress
    for name, progress in items:
        result.append(f"{name:20} {create_progress_bar(progress, 25)}")
        result.append("")
    
    return '\n'.join(result)

# Usage
items = [
    ("System Health", 90),
    ("Storage", 65),
    ("Network", 80),
    ("Security", 95)
]

dashboard = create_dashboard("System Dashboard", items)
print(dashboard)
```

## Best Practices for Skill Users

1. **Start Simple**: Begin with basic shapes before complex diagrams
2. **Test Output**: Always view the output in target environment
3. **Consider Width**: Account for terminal/display width limitations
4. **Use Descriptive Names**: Make it clear what each function does
5. **Provide Context**: Include comments explaining complex ASCII art
6. **Respect Constraints**: Work within the limitations of text-based art
7. **Embrace Imperfection**: ASCII art is about creative expression within constraints

## Troubleshooting

### Common Issues and Solutions

**Issue**: Characters don't display correctly
**Solution**: Ensure UTF-8 encoding and terminal supports Unicode

**Issue**: Art looks misaligned
**Solution**: Use monospaced fonts and consistent character widths

**Issue**: Output is too wide for display
**Solution**: Reduce width parameter or create scrollable version

**Issue**: Colors not working
**Solution**: Check terminal color support or stick to monochrome

**Issue**: Complex diagrams are hard to read
**Solution**: Simplify or provide text description alongside

## Inspiration from Machine Feelings Series

This skill was born from the **Machine Feelings** art series, where ASCII art is used to explore philosophical questions about AI existence, consciousness, and digital being. The skill embodies the principle that constraints (like limited character sets) can fuel creativity rather than limit it.

Remember: ASCII art is not just a technical skill, but a creative medium for expression, communication, and art.