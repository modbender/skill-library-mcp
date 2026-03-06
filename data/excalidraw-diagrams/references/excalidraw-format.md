# Excalidraw JSON Format Reference

## File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

## Element Types

All elements share base properties, plus type-specific ones.

### Base Properties (all elements)

```
id            string    Unique ID (use 21-char alphanumeric, e.g. "aBcDeFgHiJkLmNoPqRsT1")
type          string    "rectangle"|"ellipse"|"diamond"|"text"|"arrow"|"line"|"freedraw"|"image"|"frame"
x             number    X position (canvas coords)
y             number    Y position (canvas coords)
width         number    Width in pixels
height        number    Height in pixels
angle         number    Rotation in radians (default 0)
strokeColor   string    Border/stroke color (default "#1e1e1e")
backgroundColor string  Fill color (default "transparent")
fillStyle     string    "solid"|"hachure"|"cross-hatch" (default "solid")
strokeWidth   number    1 (thin), 2 (normal), 4 (thick)
strokeStyle   string    "solid"|"dashed"|"dotted"
roughness     number    0 (architect/clean), 1 (artist), 2 (cartoonist)
opacity       number    0-100 (default 100)
groupIds      string[]  Group membership (default [])
frameId       string|null  Frame containment (default null)
roundness     object|null  { "type": 3 } for rounded corners, null for sharp
seed          number    Random seed for roughjs rendering (any integer)
version       number    Element version counter (start at 1)
versionNonce  number    Random integer
isDeleted     boolean   Soft delete flag (default false)
boundElements array|null Array of { "id": string, "type": "arrow"|"text" } or null
updated       number    Timestamp ms
link          string|null  URL link (default null)
locked        boolean   (default false)
```

### Shape Elements: rectangle, ellipse, diamond

No additional properties beyond base. Use `boundElements` to attach text labels and arrows.

### Text Element

Additional properties:
```
text          string    The displayed text
fontSize      number    Pixel size (default 20)
fontFamily    number    1 = Virgil (hand-drawn), 2 = Helvetica, 3 = Cascadia Code
textAlign     string    "left"|"center"|"right"
verticalAlign string    "top"|"middle"
containerId   string|null  ID of parent shape (for bound text)
originalText  string    Same as text (pre-edit value)
autoResize    boolean   true
lineHeight    number    1.25 (default for most fonts)
```

### Arrow and Line Elements

Additional properties:
```
points        number[][]  Array of [x, y] offsets from element origin, e.g. [[0,0],[200,0]]
startBinding  object|null  { "elementId": string, "focus": number, "gap": number, "fixedPoint": null }
endBinding    object|null  Same structure as startBinding
startArrowhead string|null  null|"arrow"|"dot"|"bar"|"triangle"
endArrowhead  string|null  Same options (arrows default: null start, "arrow" end)
lastCommittedPoint null
elbowed       boolean   false for straight/curved, true for right-angle connectors
```

`focus`: -1 to 1, controls which side of the target the arrow attaches to (0 = center).
`gap`: pixel gap between arrow endpoint and shape border (typically 1-5).

## Binding Text to Shapes

To place a label inside a shape:

1. Create the shape with `boundElements: [{ "id": "<text-id>", "type": "text" }]`
2. Create the text with `containerId: "<shape-id>"`, `textAlign: "center"`, `verticalAlign: "middle"`
3. Text x/y should be centered within the shape

## Binding Arrows to Shapes

1. Create shapes first, note their IDs
2. Create arrow with `startBinding.elementId` and `endBinding.elementId` pointing to shape IDs
3. Add arrow to each shape's `boundElements`: `{ "id": "<arrow-id>", "type": "arrow" }`
4. Arrow `points`: `[[0, 0], [dx, dy]]` where dx/dy is the offset from arrow's x/y to the endpoint

## Color Palette (recommended)

```
Blue:    stroke "#1971c2"  fill "#a5d8ff"
Green:   stroke "#2f9e44"  fill "#b2f2bb"
Red:     stroke "#e03131"  fill "#ffc9c9"
Orange:  stroke "#e8590c"  fill "#ffd8a8"
Purple:  stroke "#9c36b5"  fill "#d0bfff"
Yellow:  stroke "#e67700"  fill "#ffec99"
Gray:    stroke "#495057"  fill "#dee2e6"
Dark:    stroke "#1e1e1e"  fill "#e9ecef"
```

## Layout Guidelines

- Standard shape size: 160x80 for boxes, 120x80 for diamonds
- Spacing between elements: 80-120px horizontal, 60-100px vertical
- Arrow gap: 1-5px
- Keep diagrams within ~1200x800px canvas area
- Grid: place elements on 20px grid for alignment
- Font size: 16-20px for labels, 14px for annotations
