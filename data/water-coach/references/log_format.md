# Water Coach Log Formats (v1.5.0)

---

## water_log.csv

| Column | Type | Description |
|--------|------|-------------|
| logged_at | ISO 8601 | When user told you (NOW) |
| drank_at | ISO 8601 | When user actually drank (can be past) |
| date | YYYY-MM-DD | Derived from drank_at |
| slot | string | Time slot: morning/lunch/afternoon/evening/manual |
| ml_drank | int | Amount (ml) |
| goal_at_time | int | Goal at that moment |
| message_id | string | Audit trail - link to conversation |

### Key Rules

1. **drank_at is MANDATORY** - always required
2. If user doesn't specify drank_at → assume drank_at = logged_at
3. **Cumulative is calculated at query time** (not stored)
4. Use drank_at to determine which day counts
5. message_id links to conversation for audit trail

### Examples

```bash
# User says "I drank 500ml right now"
water log 500
→ logged_at: NOW, drank_at: NOW, date: TODAY

# User says "I drank 500ml at 6pm"
water log 500 --drank-at=2026-02-18T18:00:00Z
→ logged_at: NOW, drank_at: 6PM, date: TODAY

# User says "Yesterday at 2pm I drank 300ml"
water log 300 --drank-at=2026-02-17T14:00:00Z
→ logged_at: NOW, drank_at: Yesterday 2PM, date: YESTERDAY
```

### Audit Trail

```bash
# Get entry by message_id
water audit msg_123

# Get entries by date
# (internal function - calculates cumulative from ml_drank)
```

---

## body_metrics.csv

| Column | Type | Description |
|--------|------|-------------|
| date | YYYY-MM-DD | Date |
| weight_kg | float | Body weight |
| height_m | float | Height |
| bmi | float | Calculated BMI |
| body_fat_pct | float | Body fat % |
| muscle_pct | float | Muscle % |
| water_pct | float | Body water % |

---

## water_config.json

```json
{
  "version": "3.0",
  "user": {
    "weight_kg": 95,
    "height_m": null
  },
  "settings": {
    "goal_multiplier": 35,
    "cutoff_hour": 22,
    "start_hour": 9
  },
  "dynamic_scheduling": {
    "enabled": true,
    "formula": {"margin_percent": 25},
    "extra_notifications": {
      "max_per_hour": 2,
      "healthy_threshold_percent": 80
    }
  }
}
```

---

## CLI Commands (water_coach.py)

### Water
```bash
water_coach.py water status                      # Current progress (calculated)
water_coach.py water log 500                     # Log intake
water_coach.py water log 500 --drank-at=2026-02-18T18:00:00Z
water_coach.py water log 500 --message-id=msg_123
water_coach.py water dynamic                     # Check if extra notification needed
water_coach.py water threshold                   # Get expected % for current hour
water_coach.py water set_body_weight 80          # Update weight
water_coach.py water audit msg_123              # Get entry by message_id
```

### Body
```bash
water_coach.py body log --weight=80 --height=1.75
water_coach.py body latest
water_coach.py body history 30
```

### Analytics
```bash
water_coach.py analytics week
water_coach.py analytics month
```
