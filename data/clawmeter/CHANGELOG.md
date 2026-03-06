# Changelog

All notable changes to ClawMeter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-14

### Added
- Initial release 🎉
- Real-time cost tracking dashboard
- Session log ingestion and parsing
- SQLite storage with automatic aggregation
- REST API with 7 endpoints
- Budget alerts via Telegram and email
- Support for Anthropic, OpenAI, Google, DeepSeek models
- Modern dark-mode UI with Chart.js visualizations
- Auto-watch for new session logs
- OpenClaw skill installation script
- Comprehensive documentation (README, SKILL.md)

### Features
- 📊 Dashboard with daily/weekly/monthly spend
- 💰 Accurate cost calculation with cache pricing
- 🔔 Configurable budget thresholds
- 📈 Daily cost chart (7/14/30/90 day views)
- 🎨 Model breakdown donut chart
- 📋 Top sessions and recent activity tables
- 🔄 Real-time log watching and ingestion
- 🗄️ Portable SQLite database (sql.js)

### Technical Details
- Built with Express.js, Chart.js, vanilla JavaScript
- No build step required (runs directly from source)
- Lightweight (~100 MB RAM, minimal CPU)
- Cross-platform (Linux, macOS, Windows)

---

## [Unreleased]

### Planned
- Multi-user authentication
- PostgreSQL support for large deployments
- CSV/JSON export
- Cost forecasting and predictions
- Slack/Discord webhook integrations
- Token usage heatmaps
- Model performance tracking (latency, quality)
- Mobile-responsive improvements
- Dark/light theme toggle

---

## Version History

- **0.1.0** (2026-02-14) — Initial release
