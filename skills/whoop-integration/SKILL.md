---
name: whoop-integration
description: Integrate with WHOOP fitness tracker API to monitor sleep, recovery, and strain data. Use when you need to check sleep quality, recovery scores, analyze fitness patterns, set up morning behavior adjustments based on sleep performance, or create automated health monitoring workflows. Supports OAuth authentication, sleep performance tracking, and adaptive assistant behavior.
metadata:
  {
    "openclaw":
      {
        "emoji": "🏃‍♀️",
        "requires": { "env": ["WHOOP_CLIENT_ID", "WHOOP_CLIENT_SECRET"] },
        "primaryEnv": "WHOOP_CLIENT_SECRET",
      }
  }
---

# WHOOP Integration

Monitor sleep, recovery, and strain data from WHOOP fitness tracker.

## Tokens

Tokens stored in `~/.openclaw/whoop_tokens.json`:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "obtained_at": "ISO timestamp",
  "expires_at": "ISO timestamp"
}
```

## Token Rotation

Refresh endpoint (IMPORTANT — other paths return 404!):
```
POST https://api.prod.whoop.com/oauth/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=REFRESH_TOKEN&client_id=CLIENT_ID&client_secret=CLIENT_SECRET
```

CLIENT_ID and CLIENT_SECRET are in env vars `WHOOP_CLIENT_ID` and `WHOOP_CLIENT_SECRET`.

Rotate when `expires_at` is within 1 hour. Save new tokens with `obtained_at` and `expires_at`.

## API Endpoints

**Base URL:** `https://api.prod.whoop.com/developer`
**Auth:** `Authorization: Bearer {access_token}`

**⚠️ Use V2 endpoints! V1 returns 404!**

### Sleep
```
GET /v2/activity/sleep?limit=1
```

Key fields in `records[0].score`:
- `sleep_performance_percentage` — overall quality (0-100%)
- `sleep_efficiency_percentage` — time asleep vs in bed
- `sleep_consistency_percentage`
- `respiratory_rate`
- `stage_summary`:
  - `total_in_bed_time_milli`
  - `total_light_sleep_time_milli`
  - `total_slow_wave_sleep_time_milli` (deep sleep)
  - `total_rem_sleep_time_milli`
  - `total_awake_time_milli`
  - `sleep_cycle_count`
  - `disturbance_count`

### Recovery
```
GET /v2/recovery?limit=1
```

Key fields in `records[0].score`:
- `recovery_score` (0-100)
- `resting_heart_rate` (bpm)
- `hrv_rmssd_milli` (ms, higher = better)
- `spo2_percentage`
- `skin_temp_celsius`

## Morning Report Format

**RECOVERY FIRST — це найважливіше для користувача!**

Send to Telegram (`channel=telegram`, `target=36171288`):

```
🏃‍♀️ WHOOP Ранковий звіт

💚 Відновлення: X% [колір]
❤️ Пульс: X bpm | HRV: X ms | SpO2: X%
📋 [Рекомендація]

😴 Сон: X% ефективність (Xг Xхв загалом)
💤 Deep: Xхв | REM: Xхв | Light: Xхв
🔄 Циклів: X | Пробуджень: X
```

### Recovery колір та рекомендація:
- **>67% (зелений 🟢):** Повний газ! Можна тренуватись на максимум
- **34-67% (жовтий 🟡):** Обережно, не перевантажуйся
- **<34% (червоний 🔴):** Відпочинок, без серйозних навантажень

### Конвертація мілісекунд:
- Ділити на 60000 для хвилин
- Ділити на 3600000 для годин

## Аналіз за період

Для аналізу трендів за будь-який період використовуй параметри `start`, `end`, `limit`.

### Sleep за період
```
GET /v2/activity/sleep?start=2026-01-28T00:00:00.000Z&end=2026-02-04T00:00:00.000Z&limit=25
```

### Recovery за період
```
GET /v2/recovery?start=2026-01-28T00:00:00.000Z&end=2026-02-04T00:00:00.000Z&limit=25
```

### Cycles (strain) за період
```
GET /v2/cycle?start=2026-01-28T00:00:00.000Z&end=2026-02-04T00:00:00.000Z&limit=25
```

### Workouts за період
```
GET /v2/activity/workout?start=2026-01-28T00:00:00.000Z&end=2026-02-04T00:00:00.000Z&limit=25
```

Дати — ISO 8601 формат. `start` inclusive, `end` exclusive. Max `limit=25`, для більше — пагінація через `nextToken`.

### Що аналізувати:
- **Тренди recovery** — чи росте/падає відновлення за тиждень/місяць
- **Середній HRV** — тренд вгору = тіло адаптується, вниз = перетренованість
- **Якість сну** — % deep/REM від загального сну, тренд ефективності
- **Strain vs Recovery** — чи відповідає навантаження відновленню
- **Resting HR тренд** — зниження = краща форма, підвищення = стрес/хвороба
- **Consistency** — наскільки стабільний графік сну

### Формат аналізу (Telegram):
```
📊 WHOOP Аналіз: [період]

💚 Recovery: avg X% (min X% — max X%) [тренд ↑↓→]
❤️ HRV: avg X ms (тренд ↑↓→)
💤 Сон: avg Xг Xхв (ефективність avg X%)
🏋️ Strain: avg X (max X)
🫀 Пульс спокою: avg X bpm (тренд ↑↓→)

📈 Висновки: [коротко що добре/погано і рекомендації]
```

## Adaptive Behavior

Adjust communication based on recovery:
- **>80%:** Energetic, suggest ambitious tasks
- **67-80%:** Normal, balanced approach
- **34-67%:** Supportive, lighter tasks
- **<34%:** Gentle, minimal complexity, focus on rest
