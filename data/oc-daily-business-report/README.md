# Daily Business Report

Automated morning briefings with weather, crypto, news, and system health.

## Features

- **Multi-Source Aggregation** — Weather, crypto, news, system stats, inspirational quotes
- **Free APIs** — No API keys required for core functionality
- **Configurable** — Set your city, preferred cryptocurrencies, news country
- **Multiple Formats** — Text, JSON, Markdown output
- **Cron-Ready** — Designed for scheduled OpenClaw execution
- **No Dependencies** — Pure Python, uses stdlib urllib

## Installation

```bash
clawhub install daily-business-report
```

## Usage

```bash
# Configure once
python scripts/report.py config --city "New York" --crypto "BTC,ETH"

# Generate daily
python scripts/report.py generate
```

## Use Cases

- **Morning briefings** — Start your day informed
- **Business dashboards** — Quick KPI overview via WhatsApp
- **Team standup prep** — Automated context before meetings
- **Client reports** — Scheduled status updates

## License

MIT

## Author

Built by OpenClaw Setup Services — Professional AI agent configuration and automation.

**Need custom business intelligence?** Contact us for tailored reporting solutions.
