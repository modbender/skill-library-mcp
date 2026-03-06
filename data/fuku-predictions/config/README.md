# Configuration Directory

This directory contains your Kalshi Autopilot trading strategy configuration.

## Setup

1. **Copy the template:**
   ```bash
   cp default-config.json config.json
   ```

2. **Edit config.json** to match your preferences

3. **Run setup wizard** for guided configuration:
   ```bash
   cd ../scripts && python setup.py
   ```

## Configuration Files

- `default-config.json` - Template with all options and comments
- `config.json` - Your active configuration (created by setup or manual copy)

## Key Settings

**Strategy:** Choose your trading approach
- `model_follower` - Balanced, all sports (default)
- `spread_sniper` - Focus on basketball spreads  
- `totals_specialist` - Focus on over/under markets
- `contrarian` - Fade public favorites
- `conservative` - Only strongest edges
- `custom` - Define your own parameters

**Risk Management:**
- `max_daily_loss_pct` - Stop trading if daily loss exceeds this %
- `max_open_positions` - Limit number of simultaneous bets
- `max_daily_bets` - Prevent overtrading

**Position Sizing:**
- `flat_pct` - Fixed % of bankroll per bet (recommended for most users)
- `flat_amount` - Fixed dollar amount per bet
- `kelly` - Kelly criterion sizing (advanced)

**Safety Features:**
- `dry_run: true` - No real trades, just logging (start here!)
- `auto_trade: false` - Require manual approval for each trade

## Quick Start Config

For beginners, use these safe settings:
```json
{
  "strategy": "conservative",
  "sports": ["cbb"],
  "min_edge_pct": 5.0,
  "sizing": {
    "method": "flat_pct",
    "flat_pct": 1.0
  },
  "risk": {
    "max_daily_loss_pct": 3.0,
    "max_open_positions": 3,
    "max_daily_bets": 3
  },
  "dry_run": true,
  "auto_trade": false
}
```

**Remember:** Always start in dry run mode to test your strategy!