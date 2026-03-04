# mcporter-railway-query

An OpenClaw skill for querying Chinese railway tickets via 12306 using mcporter CLI.

## Overview

This skill provides tools to search for G/D/C train tickets, check train schedules, query seat availability, and plan rail travel between Chinese cities. It supports filtering by date, time range, train type, and sorting results.

## Project Structure

mcporter-railway-query/
├── scripts/              # Shell helper scripts
├── references/           # Station code reference
├── README.md
├── README_zh.md
└── LICENSE

## Prerequisites

1. Install mcporter CLI: `npm install -g mcporter`
2. Configure 12306 MCP server in `~/.mcporter/mcporter.json`
    ```
      {
        "mcpServers": {
           "12306": {
              "type": "sse",
               "url": "http://127.0.0.1:8080/sse",
              "name": "12306 高铁动车查询",
              "description": "查询高铁（G开头）和动车（D开头）余票，支持出发站、到达站、日期、时间段过滤。只返回G/D车次。",
              "enabled": true
            }
        }
     }
    ```
3. Ensure MCP server is running

## Installation

This is an OpenClaw skill. Install using:

```bash
openclaw skills install mcporter-railway-query.skill
```

## Usage

The skill provides several helper scripts:

### Query afternoon trains (12:00-18:00)
```bash
./scripts/query-afternoon.sh 2026-02-18 SHH KYH
```

### Query all-day trains
```bash
./scripts/query-tickets.sh 2026-02-18 AOH HZH
```

### Get station codes
```bash
./scripts/get-station-code.sh "上海虹桥"
```

### Direct mcporter commands
```bash
mcporter call 12306.get-tickets \
  date="2026-02-18" \
  fromStation="AOH" \
  toStation="HZH" \
  trainFilterFlags="GD" \
  earliestStartTime=12 \
  latestStartTime=18 \
  sortFlag="startTime" \
  --config ~/.mcporter/mcporter.json
```

## Features

- Query train tickets with departure time filtering
- Support for G (high-speed), D (bullet train), and C (city train) trains
- Seat availability checking (商务座, 一等座, 二等座, etc.)
- Station code lookup
- Comprehensive station code reference table

## Common Station Codes

| Station | Code | Notes |
|---------|------|-------|
| 上海 | SHH | Shanghai Station |
| 上海虹桥 | AOH | Shanghai Hongqiao Station |
| 杭州东 | HZH | Hangzhou East Station |
| 江阴 | KYH | Jiangyin Station |

See `references/station-codes.md` for the complete list.

## License

MIT

## Security & Compliance

This project is a read-only OpenClaw skill that:

- Does NOT collect user data
- Does NOT store credentials
- Does NOT perform ticket booking
- Does NOT bypass 12306 authentication
- Does NOT execute arbitrary system commands
- Does NOT write to local file system
- Does NOT open network listeners
- Does NOT include obfuscated or encrypted code

All queries are executed through official 12306 MCP interfaces configured by the user.

This repository contains only helper scripts and configuration examples.