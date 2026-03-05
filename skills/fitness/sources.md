# Fitness Data Sources

Reference only — consult when adding a new data source.

## Wearable Integrations
- **Apple Watch/HealthKit**: workouts, activity rings, VO2max, HR zones
- **Fitbit**: Active Zone Minutes, cardio score, intraday HR
- **Garmin**: training load/status, Body Battery, stress, VO2max
- **Whoop**: strain score, recovery score, HRV
- **Oura**: activity score, readiness, recovery focus

## Conversational Signals
- **Workouts**: "Did legs today", "Just finished my run"
- **Metrics**: "Ran 5k", "Hit 100kg bench", "Did 3x12"
- **Achievements**: "New PR!", "Finished my first marathon"
- **Status**: "Legs are killing me", "Too tired to train"
- **Schedule**: "I go 4x a week", "Morning sessions"
- **Social**: "Spin class", "Running club", "Got a PT"

## External Sources
- **Race results**: Strava, Athlinks, official race sites
- **Gym apps**: Strong, Hevy (CSV exports)
- **Competitions**: CrossFit Open, OpenPowerlifting.org
- **Social**: Strava segments, Peloton leaderboards

## Reliability Tiers
| Tier | Sources | Trust |
|------|---------|-------|
| High | Wearables, gym app exports | Use directly |
| Medium | Conversation mentions, race results | Confirm pattern |
| Low | Inferred (calendar, stress) | Suggest only |

## Cross-Validation
When sources disagree:
- Prefer wearable over conversation for metrics
- Note discrepancy ("watch says easy run but you said it was hard")
- Track which source predicts how user FEELS best
