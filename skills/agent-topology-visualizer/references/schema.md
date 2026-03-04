# Topology JSON Schema Reference

## Full Schema

```json
{
  "title": "string (required) — diagram title",
  "theme": "dark | light (default: dark)",
  "viewBox": [width, height] (default: [1220, 1000]),
  
  "colors": {
    "accent": "#hex (default: #5d9b93)",
    "background": "#hex (default: #0a0e14)",
    "text": "#hex (default: #c8d6e0)",
    "nodeStroke": "rgba/hex (default: rgba(93,155,147,0.4))",
    "connectionHub": "rgba/hex",
    "connectionCore": "rgba/hex",
    "connectionCross": "rgba/hex"
  },
  
  "font": "string (default: Inter, system-ui, sans-serif)",
  
  "zones": {
    "zone-name": {
      "label": "string — display label",
      "bounds": [x, y, width, height] (optional — for auto-layout)
    }
  },
  
  "nodes": [
    {
      "id": "string (required) — unique identifier, lowercase with underscores",
      "name": "string (required) — display name",
      "type": "orchestrator | agent | system | pipeline | ops | human",
      "emoji": "string (optional) — emoji icon",
      "subtitle": "string (optional) — text below name",
      "position": [x, y] (optional if zone provided),
      "zone": "string (optional) — auto-layout zone name",
      "radius": "number (optional — default by type: orchestrator=58, system=44, agent=32, pipeline=25, ops=25, human=38)"
    }
  ],
  
  "connections": [
    {
      "from": "string (required) — source node id",
      "to": "string (required) — target node id",
      "type": "hub | core | cross | cluster | sys (default: core)"
    }
  ],
  
  "pipelines": {
    "pipeline-name": ["node_id_1", "node_id_2", "node_id_3"]
  }
}
```

## Node Type Defaults

| Type | Radius | Fill Opacity | Stroke Color | Glow |
|------|--------|-------------|--------------|------|
| orchestrator | 58 | 0.15 | accent | Yes, animated pulse |
| agent | 32 | 0.12 | accent | No |
| system | 44 | 0.08 | muted accent | No |
| pipeline | 25 | 0.12 | bright accent | No |
| ops | 25 | 0.06 | muted | No |
| human | 38 | 0.10 | accent | No |

## Connection Type Styles

| Type | Stroke Opacity | Stroke Width | Dash | Use |
|------|---------------|-------------|------|-----|
| hub | 0.35 | 2.0 | solid | Orchestrator ↔ major systems |
| core | 0.25 | 1.5 | solid | Orchestrator ↔ agents |
| cross | 0.18 | 1.2 | solid | Agent ↔ system data flows |
| cluster | 0.30 | 1.5 | solid | Pipeline sequential chain |
| sys | 0.15 | 1.0 | 4,4 dash | System ↔ system |

## Edge-to-Edge Math

Connections are calculated as cubic bezier curves (`M x1,y1 C cx1,cy1 cx2,cy2 x2,y2`) where start/end points are on the circle perimeter (not center). The generator:

1. Calculates the angle between node centers
2. Projects start/end points to circle edge using `(cx + r*cos(θ), cy + r*sin(θ))`
3. Computes control points perpendicular to the center line for natural curves
4. Adjusts curve intensity based on distance between nodes

## Optional Fields

- `css` (string): Custom CSS injected into the output `<style>` block. Only styles, no scripts.
- `background.stars` (bool): Enable/disable star field canvas (default: true)
- `background.starCount` (int): Number of stars (default: 150)
- `background.starColor` (string): Star fill color

## Validation Rules

- All `from`/`to` in connections must reference valid node `id`s
- All node ids in `pipelines` must exist in `nodes`
- Node `id`s must be unique
- At least one node required
- `orchestrator` type nodes limited to 3 per diagram
