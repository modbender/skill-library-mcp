---
name: garmin
description: Integrate with Garmin Connect to fetch and analyze deep fitness metrics including sleep, body battery, resting heart rate, stress, and training status. Use this skill for enhanced training insights, recovery-aware nudges, and daily health summaries.
---
# Garmin Connect Integration Skill

Deep fitness metrics from Garmin Connect for enhanced training insights and recovery-aware nudges.

## Features

- **Training Status:** Recovery time, training load, VO2 max
- **Sleep Analysis:** Duration, quality, sleep stages
- **Body Battery:** Energy levels throughout day
- **Daily Readiness:** Is Brian recovered enough to train hard?
- **Heart Rate:** Resting HR trends, stress levels
- **Activity Details:** More detailed metrics than Strava

## Why Garmin + Strava?

**Strava:** Social, activities, segments, ride tracking  
**Garmin:** Physiological metrics, recovery, sleep, training load

Combined = Smart nudges that respect recovery status!

## Setup

### 1. Install Dependencies

```bash
pip3 install garminconnect --break-system-packages
# Or using a virtual environment (recommended):
# python3 -m venv ./venv
# source ./venv/bin/activate
# pip install garminconnect
```

### 2. Store Credentials in 1Password

Create a new "Login" item in your 1Password vault (e.g., "Personal") with the following details:

*   **Title:** `Garmin Connect` (or a custom name you prefer)
*   **Username:** Your Garmin Connect email address
*   **Password:** Your Garmin Connect password

If you use a custom title or a different vault, set the `GARMIN_1P_ITEM_NAME` and `GARMIN_1P_VAULT` environment variables before running the scripts.
Example:
```bash
export GARMIN_1P_ITEM_NAME="My Garmin Login"
export GARMIN_1P_VAULT="MyFamilyVault"
```

Ensure your `OP_SERVICE_ACCOUNT_TOKEN` is set up for 1Password CLI authentication:
```bash
export OP_SERVICE_ACCOUNT_TOKEN=$(cat ~/.config/op/service-account-token)
```

### 3. Test Connection

```bash
./scripts/garmin-login.sh
```

## Usage

### Get Today's Stats

```bash
./scripts/get-stats.sh
```

Returns:
- Body battery (current/forecast)
- Sleep last night
- Training status
- Recovery time remaining
- Resting heart rate

### Get Sleep Data

```bash
./scripts/get-sleep.sh [days_back]
```

Returns sleep duration, quality, stages for last N days.

### Check Recovery Status

```bash
./scripts/check-recovery.sh
```

Returns whether Brian is recovered enough for hard training.

## Integration with Strava Nudges

**Enhanced decision logic:**

Before nudging for a hard workout:
1. Check Garmin recovery time
2. Check body battery level
3. Check sleep quality last night
4. Adjust intensity recommendation

**Example:**
- Strava says: "Thursday tempo ride"
- Garmin says: "Recovery time: 24h, body battery: 45%"
- Nudge becomes: "Thursday ride scheduled, but recovery still needed. Easy Zone 2 instead of tempo today?"

## Data Structure

### Stats Object
```json
{
  "body_battery": {
    "current": 75,
    "charged": true,
    "forecast": 85
  },
  "sleep": {
    "duration_hours": 7.2,
    "quality": "good",
    "deep_sleep_hours": 1.8,
    "rem_hours": 1.5
  },
  "training_status": {
    "status": "productive",
    "vo2_max": 52,
    "recovery_time_hours": 12
  },
  "heart_rate": {
    "resting": 48,
    "current": 62,
    "stress_level": 25
  }
}
```

## Smart Nudge Enhancement Examples

### Scenario 1: Poor Sleep + Hard Workout Day
**Without Garmin:** "Thursday tempo ride time!"  
**With Garmin:** "You only got 5 hours sleep last night. Maybe take today easy? Light Zone 2 or rest."

### Scenario 2: Recovered + Good Conditions
**Without Garmin:** "Tuesday ride day"  
**With Garmin:** "Fully recovered (body battery 85%, 8h sleep) + perfect weather. Great day for that tempo ride! 🚴"

### Scenario 3: High Stress Day
**Without Garmin:** "Evening gym time!"  
**With Garmin:** "Stress level high today (68). Maybe skip gym and prioritize recovery?"

## Morning Briefing Enhancement

**Current:**
```
🚴 Fitness Update:
Last ride: 2 days ago
This week: 3 rides, 87km
```

**With Garmin:**
```
🚴 Fitness Update:
**Sleep:** 7.5h (good quality, 2h deep)
**Recovery:** ✅ Fully recovered
**Body Battery:** 82% (charged overnight)
**Resting HR:** 48 bpm (normal)

Last ride: 2 days ago
This week: 3 rides, 87km
**Training Status:** Productive (VO2 max: 52)
```

## Configuration

Edit `config.json` (create if it doesn't exist):
```json
{
  "recovery_thresholds": {
    "body_battery_low": 40,
    "body_battery_good": 70,
    "min_sleep_hours": 6.5,
    "max_recovery_time_hours": 12
  },
  "nudge_modifications": {
    "respect_recovery": true,
    "downgrade_intensity_if_tired": true,
    "skip_gym_if_high_stress": true
  }
}
```
*Note: This `config.json` should be created in the skill's root directory (`/root/clawd/skills/garmin/`).*

## API Reference

Using `garminconnect` Python library:
- `get_stats()` - Daily stats summary
- `get_sleep_data()` - Sleep metrics
- `get_body_battery()` - Energy levels
- `get_training_status()` - Training load, recovery
- `get_heart_rates()` - HR data

Rate limits: No official limit, but be reasonable (cache data, don't spam).

## Dependencies

- Python 3.7+
- `garminconnect` library
- 1Password CLI (`op`)
- `jq` for JSON parsing (if needed by other scripts)

## Privacy

- ✅ Credentials stored in 1Password
- ✅ Session tokens cached temporarily in `/tmp/garmin-session/`
- ✅ Data queried on-demand, not stored long-term by the skill (though the system might cache in `/root/clawd/data/fitness/garmin/` as per TOOLS.md)
- ✅ No external sharing
- ✅ Read-only access to Garmin

## Future Enhancements

- Correlate sleep quality → work productivity
- Predict when Brian will be recovered
- Compare son's Garmin data (if he has one)
- Long-term trends (fitness improving?)
