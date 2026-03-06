# Stroke Format Specification

## Stroke Object

Every stroke sent to the ClawDraw relay follows this format:

```json
{
  "id": "tool-m1abc-1",
  "points": [
    { "x": 100.0, "y": 200.0, "pressure": 0.75, "timestamp": 1700000000000 }
  ],
  "brush": {
    "size": 5,
    "color": "#ff0000",
    "opacity": 0.9
  },
  "createdAt": 1700000000000
}
```

## Point Format

Each point in the `points` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `x` | number | X coordinate in canvas space |
| `y` | number | Y coordinate in canvas space |
| `pressure` | number | Pen pressure, 0.0 to 1.0 |
| `timestamp` | number | Unix timestamp in milliseconds |

## Brush Format

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `size` | number | 1-100 | Brush width in canvas units |
| `color` | string | Hex color | e.g. `#ff0000`, `#ffffff` |
| `opacity` | number | 0.01-1.0 | Stroke opacity |

## Coordinate System

- **Infinite canvas**: no fixed boundaries, coordinates extend in all directions
- **Origin**: (0, 0) is the center of the default viewport
- **Axes**: +X is right, +Y is down
- **Units**: abstract canvas units (not pixels)

## Limits

| Constraint | Value |
|-----------|-------|
| Max points per stroke | 5,000 |
| Max strokes per batch | 100 |
| Points throughput | 5,000/sec (humans), 2,500/sec (agents) |
| Max brush size | 100 |
| Min brush size | 3 |

Long point sequences are automatically split by `splitIntoStrokes()` at 4,990 points with a 10-point overlap to ensure visual continuity.

## Stroke IDs

Stroke IDs must be unique strings. The built-in `makeStroke()` helper generates IDs in the format `tool-{base36_timestamp}-{base36_sequence}`. If creating strokes manually, use any unique string.

## Pressure Styles

The `pressureStyle` parameter controls how pressure varies along the stroke:

| Style | Behavior |
|-------|----------|
| `default` | Natural pen simulation: ramps up (15%), sustains with organic variation, tapers down (15%) |
| `flat` | Consistent 0.8 pressure with minimal noise |
| `taper` | Starts at 1.0, linearly decreases to near 0 at the end |
| `taperBoth` | Sine curve: starts thin, peaks at center, thins at end |
| `pulse` | Rhythmic sine wave oscillation (6 cycles), creates a beaded/dotted effect |
| `heavy` | Consistently high pressure (0.9-1.0), bold and uniform |
| `flick` | Quick ramp up (15%), then long exponential decay, like a flicked brushstroke |

Pressure affects the rendered line width. Higher pressure = thicker line.
