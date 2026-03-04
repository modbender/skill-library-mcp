---
name: estat-mcp
description: "Search and retrieve Japanese government statistics (人口, GDP, CPI, 貿易, 雇用) from e-Stat API — Japan's official open data portal with 3,000+ statistical tables. Population, economy, trade, employment data. Free API."
metadata: {"openclaw":{"emoji":"📈","requires":{"bins":["estat-mcp"],"env":["ESTAT_APP_ID"]},"install":[{"id":"uv","kind":"uv","package":"estat-mcp","bins":["estat-mcp"],"label":"Install estat-mcp (uv)"}],"tags":["japan","statistics","government","open-data","mcp","estat","gdp","economy"]}}
---

# e-Stat: Japanese Government Statistics API

Search and fetch official statistics from e-Stat (政府統計の総合窓口), Japan's central portal for government open data. Covers population, GDP, CPI, trade, labor, and 3,000+ statistical tables from all ministries.

## Use Cases

- Look up Japan's population by prefecture and year
- Compare CPI (消費者物価指数) trends over time
- Fetch GDP and national accounts data for economic analysis
- Retrieve trade statistics (輸出入) by commodity or country
- Access labor force survey data (完全失業率, 就業者数)

## Commands

### Search for statistics
```bash
# Search by keyword (Japanese or English)
estat-mcp search 人口
estat-mcp search "消費者物価指数" --limit 10
estat-mcp search GDP --format json
```

### Fetch statistical data
```bash
# Basic data fetch
estat-mcp data 0003410379

# With filters (area=Tokyo, year=2024)
estat-mcp data 0003410379 --cd-area 13000 --cd-time 2024000

# JSON output for programmatic use
estat-mcp data 0003410379 --limit 50 --format json
```

### Test connectivity
```bash
estat-mcp test
```

## Filter Parameters

- `--cd-tab` — Table item code (表章事項コード)
- `--cd-time` — Time code (時間軸事項コード). Example: `2024000` for 2024
- `--cd-area` — Area code (地域事項コード). Example: `13000` for Tokyo
- `--cd-cat01` — Classification code 01 (分類事項01コード)

## Common Statistics

Find table IDs via `estat-mcp search`:

| Topic | Search keyword | Examples |
|---|---|---|
| Population (人口) | `人口推計` | Total, by age, by prefecture |
| CPI (物価) | `消費者物価指数` | Monthly/annual price indices |
| GDP (国民経済計算) | `国民経済計算` | Nominal/real GDP, expenditure |
| Labor (労働) | `労働力調査` | Unemployment, employment |
| Trade (貿易) | `貿易統計` | Imports/exports by country |

## Workflow

1. `estat-mcp search <keyword>` → find statistics table ID
2. `estat-mcp data <id> --format json` → fetch data with filters
3. Analyze the JSON output

## Setup

- Requires `ESTAT_APP_ID` environment variable
- Free API key registration: https://www.e-stat.go.jp/api/api-info/use-api
- Rate limited to 1 req/sec
- Python package: `pip install estat-mcp` or `uv tool install estat-mcp`
