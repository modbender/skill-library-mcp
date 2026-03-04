---
name: kma-weather
description: KMA short-term forecast API - ultra-short-term observation/forecast, short-term forecast
version: 2.2.0
author: chumjibot
created: 2026-02-10
updated: 2026-02-19
tags: [weather, korea, openapi, data.go.kr]
connectors: [~~weather, ~~air, ~~notify]
---

# KMA Weather Forecast Skill

Korea Meteorological Administration short-term forecast API + AirKorea air quality integration.

## Overview

| Key | Value |
|-----|-------|
| Provider | KMA (Korea Meteorological Administration) |
| Service ID | 15084084 |
| Auth | `~/.config/data-go-kr/api_key` |
| Endpoint | `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0` |
| Playbook | `playbook.md` |

## Scripts

```
scripts/
├── weather.sh             → Weather query (ncst/fcst/short)
├── morning_briefing.sh    → Morning briefing (weather + air quality)
└── grid_convert.py        → Lat/lon → grid coordinate conversion
```

## Workflow

### Step 1: Identify location & time
- "서울 날씨" → Seoul Jongno-gu (nx=60, ny=127)
- "내일 날씨" → short-term forecast (short)
- "지금 비 와?" → ultra-short-term observation (ncst)
- Refer to `playbook.md` for default location

### Step 2: Fetch weather data
- Current: `weather.sh ncst [nx] [ny]`
- 6-hour: `weather.sh fcst [nx] [ny]`
- 3-day: `weather.sh short [nx] [ny]`

### Step 3: Air quality integration (~~air)
- Fetch PM data via AirKorea skill
- `skills/airkorea-air-quality/scripts/air_quality.sh [station]`

### Step 4: Structured response using output template

## Output Template

```markdown
## 🌤️ [Location] Weather

### Current
🌡️ Temp: X°C (Feels like X°C)
💧 Humidity: X% | 🌬️ Wind: Xm/s
🌧️ Precip: [None/Rain/Snow]

### Today's Forecast
☀️ High X°C / Low X°C
🌧️ Precip probability: X%
🌫️ PM2.5: [Good/Moderate/Bad/Very Bad] (X㎍/㎥)

### 💡 One-liner
[Bring umbrella / Wear mask / Great day to go out]
```

## API Types

| API | Command | Description | Update Cycle |
|-----|---------|-------------|-------------|
| Ultra-short obs | `ncst` | Current observation | Hourly |
| Ultra-short fcst | `fcst` | 6hr forecast | Every 30min |
| Short-term fcst | `short` | 3-day hourly | 8x/day |

## Key Grid Coordinates

| Location | nx | ny |
|----------|----|----|
| Seoul Jongno | 60 | 127 |
| Seoul Gangnam | 61 | 126 |
| Busan | 98 | 76 |
| Daegu | 89 | 90 |
| Incheon | 55 | 124 |
| Daejeon | 67 | 100 |
| Jeju | 52 | 38 |

## Codes

### Sky (SKY)
`1`: Clear ☀️ | `3`: Mostly cloudy ⛅ | `4`: Overcast ☁️

### Precipitation (PTY)
`0`: None | `1`: Rain 🌧️ | `2`: Rain/Snow 🌧️❄️ | `3`: Snow ❄️ | `4`: Shower 🌦️

## base_time Rules

| API | Release time | Queryable |
|-----|-------------|-----------|
| Ultra-short obs | Every hour | +10min |
| Ultra-short fcst | Every 30min | +10min |
| Short-term fcst | 02,05,08,11,14,17,20,23h | +10min |

## Connectors

| Placeholder | Purpose | Current Tool |
|-------------|---------|-------------|
| `~~weather` | Weather API | KMA Short-term Forecast |
| `~~air` | Air quality | AirKorea |
| `~~notify` | Notification | Telegram |

## Intent Router

| Intent | Trigger Examples | Strategy |
|--------|-----------------|----------|
| Quick Check | "오늘 날씨 어때?", "지금 비 와?", "기온 몇 도?" | `ncst` (현재 관측) + `fcst` (3시간 예보) → 간단 요약 |
| Daily Forecast | "내일 비 와?", "주말 날씨", "모레 눈 올까?" | `short` (단기예보 3일) → 시간대별 상세 |
| Morning Briefing | "아침 날씨 브리핑" | `morning_briefing.sh` → 날씨+대기질 통합 |

**Routing logic:** 현재/지금 → Quick Check, 내일/모레/주말 → Daily Forecast, 브리핑 → Morning Briefing

## Cross-Skill Integration

| Trigger | Target Skill | Integration |
|---------|-------------|-------------|
| 날씨 응답 시 항상 | `airkorea-air-quality` | PM2.5 수치를 날씨 응답에 포함 (Output Template 참조) |
| 미세먼지 나쁨 이상 | `airkorea-air-quality` | "마스크 챙기세요" 팁 추가 |
| 비/눈 예보 시 | — | "우산 챙기세요" 자동 팁 |

## Notes
1. Uses grid coordinate system (not lat/lon) → use `grid_convert.py`
2. Query after release time + 10 minutes
3. Short-term forecast returns large data → set sufficient `numOfRows`

---
*Cowork architecture v2.2 — 🦞 chumjibot (2026-02-19)*

## 🔧 Setup (공공데이터 포털 API)

1. [data.go.kr](https://www.data.go.kr) 회원가입
2. 로그인 → 마이페이지 → **일반 인증키(Decoding)** 복사
3. API 키 저장:
   ```bash
   mkdir -p ~/.config/data-go-kr
   echo "YOUR_API_KEY" > ~/.config/data-go-kr/api_key
   ```
4. 아래 서비스 **활용신청** 후 사용 (자동승인)
   - [기상청 단기예보](https://www.data.go.kr/data/15084084/openapi.do) (15084084)
