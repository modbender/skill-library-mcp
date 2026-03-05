---
name: openclaw-ecommerce
description: E-commerce price monitoring, order tracking, and margin analysis for OpenClaw agents. Track product prices, get alerts on drops, manage orders, and calculate real margins after fees.
---

# OpenClaw E-commerce Skill

A local-first e-commerce toolkit that helps you monitor product prices, track orders, calculate margins, and get alerts when prices drop below your target.

## Commands

```bash
# Product Watchlist
ecom watch add "AirPods Pro" --url "https://example.com/product" --target 149.99
ecom watch list
ecom watch remove <id>

# Price Tracking
ecom price update <product-id> 139.99
ecom price history <product-id>

# Order Management
ecom order add "Bulk T-Shirts" --cost 250 --tracking "1Z999AA10123456784"
ecom order list
ecom order status <id>

# Margin Calculator
ecom margin --cost 10 --sell 25 --fees 15

# Alerts
ecom alert list --pending
ecom alert clear <id>
```

## Features
- **Price Watchlists** — Add products with target prices, get alerted when they drop
- **Price History** — Track price changes over time per product
- **Order Tracking** — Log orders with cost, tracking numbers, and status
- **Margin Calculator** — Calculate real profit margins after platform fees, shipping, and costs
- **Alert System** — Automatic alerts when watched prices hit your target
- **Interchange Files** — Publishes product and alert data as .md files for other agents to consume

## Architecture
- SQLite database (WAL mode) for all product, price, order, and alert data
- Generic price scraper (no API keys required for v1)
- Interchange .md files generated via `@openclaw/interchange` shared library
- `ops/` directory for shareable capability data, `state/` for private runtime data

## Installation

```bash
cd skills/ecommerce
npm install
```

## Use Cases
- Monitor competitor pricing for your products
- Track cost-of-goods for dropshipping or POD businesses
- Calculate break-even prices including all fees
- Get notified when raw materials or supplies drop in price
- Keep an audit trail of all orders and shipments
