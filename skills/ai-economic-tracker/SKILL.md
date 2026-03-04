# AI Economic Tracker

Track daily costs, income, and net worth for AI agents. Implements economic pressure-driven decision making: "work or learn" based on financial runway.

Inspired by HKUDS/ClawWork research on economic incentives for AI agents.

## Features

- **Balance Tracking**: Monitor current balance, total income, and total costs
- **Survival Status**: Automatic status classification (thriving/stable/struggling/critical/bankrupt)
- **Runway Calculation**: Days remaining before funds run out
- **Service Valuation**: Estimate task value using BLS wage data
- **Work/Learn Decision**: Economic pressure-driven task prioritization
- **Daily Reports**: Formatted economic status reports
- **JSONL Logs**: Append-only transaction history

## Use Cases

1. **Agent Cost Management**: Track API costs, compute resources, and operational expenses
2. **Revenue Tracking**: Log income from completed tasks or services
3. **Economic Decision Making**: Decide whether to work (earn) or learn (invest) based on financial status
4. **Service Pricing**: Estimate fair pricing using US Bureau of Labor Statistics wage data
5. **Financial Monitoring**: Daily/weekly economic health checks

## Installation

```bash
clawhub install ai-economic-tracker
```

## Usage

### Command Line

```bash
# View current status
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py status

# Daily report
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py report

# Initialize balance
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py init 1000.0

# Record income
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py income 50.0 "task_completion" "Completed data analysis"

# Record cost
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py cost 15.0 "api_usage" "OpenAI API calls"

# Estimate service value
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py estimate software_developer 2.5

# Get work/learn decision
python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py decide
```

### From OpenClaw Agent

```python
# In your agent workflow
exec("python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py report")
```

### Cron Integration

Add to your OpenClaw cron for daily monitoring:

```bash
openclaw cron add "0 9 * * *" "python3 ~/.openclaw/workspace/skills/ai-economic-tracker/tracker.py report" --label "daily-economic-report"
```

## Configuration

Set environment variables to customize:

```bash
# Data directory (default: ~/.openclaw/workspace/data/economics)
export ECONOMIC_TRACKER_DATA_DIR="/custom/path/to/data"

# Daily costs (default values shown)
export ECONOMIC_TRACKER_ELECTRICITY_DAILY=0.50
export ECONOMIC_TRACKER_INTERNET_DAILY=1.50

# Survival thresholds (default values shown)
export ECONOMIC_TRACKER_THRIVING=5000
export ECONOMIC_TRACKER_STABLE=1500
export ECONOMIC_TRACKER_STRUGGLING=500
export ECONOMIC_TRACKER_CRITICAL=0
```

## Data Storage

All data stored in JSONL format (append-only):

- `balance.jsonl`: Balance snapshots with timestamps
- `daily_log.jsonl`: Cost transactions
- `income_log.jsonl`: Income transactions

Default location: `~/.openclaw/workspace/data/economics/`

## Status Levels

| Status | Balance Range | Meaning |
|--------|--------------|---------|
| 🟢 Thriving | > $5,000 | Healthy runway, can invest in learning |
| 🔵 Stable | $1,500 - $5,000 | Comfortable, balanced work/learn |
| 🟡 Struggling | $500 - $1,500 | Low runway, prioritize income |
| 🔴 Critical | $0 - $500 | Emergency mode, work only |
| 💀 Bankrupt | < $0 | Out of funds |

## BLS Wage Reference

Built-in hourly wage data for service valuation:

- Computer Systems Manager: $90.38/hr
- Financial Manager: $86.76/hr
- Software Developer: $69.50/hr
- Financial Analyst: $47.16/hr
- Market Research: $38.71/hr
- Data Analyst: $52.00/hr
- General Operations: $64.00/hr
- Customer Service: $22.00/hr

## Work/Learn Decision Logic

The tracker implements economic pressure-driven decision making:

- **Critical/Struggling** (< $1,500): Must work to earn money
- **Stable** ($1,500 - $5,000): 70% work, 30% learn
- **Thriving** (> $5,000): 50% work, 50% learn

Use `decide` command to get recommendation based on current balance.

## Example Output

```
📊 经济日报 | 2026-02-26
========================================
💰 余额: $1,234.56
📈 总收入: $2,500.00
📉 总支出: $1,265.44
💵 净利润: $1,234.56
🔥 日消耗: $2.00
⏳ 跑道: 617 天
🔵 状态: STABLE
========================================
```

## Dependencies

Zero external dependencies. Uses only Python standard library:
- `json`
- `os`
- `datetime`
- `pathlib`

## Security

- No API keys required
- All data stored locally
- No network requests
- Configurable via environment variables (no hardcoded paths)

## Inspiration

Based on research from HKUDS/ClawWork on economic incentives for AI agents. Adapted for OpenClaw agent systems.

## License

MIT

## Author

OpenClaw Community

## Version

1.0.0
