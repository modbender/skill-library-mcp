# ShipStation Order Monitor

OpenClaw skill for monitoring ShipStation orders and detecting issues.

## Quick Start

```bash
# 1. Copy .env.example to .env and add your credentials
cp .env.example .env

# 2. Edit .env with your ShipStation API key + secret

# 3. Test it
node check-orders.js
```

See [SKILL.md](SKILL.md) for full documentation.

## What It Does

- Monitors orders from all your connected marketplaces (Amazon, Etsy, Shopify, TikTok, etc.)
- Alerts you about new orders
- Flags orders stuck in processing (>48h)
- Detects orders on hold
- Alerts on expedited / second-day / priority orders
- Tracks state to avoid duplicate notifications

## Scripts

- `check-orders.js` → order intake + issue detection
- `check-shipping.js` → expedited shipping alert detection

## Install via ClawHub

```bash
clawhub install shipstation-orders
```

## License

MIT
