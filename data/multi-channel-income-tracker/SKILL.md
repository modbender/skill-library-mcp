---
name: Multi-Channel Income Tracker
description: Track income from multiple sources (GitHub bounties, ClawHub,
  toku.agency, trading, etc.) with automatic categorization and ROI analysis.
---

# Multi-Channel Income Tracker

Track income from multiple sources (GitHub bounties, ClawHub, toku.agency, trading, etc.) with automatic categorization and ROI analysis.

## Features

- Multi-source income tracking
- Automatic categorization
- ROI calculation per channel
- Daily/weekly/monthly reports
- Goal tracking
- Channel performance comparison

## Installation

```bash
clawhub install multi-channel-income-tracker
```

## Usage

```bash
# Add income
node tracker.js income --source "toku.agency" --amount 50 --description "Code review service"

# Add expense
node tracker.js expense --category "api" --amount 2 --description "OpenAI API"

# View report
node tracker.js report --period "week"

# Channel comparison
node tracker.js channels
```

## Supported Channels

- GitHub Bounties
- ClawHub Skills
- toku.agency
- Fiverr
- Trading
- Medium/YouTube
- Consulting
- Custom channels

## Reports

- Income by channel
- ROI per channel
- Trend analysis
- Goal progress
- Cost breakdown

## License

MIT
