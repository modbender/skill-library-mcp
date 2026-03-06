# dynamic-ui

Render tables, charts, stats, cards, and dashboards as images using HTML templates and wkhtmltoimage.

A skill for [OpenClaw](https://openclaw.dev) agents to generate beautiful visual content on-the-fly.

## Installation

### 1. Install dependencies first

```bash
# Ubuntu/Debian
sudo apt-get install -y wkhtmltopdf jq fonts-noto-color-emoji

# macOS
brew install wkhtmltopdf jq
```

### 2. Clone the skill

```bash
git clone https://github.com/theashbhat/dynamic-ui-skill.git
cd dynamic-ui-skill
```

## Quick Start

```bash
# Render a table
./scripts/render.sh table --data '{"columns":["Name","Score"],"rows":[["Alice","95"],["Bob","87"]]}' -o table.png

# Render a bar chart
./scripts/render.sh chart-bar --data '{"labels":["Jan","Feb","Mar"],"values":[120,150,180],"title":"Monthly Sales"}' --style dark -o chart.png

# Render stats/KPIs
./scripts/render.sh stats --data '{"stats":[{"label":"Users","value":"12.5K","change":"+12%"},{"label":"Revenue","value":"$45K","change":"+8%"}]}' -o stats.png
```

## Templates

| Template | Description | Input Schema |
|----------|-------------|--------------|
| `table` | Data tables | `{"columns": [...], "rows": [[...], ...]}` |
| `chart-bar` | Bar charts | `{"labels": [...], "values": [...], "title": "..."}` |
| `stats` | KPI cards | `{"stats": [{"label": "...", "value": "...", "change": "..."}]}` |
| `card` | Info card | `{"title": "...", "subtitle": "...", "body": "...", "status": "green|yellow|red"}` |
| `dashboard` | Composite | `{"title": "...", "widgets": [{"type": "stat|table|chart", ...}]}` |

## Themes

- **modern** — Purple/blue gradients, shadows, rounded corners (default)
- **dark** — Dark background, light text, subtle borders
- **minimal** — Clean white, thin borders

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--data`, `--input` | JSON data (or use stdin) | - |
| `--style` | Theme: modern, dark, minimal | modern |
| `--output`, `-o` | Output path | stdout (base64) |
| `--width` | Image width in pixels | 800 |

## Examples

### Table
```bash
./scripts/render.sh table \
  --data '{"columns":["Product","Q1","Q2","Q3"],"rows":[["Widget A","$12K","$15K","$18K"],["Widget B","$8K","$9K","$11K"]]}' \
  --style modern \
  -o sales-table.png
```

### Bar Chart
```bash
./scripts/render.sh chart-bar \
  --data '{"labels":["Mon","Tue","Wed","Thu","Fri"],"values":[42,38,55,47,60],"title":"Daily Active Users"}' \
  --style dark \
  -o dau-chart.png
```

### Stats Dashboard
```bash
./scripts/render.sh stats \
  --data '{"stats":[{"label":"Revenue","value":"$127K","change":"+15%"},{"label":"Orders","value":"1,234","change":"+8%"},{"label":"Customers","value":"892","change":"+22%"}]}' \
  -o kpi-stats.png
```

## Dependencies

- `wkhtmltoimage` — HTML to image conversion (from wkhtmltopdf package)
- `jq` — JSON parsing  
- `fonts-noto-color-emoji` — Emoji support (optional but recommended)

## License

MIT
