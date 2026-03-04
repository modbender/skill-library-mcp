---
name: fireant-stock
description: Automated Vietnamese stock price and index checking on FireAnt.vn. Use when checking current stock prices, market indices, trading volumes, or financial information for Vietnamese stocks (HOSE, HNX, UPCOM) and market indices (VNINDEX, HNX30, VN30). Accepts stock symbols like DPM, VCB, FPT, or indices like VNINDEX. Returns formatted price/index data, market statistics, and key financial metrics.
---

# FireAnt Stock Price Checker

## Overview

Automatically retrieves real-time stock information from FireAnt.vn for Vietnamese equities. Handles the full workflow from searching to data extraction and formatting.

## Quick Start

Check a single stock:
```bash
scripts/check_stock.py DPM
```

Check multiple stocks:
```bash
scripts/check_stock.py VCB FPT BID
```

## Core Workflow

1. **Search** - Uses Google search to find the FireAnt stock page for the symbol
2. **Navigate** - Opens the FireAnt stock page via Agent Browser (Rust headless browser automation)
3. **Extract** - Parses current price, volume, market cap, and key statistics from page snapshot
4. **Format** - Returns structured data in readable format

## Requirements

- **Agent Browser** - Fast Rust-based headless browser (`agent-browser` CLI must be installed)
- Python 3.x with standard libraries (sys, re, subprocess, json, typing)

## Supported Data

### For Stocks:
- **Current Price** - Real-time price with change percentage
- **Trading Data** - Volume, value, opening/high/low prices  
- **Market Metrics** - Market cap, beta, P/E ratio, reference price
- **Technical Analysis** - Moving averages (MA10, MA50)
- **Company Info** - Full company name, stock exchange listing

### For Indices (VNINDEX, HNX30, VN30, etc.):
- **Current Index** - Real-time index value with change percentage
- **Trading Data** - Total volume, matched volume, value traded
- **Foreign Trading** - NĐTNN (foreign investor) buy/sell activity and net position
- **Technical Analysis** - Moving averages (MA10, MA50)
- **Market Overview** - Reference price, opening, high/low range

## Usage Patterns

**Single stock inquiry:**
"Check giá cổ phiếu DPM"
"What's the current price of VCB?"

**Multiple stocks:**
"Compare VCB, BID, and CTG prices"
"Show me bank stocks: VCB BID CTG"

**Market indices:**
"Check VNINDEX"
"How is the market doing today?" (→ VNINDEX)
"Show me VN30 index"

**Mixed (stocks + index):**
"Check ACB, L18, AAA và VNINDEX"
"Give me tech stocks and market index: FPT VNM VNINDEX"

**Market research:**
"Find information about DPM stock on FireAnt"
"Get latest trading data for FPT"

## Scripts

### scripts/check_stock.py

Main script that automates the full stock checking workflow for one or more symbols (stocks or indices).

**Usage:** `python3 scripts/check_stock.py <SYMBOL1> [SYMBOL2] ...`

**Examples:**
```bash
# Check stocks
python3 scripts/check_stock.py ACB VCB FPT

# Check index
python3 scripts/check_stock.py VNINDEX

# Check mixed
python3 scripts/check_stock.py ACB L18 AAA VNINDEX
```

**Returns:** Formatted stock/index data including price/index value, volume, and key metrics.

**Note:** FireAnt URL format is the same for both stocks and indices: `https://fireant.vn/ma-chung-khoan/{SYMBOL}`
