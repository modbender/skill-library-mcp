---
name: dynamic-ui
description: Render tables, charts, stats, cards, and dashboards as images using HTML templates and wkhtmltoimage.
metadata:
  openclaw:
    requires:
      bins: ["wkhtmltoimage", "jq"]
    install:
      - id: apt-wkhtmltopdf
        kind: apt
        packages: ["wkhtmltopdf", "jq", "fonts-noto-color-emoji"]
        bins: ["wkhtmltoimage", "jq"]
        label: "Install wkhtmltoimage + jq (apt)"
      - id: brew-wkhtmltopdf
        kind: brew
        packages: ["wkhtmltopdf", "jq"]
        bins: ["wkhtmltoimage", "jq"]
        label: "Install wkhtmltoimage + jq (brew)"
    installHint: |
      This skill requires wkhtmltoimage and jq. Install with:
      Ubuntu/Debian: sudo apt-get install -y wkhtmltopdf jq fonts-noto-color-emoji
      macOS: brew install wkhtmltopdf jq
---

# Dynamic UI Skill

Render dynamic visual content (tables, charts, stats, cards, dashboards) as images using HTML templates and wkhtmltoimage.

## Triggers
- "render", "visualize", "chart", "dashboard", "dynamic-ui"

## Usage

```bash
# Basic usage
./scripts/render.sh <template> --data '<json>'

# With options
./scripts/render.sh table --data '{"columns":["A","B"],"rows":[["1","2"]]}' --style dark --output out.png

# From stdin
echo '{"labels":["Q1","Q2"],"values":[100,200]}' | ./scripts/render.sh chart-bar --style modern
```

## Templates

| Template | Description | Input Schema |
|----------|-------------|--------------|
| `table` | Data tables | `{"columns": [...], "rows": [[...], ...]}` |
| `chart-bar` | Bar charts | `{"labels": [...], "values": [...], "title": "..."}` |
| `stats` | KPI cards | `{"stats": [{"label": "...", "value": "...", "change": "..."}]}` |
| `card` | Info card | `{"title": "...", "subtitle": "...", "body": "...", "status": "green\|yellow\|red"}` |
| `dashboard` | Composite | `{"title": "...", "widgets": [{"type": "stat\|table\|chart", ...}]}` |

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--data`, `--input` | JSON data (or use stdin) | - |
| `--style` | Theme: modern, dark, minimal | modern |
| `--output`, `-o` | Output path | stdout (base64) |
| `--width` | Image width in pixels | 800 |

## Themes

- **modern** — Purple/blue gradients, shadows, rounded corners
- **dark** — Dark background, light text, subtle borders
- **minimal** — Clean white, thin borders

## Examples

```bash
# Render a table
./scripts/render.sh table --data '{"columns":["Name","Score"],"rows":[["Alice","95"],["Bob","87"]]}' -o table.png

# Render a bar chart
./scripts/render.sh chart-bar --data '{"labels":["Jan","Feb","Mar"],"values":[120,150,180],"title":"Monthly Sales"}' --style dark -o chart.png

# Render stats
./scripts/render.sh stats --data '{"stats":[{"label":"Users","value":"12.5K","change":"+12%"},{"label":"Revenue","value":"$45K","change":"+8%"}]}' -o stats.png
```

## 💡 Sending Images to Users

After rendering an image, you'll typically want to send it to the user. Here's the recommended workflow:

### Recommended Workflow:
```bash
# 1. Render to ~/.openclaw/media/ (recommended path)
./scripts/render.sh table --data '...' -o ~/.openclaw/media/my-table.png

# 2. Send inline via message tool
message(action=send, filePath=/home/ubuntu/.openclaw/media/my-table.png, caption="Caption", channel=telegram, to=<user_id>)
```

### Tips:
- **Save to `~/.openclaw/media/`** — this path works reliably for inline sending
- **Use descriptive captions** — helps users understand the visual
- **Consider the context** — sometimes saving to disk is fine if the user requested it

### Example (complete flow):
```bash
# Render
echo '{"title":"My Data","columns":["A","B"],"rows":[["1","2"]]}' | \
  ./scripts/render.sh table -o ~/.openclaw/media/data.png

# Send
message(action=send, filePath=/home/ubuntu/.openclaw/media/data.png, caption="Here's your data", channel=telegram, to=USER_ID)
```

## Dependencies
- `/usr/bin/wkhtmltoimage` — HTML to image conversion
- `jq` — JSON parsing
