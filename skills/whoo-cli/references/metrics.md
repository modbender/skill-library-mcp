# whoo CLI — Metric Interpretation Guide

WHOOP metrics are personal and relative — compare against the user's own baseline rather than
population averages. Trends over time are more meaningful than single data points.

---

## Recovery Score (`recovery_score`, 0–100 %)

WHOOP's primary readiness signal, computed from HRV, resting HR, SpO2, and sleep performance.

| Zone   | Range    | Meaning                                          |
| ------ | -------- | ------------------------------------------------ |
| Green  | 67–100 % | Well recovered; high-intensity training OK       |
| Yellow | 34–66 %  | Moderate recovery; manageable effort recommended |
| Red    | 0–33 %   | Under-recovered; prioritize rest and low strain  |

---

## HRV — `hrv_rmssd_milli` (ms)

Higher is generally better. The absolute value matters less than the user's personal trend — a
drop of 20 %+ from their rolling average signals accumulated stress or fatigue.

---

## Resting Heart Rate — `resting_heart_rate` (bpm)

Lower is better when recovered. An elevation of 5+ bpm above personal baseline often indicates
illness, alcohol consumption, or incomplete recovery.

---

## Blood Oxygen — `spo2_percentage` (%)

| Range    | Interpretation                               |
| -------- | -------------------------------------------- |
| 95–100 % | Normal                                       |
| 90–94 %  | Low — investigate (altitude, illness, sleep) |
| < 90 %   | Clinically significant; advise medical check |

---

## Strain — `strain` (0–21 scale)

Measures cardiovascular load for the day. Not inherently good or bad — should match the user's
training intent.

| Range | Effort level      |
| ----- | ----------------- |
| 0–9   | Light / rest day  |
| 10–13 | Moderate          |
| 14–17 | Hard              |
| 18–21 | All-out / maximal |

---

## Sleep Performance — `sleep_performance_percentage` (%)

Actual sleep vs WHOOP's computed sleep need. ≥ 85 % is generally optimal. Values below 70 %
compound sleep debt over time and suppress recovery scores.

---

## Respiratory Rate — `respiratory_rate` (breaths/min)

Typical resting range: 12–20. A sustained elevation of 1–2 breaths/min above personal baseline
can be an early marker of illness or overtraining before other symptoms appear.

---

## Skin Temperature — `skin_temp_celsius` (°C delta)

A deviation from personal baseline, not an absolute temperature. Positive spikes (> +0.5 °C)
during sleep can indicate immune activation or alcohol consumption.

---

## Sleep Efficiency — `sleep_efficiency_percentage` (%)

Time spent asleep divided by total time in bed. < 85 % suggests fragmented sleep or prolonged
time to fall asleep. Target > 90 % for restorative sleep.

---

## `score_state` Values

| Value            | Meaning                                         |
| ---------------- | ----------------------------------------------- |
| `SCORED`         | Full metrics available — safe to interpret      |
| `PENDING_MANUAL` | WHOOP hasn't finished scoring yet — check later |
| `UNSCORABLE`     | Insufficient data (e.g. device not worn)        |

Always guard on `score_state === "SCORED"` before using numeric metrics.
