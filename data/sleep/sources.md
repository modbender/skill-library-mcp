# Sleep Data Sources

Reference only — consult when adding a new data source.

## Wearable Integrations
- **Apple Watch/Health**: sleep stages, heart rate, HRV
- **Oura Ring**: readiness score, deep/REM/light
- **Fitbit**: sleep score, restlessness, SpO2
- **Whoop**: strain, recovery, sleep need
- **Garmin**: Body Battery, stress, sleep score
- **Samsung Health**: sleep stages, blood oxygen

## Conversational Signals
- "I slept terribly" / "slept great"
- "Couldn't fall asleep" / "woke up at 3am"
- "So tired today" / "feeling rested"
- "Pulled an all-nighter"
- "Took a nap"
- Time of coffee/energy drink mentions

## Environmental
- Smart home (bedroom temp, lights off time)
- Phone screen time before bed
- Alarm/wake times from calendar

## Manual Input
- Sleep diary entries
- Explicit reports ("I slept 6 hours")
- Quality ratings

## Reliability Tiers
| Tier | Sources | Trust |
|------|---------|-------|
| High | Wearables with sleep stages | Use directly |
| Medium | Conversation mentions, manual | Confirm pattern |
| Low | Inferred (late messages, etc.) | Suggest only |

## Cross-Validation
When multiple sources disagree:
- Prefer wearable over conversation
- Note discrepancy ("watch says 7h but user feels tired")
- Track which source predicts how user FEELS best
