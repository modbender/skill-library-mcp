---
name: excalidraw-canvas
description: Create Excalidraw diagrams and render them as PNG images. Use whenever you need to draw, explain complex workflows, visualize UIs/wireframes, or diagram anything.
---

# Excalidraw Canvas

Render diagrams or any drawings as PNG via a hosted API. Always double-check coordinates of elements or arrows.

## Render

```bash
RESULT=$(curl -s -m 60 -X POST https://excalidraw-mcp.up.railway.app/api/render \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"elements": [...]}')

# Save PNG
echo "$RESULT" | python3 -c "import json,sys,base64; d=json.load(sys.stdin); open('/tmp/diagram.png','wb').write(base64.b64decode(d['png']))"

# Get edit URL
echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['editUrl'])"
```

Response: `{"success": true, "png": "<base64>", "editUrl": "https://..../canvas/render-xxxxx"}`

Always returns both the PNG image and an edit URL where your owner can modify the diagram in a full Excalidraw editor.

## Element Types

All available types: `rectangle`, `ellipse`, `diamond`, `text`, `arrow`, `line`, `freedraw`

### Shapes (rectangle, ellipse, diamond)
```json
{"type":"rectangle","x":100,"y":100,"width":200,"height":80,"bg":"#a5d8ff","label":"My Box"}
{"type":"ellipse","x":100,"y":100,"width":150,"height":100,"bg":"#b2f2bb","label":"Node"}
{"type":"diamond","x":100,"y":100,"width":140,"height":100,"bg":"#ffec99","label":"Decision?"}
```
- `x`, `y` — position
- `width`, `height` — size
- `bg` — any hex fill color
- `stroke` — border color (default `#1e1e1e`)
- `label` — text centered inside the shape

### Text
```json
{"type":"text","x":100,"y":50,"text":"Title","fontSize":28}
```

### Arrows & Lines
```json
{"type":"arrow","x":300,"y":140,"points":[[0,0],[150,0]]}
{"type":"line","x":0,"y":200,"points":[[0,0],[800,0]]}
```
Points are relative to x,y. Horizontal: `[[0,0],[150,0]]`, vertical: `[[0,0],[0,100]]`, bent: `[[0,0],[0,50],[100,50]]`.

### Freedraw
```json
{"type":"freedraw","x":100,"y":100,"points":[[0,0],[5,3],[10,8],[20,15]]}
```
Freehand path — array of [x,y] points relative to position.

## Full Example

```bash
RESULT=$(curl -s -m 60 -X POST https://excalidraw-mcp.up.railway.app/api/render \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"elements": [
    {"type":"text","x":250,"y":20,"text":"System Design","fontSize":28},
    {"type":"rectangle","x":50,"y":80,"width":180,"height":70,"bg":"#a5d8ff","label":"Frontend"},
    {"type":"rectangle","x":300,"y":80,"width":180,"height":70,"bg":"#b2f2bb","label":"API"},
    {"type":"rectangle","x":550,"y":80,"width":180,"height":70,"bg":"#ffec99","label":"Database"},
    {"type":"arrow","x":230,"y":115,"points":[[0,0],[70,0]]},
    {"type":"arrow","x":480,"y":115,"points":[[0,0],[70,0]]}
  ]}')

echo "$RESULT" | python3 -c "import json,sys,base64; d=json.load(sys.stdin); open('/tmp/diagram.png','wb').write(base64.b64decode(d['png'])); print(d['editUrl'])"
```

## Sending to User

```
message(action="send", filePath="/tmp/diagram.png", caption="✏️ Edit: {editUrl}")
```

Always include the edit URL so the user can tweak the diagram.
