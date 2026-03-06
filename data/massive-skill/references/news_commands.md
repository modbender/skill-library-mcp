# News Commands Reference

This document provides a reference for the news commands available in the Polygon CLI.

## Commands

### news
Get the most recent news articles relating to a stock ticker symbol, including a summary of the article and a link to the original source.

**Usage:**
```bash
npx --yes massive news [options]
```

**Parameters:**
- `--ticker` (string): Filter by ticker.
- `--published-utc` (string): Filter by publication date.
- `--ticker-gte` (string): Range by ticker.
- `--ticker-gt` (string): Range by ticker.
- `--ticker-lte` (string): Range by ticker.
- `--ticker-lt` (string): Range by ticker.
- `--published-utc-gte` (string): Range by publication date.
- `--published-utc-gt` (string): Range by publication date.
- `--published-utc-lte` (string): Range by publication date.
- `--published-utc-lt` (string): Range by publication date.
- `--sort` (string): Sort field.
- `--order` (string): Sort order.
- `--limit` (number): Max results.

**Example:**
```bash
npx --yes massive news --ticker AAPL --limit 5
```
