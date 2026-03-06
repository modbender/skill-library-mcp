---
name: weather-enhanced
displayName: Weather Trading (Enhanced)
description: Trade Polymarket weather markets using NOAA forecasts with dynamic confidence modeling and quality filtering. Use when user wants to trade temperature markets with advanced safeguards.
metadata: {"clawdbot":{"emoji":"🌡️","requires":{"env":["SIMMER_API_KEY"]},"cron":"0 */6 * * *","autostart":false}}
authors:
  - Enhanced by Claude
attribution: "Based on Simmer weather skill, enhanced with dynamic confidence and quality scoring"
version: "2.0.0"
---

# Weather Trading (Enhanced)

## CRITICAL: Autonomous Trading Skill

This skill places REAL TRADES with REAL MONEY when enabled.

Key information:
- Default State: `autostart:false` - Will NOT run automatically
- Autonomous Behavior: Runs every 6 hours when manually enabled
- Financial Risk: Can deploy $30-60/day (max $100/day with quality filter)
- No Per-Trade Review: Trades execute automatically without approval

## Installation & Security

### Credentials

Required:
- `SIMMER_API_KEY` - Trading API key from simmer.markets/dashboard

Optional (non-secret configuration):
- 6 `SIMMER_WEATHER_*` environment variables for trading parameters (see Configuration)

No other credentials needed (no wallet keys, RPC endpoints, or cloud credentials).

Optional dependency: If you install `tradejournal`, it will log trade details. Not installed by default. Inspect source code before installing.

### Installation Method

- Manual installation (no automatic scripts)
- Place files in `~/.openclaw/skills/weather-enhanced/`
- Create `.env` file with API key
- No automatic system writes

### Dependencies

```
python-dotenv>=1.0.0  # Optional
```

Clean dependency list:
- Uses built-in `urllib` (no requests library)
- No web3, telegram bot, or other unused dependencies
- Optional: `tradejournal` for trade logging (commented out in requirements.txt)

### Network Endpoints

This skill connects to 3 endpoints:

1. **api.weather.gov** (NOAA)
   - Purpose: Fetch temperature forecasts
   - Data sent: Latitude/longitude (public coordinates)
   - Data received: Weather forecasts (public data)
   - Authentication: None
   - Code location: `weather_trader_enhanced.py` line ~250-280

2. **nominatim.openstreetmap.org** (Geocoding)
   - Purpose: Convert city names to coordinates
   - Data sent: City name string (e.g., "Chicago")
   - Data received: Lat/lon coordinates
   - Authentication: None
   - Code location: `weather_trader_enhanced.py` line ~200-230

3. **api.simmer.markets** (Trading)
   - Purpose: Execute trades, read portfolio
   - Data sent: SIMMER_API_KEY (bearer token), trade orders
   - Data received: Trade confirmations, positions, balance
   - Authentication: Bearer token
   - Code location: `weather_trader_enhanced.py` line ~300-350

Note: If you install the optional `tradejournal` dependency, it may add endpoints.

### Security Guarantees

- No other network connections in code
- API key never logged to disk or console
- API key sent only to api.simmer.markets
- No tracking, analytics, or telemetry
- No data exfiltration
- All network calls visible in source (use grep to verify)

### API Key Permissions

Your `SIMMER_API_KEY` should have:
- Read portfolio (required)
- Read positions (required)
- Place trades (required)
- NO withdrawal permissions
- NO account modification permissions

Create least-privilege key:
1. Visit simmer.markets/dashboard → SDK tab
2. Create new API key
3. Select "Trading Only" if available
4. Never grant withdrawal rights
5. Store in `.env` file (git-ignored)
6. Rotate key after testing

### Configuration Storage

- `.env` file: Contains SIMMER_API_KEY (never committed)
- `config.json`: Trading parameters only (no secrets)
- No persistent logs
- All data ephemeral (console output only)

Note: Legacy variables `WALLET_PRIVATE_KEY` and `POLYGON_RPC_URL` in .env are unused (web3 removed).

## Safety Features

- Default: autostart disabled - Must manually enable
- Quality filter (60%) - Skips low-liquidity markets
- Position limits ($5) - Caps risk per trade
- Trade limits (5/run) - Maximum 5 trades every 6 hours
- Entry threshold (15%) - Only buys undervalued markets
- Exit threshold (45%) - Auto-sells at profit

## Before Enabling

DO NOT SKIP THESE STEPS

### 1. Review Source Code

```bash
# Inspect main trading logic
cat weather_trader_enhanced.py | less

# Verify network endpoints (should only find 3)
grep -n "urlopen\|Request\|http" weather_trader_enhanced.py

# Check API key usage (should only send to simmer.markets)
grep -n "api_key\|SIMMER_API_KEY" weather_trader_enhanced.py

# Check optional tradejournal usage
grep -n "tradejournal\|log_trade" weather_trader_enhanced.py
```

### 2. Understand Platform Behavior

OpenClaw metadata controls:
- `autostart:false` = Skill will NOT run on startup (safe default)
- `cron:"0 */6 * * *"` = Schedule (executes only when autostart enabled)
- Enable by editing line 5: change `autostart:false` to `autostart:true`
- Verify this method with OpenClaw docs: https://docs.openclaw.ai/
- Manual file editing prevents accidental activation
- Alternative: Run manually without enabling autostart

When enabled: Runs every 6 hours (12am, 6am, 12pm, 6pm)
When disabled: 100% inactive

### 3. Verify API Key Permissions

Check your Simmer API key:
- Can read portfolio? (required)
- Can place trades? (required)
- Can withdraw funds? (should be NO)
- Can modify account? (should be NO)

If your key has withdrawal permissions, create a new trading-only key.

### 4. Test Live Trading

```bash
# Check balance first
python scripts/status.py

# Execute live trades (start with small balance)
python weather_trader_enhanced.py --live --smart-sizing
```

- Monitor closely on simmer.markets/dashboard
- Verify trades execute correctly
- Let positions resolve (1-3 days)
- Analyze results

### 5. Enable Autonomous Trading (Optional)

Only after successful manual testing.

OpenClaw uses metadata-based activation:
- Skills enable via `autostart` field in SKILL.md
- Verify with OpenClaw docs or platform UI
- Manual editing prevents accidental activation

Steps:
1. Edit `SKILL.md` line 5 (the metadata line)
2. Change `"autostart":false` to `"autostart":true`
3. Save file
4. Restart: `openclaw restart`
5. Check logs to verify scheduled runs

Manual runs only (alternative):
```bash
python weather_trader_enhanced.py --live --smart-sizing
```
This gives full control over trade timing.

## Quick Start

```bash
# Check balance
python scripts/status.py

# Execute live trades
python weather_trader_enhanced.py --live --smart-sizing

# Optional: Dry run for testing
python weather_trader_enhanced.py --dry-run
```

## Requirements

- `SIMMER_API_KEY` from simmer.markets/dashboard → SDK tab
- USDC balance in Simmer wallet

## Configuration

Configure via environment variables or `config.json`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMMER_WEATHER_ENTRY` | 0.15 | Buy below this price |
| `SIMMER_WEATHER_EXIT` | 0.45 | Sell above this price |
| `SIMMER_WEATHER_MAX_POSITION` | 5.00 | Max USD per trade |
| `SIMMER_WEATHER_MAX_TRADES` | 5 | Max trades per run |
| `SIMMER_WEATHER_LOCATIONS` | "ALL" | Cities to target |
| `SIMMER_WEATHER_MIN_QUALITY` | 0.6 | Min market quality |

## Features

- Dynamic Confidence - Adjusts 60-90% based on forecast lead time
- Market Quality Scoring - Filters low-liquidity markets
- Smart Geocoding - Supports any US city
- Enhanced Parsing - Better temperature bucket detection
- Retry Logic - Recovers from API failures

## Commands

```bash
# Live trading
python weather_trader_enhanced.py --live --smart-sizing

# Check positions
python weather_trader_enhanced.py --positions

# View config
python weather_trader_enhanced.py --config

# Set config
python weather_trader_enhanced.py --set entry_threshold=0.20

# Optional: Dry run for testing
python weather_trader_enhanced.py --dry-run
```

## How It Works

1. Fetches NOAA forecasts for target locations
2. Discovers weather markets via Simmer API
3. Calculates edge using dynamic confidence model (adjusts 60-90% based on forecast timing)
4. Filters markets by quality score (liquidity, volume, time)
5. Executes trades when price < entry threshold
6. Auto-exits when price > exit threshold

Dynamic confidence adjusts based on lead time:
- Same day: 90%
- 1 day out: 88%
- 2 days out: 85%
- 3 days out: 80%
- 7+ days: 60%

Market quality scoring weights:
- Liquidity (40%)
- Volume (30%)
- Time to resolution (20%)
- Price extremes (10%)

Only trades markets with score ≥ 60%.

## Troubleshooting

**"SIMMER_API_KEY not set"**
Set env var or add to .env file

**"No weather markets found"**
Normal if no active markets on Polymarket

**"Position size too small"**
Increase `max_position_usd` or use `--smart-sizing`

**"Quality score too low"**
Market filtered for low liquidity/volume

## Security Checklist

Before installing, verify:

### Code Review
- [ ] Inspected `weather_trader_enhanced.py` source
- [ ] Verified 3 network endpoints (NOAA, Nominatim, Simmer)
- [ ] Confirmed API key only sent to api.simmer.markets
- [ ] No suspicious code or obfuscation

### Dependencies
- [ ] Verified `requirements.txt` has only `python-dotenv>=1.0.0`
- [ ] No unused dependencies (web3, telegram, requests removed)
- [ ] Using built-in `urllib` for HTTP
- [ ] If installing `tradejournal`, inspected source first

### Configuration
- [ ] Confirmed `autostart:false` in SKILL.md line 5
- [ ] Verified activation method with OpenClaw docs/UI
- [ ] Know how to disable
- [ ] Reviewed position limits ($5 max per trade)

### API Key Setup
- [ ] Created least-privilege Simmer API key
- [ ] Key does NOT have withdrawal permissions
- [ ] Key stored in `.env` file (local, never committed)
- [ ] Understand key can read portfolio and place trades

### Testing
- [ ] Ran `python scripts/status.py` successfully
- [ ] Executed manual trade with small balance using `--live`
- [ ] Monitored trade on simmer.markets/dashboard
- [ ] Comfortable with autonomous behavior
- [ ] Optional: Tested with `--dry-run` first

### Risk Understanding
- [ ] Understand autonomous trading risks
- [ ] Know max daily deployment (~$30-60, max $100)
- [ ] Comfortable with no per-trade approval
- [ ] Know how to stop (disable in OpenClaw or edit SKILL.md)
- [ ] Started with small balance ($50-100)

### Platform Behavior
- [ ] Confirmed OpenClaw respects `autostart:false`
- [ ] Know skill won't run until manually enabled
- [ ] Understand cron schedule (every 6 hours when enabled)
- [ ] Know how to check OpenClaw logs

If any checkbox is unchecked, DO NOT enable this skill.

## Emergency Stop

To stop immediately:

```bash
# Option 1: Disable in OpenClaw UI

# Option 2: Edit SKILL.md
# Change line 5: "autostart":false
# Then: openclaw restart

# Option 3: Stop OpenClaw entirely
openclaw stop

# Close positions manually on simmer.markets/dashboard
```

## Support

Source code is visible in `weather_trader_enhanced.py`
All network calls documented in this file
No hidden functionality or obfuscation

**Use at your own risk. This skill places real trades with real money.**
**Understand prediction markets and trading risks before use.**
