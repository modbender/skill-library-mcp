---
name: serpapi-flights
description: Query Google Flights via SerpApi for flight schedules, prices, and cabin class info. Use when user asks about flight/机票/航班 prices, schedules, or comparisons.
metadata: {"openclaw":{"emoji":"✈️","requires":{"bins":["node"],"env":["SERPAPI_KEY"]}}}
---

# SerpApi Flights (Google Flights)

Query real-time flight data from Google Flights via SerpApi. Returns airline, flight number, times, prices, aircraft type, and cabin class info.

## Setup

```bash
export SERPAPI_KEY=your_api_key
```

Free tier: 100 searches/month at serpapi.com

## Query Flights

```bash
node {baseDir}/scripts/query.mjs <FROM> <TO> [-d YYYY-MM-DD] [options]
```

FROM/TO can be IATA codes (HKG, PVG) or Chinese city names (香港, 上海).

### Examples

```bash
# Basic query
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25

# Business class
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 -c 3

# All cabin classes (economy + business)
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 --all

# Direct flights only
node {baseDir}/scripts/query.mjs 香港 上海 -d 2026-02-25 --direct

# Round trip
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 -r 2026-03-01

# JSON output
node {baseDir}/scripts/query.mjs HKG PVG -d 2026-02-25 --json
```

### Options

- `-d, --date <YYYY-MM-DD>`: Departure date (default: today)
- `-r, --return <YYYY-MM-DD>`: Return date (makes it round-trip)
- `-c, --class <1-4>`: 1=economy, 2=premium economy, 3=business, 4=first
- `--all`: Query economy + business together
- `-a, --adults <n>`: Passengers (default: 1)
- `--direct`: Non-stop flights only
- `--currency <code>`: Currency (default: CNY)
- `--json`: Raw JSON output

### Output Columns

| Column | Meaning |
|--------|---------|
| 航空公司 | Airline name |
| 航班号 | Flight number |
| 出发→到达 | Departure → arrival time (+1 = next day) |
| 飞行时间 | Total duration |
| 经停 | Non-stop or number of stops |
| 价格 | Price in specified currency |
| 机型 | Aircraft type |
| 延误 | ⚠️ = often delayed >30min |

### Supported Cities (Chinese)

北京 上海 广州 深圳 成都 重庆 杭州 南京 武汉 西安 长沙 昆明 厦门 青岛 大连 天津 郑州 沈阳 哈尔滨 海口 三亚 贵阳 南宁 福州 济南 合肥 太原 乌鲁木齐 兰州 珠海 温州 宁波 无锡 揭阳/潮汕/汕头 香港 澳门 台北

## Notes

- Prices from Google Flights, may differ from airline direct prices
- No seat availability/remaining tickets (Google Flights limitation)
- Some flights show "待查" price when Google doesn't have pricing
- ⚠️ delay indicator based on historical data
