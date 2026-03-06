---
name: tdnet-disclosure-mcp
description: "Access TDNET timely disclosures (適時開示) from Tokyo Stock Exchange (JPX/TSE) — earnings reports (決算短信), dividends, buybacks, forecast revisions, governance changes. Search by company, stock code, date. Japan stock market corporate announcements. No API key required."
metadata: {"openclaw":{"emoji":"📋","requires":{"bins":["tdnet-disclosure-mcp"]},"install":[{"id":"uv","kind":"uv","package":"tdnet-disclosure-mcp","bins":["tdnet-disclosure-mcp"],"label":"Install tdnet-disclosure-mcp (uv)"}],"tags":["japan","finance","tdnet","disclosure","earnings","stock","jpx","tse","mcp"]}}
---

# TDNET Disclosure: Tokyo Stock Exchange Timely Disclosures

Access TDNET timely disclosures (適時開示) from Tokyo Stock Exchange listed companies via the Yanoshin Web API. Get earnings, dividends, buybacks, M&A, and other corporate announcements.

**No API key required** — uses the free Yanoshin Web API which mirrors TDNET data.

## Use Cases

- Monitor latest corporate disclosures from TSE-listed companies
- Get earnings announcements (決算短信) for specific companies
- Search disclosures by company name, code, or keyword
- Track dividends, buybacks, and forecast revisions
- Get disclosures by date or date range

## Commands

### Get latest disclosures
```bash
# Default: last 50 disclosures
tdnet-disclosure-mcp latest

# With limit
tdnet-disclosure-mcp latest --limit 20

# JSON output
tdnet-disclosure-mcp latest --json-output
```

### Search disclosures
```bash
# By company name
tdnet-disclosure-mcp search トヨタ

# By keyword
tdnet-disclosure-mcp search 決算短信

# JSON output
tdnet-disclosure-mcp search ソニー --json-output
```

### Get company disclosures
```bash
# By stock code
tdnet-disclosure-mcp company 7203
tdnet-disclosure-mcp company 6758 --json-output
```

### Get disclosures by date
```bash
tdnet-disclosure-mcp by-date 2026-02-14
tdnet-disclosure-mcp by-date 2026-02-14 --json-output
```

### Test connectivity
```bash
tdnet-disclosure-mcp test
```

## Disclosure Categories

| Category | Japanese | Examples |
|---|---|---|
| earnings | 決算短信 | Quarterly/annual earnings |
| dividend | 配当 | Dividend announcements |
| forecast_revision | 業績予想修正 | Earnings forecast revisions |
| buyback | 自己株式 | Share buybacks |
| offering | 新株/増資 | New share offerings |
| governance | 役員/取締役 | Board changes |
| other | その他 | Other disclosures |

## Workflow

1. `tdnet-disclosure-mcp latest` → browse recent disclosures
2. `tdnet-disclosure-mcp search <company>` → find specific company
3. `tdnet-disclosure-mcp company <code>` → get all disclosures for a company
4. `tdnet-disclosure-mcp by-date <date>` → get disclosures for a specific date

## Setup

- No API key required
- Python package: `pip install tdnet-disclosure-mcp` or `uv tool install tdnet-disclosure-mcp`
- Data source: Yanoshin Web API (mirrors TDNET data)
