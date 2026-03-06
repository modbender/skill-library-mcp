# Deployment Guide

Complete guide to deploying the OpenClaw Trading Bot — from local testing to production VPS.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [Running Strategies](#running-strategies)
- [VPS Deployment (systemd)](#vps-deployment-systemd)
- [Docker Deployment](#docker-deployment)
- [External API Keys](#external-api-keys)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security Hardening](#security-hardening)

---

## Prerequisites

**Required:**
- Python 3.8+ (no pip dependencies — stdlib only)
- [prob.trade](https://app.prob.trade) account with API key and secret
- [probtrade](https://clawhub.ai/vlprosvirkin/prob-trade-polymarket-analytics) OpenClaw skill installed

**Optional (for specific strategies):**
- NOAA API token — for `weather_arb` strategy
- LLM API key (Anthropic or OpenAI) — for `logic_arb` strategy
- FinBERT + Twitter/Reddit API — for `sentiment` strategy

### Install probtrade skill

```bash
npx clawhub@latest install probtrade
```

Or clone manually:
```bash
git clone https://github.com/vlprosvirkin/prob-trade-polymarket-analytics.git openclaw-skill
```

---

## Local Development

### 1. Clone the repo

```bash
git clone https://github.com/vlprosvirkin/openclaw-bot-prob-trade.git
cd openclaw-bot-prob-trade
```

### 2. Set up environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
PROBTRADE_API_KEY=ptk_live_your_key_here
PROBTRADE_API_SECRET=pts_your_secret_here
```

If the probtrade skill is not in the default location (`../openclaw-skill/lib/`), set the path:
```bash
PROBTRADE_SKILL_PATH=/path/to/openclaw-skill/lib
```

### 3. Verify setup

```bash
# List available strategies
python3 scripts/bot.py strategies

# Check connection to prob.trade
python3 scripts/bot.py status

# Run a single scan (no orders)
python3 scripts/bot.py scan
```

### 4. Start the bot

```bash
# Dry run (default) — logs signals but doesn't place orders
python3 scripts/bot.py run

# Override strategy
python3 scripts/bot.py run --strategy pair_arb

# Override via environment
DRY_RUN=true STRATEGY=momentum python3 scripts/bot.py run
```

### 5. Go live

When you're confident in your strategy, disable dry run:

In `config.yaml`:
```yaml
dry_run: false
```

Or via environment:
```bash
DRY_RUN=false python3 scripts/bot.py run
```

---

## Configuration

### config.yaml

```yaml
# Strategy to run (must match a class name in lib/strategies/)
strategy: momentum

# Safety: true = log only, false = place real orders
dry_run: true

# Seconds between scan cycles (default: 300 = 5 minutes)
loop_interval_sec: 300

# Risk Management
risk:
  max_position_size: 50      # max USDC per single order
  max_total_exposure: 0.5    # max 50% of balance in positions
  stop_loss_pct: 0.20        # 20% stop-loss per position
  max_drawdown_pct: 0.30     # circuit breaker: halt at 30% portfolio loss
  max_daily_spend: 50        # max USDC spent per day
  min_balance: 10            # halt if balance drops below $10
  max_consecutive_losses: 3  # circuit breaker: halt after 3 losses in a row
  max_open_positions: 5      # max concurrent positions

# Strategy-specific parameters (passed to strategy.initialize())
strategy_params:
  order_size: 5              # USDC per order (all strategies)
  drop_threshold: -0.10      # momentum: 10% drop trigger
  take_profit: 0.10          # momentum: 10% profit target
  min_liquidity: 5000        # minimum market liquidity ($)
  min_volume_24h: 1000       # minimum 24h volume ($)
  min_yes_price: 0.10        # skip dead markets
  max_yes_price: 0.85        # skip overpriced markets
  target_sum: 0.95           # pair_arb: YES+NO threshold
```

### Environment variables

All config values can be overridden via environment:

| Variable | Description | Example |
|----------|-------------|---------|
| `PROBTRADE_API_KEY` | prob.trade API key | `ptk_live_abc123` |
| `PROBTRADE_API_SECRET` | prob.trade API secret | `pts_xyz789` |
| `PROBTRADE_SKILL_PATH` | Path to probtrade skill lib/ | `/opt/openclaw-skill/lib` |
| `DRY_RUN` | Override dry_run setting | `true` / `false` |
| `STRATEGY` | Override strategy name | `pair_arb` |
| `LOOP_INTERVAL` | Override loop interval (seconds) | `600` |
| `LLM_PROVIDER` | LLM provider for logic_arb | `anthropic` / `openai` |
| `LLM_API_KEY` | LLM API key | `sk-...` |
| `LLM_MODEL` | LLM model name | `claude-sonnet-4-20250514` |
| `NOAA_API_TOKEN` | NOAA API token for weather_arb | `abc123` |

---

## Running Strategies

### Quick reference

```bash
# See all 11 strategies
python3 scripts/bot.py strategies

# Test any strategy with a single scan
python3 scripts/bot.py scan --strategy momentum
python3 scripts/bot.py scan --strategy pair_arb
python3 scripts/bot.py scan --strategy trend_breakout
python3 scripts/bot.py scan --strategy value_investor
python3 scripts/bot.py scan --strategy whale_tracking
python3 scripts/bot.py scan --strategy expiration_timing
python3 scripts/bot.py scan --strategy market_making
python3 scripts/bot.py scan --strategy logic_arb
python3 scripts/bot.py scan --strategy weather_arb
python3 scripts/bot.py scan --strategy sentiment
python3 scripts/bot.py scan --strategy ensemble
```

### Strategy categories

**Works out of the box** (no external APIs):
- `momentum` — mean reversion on breaking markets
- `pair_arb` — YES+NO arbitrage
- `trend_breakout` — ride rising markets
- `value_investor` — buy undervalued (heuristic mode)
- `whale_tracking` — follow smart money signals
- `expiration_timing` — trade near-expiry volatility
- `market_making` — two-sided spread capture
- `ensemble` — combines multiple strategies with consensus voting

**Requires external API keys:**
- `logic_arb` — needs LLM API (Anthropic or OpenAI)
- `weather_arb` — needs NOAA API token
- `sentiment` — needs FinBERT + social media API (stub)

### Strategy-specific config examples

**Momentum (conservative):**
```yaml
strategy: momentum
strategy_params:
  drop_threshold: -0.15    # only big drops
  min_liquidity: 10000     # high liquidity only
  min_volume_24h: 5000
  order_size: 3            # small orders
```

**Pair Arbitrage (aggressive):**
```yaml
strategy: pair_arb
strategy_params:
  target_sum: 0.97         # tighter threshold
  min_liquidity: 3000
  min_volume_24h: 2000
  order_size: 10           # bigger positions
```

**Ensemble (3-strategy consensus):**
```yaml
strategy: ensemble
strategy_params:
  sub_strategies: momentum,trend_breakout,value_investor
  quorum: 0.6              # 2/3 must agree
  order_size: 5
  # params below passed to all sub-strategies too
  min_liquidity: 5000
  min_volume_24h: 3000
```

**Logic Arbitrage (with Claude):**
```yaml
strategy: logic_arb
strategy_params:
  llm_provider: anthropic
  llm_api_key: sk-ant-...        # or set LLM_API_KEY env var
  llm_model: claude-sonnet-4-20250514
  min_confidence: 0.90
  min_spread: 0.05
  search_limit: 20
  order_size: 5
```

---

## VPS Deployment (systemd)

### 1. Prepare the server

Ubuntu 22.04+ or Debian 12+ recommended. Minimum: 1 vCPU, 512MB RAM.

```bash
# Create deploy user
sudo useradd -m -s /bin/bash deploy

# Install Python (usually pre-installed)
sudo apt update
sudo apt install -y python3

# Create app directory
sudo mkdir -p /opt/openclaw-bot
sudo chown deploy:deploy /opt/openclaw-bot
```

### 2. Deploy code

```bash
# As deploy user
sudo -u deploy -i

# Clone repos
cd /opt
git clone https://github.com/vlprosvirkin/openclaw-bot-prob-trade.git openclaw-bot
git clone https://github.com/vlprosvirkin/prob-trade-polymarket-analytics.git openclaw-skill

# Or copy from local machine
# scp -r openclaw-bot-prob-trade/ user@server:/opt/openclaw-bot/
# scp -r openclaw-skill/ user@server:/opt/openclaw-skill/
```

### 3. Configure

```bash
cd /opt/openclaw-bot

# Create .env
cat > .env << 'EOF'
PROBTRADE_API_KEY=ptk_live_your_key
PROBTRADE_API_SECRET=pts_your_secret
PROBTRADE_SKILL_PATH=/opt/openclaw-skill/lib
DRY_RUN=true
EOF

# Secure .env
chmod 600 .env

# Edit config.yaml for your strategy
nano config.yaml
```

### 4. Test

```bash
cd /opt/openclaw-bot
python3 scripts/bot.py status
python3 scripts/bot.py scan
```

### 5. Install systemd service

```bash
sudo cp /opt/openclaw-bot/deploy/openclaw-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw-bot
sudo systemctl start openclaw-bot
```

### 6. Manage

```bash
# Check status
sudo systemctl status openclaw-bot

# View logs
sudo journalctl -u openclaw-bot -f

# View last 100 lines
sudo journalctl -u openclaw-bot -n 100

# Restart after config changes
sudo systemctl restart openclaw-bot

# Stop
sudo systemctl stop openclaw-bot
```

### 7. Update

```bash
cd /opt/openclaw-bot
git pull
sudo systemctl restart openclaw-bot
```

---

## Docker Deployment

### Build

The Dockerfile expects both repos at the same parent directory level:

```
parent/
├── openclaw-bot-prob-trade/    # this repo
└── openclaw-skill/             # probtrade skill
```

```bash
cd parent/
docker build -f openclaw-bot-prob-trade/deploy/Dockerfile -t openclaw-bot .
```

### Run

```bash
docker run -d \
  --name openclaw-bot \
  --restart unless-stopped \
  -e PROBTRADE_API_KEY=ptk_live_your_key \
  -e PROBTRADE_API_SECRET=pts_your_secret \
  -e DRY_RUN=true \
  openclaw-bot
```

### With custom config

```bash
docker run -d \
  --name openclaw-bot \
  --restart unless-stopped \
  -v /path/to/my-config.yaml:/app/config.yaml:ro \
  -v /path/to/.env:/app/.env:ro \
  openclaw-bot
```

### Manage

```bash
# Logs
docker logs -f openclaw-bot

# Stop
docker stop openclaw-bot

# Restart with new config
docker restart openclaw-bot

# Remove and recreate
docker rm -f openclaw-bot
docker run -d ... openclaw-bot
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"
services:
  openclaw-bot:
    build:
      context: ../
      dockerfile: openclaw-bot-prob-trade/deploy/Dockerfile
    container_name: openclaw-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./config.yaml:/app/config.yaml:ro
```

```bash
docker compose up -d
docker compose logs -f
```

---

## External API Keys

### NOAA (weather_arb strategy)

1. Go to https://www.weather.gov/documentation/services-web-api
2. Get a free API token (no registration required for basic access)
3. Add to `.env`:
   ```
   NOAA_API_TOKEN=your_token
   ```
4. Or in `config.yaml`:
   ```yaml
   strategy_params:
     noaa_api_token: your_token
   ```

**Note:** The `weather_arb` strategy includes a `_get_forecast_probability()` stub. You need to implement the NOAA API integration for your specific weather markets. See the docstring in `lib/strategies/weather_arb.py` for examples.

### LLM API (logic_arb strategy)

**Anthropic (Claude):**
1. Get API key at https://console.anthropic.com
2. Add to `.env`:
   ```
   LLM_PROVIDER=anthropic
   LLM_API_KEY=sk-ant-your-key
   LLM_MODEL=claude-sonnet-4-20250514
   ```

**OpenAI (GPT-4):**
1. Get API key at https://platform.openai.com
2. Add to `.env`:
   ```
   LLM_PROVIDER=openai
   LLM_API_KEY=sk-your-key
   LLM_MODEL=gpt-4o-mini
   ```

### Social media (sentiment strategy)

The `sentiment` strategy is a documented stub. To use it:

1. Install dependencies: `pip install transformers torch tweepy`
2. Get Twitter API bearer token at https://developer.twitter.com
3. Override `_analyze_sentiment()` in a subclass — see docstring in `lib/strategies/sentiment.py` for FinBERT + Twitter example

---

## Monitoring

### Log output

All logging goes to stdout/stderr. In production:

```bash
# systemd: journald
sudo journalctl -u openclaw-bot -f

# Docker
docker logs -f openclaw-bot

# Filter by level
sudo journalctl -u openclaw-bot -p warning
```

### Key log messages to watch

```
# Normal operation
Engine started [DRY RUN] — interval 300s
Balance: $45.00 | Positions: 2 | Orders: 1
Strategy produced 3 signal(s)
Cycle done: 3 signals, 2 orders placed

# Risk limits hit
Trading blocked: Daily spend $50.00 >= limit $50.00
Signal rejected: Amount $10.00 > max position $5.00

# Circuit breaker
CIRCUIT BREAKER: 3 consecutive losses
Trading blocked: Max drawdown 31.2% >= 30.0% — CIRCUIT BREAKER
```

### Health check

Create a simple health check script:

```bash
#!/bin/bash
# health-check.sh
STATUS=$(python3 /opt/openclaw-bot/scripts/bot.py status 2>/dev/null)
if echo "$STATUS" | grep -q '"trading_ready": true'; then
    echo "OK"
    exit 0
else
    echo "UNHEALTHY: $STATUS"
    exit 1
fi
```

### Cron-based restart on failure

```bash
# /etc/cron.d/openclaw-bot-watchdog
*/5 * * * * root systemctl is-active openclaw-bot || systemctl restart openclaw-bot
```

---

## Troubleshooting

### "Could not fetch trading state"

**Cause:** Cannot connect to prob.trade API.

**Fix:**
1. Check API keys in `.env`: `PROBTRADE_API_KEY` and `PROBTRADE_API_SECRET`
2. Check probtrade skill path: `PROBTRADE_SKILL_PATH`
3. Test manually: `python3 scripts/bot.py status`

### "Trading not ready (wallet not set up)"

**Cause:** prob.trade wallet is not fully set up.

**Fix:**
1. Go to [app.prob.trade](https://app.prob.trade)
2. Complete wallet setup (deposit USDC)
3. Verify at **Settings > API Keys** that the key is active

### "Strategy 'X' not found"

**Cause:** Strategy name in config doesn't match any class in `lib/strategies/`.

**Fix:**
1. Run `python3 scripts/bot.py strategies` to see available names
2. Check that your strategy file has `name = "your_name"` matching what you put in config
3. Check for import errors: `python3 -c "from lib.strategies import list_strategies; print(list_strategies())"`

### "No signals found"

**Cause:** Strategy filters are too strict, or no markets match criteria.

**Fix:**
1. Lower thresholds in `config.yaml`:
   - `drop_threshold: -0.05` (momentum)
   - `min_liquidity: 1000`
   - `min_volume_24h: 500`
2. Check if markets are available: `python3 scripts/bot.py scan`

### Circuit breaker activated

**Cause:** Hit `max_consecutive_losses` or `max_drawdown_pct`.

**Fix:**
1. Check logs: `journalctl -u openclaw-bot | grep "CIRCUIT BREAKER"`
2. Review strategy performance
3. Restart the bot to reset circuit breaker:
   ```bash
   sudo systemctl restart openclaw-bot
   ```
4. Consider adjusting risk limits or switching strategy

### "No LLM API key configured" (logic_arb)

**Fix:** Set environment variables:
```bash
export LLM_PROVIDER=anthropic
export LLM_API_KEY=sk-ant-your-key
```

### Python version issues

```bash
python3 --version  # Need 3.8+
```

If your system has an older Python, install a newer version:
```bash
# Ubuntu/Debian
sudo apt install python3.11

# Use specific version
python3.11 scripts/bot.py run
```

### Permission denied on .env

```bash
chmod 600 /opt/openclaw-bot/.env
chown deploy:deploy /opt/openclaw-bot/.env
```

---

## Security Hardening

### API key protection

- Never commit `.env` files (already in `.gitignore`)
- Set strict permissions: `chmod 600 .env`
- Use environment variables instead of config file for secrets
- Rotate API keys periodically at [app.prob.trade](https://app.prob.trade)

### systemd hardening

The included service file (`deploy/openclaw-bot.service`) already applies:

- `NoNewPrivileges=yes` — prevents privilege escalation
- `ProtectSystem=strict` — read-only filesystem except allowed paths
- `ReadWritePaths=/opt/openclaw-bot/logs` — only logs dir is writable
- Runs as `deploy` user (not root)

### Network security

- The bot only makes outbound HTTPS connections to prob.trade
- No incoming ports need to be opened
- Consider using a firewall to restrict outbound traffic:
  ```bash
  # Allow only prob.trade API
  sudo ufw default deny outgoing
  sudo ufw allow out to any port 443
  sudo ufw enable
  ```

### Docker security

```bash
# Run as non-root
docker run --user 1000:1000 ...

# Read-only filesystem
docker run --read-only --tmpfs /tmp ...

# Drop all capabilities
docker run --cap-drop ALL ...

# No network except what's needed
docker run --network=bridge ...
```

### Dry run first

Always start with `dry_run: true` on a new deployment. Monitor logs for at least 24 hours before switching to live trading.

### Start small

Begin with small order sizes and strict risk limits:
```yaml
risk:
  max_position_size: 5       # $5 per order
  max_daily_spend: 10        # $10/day max
  max_open_positions: 2      # only 2 positions
strategy_params:
  order_size: 2              # $2 per trade
```

Scale up gradually as you gain confidence in the strategy.
