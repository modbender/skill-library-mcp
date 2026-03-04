---
name: kma-weather
description: Get weather from Korea Meteorological Administration (기상청). Provides current conditions, forecasts (3-10 days), and weather warnings/advisories (기상특보). Use when user needs Korean weather data, 기상특보, or precise local forecasts (5km grid). Requires KMA_SERVICE_KEY.
metadata:
  openclaw:
    emoji: "🌦️"
    homepage: "https://www.data.go.kr/data/15084084/openapi.do"
    requires:
      bins: ["python3"]
      env: ["KMA_SERVICE_KEY"]
    primaryEnv: "KMA_SERVICE_KEY"
---

# kma-weather

## Quick Start

```bash
# Current weather + 6-hour forecast
python3 skills/kma-weather/scripts/forecast.py brief --lat 37.5665 --lon 126.9780

# All forecasts as JSON (current + ultrashort + shortterm)
python3 skills/kma-weather/scripts/forecast.py all --lat 37.5665 --lon 126.9780 --json

# Short-term forecast (3 days)
python3 skills/kma-weather/scripts/forecast.py shortterm --lat 37.5665 --lon 126.9780 --days all

# Nationwide weather warnings/advisories (기상특보)
python3 skills/kma-weather/scripts/weather_warnings.py

# Mid-term forecast (3-10 days)
python3 skills/kma-weather/scripts/midterm.py --region 서울
```

## Setup

### 1. Get API Key

1. Visit [공공데이터포털](https://www.data.go.kr)
2. Request access to these 3 APIs (all use the same key):
   - [기상청 단기예보 조회서비스](https://www.data.go.kr/data/15084084/openapi.do) (15084084)
   - [기상청 기상특보 조회서비스](https://www.data.go.kr/data/15000415/openapi.do) (15000415)
   - [기상청 중기예보 조회서비스](https://www.data.go.kr/data/15059468/openapi.do) (15059468)
3. Copy your `ServiceKey` from My Page → API Key Management

### 2. Set Environment Variable

In `~/.openclaw/openclaw.json`:

**Sandbox** (add to `agents.defaults.sandbox.docker.env`):
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "env": {
            "KMA_SERVICE_KEY": "your-key"
          }
        }
      }
    }
  }
}
```

**Host** (add to `env.vars`):
```json
{
  "env": {
    "vars": {
      "KMA_SERVICE_KEY": "your-key"
    }
  }
}
```

## Usage

### forecast.py

| Command | Description |
|---------|-------------|
| `current` | Real-time observations |
| `ultrashort` | 6-hour forecast |
| `shortterm` | 3-day forecast |
| `brief` | current + ultrashort |
| `all` | current + ultrashort + shortterm |

**Options**:
- `--lat`, `--lon`: Coordinates (required)
- `--days`: For shortterm - `1` (tomorrow, default), `2`, `3`, or `all`
- `--json`: Raw JSON output

**Output example** (`current`):
```
🌤️ 현재 날씨 (초단기실황)
🌡️  기온: 5.2°C
💧 습도: 65%
🌧️  강수량: 0mm (1시간)
💨 풍속: 2.3m/s
🧭 풍향: NW (315°)
```

### weather_warnings.py

Returns current nationwide 기상특보:
```
🚨 기상특보 현황
발표시각: 2026-02-01 10:00
발효시각: 2026-02-01 10:00

📍 현재 발효 중인 특보
  • 건조경보 : 강원도, 경상북도, ...
  • 풍랑주의보 : 동해중부안쪽먼바다, ...

⚠️  예비특보
  • (1) 강풍 예비특보 : 02월 02일 새벽(00시~06시) : 울릉도.독도
```

### midterm.py

3-10 day forecast by region.

```bash
python3 skills/kma-weather/scripts/midterm.py --region 서울
python3 skills/kma-weather/scripts/midterm.py --stn-id 109
```

**Regions**: 서울, 인천, 경기, 부산, 대구, 광주, 대전, 울산, 세종, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주

### grid_converter.py

Convert lat/lon to KMA 5km grid (auto-handled by other scripts):
```bash
python3 skills/kma-weather/scripts/grid_converter.py 37.5665 126.9780
# Output: Grid: (60, 127)
```

## API Notes

- **Release Schedule**:
  - Current: Every hour at :40 (base_time: HH00)
  - Ultra-short: Every hour at :45 (base_time: HH30)
  - Short-term: 02:10, 05:10, 08:10, 11:10, 14:10, 17:10, 20:10, 23:10 (KST)
  - Mid-term: 06:00, 18:00 (KST)
- **Coverage**: South Korea only
- **Auto-pagination**: Scripts fetch all pages automatically

## vs weather skill

| | weather | kma-weather |
|-|---------|-------------|
| Coverage | Global | Korea only |
| API Key | No | **Required** |
| Resolution | City-level | 5km grid |
| Weather Warnings | No | **Yes** (기상특보) |

**Use both**: `weather` for global, `kma-weather` for detailed Korean forecasts and 기상특보.

## Troubleshooting

| Error | Solution |
|-------|----------|
| `KMA API service key not found` | Set `KMA_SERVICE_KEY` env var |
| `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` | Check API approval status, verify key |
| `SERVICE_TIMEOUT_ERROR` | Retry later |
| No data returned | Verify coordinates are in South Korea |

## References (Raw API Documentation)

- [references/api-forecast.md](references/api-forecast.md) - 단기예보 API endpoints, parameters, response format
- [references/api-warnings.md](references/api-warnings.md) - 기상특보 API endpoints, parameters, response format
- [references/api-midterm.md](references/api-midterm.md) - 중기예보 API endpoints, parameters, response format
- [references/category-codes.md](references/category-codes.md) - KMA category codes (SKY, PTY, etc.)
- [implement-status.md](implement-status.md) - Implementation status
