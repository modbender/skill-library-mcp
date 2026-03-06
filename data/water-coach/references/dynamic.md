# Dynamic Scheduling (Coach Mode)

**Only needed when tuning** - default works for most users.

---

## Concept

Coach Mode: helps when behind, backs off when doing well, comes back if struggling again.

---

## Formula

```
expected_percent = ((hour - start + 1) / (cutoff - start)) × 100
effective_threshold = expected_percent - margin_percent + aggressiveness_adjustment
```

---

## Parameters (in water_config.json)

```json
{
  "settings": {
    "start_hour": 9,
    "cutoff_hour": 22
  },
  "dynamic_scheduling": {
    "enabled": true,
    "formula": {
      "margin_percent": 25
    },
    "extra_notifications": {
      "max_per_hour": 2,
      "interval_minutes": 30,
      "healthy_threshold_percent": 80,
      "aggressiveness_curve": {
        "enabled": true,
        "schedule": [
          {"start": 9, "end": 15, "adjustment": 0},
          {"start": 15, "end": 20, "adjustment": -10},
          {"start": 20, "end": 22, "adjustment": -20}
        ]
      }
    }
  }
}
```

---

## Parameter Guide

| Parameter | Description | Default |
|-----------|-------------|---------|
| start_hour | First notification hour | 9 |
| cutoff_hour | Last notification hour | 22 |
| margin_percent | Below expected - margin = trigger | 25 |
| max_per_hour | Max extras per hour | 2 |
| interval_minutes | Min time between extras | 30 |
| healthy_threshold | Above this = no extras | 80% |
| aggressiveness_curve | Easier to trigger near cutoff | - |

---

## Aggressiveness Curve

| Time | Adjustment | Effect |
|------|------------|--------|
| 9am-3pm | 0 | Standard |
| 3pm-8pm | -10 | Easier trigger |
| 8pm-10pm | -20 | Much easier |

---

## Get Current Values

```bash
python3 skills/water-coach/scripts/water.py threshold
```

Returns:
```json
{
  "expected_percent": 69.2,
  "threshold": 44.2,
  "margin_percent": 25,
  "current_hour": 17
}
```

---

## Check if Should Send

```bash
python3 skills/water-coach/scripts/water.py dynamic
```

Returns:
```json
{
  "should_send": true/false,
  "reason": "under_threshold|healthy_progress|...",
  "current_percent": 45.1,
  "effective_threshold": 26.5
}
```
