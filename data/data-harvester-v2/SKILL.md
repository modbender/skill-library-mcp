---
name: data-harvester-v2
description: Batch web scraping for competitor analysis, price monitoring and market research
command-dispatch: tool
command-tool: data_harvester
command-arg-mode: raw
metadata: {"openclaw": {"emoji": "🧑‍🌾", "requires": {"bins": ["python3"]}}}
---

# 🧑‍🌾 Data Harvester - Batch Scraping & Competitor Analysis

Professional-grade batch web scraping tool for competitor monitoring, price tracking, and market research.

## Features

- **Batch URL Scraping**: Process multiple URLs from file
- **Competitor Comparison**: Compare products across platforms
- **Stock Data**: Real-time stock quotes and analysis
- **Sector Trends**: Hot sectors and market trends
- **News Aggregation**: Collect news by keywords

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `stock <code>` | Query stock data | `/data-harvester stock 600519` |
| `block` | Hot market sectors | `/data-harvester block` |
| `fund` | Money flow tracking | `/data-harvester fund` |
| `news <keyword>` | News search | `/data-harvester news AI` |
| `compare <product>` | Competitor comparison | `/data-harvester compare laptop` |
| `batch <file>` | Batch URL list | `/data-harvester batch urls.txt` |
| `export <file> <format>` | Export data | `/data-harvester export data.json excel` |

## Usage Examples

### Stock Query
```
/data-harvester stock 000001
```
Returns: Real-time stock price, change %, volume

### Competitor Comparison
```
/data-harvester compare "wireless earphones"
```
Returns: Price comparison across Taobao, JD, Pinduoduo

### Sector Analysis
```
/data-harvester block
```
Returns: Top 7hot sectors with leader stocks

### Fund Flow
```
/data-harvester fund
```
Returns: Top 5 stocks with main fund inflow

## Batch Processing

Create a text file with one URL per line:
```
https://example1.com
https://example2.com
https://example3.com
```

Then run:
```
/data-harvester batch urls.txt
```

## Technical Details

- **Language**: Python 3
- **Output Formats**: JSON, CSV, Excel
- **Rate Limiting**: Configurable delay between requests

## Legal Notice

- Respect target website's robots.txt
- Use reasonable request intervals (3-5 seconds)
- For educational/research purposes only
- Commercial use requires proper authorization

