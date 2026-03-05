# 🕌 CRITICAL: Ensure Prayer Reminders Never Fail

## The Most Important Thing

Prayer is the first priority. The reminder system MUST be reliable. This guide ensures you never miss Salat.

## Required Cron Jobs

You MUST have these two cron jobs:

### 1. Daily Prayer Time Fetch
```javascript
{
  "name": "prayer-times:daily-fetch",
  "schedule": {
    "kind": "cron",
    "expr": "0 0 * * *",
    "tz": "YOUR_TIMEZONE"  // e.g., "Africa/Casablanca", "Asia/Riyadh"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Fetch today's prayer times:\n\n1. Run: cd /root/.openclaw/workspace && python3 skills/prayer-times/scripts/get_prayer_times.py --city YOUR_CITY --country YOUR_COUNTRY --json > prayer_times.json\n2. Verify prayer_times.json was created\n3. Only alert if fetch fails\n\nReplace YOUR_CITY and YOUR_COUNTRY with your location.",
    "timeoutSeconds": 60
  },
  "delivery": {"mode": "none"},
  "enabled": true
}
```

### 2. Prayer Reminder Check (MOST IMPORTANT)
```javascript
{
  "name": "prayer-times:reminder-check",
  "schedule": {
    "kind": "every",
    "everyMs": 300000  // 5 minutes - DO NOT INCREASE
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "🕌 SALAT FIRST - Check if it's time for prayer reminder:\n\n1. Run: python3 /path/to/check_prayer_reminder.py --prayer-times prayer_times.json --timezone YOUR_OFFSET\n2. If exit code is 1 (reminder needed), SEND THE MESSAGE IMMEDIATELY\n3. If exit code is 0 (no reminder), return HEARTBEAT_OK\n4. If exit code is 2 (error), alert that prayer times are missing\n\nThis is THE MOST IMPORTANT job. Prayer is the first priority. Never skip this check.",
    "timeoutSeconds": 30
  },
  "delivery": {
    "mode": "announce",
    "channel": "last"
  },
  "enabled": true
}
```

## Verification Steps

### At Every Session Start

Your agent should automatically verify:

1. **Check cron jobs exist:**
   ```
   List my cron jobs
   ```
   
   You MUST see both:
   - `prayer-times:daily-fetch`
   - `prayer-times:reminder-check`

2. **Check prayer times file exists:**
   ```bash
   ls -lh prayer_times.json
   ```
   
   Should show today's file with recent timestamp.

3. **Test reminder check:**
   ```bash
   python3 check_prayer_reminder.py --prayer-times prayer_times.json --timezone YOUR_OFFSET
   ```
   
   Should return exit code 0 (no reminder) or 1 (reminder message).

### If Anything is Missing

**DO NOT WAIT. FIX IMMEDIATELY.**

The agent should:
1. Recreate missing cron jobs
2. Fetch prayer times if file is missing
3. Test the system
4. Confirm everything works

## Why This Matters

Missing a prayer reminder is a CRITICAL FAILURE. Prayer is not optional - it's the foundation of faith. The system must be 100% reliable.

### What Can Go Wrong

1. **Cron job deleted accidentally** - Agent must recreate at session start
2. **Prayer times file missing** - Agent must fetch immediately
3. **Wrong timezone** - Reminders at wrong times
4. **Check interval too long** - Might miss reminder windows
5. **Delivery mode = "none"** - Reminders never sent

## Integration with AGENTS.md

Add this to your `AGENTS.md`:

```markdown
## Every Session

**🕌 SALAT FIRST - CRITICAL CHECK**

Before doing ANYTHING else, verify prayer reminder system is active:
1. Check if cron job `prayer-times:reminder-check` exists and is enabled
2. If missing, recreate immediately - don't wait, don't ask
3. Verify prayer times file exists and is recent
4. If file missing, run fetch script immediately

Prayer is [User]'s first priority. Never let them miss Salat due to technical failures.
```

## Testing the System

### Manual Test

1. **Check current time vs next prayer:**
   ```bash
   python3 get_prayer_times.py --city YOUR_CITY --country YOUR_COUNTRY --next --timezone YOUR_OFFSET
   ```

2. **Force a reminder check:**
   ```bash
   python3 check_prayer_reminder.py --prayer-times prayer_times.json --timezone YOUR_OFFSET
   ```

3. **Verify cron job schedule:**
   ```
   Show me when my prayer-times:reminder-check will run next
   ```

### What to Expect

- **Before reminder window:** Script returns exit code 0, HEARTBEAT_OK
- **Inside reminder window:** Script returns exit code 1 + message
- **Prayer times missing:** Script returns exit code 2 + error

## Recovery Procedures

### If You Missed a Prayer Reminder

1. **Check cron jobs:**
   ```
   List my cron jobs
   ```

2. **Check last run:**
   ```
   Show me the last runs of prayer-times:reminder-check
   ```

3. **Recreate if missing:**
   Use the cron job definitions above

4. **Test immediately:**
   Run manual check to confirm it works

### If Prayer Times are Wrong

1. **Verify your location:**
   ```bash
   cat prayer_times.json
   ```

2. **Check calculation method:**
   Should match your country (see methods.md)

3. **Refetch with correct location:**
   ```bash
   python3 get_prayer_times.py --city YOUR_CITY --country YOUR_COUNTRY --json > prayer_times.json
   ```

## Support

If the system fails:
1. Check this guide first
2. Verify cron jobs exist and are enabled
3. Check prayer times file is recent
4. Test manually with the scripts
5. Recreate cron jobs if needed

**Never accept "it should work" - TEST and VERIFY.**

---

> "Indeed, prayer has been decreed upon the believers at specified times." - Quran 4:103

May Allah help us maintain our Salat 🤲
