# Setting Up Automated Prayer Reminders

This guide shows how to set up automated prayer reminders that work in the background and notify you before, during, and after prayer times - even while you're chatting.

## Overview

The reminder system consists of:

1. **Daily Prayer Time Fetch** - Runs at midnight to get today's prayer times
2. **Periodic Reminder Check** - Runs every 5-10 minutes to check if it's time to remind
3. **Three-Stage Reminders**:
   - **10 minutes before** - Heads up that prayer is approaching
   - **At prayer time** - "Salat First" reminder
   - **5 minutes after** - Gentle reminder if still chatting

## Setup Instructions

### Step 1: Set Your Location and Timezone

First, determine your:
- **City and Country** (e.g., "Mecca, Saudi Arabia", "Istanbul, Turkey", "Cairo, Egypt")
- **Timezone offset** from UTC (e.g., +3 for Saudi Arabia, +3 for Turkey, +2 for Egypt)

### Step 2: Create Daily Prayer Time Fetch Job

This cron job fetches fresh prayer times at midnight local time.

```javascript
{
  "name": "prayer-times:daily-fetch",
  "schedule": {
    "kind": "cron",
    "expr": "0 0 * * *",           // Midnight
    "tz": "Africa/Casablanca"      // Your timezone
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Fetch today's prayer times:\n\n1. Run: python3 /path/to/get_prayer_times.py --city YourCity --country YourCountry --json > prayer_times.json\n2. Verify prayer_times.json was created\n3. Silent operation - only alert if fetch fails after retry",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "none"
  },
  "enabled": true
}
```

**Replace:**
- `YourCity` → Your city name
- `YourCountry` → Your country name
- `/path/to/` → Path where skill scripts are located
- `Africa/Casablanca` → Your timezone (use same format)

### Step 3: Create Periodic Reminder Check Job

This job checks every 5-10 minutes if it's time to remind about prayer.

```javascript
{
  "name": "prayer-times:reminder-check",
  "schedule": {
    "kind": "every",
    "everyMs": 300000               // 5 minutes (300,000 ms)
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check if it's time for Salat reminder:\n\n1. Run: python3 /path/to/check_prayer_reminder.py --prayer-times prayer_times.json --timezone OFFSET\n2. If exit code is 1, send the reminder message to the main session\n3. If exit code is 0, do nothing (HEARTBEAT_OK)\n4. If exit code is 2, log error (missing prayer times)",
    "timeoutSeconds": 30
  },
  "delivery": {
    "mode": "announce",
    "channel": "last"                // Send to last active channel
  },
  "enabled": true
}
```

**Replace:**
- `OFFSET` → Your timezone offset (e.g., 1 for GMT+1)
- `/path/to/` → Path where skill scripts are located

### Step 4: Add Jobs via OpenClaw CLI

Use the `cron` tool to add these jobs:

**Option A: Via Chat**
```
Add a cron job to fetch prayer times daily at midnight and check every 5 minutes for reminders. Use Rabat, Morocco (timezone +1).
```

**Option B: Via Tool Call**
Use the `cron` tool with action `add` and the job objects above.

## Configuration Examples

### Morocco (GMT+1)
```javascript
// Daily fetch
"expr": "0 0 * * *"
"tz": "Africa/Casablanca"

// Reminder check
"message": "...--timezone 1..."
```

### Saudi Arabia (GMT+3)
```javascript
// Daily fetch
"expr": "0 0 * * *"
"tz": "Asia/Riyadh"

// Reminder check
"message": "...--timezone 3..."
```

### Egypt (GMT+2)
```javascript
// Daily fetch
"expr": "0 0 * * *"
"tz": "Africa/Cairo"

// Reminder check
"message": "...--timezone 2..."
```

### Turkey (GMT+3)
```javascript
// Daily fetch
"expr": "0 0 * * *"
"tz": "Europe/Istanbul"

// Reminder check
"message": "...--timezone 3..."
```

## How Reminders Work

### Reminder Windows

The check script looks for three reminder windows:

1. **Before (9-11 minutes)**
   - Triggers: 10 minutes before prayer time (±1 min buffer)
   - Message: "🕌 Salat approaching: Asr in 10 minutes (16:43)"

2. **Now (-1 to +2 minutes)**
   - Triggers: At prayer time (±2 min buffer)
   - Message: "🕌 Salat First: Asr time is now (16:43)"

3. **After (-6 to -4 minutes)**
   - Triggers: 5 minutes after prayer started (±1 min buffer)
   - Message: "🕌 Salat reminder: Asr started 5 minutes ago (16:43)"

### Why These Windows?

- **Wide windows (±1-2 min)** ensure reminders don't get missed if check runs at slightly different times
- **5-minute check interval** balances responsiveness with resource usage
- **Three stages** provide multiple opportunities to catch the prayer

## Testing

### Test Prayer Time Fetch
```bash
python3 get_prayer_times.py --city YourCity --country YourCountry --json > prayer_times.json
cat prayer_times.json
```

### Test Reminder Check
```bash
# Should output "HEARTBEAT_OK" if no reminder needed
python3 check_prayer_reminder.py --prayer-times prayer_times.json --timezone OFFSET

# To test near prayer time, manually edit prayer_times.json with a time 10 minutes from now
```

### Test Cron Jobs
```
List my cron jobs
```

Should show:
- `prayer-times:daily-fetch`
- `prayer-times:reminder-check`

## Adjusting Check Frequency

### More Frequent (Every 2 Minutes)
```javascript
"everyMs": 120000  // 2 minutes
```

### Less Frequent (Every 10 Minutes)
```javascript
"everyMs": 600000  // 10 minutes
```

**Recommendation:** 5 minutes is a good balance. More frequent uses more resources; less frequent risks missing reminders.

## Troubleshooting

### Prayer times not fetching
- Check network connectivity to api.aladhan.com
- Verify city/country names are correct
- Check if VPN is needed (see main SKILL.md)

### Reminders not appearing
- Verify `prayer_times.json` exists and is updated daily
- Check timezone offset is correct
- Confirm cron jobs are enabled and running
- Test manually with scripts

### Wrong prayer times
- Ensure correct calculation method for your country
- Verify coordinates if using lat/lon instead of city

### Too many/few reminders
- Adjust check frequency (everyMs)
- Modify reminder windows in check_prayer_reminder.py

## Maintenance

### Disable Temporarily
```
Disable my prayer-times cron jobs
```

### Re-enable
```
Enable my prayer-times cron jobs
```

### Remove Completely
```
Remove all prayer-times cron jobs
```

## Cost Estimate

Running these cron jobs:
- **Daily fetch**: ~500-800 tokens/day
- **Reminder checks**: ~200-300 tokens/check × 288 checks/day = ~60K tokens/day
- **Total**: ~60-65K tokens/day (~$1.80-2.00/month at $0.03/1K tokens)

The reminders check frequently but only alert when needed, keeping the cost manageable while providing reliable notifications.
