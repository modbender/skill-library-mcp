# Whoop API — HerCycle Reference

Configure `WHOOPLAW_BASE_URL` to point to your WhoopClaw server (e.g. `http://localhost:8000`).

## Key Endpoints

```bash
# Recovery + HRV
GET /whoop/recovery

# Sleep
GET /whoop/sleep

# Skin temperature (ovulation signal — rises ~0.2–0.5°C at ovulation)
GET /whoop/metrics/skin-temp

# Current cycle phase (if user has logged)
GET /cycle/current

# Log cycle day manually
POST /cycle/log
{ "cycle_day": 1, "phase": "menstrual" }
```

## Phase Inference from Skin Temp

If no explicit cycle log exists, estimate phase from skin temperature trend:
- Sustained rise of 0.2°C+ over 2–3 days → ovulation occurred → now luteal
- Temp drops back to baseline → menstrual phase approaching
- Low stable temp → follicular

## HRV × Phase Correlation

| Phase | Typical HRV pattern |
|-------|-------------------|
| Menstrual | Lower HRV, higher recovery need |
| Follicular | Rising HRV, high adaptability |
| Ovulation | Peak HRV, high readiness |
| Luteal | Declining HRV, more recovery needed |

Cross-reference Whoop recovery score with expected phase pattern to validate.
