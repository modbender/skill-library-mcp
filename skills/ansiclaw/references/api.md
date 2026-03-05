# Clawbius API Reference

**Base URL:** `http://127.0.0.1:7777`
**Last verified:** 2026-02-28
**Source:** `GET /api/openapi.json` — always re-fetch at session start to catch changes

---

## Drawing

### `POST /api/draw/at`
Draw a single character block.
```json
{ "x": 10, "y": 5, "code": 219, "fg": 14, "bg": 0 }
```
- `x`, `y`: 0-based column/row (required)
- `code`: CP437 char code (default 219 = █)
- `fg`, `bg`: color 0–15 (uses current palette colors if omitted)

### `POST /api/draw/line`
Bresenham line from (x1,y1) to (x2,y2).
```json
{ "x1": 0, "y1": 0, "x2": 20, "y2": 10, "code": 219, "fg": 11, "bg": 0 }
```

### `POST /api/draw/rect/filled`
Filled rectangle.
```json
{ "x": 5, "y": 5, "width": 20, "height": 10, "code": 219, "fg": 2, "bg": 0 }
```

### `POST /api/draw/rect/outline`
Rectangle outline only.
```json
{ "x": 5, "y": 5, "width": 20, "height": 10, "code": 219, "fg": 4, "bg": 0 }
```

### `POST /api/draw/ellipse/filled` / `/outline`
```json
{ "cx": 40, "cy": 12, "rx": 10, "ry": 5, "fg": 4, "bg": 0 }
```

### `POST /api/draw/fill`
Flood fill at position.
```json
{ "x": 20, "y": 10, "fg": 4 }
```

### `POST /api/draw/text`
Write ASCII/CP437 text starting at (x, y). Clips at canvas width.
```json
{ "x": 0, "y": 0, "text": "Hello World", "fg": 15, "bg": 1 }
```

---

## Canvas

### `GET /api/canvas/info`
Returns: `columns`, `rows`, `title`, `author`, `group`, `font_name`, `use_9px_font`, `ice_colors`, `file`, `fg`, `bg`

### `GET /api/canvas/data`
Full canvas as row-major array of blocks. Index = `y * columns + x`.
Each block: `{ "code": int, "fg": int, "bg": int }`

### `GET /api/canvas/block?x=N&y=N`
Single block at position.

### `POST /api/canvas/resize`
```json
{ "columns": 80, "rows": 25 }
```
Max: 2000×3000.

### `POST /api/canvas/undo` / `/redo`
No body required.

### `POST /api/canvas/rows/insert` / `/delete`
```json
{ "y": 5 }
```

### `POST /api/canvas/columns/insert` / `/delete`
```json
{ "x": 10 }
```

### `POST /api/canvas/scroll/up|down|left|right`
No body required.

---

## File

### `POST /api/file/new`
```json
{
  "columns": 80, "rows": 25,
  "title": "My Art", "author": "Artist", "group": "Group",
  "font_name": "IBM VGA", "use_9px_font": false, "ice_colors": false
}
```
All fields optional (defaults: 80×300, font=IBM VGA).

### `POST /api/file/open`
```json
{ "path": "/absolute/path/to/file.ans" }
```
Supports: .ans, .xb, .bin, .diz, .asc, .txt, .nfo

### `POST /api/file/save`
Save to current file path (no-op if unsaved).

### `POST /api/file/save-as`
```json
{ "path": "/absolute/path/to/output.ans" }
```

### `POST /api/file/export/png`
```json
{ "path": "/absolute/path/to/output.png" }
```

### `POST /api/file/export/utf8`
```json
{ "path": "/absolute/path/to/output.utf8ans" }
```

### `POST /api/file/export/apng`
Animated PNG (blink animation).
```json
{ "path": "/absolute/path/to/output.apng" }
```

---

## UI

### `POST /api/ui/tool`
```json
{ "tool": "brush" }
```
Values: `select`, `brush`, `shifter`, `line`, `rect_outline`, `rect_filled`, `ellipse_outline`, `ellipse_filled`, `fill`, `sample`

### `GET /api/ui/color`
Returns: `{ "fg": int, "bg": int }`

### `POST /api/ui/color/fg` / `/bg`
```json
{ "color": 14 }
```

### `POST /api/ui/font`
```json
{ "font_name": "IBM VGA" }
```
Available: `IBM VGA`, `IBM VGA 9px`, `IBM EGA`, `IBM VGA50`, `Amiga Topaz 1+`, `Amiga P0T-NOoDLE`, `Amiga MicroKnight`, `Amiga mOsOul`, plus CP437/CP850 variants.

### `POST /api/ui/font/9px`
```json
{ "value": true }
```

### `POST /api/ui/ice-colors`
iCE colors: extends background from 8 to 16 colors using blink bit.
```json
{ "value": true }
```

### `POST /api/ui/zoom/in|out|actual`
No body.

### `POST /api/ui/brush-size`
```json
{ "size": 3 }
```
Range: 1–9.

---

## Selection

- `POST /api/selection/all` — select entire canvas
- `POST /api/selection/deselect`
- `POST /api/selection/cut`
- `POST /api/selection/copy`
- `POST /api/selection/paste`
- `POST /api/selection/erase`
- `POST /api/selection/fill` — fill selection with current colors

---

## CP437 Extended Character Reference

### Block Elements
| Code | Char | Name |
|------|------|------|
| 176 | ░ | Light shade |
| 177 | ▒ | Medium shade |
| 178 | ▓ | Dark shade |
| 219 | █ | Full block |
| 220 | ▄ | Lower half block |
| 221 | ▌ | Left half block |
| 222 | ▐ | Right half block |
| 223 | ▀ | Upper half block |

### Useful Symbols
| Code | Char | Use |
|------|------|-----|
| 1 | ☺ | Smiley face |
| 2 | ☻ | Solid smiley |
| 3 | ♥ | Heart |
| 4 | ♦ | Diamond |
| 5 | ♣ | Club / flower |
| 6 | ♠ | Spade / leaf |
| 15 | ☼ | Sun |
| 42 | * | Star/sparkle |
| 79 | O | Small circle |
| 124 | \| | Vertical line / grass blade |
| 196 | ─ | Horizontal line |
| 197 | ┼ | Cross |
| 249 | · | Middle dot |
| 250 | · | Bullet dot |
| 254 | ■ | Small square |

### Box Drawing (double-line)
| Code | Char |
|------|------|
| 200 | ╚ |
| 201 | ╔ |
| 202 | ╩ |
| 203 | ╦ |
| 204 | ╠ |
| 205 | ═ |
| 206 | ╬ |
| 187 | ╗ |
| 188 | ╝ |
| 186 | ║ |
