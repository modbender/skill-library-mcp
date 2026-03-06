# animate.json Reference

Every oanim project has an `animate.json` at the root that configures rendering.

## Schema

```json
{
  "name": "My Video",
  "compositionId": "MyComp",
  "render": {
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "codec": "h264",
    "crf": 18
  },
  "props": {}
}
```

## Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | required | Human-readable name |
| `compositionId` | string | required | Must match `<Composition id="...">` in Root.tsx |
| `render.fps` | number | 30 | Frames per second |
| `render.width` | number | 1920 | Video width in px |
| `render.height` | number | 1080 | Video height in px |
| `render.codec` | string | "h264" | One of: h264, h265, vp8, vp9 |
| `render.crf` | number | 18 | Constant Rate Factor (lower = higher quality, bigger file) |
| `props` | object | {} | inputProps passed to the composition |

## Common presets

### 1080p (default)
```json
{ "width": 1920, "height": 1080, "fps": 30 }
```

### 4K
```json
{ "width": 3840, "height": 2160, "fps": 30 }
```

### Vertical (Reels/TikTok)
```json
{ "width": 1080, "height": 1920, "fps": 30 }
```

### Square (Instagram)
```json
{ "width": 1080, "height": 1080, "fps": 30 }
```

## CLI overrides

All render settings can be overridden via CLI flags:
```bash
oanim render --fps 60 --res 3840x2160 --codec h265 --out out/4k.mp4
```
