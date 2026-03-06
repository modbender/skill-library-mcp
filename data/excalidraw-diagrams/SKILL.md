---
name: excalidraw-diagrams
description: Generate Excalidraw diagrams for Obsidian. Supports two output modes - Obsidian (.md for direct plugin use) and Standard (.excalidraw for excalidraw.com). Use when asked to create, draw, or diagram architecture diagrams, flowcharts, concept maps, sequence flows, system designs, or any visual diagram.
---

# Excalidraw Diagram Generator

Create Excalidraw diagrams from text content with multiple output formats compatible with Obsidian's Excalidraw plugin.

## Output Modes

The user must explicitly request a diagram. Do not generate or save files unless the user asks for one.

| Mode | When to use | File Extension | Use Case |
|------|-------------|----------------|----------|
| **Obsidian** | User asks for an Obsidian/Excalidraw diagram | `.md` | Open directly in Obsidian with Excalidraw plugin |
| **Standard** | User asks for a standard/excalidraw.com file | `.excalidraw` | Open on excalidraw.com |

If the mode is ambiguous, ask the user which format they want.

## Process

1. **Confirm output mode** with the user if ambiguous
2. **Analyze content** - identify concepts, relationships, hierarchy
3. **Choose diagram type** based on content structure
4. **Generate Excalidraw JSON** following design rules below
5. **Output in correct format** based on mode
6. **Ask the user** for the save path and filename before writing
7. **Check if file exists** at the target path. If it does, ask before overwriting
8. **Save the file** only after user confirmation

## Output Formats

### Mode 1: Obsidian Format (Default)

This format wraps the JSON in Markdown so Obsidian's Excalidraw plugin opens it directly:

```markdown
---
excalidraw-plugin: parsed
tags: [excalidraw]
---

==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==
You can decompress Drawing data with the command palette: 'Decompress current Excalidraw file'. For more info check in plugin settings under 'Saving'

# Excalidraw Data

## Text Elements
%%

## Drawing
```json
{"type":"excalidraw","version":2,"source":"https://github.com/zsviczian/obsidian-excalidraw-plugin","elements":[...],"appState":{"gridSize":null,"viewBackgroundColor":"#ffffff"},"files":{}}
```
%%
```

**Critical formatting rules:**
- Frontmatter MUST include `tags: [excalidraw]`
- The warning message must be complete
- JSON must be inside a ```json code block
- Text Elements section stays empty (just `%%`)
- Source must be `"https://github.com/zsviczian/obsidian-excalidraw-plugin"` for Obsidian mode

### Mode 2: Standard Excalidraw Format

Pure JSON for excalidraw.com:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

## Design Rules

### Typography
- **All text elements must use `"fontFamily": 5`** (Excalifont - hand-drawn style)
- **Font sizes:**
  - Titles: 24-28px (minimum 20px)
  - Subtitles: 18-20px
  - Body/labels: 16-18px (minimum 16px)
  - Annotations: 14px (use sparingly)
- **Never use font size below 14px** - unreadable at normal zoom
- Line height: `"lineHeight": 1.25` for all text
- Text alignment: `"textAlign": "center"`, `"verticalAlign": "middle"` for labels

### Layout
- **Canvas range:** Keep all elements within 0-1200 x 0-800 pixels
- **Minimum shape size:** Rectangles/ellipses with text should be at least 120x60px
- **Element spacing:** Minimum 20-30px between elements to prevent overlap
- **Padding:** Leave 50-80px padding around all edges
- **Grid:** Place elements on 20px grid for alignment

### Color Palette

**Shape fill colors (backgroundColor, fillStyle: "solid"):**

| Color | Hex | Usage |
|-------|-----|-------|
| Light Blue | `#a5d8ff` | Input, data sources, primary nodes |
| Light Green | `#b2f2bb` | Success, output, completed states |
| Light Orange | `#ffd8a8` | Warnings, pending, external dependencies |
| Light Purple | `#d0bfff` | Processing, middleware, special items |
| Light Red | `#ffc9c9` | Errors, critical alerts |
| Light Yellow | `#fff3bf` | Notes, decisions, planning |
| Light Cyan | `#c3fae8` | Storage, data, cache |
| Light Pink | `#eebefa` | Analysis, metrics, statistics |

**Text colors (strokeColor):**

| Usage | Hex | Notes |
|-------|-----|-------|
| Headings | `#1e40af` | Deep blue |
| Subtitles/connectors | `#3b82f6` | Bright blue |
| Body text | `#374151` | Dark gray (minimum `#757575` on white) |
| Emphasis | `#f59e0b` | Gold/amber |

**Contrast rules:**
- White background text: minimum `#757575` lightness
- Light fills: use dark variants (e.g., light green fill → `#15803d` text)
- Avoid light gray text (`#b0b0b0`, `#999`) on white

### Styling
- **Roughness:** `1` (artist style) for hand-drawn look, or `0` (architect) for clean diagrams
- **Stroke width:** `2` (normal) for most elements
- **Roundness:** `{ "type": 3 }` for rounded corners on rectangles
- **Opacity:** `100` for most elements, `30-50` for background layers

## Diagram Types

Choose the appropriate visualization based on content:

| Type | Best For | Layout |
|------|----------|--------|
| **Flowchart** | Step-by-step processes, workflows | Top-to-bottom or left-to-right with arrows |
| **Mind Map** | Concept expansion, brainstorming | Radial from center |
| **Hierarchy** | Org charts, system decomposition | Top-down tree structure |
| **Relationship** | Dependencies, interactions | Network with connecting lines |
| **Comparison** | A vs B analysis | Side-by-side columns |
| **Timeline** | Event progression, milestones | Horizontal time axis |
| **Matrix** | 2D categorization, priority grids | X/Y coordinate plane |
| **Architecture** | System components, data flow | Layered (frontend/middleware/backend) |

## JSON Structure

### Root Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [...],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

### Element Template

**All elements require these fields:**

```json
{
  "id": "unique-id-string",
  "type": "rectangle|ellipse|text|arrow|diamond|line",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 50,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": { "type": 3 },
  "seed": 123456789,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

**Important:**
- Use `"boundElements": null` (not `[]`)
- Use `"updated": 1` (not timestamps)
- Do NOT include `frameId`, `index`, `versionNonce`, or `rawText`

### Text Element (additional fields)

```json
{
  "type": "text",
  "text": "Label Text",
  "fontSize": 20,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": null,
  "originalText": "Label Text",
  "autoResize": true,
  "lineHeight": 1.25
}
```

### Arrow Element (additional fields)

```json
{
  "type": "arrow",
  "points": [[0, 0], [200, 0]],
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "elbowed": false
}
```

For arrows connecting shapes, use `startBinding` and `endBinding`:

```json
{
  "startBinding": { "elementId": "shape-id-1", "focus": 0, "gap": 1, "fixedPoint": null },
  "endBinding": { "elementId": "shape-id-2", "focus": 0, "gap": 1, "fixedPoint": null }
}
```

Add the arrow to each shape's `boundElements`:

```json
{
  "boundElements": [
    { "id": "arrow-id", "type": "arrow" }
  ]
}
```

### Text Centering Calculation

Text elements use left-edge x coordinate. To center text:

```
estimatedWidth = text.length * fontSize * 0.5  (use * 1.0 for CJK characters)
x = centerX - estimatedWidth / 2
```

Example: Text "Hello" (5 chars, 20px) centered at x=300:
- `estimatedWidth = 5 * 20 * 0.5 = 50`
- `x = 300 - 25 = 275`

## Common Patterns

### Architecture Diagram

- Rectangles for services/components
- Color-code by layer (frontend=blue, middleware=purple, backend=green)
- Arrows for data flow
- Group related components visually

### Flowchart

- Rectangles for process steps
- Diamonds for decision points
- Arrows showing flow direction
- Top-to-bottom or left-to-right layout

### Mind Map

- Central topic in middle
- Branches radiating outward
- Use consistent colors per branch
- Sub-branches connect to main branches

## File Naming

Suggest descriptive filenames based on content, but always confirm with the user before saving:

| Mode | Format | Example |
|------|--------|---------|
| Obsidian | `[topic].[type].md` | `system-architecture.diagram.md` |
| Standard | `[topic].[type].excalidraw` | `system-architecture.diagram.excalidraw` |

**Before writing any file:**
- Confirm the full save path and filename with the user
- If a file already exists at that path, warn the user and ask before overwriting
- Never write files silently or to assumed default paths

## Example User Messages

- "Create an Excalidraw diagram of our microservices architecture"
- "Draw a flowchart showing the CI/CD pipeline"
- "Make a mind map of machine learning concepts"
- "Generate a standard excalidraw file for this workflow" (forces .excalidraw output)

## Implementation Checklist

When generating a diagram:

1. [ ] Confirm output mode with user (Obsidian or Standard)
2. [ ] Analyze content and select diagram type
3. [ ] Plan layout (positions, connections, groupings)
4. [ ] Generate elements with:
   - [ ] Unique IDs for each element
   - [ ] `"fontFamily": 5` for all text
   - [ ] Proper colors from palette
   - [ ] Correct bindings for arrows and labels
5. [ ] Validate JSON is syntactically correct
6. [ ] Wrap in appropriate output format
7. [ ] Confirm save path and filename with user
8. [ ] Check for existing file at target path (warn if exists)
9. [ ] Save only after user confirmation
10. [ ] Report file path and usage instructions to user
