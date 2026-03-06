---
name: variflight
description: Query flight information, train tickets, and travel data using Variflight (飞常准) HTTP API. Use when the user needs to (1) search flights by route or flight number, (2) check flight status and punctuality, (3) find train tickets, (4) get airport weather forecasts, (5) check flight prices, (6) plan multi-modal trips (flight+train), or (7) get flight comfort metrics (happiness index).
---

# Variflight HTTP API Tool

Official Variflight Agent Skills enabling AI assistants to retrieve flight and railway data via zero-dependency tools.

## API Endpoint

- **Base URL:** `https://ai.variflight.com/api/v1/mcp/data`
- **Method:** POST
- **Header:** `X-VARIFLIGHT-KEY: your_api_key`
- **Content-Type:** `application/json`

## Configuration

支持多种配置方式（按优先级排序）：

### 1. 环境变量（推荐用于 CI/CD）

```bash
export VARIFLIGHT_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

### 2. 配置文件

按以下顺序查找（找到即停止）：
- `./.variflight.json`（项目级配置）
- `~/.variflight.json`（用户级配置）
- `~/.config/variflight/config.json`（XDG 标准）

配置格式：
```json
{
  "api_key": "sk-xxxxxxxxxxxxxxxx"
}
```

### 3. 命令行参数

```bash
./flights.sh --api-key sk-xxxx PEK SHA 2025-02-15
```

## Quick Start

### Installation

```bash
# Clone or copy the skill
git clone https://github.com/variflight-ai/variflight-skill.git

# Or copy to your project
cp -r variflight-skill/scripts ./scripts
```

### Get API Key

Visit https://ai.variflight.com 

### Setup

方式一：环境变量
```bash
export VARIFLIGHT_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

方式二：配置文件
```bash
echo '{"api_key": "sk-xxxxxxxxxxxxxxxx"}' > ~/.variflight.json
```

### Usage

```bash
# Search flights
./scripts/flights.sh PEK SHA 2025-02-15

# Search by flight number
./scripts/flight.sh MU2157 2025-02-15

# Search train tickets
./scripts/train.sh "上海" "合肥" 2025-02-15

# Airport weather
./scripts/weather.sh PEK

# With explicit API key
./scripts/flights.sh --api-key sk-xxxx PEK SHA 2025-02-15
```

## Available Endpoints

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `flights` | Search by departure/arrival | dep, arr, date, depcity, arrcity |
| `flight` | Search by flight number | fnum, date, dep, arr |
| `transfer` | Flight transfer info | depcity, arrcity, depdate |
| `happiness` | Flight comfort index | fnum, date, dep, arr |
| `realtimeLocation` | Aircraft location | anum |
| `futureAirportWeather` | Airport weather | code, type="1" |
| `searchFlightItineraries` | Flight itineraries | depCityCode, arrCityCode, depDate |
| `trainStanTicket` | Train tickets | cdep, carr, date |
| `searchTrainStations` | Train stations | query |
| `getFlightPriceByCities` | Flight prices | dep_city, arr_city, dep_date |

## Common Airport Codes

| City | Airport | Code |
|------|---------|------|
| 北京 | 首都机场 | PEK |
| 北京 | 大兴机场 | PKX |
| 上海 | 虹桥机场 | SHA |
| 上海 | 浦东机场 | PVG |
| 广州 | 白云机场 | CAN |
| 深圳 | 宝安机场 | SZX |
| 成都 | 双流机场 | CTU |
| 杭州 | 萧山机场 | HGH |
| 合肥 | 新桥机场 | HFE |
| 西安 | 咸阳机场 | XIY |

## Response Format

```json
{
  "code": 200,
  "message": "Success",
  "data": { ... }
}
```

## Error Handling

- `401` - Invalid API key
- `400` - Bad request
- `500` - Server error

## Integration Examples

### OpenClaw (特别支持)

OpenClaw 会自动识别并加载本 skill。

**安装：**
```bash
# 通过 ClawHub 安装
openclaw skill install variflight

# 或手动安装
cp -r variflight-skill ~/.openclaw/workspace/skills/variflight
```

**配置：**
```bash
# OpenClaw 专用环境文件
echo 'VARIFLIGHT_API_KEY=sk-xxxx' > ~/.openclaw/workspace/.env.variflight

# 或使用通用配置
echo '{"api_key": "sk-xxxx"}' > ~/.variflight.json
```

**使用：**
```bash
./skills/variflight/scripts/flights.sh PEK SHA 2025-02-15
./skills/variflight/scripts/train.sh "上海" "合肥" 2025-02-15
```

### Claude Code / Cursor

Add to your settings:
```json
{
  "variflight_api_key": "sk-xxxxxxxxxxxxxxxx"
}
```

Or set environment variable in your shell config:
```bash
export VARIFLIGHT_API_KEY="sk-xxxxxxxxxxxxxxxx"
```

### GitHub Actions

```yaml
- name: Setup Variflight
  env:
    VARIFLIGHT_API_KEY: ${{ secrets.VARIFLIGHT_API_KEY }}
  run: |
    ./scripts/flights.sh PEK SHA 2025-02-15
```

### Docker

```dockerfile
ENV VARIFLIGHT_API_KEY=sk-xxxxxxxxxxxxxxxx
COPY scripts/ /app/scripts/
```

## Links

- Variflight AI: https://ai.variflight.com
- ClawHub: https://clawhub.com

