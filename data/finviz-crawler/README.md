# finviz-crawler

A continuous financial news crawler that scrapes headlines and articles from [Finviz](https://finviz.com), stores them in SQLite, and provides a query interface.

Powers the **📰 Market News** app in [PrivateApp](https://github.com/camopel/PrivateApp).

## Install

```bash
python3 scripts/install.py
```

This will:
- Install Python dependencies (`crawl4ai`, `feedparser`)
- Create data directory at `~/workspace/finviz/`
- Set up a SQLite database with default tickers
- Create a background service (systemd on Linux, launchd on macOS)

## Usage

### Run the crawler

```bash
# Crawl once
python3 scripts/finviz_crawler.py

# Crawl and delete articles older than 30 days
python3 scripts/finviz_crawler.py --expiry-days 30
```

### Query articles

```bash
# List tickers being tracked
python3 scripts/finviz_query.py --list-tickers

# Recent headlines (last 24h)
python3 scripts/finviz_query.py --hours 24 --titles-only

# Add/remove tickers
python3 scripts/finviz_query.py --add-ticker NVDA:nvidia,jensen
python3 scripts/finviz_query.py --remove-ticker MSFT

# Output JSON
python3 scripts/finviz_query.py --hours 48 --format json
```

## Default Tickers

The installer seeds these tickers by default:

| Symbol | Keywords |
|--------|----------|
| QQQ | qqq, nasdaq |
| AMZN | amazon, amzn, aws |
| GOOGL | google, googl, alphabet |
| TSLA | tesla, tsla, elon musk |
| META | meta, facebook, zuckerberg |
| NVDA | nvidia, nvda, jensen |

Add your own with `--add-ticker SYMBOL:keyword1,keyword2`.

## Data

Articles are stored in `~/workspace/finviz/`:
- `finviz.db` — SQLite database (articles, tickers, settings)
- `articles/` — Full article text as Markdown files
- `finviz_settings.db` — Ticker and keyword configuration

## Background Service

The installer creates a service that runs the crawler continuously (restarts on failure):

```bash
# Linux
systemctl --user status finviz-crawler
systemctl --user start finviz-crawler
journalctl --user -u finviz-crawler -f

# macOS
launchctl list | grep finviz
```

## Requirements

- Python 3.10+
- ~512MB RAM, ~1GB disk per 10K articles
- macOS or Linux

## License

MIT
