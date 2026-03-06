---
name: agent-topology
description: Generate interactive SVG architecture diagrams for AI agent systems. Use when visualizing multi-agent setups, orchestration flows, data pipelines, or system topology. Produces a self-contained HTML page with hover-highlighting, tooltips, curved bezier connections, and zone-based layout. Works with any agent framework (OpenClaw, CrewAI, LangGraph, AutoGen, etc).
---

# Agent Topology

Generate interactive architecture diagrams from a JSON topology definition.

## Quick Start

1. Create a topology JSON file (see `references/schema.md` for full spec)
2. Run the generator:

```bash
python3 scripts/generate.py topology.json -o diagram.html
```

3. Output is a self-contained HTML file with embedded SVG, CSS, and JS.

## Topology JSON Format

```json
{
  "title": "My Agent System",
  "theme": "dark",
  "viewBox": [1220, 1000],
  "zones": {
    "center": { "label": "Orchestration" },
    "left": { "label": "Content Pipeline" },
    "right": { "label": "Infrastructure" }
  },
  "nodes": [
    {
      "id": "orchestrator",
      "name": "Main Agent",
      "type": "orchestrator",
      "emoji": "🤖",
      "subtitle": "Central Hub",
      "position": [610, 480],
      "radius": 58
    },
    {
      "id": "tool_agent",
      "name": "Tool Agent",
      "type": "agent",
      "emoji": "🔧",
      "subtitle": "Executes tools",
      "position": [400, 300],
      "radius": 32
    }
  ],
  "connections": [
    { "from": "orchestrator", "to": "tool_agent", "type": "core" }
  ],
  "pipelines": ["tool_agent", "processor", "output"]
}
```

### Node Types

| Type | Visual | Use for |
|------|--------|---------|
| `orchestrator` | Large glowing circle | Central agent/router |
| `agent` | Medium teal circle | Sub-agents, workers |
| `system` | Medium muted circle | External systems (DBs, APIs) |
| `pipeline` | Small bright circle | Sequential pipeline steps |
| `ops` | Small circle | Operational/maintenance agents |
| `human` | Medium circle | Human-in-the-loop nodes |

### Connection Types

| Type | Style | Use for |
|------|-------|---------|
| `hub` | Bright, thicker | Orchestrator ↔ systems |
| `core` | Medium brightness | Orchestrator ↔ agents |
| `cross` | Subtle | Agent ↔ system (data flow) |
| `cluster` | Pipeline style | Sequential chain steps |
| `sys` | Dashed subtle | System ↔ system |

### Pipelines

The `pipelines` array lists node IDs that form sequential chains. Hovering any pipeline node highlights the full chain transitively (not just direct connections).

Multiple pipelines supported:
```json
"pipelines": {
  "content": ["feed_hunter", "synthesizer", "writer", "website"],
  "deploy": ["builder", "tester", "deployer"]
}
```

## Auto-Layout Mode

If positions are omitted, the generator auto-places nodes by zone:

```json
{
  "nodes": [
    { "id": "main", "type": "orchestrator", "zone": "center" },
    { "id": "researcher", "type": "agent", "zone": "top-left" },
    { "id": "db", "type": "system", "zone": "right" }
  ]
}
```

Available zones: `center`, `top-left`, `top-right`, `left`, `right`, `bottom-left`, `bottom-right`, `bottom`.

## Theming

```json
{
  "theme": "dark",
  "colors": {
    "accent": "#5d9b93",
    "background": "#0a0e14",
    "text": "#c8d6e0",
    "nodeStroke": "rgba(93,155,147,0.4)"
  },
  "font": "Inter, system-ui, sans-serif"
}
```

Built-in themes: `dark` (default), `light`. Override any color individually.

## Output Formats

```bash
# Self-contained HTML page (default)
python3 scripts/generate.py topology.json -o diagram.html

# SVG only (for embedding)
python3 scripts/generate.py topology.json -o diagram.svg --format svg

# SVG paths only (for injection into existing page)
python3 scripts/generate.py topology.json --format paths
```

## Features

- **Edge-to-edge connections**: Lines connect at circle perimeters, not centers
- **Curved bezier paths**: All connections use smooth cubic bezier curves
- **Hover highlighting**: Hover a node to highlight its connections; dims everything else
- **Pipeline walk**: Hovering a pipeline node lights up the full sequential chain
- **Path tooltips**: Hover a connection line to see "Source → Target"
- **Mobile/tap support**: Tap works like hover with auto-dismiss
- **Responsive**: SVG scales to container width
- **Zero dependencies**: Output is a single self-contained HTML file

## Advanced

- For custom CSS injection and embedding options, see `references/customization.md`
