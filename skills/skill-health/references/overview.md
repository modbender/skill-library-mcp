# Skill Health overview

## Data sources (CSV)

- `heart_rate.csv`: Date, Time, Heart Rate (bpm), Source
- `steps.csv`: Date, Time, Steps (cumulative), Source
- `calories.csv`: Date, Start Time, End Time, Active Calories, Total Calories, Source
- `sleep_sessions.csv`: Date, Start Time, End Time, Duration (hours), Source
- `oxygen_saturation.csv`: Date, Time, SpO2 (%), Source
- `exercise_sessions.csv`: Date, Start Time, End Time, Duration, Type, Title, Source
- `distance.csv`: Date, Start Time, End Time, Distance (m/km), Source

## Key decisions

- Kingsmith treadmill sessions: steps are estimated from distance (`steps = distance_m / 0.75`).
- Active calories often missing; `active_kcal_measured=false` and `total_kcal` is the reliable signal.
- HR zones computed from inter-sample intervals (not uniform sampling).
- `hr_range_during_sleep` is a proxy, not clinical HRV.
- Sleep window uses last 30h by default; metrics include suffix `last_{window_hours}h`.

## Output format (compact JSON)

- `time_window`: `s` (start), `e` (end), `r` (resolution).
- `data_quality`: `cov` (coverage 0-1), `rel` (high/medium/low/unavailable), `notes` (optional).
