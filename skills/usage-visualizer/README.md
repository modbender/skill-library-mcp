# Usage Visualizer 📊

**Usage Visualizer** is a high-fidelity analytics engine for OpenClaw that transforms raw session logs into professional, actionable visual reports.

## 🛡 Security & Privacy First

- **100% Local**: All processing happens on your machine.
- **No External Calls**: This skill does NOT use webhooks or external APIs. It has zero network dependencies.
- **Privacy**: Only extracts token counts and model names. No conversation content is transmitted.
- **Native Delivery**: Reports are delivered via OpenClaw's internal message system.

## ✨ Key Features

- 📊 **High-Res Visual Reporting** - Generates horizontal PPT-style cards with 30-day SVG trend lines.
- ⚡ **Token-First Analytics** - Deep dive into input/output tokens and cache performance.
- 🔄 **Zero-Config Sync** - Auto-detects OpenClaw session logs from your workspace.
- 🎨 **Beautiful Console Output** - Clean, emoji-rich text summaries.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate your first visual report (Today)
python3 scripts/run_usage_report.py --mode image --period today
```

## 📈 Usage Guide

### Visual Reports
```bash
# Today image report
python3 scripts/run_usage_report.py --mode image --period today

# Weekly image report
python3 scripts/run_usage_report.py --mode image --period week
```

### Text Summaries
```bash
# Current day summary
python3 scripts/run_usage_report.py --mode text --period today
```

## 🛠 Project Structure

- `scripts/fetch_usage.py`: Log parser and SQLite sync engine.
- `scripts/report.py`: Text/JSON reporting.
- `scripts/generate_report_image.py`: PNG renderer (headless browser).
- `scripts/run_usage_report.py`: One-step runner for Agents.

## 📝 Prerequisites

- **Python 3.8+**
- **Chromium/Chrome**: Required for image rendering.
- **jq**: Required for shell integrations.

## 📄 License
MIT
