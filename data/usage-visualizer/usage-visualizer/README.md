# Usage Visualizer

**Usage Visualizer** is a high-fidelity analytics engine for OpenClaw that transforms raw session logs into professional, actionable visual reports. It prioritizes **token usage patterns** and **model efficiency** over simple cost tracking.

![Usage Visualizer Report](assets/report-sample.png)

## ✨ Features

- **No config required!** - Automatically detects OpenClaw and Clawdbot session logs.
- **Token-First Analytics** - Deep dive into input/output tokens and Anthropic prompt caching (read/write) performance.
- **High-Res Visual Reporting** - Generates horizontal PPT-style cards with 30-day SVG trend lines and multi-dimensional charts.
- **Smart Efficiency Metrics** - Calculates cost-per-million-tokens and cache savings to optimize your model selection.
- **SQLite Persistence** - Historical data is stored locally for fast, idempotent querying.
- **Budget & Usage Guards** - Threshold-based monitoring for daily/weekly/monthly usage with flexible notification formats.
- **Multi-Provider Support** - Native support for Anthropic, OpenAI, Gemini, MiniMax, and more.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/VintLin/usage-visualizer.git
cd usage-visualizer

# Install dependencies
pip install -r requirements.txt

# Initial full sync of historical logs
python3 scripts/fetch_usage.py --full

# Generate your first visual report (Today)
python3 scripts/generate_report_image.py --today
```

## 📈 Usage Guide

### Visual Reports
The visualizer produces high-fidelity PNG images saved directly to your workspace.

```bash
# Today's report card
python3 scripts/generate_report_image.py --today

# Weekly overview
python3 scripts/generate_report_image.py --period week

# Last 30 days trend
python3 scripts/generate_report_image.py --period month
```

### Text Summaries
For a lightweight summary in the console:

```bash
# Current day summary
python3 scripts/report.py --period today

# Detailed JSON output for integrations
python3 scripts/report.py --json
```

### Budget & Usage Guards
Set limits to receive alerts when usage spikes.

```bash
# Alert if daily usage exceeds $10
python3 scripts/alert.py --budget-usd 10 --period today
```

## 📁 Project Structure

```
usage-visualizer/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── config/
│   └── config.yaml.example    # Optional config template
├── scripts/
│   ├── fetch_usage.py          # Log parser and SQLite sync engine
│   ├── calc_cost.py            # Model pricing and savings logic
│   ├── store.py                # Database interface
│   ├── report.py               # Text/JSON reporting
│   ├── html_report.py          # HTML/SVG template engine
│   ├── generate_report_image.py # PNG renderer (headless browser)
│   └── alert.py                # Monitoring and alert logic
└── assets/
    └── report-sample.png       # Sample image output
```

## 🔧 Available Commands

```bash
# Full flow: fetch + generate report
python3 scripts/fetch_usage.py --today && python3 scripts/generate_report_image.py --today

# Weekly text report
python3 scripts/report.py --period week

# Budget alerts
python3 scripts/alert.py --budget-usd 50
```

## 💾 Data Schema (SQLite)

| Field | Description |
|-------|-------------|
| `date` | ISO Date (YYYY-MM-DD) |
| `provider` | Model provider (Anthropic, OpenAI, Gemini, etc.) |
| `model` | Specific model name |
| `input_tokens` | Prompt tokens consumed |
| `output_tokens` | Completion tokens generated |
| `cache_read_tokens` | Tokens retrieved from cache (Savings applied) |
| `cost` | Total calculated cost in USD |
| `savings` | Estimated money saved via prompt caching |

## ⏰ Automation

### OpenClaw Cron Integration

Add this to your OpenClaw cron configuration:

```json
{
  "name": "usage-weekly-visual-report",
  "schedule": {"kind": "cron", "expr": "0 9 * * 1", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn", 
    "message": "Run generate_report_image.py --period week and send the resulting PNG from my workspace."
  },
  "sessionTarget": "isolated"
}
```

## 📝 Requirements

- Python 3.8+
- `html2image` (Browser-based rendering)
- `Pillow` (Smart cropping and image processing)
- `PyYAML` (Config parsing)

## 📄 License

MIT
