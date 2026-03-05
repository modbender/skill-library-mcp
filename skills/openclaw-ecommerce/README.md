# openclaw-ecommerce

[![Tests](https://img.shields.io/badge/tests-13%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> E-commerce price monitoring, order tracking, and margin analysis.

Watch product prices across the web, get alerts when they drop, track your orders, and calculate margins — all from a single CLI. Built on SQLite for zero-dependency local operation.

## Features

- **Product watchlist** — track products by URL with target prices
- **Price history** — record and review price changes over time
- **Price alerts** — automatic alerts when prices hit targets
- **Order tracking** — manage orders with status and tracking numbers
- **Margin calculator** — compute profit, margin percentage, and fees
- **Interchange output** — publish price and alert data as `.md` files
- **Backup & restore** — full database backup and recovery

## Quick Start

```bash
cd skills/ecommerce
npm install

# Watch a product
node src/cli.js watch add "MacBook Air M4" --url https://apple.com/macbook-air --target 999

# Update price and check history
node src/cli.js price update 1 1099
node src/cli.js price history 1

# Track an order
node src/cli.js order add "MacBook Air M4" --tracking 1Z999AA10123456784

# Calculate margins
node src/cli.js margin --cost 750 --sell 1099 --fees 3
```

## CLI Reference

### Product Watchlist

```bash
ecom watch add <name> --url <url> [--target <price>]
ecom watch list
ecom watch remove <id>
```

### Price Tracking

```bash
ecom price history <product-id>
ecom price update <product-id> <new-price>
```

### Order Management

```bash
ecom order add <name> [--tracking <number>]
ecom order list [--status <status>]
ecom order update <id> [--status <status>] [--tracking <number>]
```

### Margin Calculator

```bash
ecom margin --cost <cost> --sell <sell> [--fees <percentage>]
```

### Alerts

```bash
ecom alert list [--pending]
ecom alert ack <id>
```

### Utilities

```bash
ecom refresh              # Regenerate interchange .md files
```

## Architecture

SQLite database (`data/`) stores products, price history, orders, and alerts. Price updates automatically create history entries and trigger alert checks against target prices. No external APIs required for core functionality.

## .md Interchange

Running `ecom refresh` generates `.md` files with current watchlist status, pending alerts, and price trends. Other agents can monitor these via `@openclaw/interchange` to act on price drops or alert conditions.

## Testing

```bash
npm test
```

13 tests covering product CRUD, price tracking, alert generation, order management, margin calculation, and interchange output.

## Part of the OpenClaw Ecosystem

E-commerce publishes price alerts and watchlist data via `@openclaw/interchange`. The `orchestration` skill can queue tasks based on price alerts, and `monitoring` can track scraping success rates.

## License

MIT
