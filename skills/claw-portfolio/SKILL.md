---
name: claw-portfolio
description: Track stock and crypto portfolios with CLI - real-time prices, P&L, dividend tracking, multiple portfolios
homepage: https://github.com/rsoutar/claw-portfolio
metadata:
  clawdbot:
    emoji: "💰"
    requires:
      env: []
      files:
        - portfolio.ts
---

# Portfolio Tracker

A CLI tool for tracking stock and crypto portfolios with real-time prices, P&L, and dividend tracking.

## When to Use This Skill

Use this skill when you need to:
- Track stock and crypto holdings locally
- Get real-time prices and P&L
- Track dividend yields, Yield on Cost, and projected income
- View upcoming ex-dividend dates
- Manage multiple portfolios
- Export portfolio data to CSV

## Tools

This skill provides the following capabilities:

### 1. List Holdings
Show all holdings with current values and P&L.

**Command:**
```
npx tsx portfolio.ts list
```

### 2. Add Holding
Add a new stock or crypto holding.

**Command:**
```
npx tsx portfolio.ts add <symbol> <quantity> <price> <name> [type]
```

**Examples:**
```
npx tsx portfolio.ts add AAPL 10 150 "Apple Inc." stock
npx tsx portfolio.ts add BTC 0.5 45000 Bitcoin crypto
```

### 3. Sell Holding
Sell shares using FIFO (First-In-First-Out) cost basis method.

**Command:**
```
npx tsx portfolio.ts sell <symbol> <quantity> <price> [date]
```

**Examples:**
```
npx tsx portfolio.ts sell AAPL 5 180 2025-06-01
npx tsx portfolio.ts sell BTC 0.25 50000
```

### 4. Transaction History
View sell history for all holdings or a specific symbol.

**Command:**
```
npx tsx portfolio.ts history [symbol]
```

**Examples:**
```
npx tsx portfolio.ts history
npx tsx portfolio.ts history AAPL
```

### 5. P&L Summary
Show both realized and unrealized profit/loss.

**Command:**
```
npx tsx portfolio.ts pnl
```

### 6. Dividend Tracking
View detailed dividend information for stock holdings including yield, Yield on Cost (YOC), and projected annual income.

**Command:**
```
npx tsx portfolio.ts dividends
```

### 7. Dividend Summary
Show portfolio-level dividend summary: total projected income, weighted average yield, and Yield on Cost.

**Command:**
```
npx tsx portfolio.ts dividend-summary
```

**Output includes:**
- Total projected annual income
- Monthly/quarterly income estimates
- Weighted average yield across all holdings
- Portfolio Yield on Cost
- Count of dividend-paying stocks

### 8. Dividend Calendar
View upcoming ex-dividend dates for your holdings.

**Command:**
```
npx tsx portfolio.ts calendar [days]
```

**Examples:**
```
npx tsx portfolio.ts calendar       # Next 30 days
npx tsx portfolio.ts calendar 60    # Next 60 days
```

### 9. List with Dividends
The `list` command automatically fetches dividend data. Use `--no-dividends` flag to skip.

**Commands:**
```
npx tsx portfolio.ts list           # With dividend info
npx tsx portfolio.ts list --no-dividends  # Skip dividends
```

### 10. Remove Holding
Remove a holding by symbol.

**Command:**
```
npx tsx portfolio.ts remove <symbol>
```

### 11. Portfolio Value
Show total portfolio value and P&L.

**Command:**
```
npx tsx portfolio.ts value
```

### 12. Manage Portfolios
List, switch, or create portfolios.

**Commands:**
```
npx tsx portfolio.ts portfolios
npx tsx portfolio.ts switch "Portfolio Name"
npx tsx portfolio.ts create "New Portfolio"
```

**Tip:** After running `npm link`, you can use the shorter `portfolio` command instead of `npx tsx portfolio.ts`.

## Installation

First, install the required dependencies:

```bash
npm install
```

This will install all necessary packages including TypeScript runtime (tsx), Next.js, React, and other dependencies listed in package.json.

**Optional:** Link the CLI globally for easier access:
```bash
npm link
```

After linking, you can use `portfolio <command>` instead of `npx tsx portfolio.ts <command>`.

## NPM Scripts

```bash
npm run dev        # Start web UI (optional)
npm run build      # Build for production
```

## Web UI (Optional)

You can also run an optional web interface with full dividend tracking support:

```bash
npm run dev
```

Then open http://localhost:3000

**Web UI Features:**
- Real-time portfolio value and P&L tracking
- Dividend summary cards (annual income, weighted yield, YOC, upcoming dates)
- Detailed dividend breakdown table per stock
- Visual calendar of upcoming ex-dividend dates
- Interactive pie chart for portfolio allocation

## Data Storage

Portfolio data is stored locally in `data/portfolio.json`. The data file is created automatically on first run with an empty portfolio.

## Features

- Real-time stock prices via Yahoo Finance API
- Real-time crypto prices via CoinGecko API
- Multiple portfolio support
- P&L tracking per holding
- Dividend tracking (yield, YOC, projected income, ex-dates)
- CLI and optional web interface
