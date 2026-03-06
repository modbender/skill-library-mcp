---
name: prayer-times
description: Get accurate Islamic prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha) for any location worldwide using official calculation methods. Use when users ask about prayer times, Salat schedules, next prayer, or need to set up automated prayer reminders. Includes automated background reminder system that alerts users 10 minutes before, at prayer time, and 5 minutes after - even during conversations. Supports 20+ country-specific calculation methods including Morocco, Saudi Arabia, Egypt, Turkey, UAE, and more.
---

# Prayer Times Skill

Get accurate Islamic prayer times for any location using the AlAdhan API with region-specific calculation methods, plus automated reminders that work in the background.

## Two Ways to Use This Skill

### 1. Query Prayer Times (Instant)
Ask about prayer times for any location, get next prayer info, or check specific dates.

### 2. Automated Reminders (Background)
Set up cron jobs that fetch daily prayer times and check periodically for reminders. Alerts you:
- **10 minutes before** prayer time
- **At prayer time** ("Salat First")
- **5 minutes after** (if you're still chatting)

**To set up reminders:** See [references/setup-reminders.md](references/setup-reminders.md) for complete guide.

## Quick Start

### Get today's prayer times

**By city and country:**
```bash
cd scripts/
python3 get_prayer_times.py --city Mecca --country "Saudi Arabia"
python3 get_prayer_times.py --city Istanbul --country Turkey
python3 get_prayer_times.py --city Cairo --country Egypt
```

**By coordinates:**
```bash
python3 get_prayer_times.py --lat 21.4225 --lon 39.8262  # Mecca
```

**With next prayer info:**
```bash
python3 get_prayer_times.py --city Istanbul --country Turkey --next --timezone 3
```

### Output
```
📍 Mecca, Saudi Arabia
📆 10 Feb 2026
🌙 22-08-1447
🔢 Method: 4

🕌 Fajr     05:37
🌅 Sunrise  06:54
🕌 Dhuhr    12:35
🕌 Asr      15:50
🕌 Maghrib  18:16
🕌 Isha     19:46

⏳ Next: Maghrib at 18:16 (in 15 minutes)
```

## Calculation Methods

The script **automatically selects** the correct calculation method based on country:

- **Morocco** → Method 21 (official)
- **Saudi Arabia** → Method 4 (Umm Al-Qura)
- **Egypt** → Method 5 (Egyptian Authority)
- **Turkey** → Method 13 (Diyanet)
- **UAE** → Method 16 (Dubai)
- And 15+ more countries...

**When to override:** Only specify `--method` if you need a different calculation than the country default.

For full method list and details, see [references/methods.md](references/methods.md).

## Script Reference

### `get_prayer_times.py`

**Location:** `scripts/get_prayer_times.py`

**Purpose:** Fetch prayer times for any location.

**Arguments:**
- `--city <name>` - City name (e.g., "Rabat")
- `--country <name>` - Country name (e.g., "Morocco")
- `--lat <float>` - Latitude coordinate
- `--lon <float>` - Longitude coordinate
- `--method <id>` - Calculation method ID (1-24, optional)
- `--date <DD-MM-YYYY>` - Specific date (optional, defaults to today)
- `--timezone <hours>` - Timezone offset from UTC for "next prayer" calculation
- `--next` - Show next prayer and time remaining
- `--json` - Output as JSON

**Returns:**
- Exit code 0 on success
- Exit code 1 on failure
- JSON or formatted text output

### `check_prayer_reminder.py`

**Location:** `scripts/check_prayer_reminder.py`

**Purpose:** Check if it's time to send a prayer reminder. Designed for periodic cron execution.

**Arguments:**
- `--prayer-times <path>` - Path to prayer_times.json file (required)
- `--timezone <hours>` - Timezone offset from UTC (required)
- `--json` - Output as JSON

**Returns:**
- Exit code 0 - No reminder needed
- Exit code 1 - Reminder needed (message printed to stdout)
- Exit code 2 - Error loading prayer times

**Reminder Windows:**
- **Before:** 9-11 minutes before prayer time
- **Now:** -1 to +2 minutes from prayer time
- **After:** 4-6 minutes after prayer time

## Common Usage Patterns

### 1. Get prayer times for user's city
```bash
python3 get_prayer_times.py --city "User's City" --country "User's Country" --next --timezone <offset>
```

### 2. Set up automated daily fetch
```python
from get_prayer_times import get_prayer_times
import json

# Fetch and save
times = get_prayer_times(city="Rabat", country="Morocco")
with open('prayer_times.json', 'w') as f:
    json.dump(times, f)
```

### 3. Check next prayer
```python
from get_prayer_times import get_prayer_times, get_next_prayer

times = get_prayer_times(city="Rabat", country="Morocco")
next_prayer = get_next_prayer(times, timezone_offset=1)  # GMT+1 for Morocco

print(f"Next: {next_prayer['name']} in {next_prayer['hours_until']}h {next_prayer['minutes_until']}m")
```

### 4. Set up automated reminders (recommended)

**Complete setup guide:** [references/setup-reminders.md](references/setup-reminders.md)

**Quick setup:**
1. Create daily fetch job (runs at midnight):
   - Fetches today's prayer times
   - Saves to `prayer_times.json`

2. Create reminder check job (runs every 5 min):
   - Checks if it's time to remind
   - Sends alert to active session
   - Three-stage reminders: before, during, after

**Example prompts to set up:**
```
Set up prayer time reminders for Mecca, Saudi Arabia (GMT+3). 
Fetch daily at midnight and check every 5 minutes.
```

```
Set up prayer time reminders for Istanbul, Turkey (GMT+3). 
Fetch daily at midnight and check every 5 minutes.
```

```
Set up prayer time reminders for Cairo, Egypt (GMT+2). 
Fetch daily at midnight and check every 5 minutes.
```

This enables background reminders even while chatting - you'll never miss Salat!

## Important Notes

### Network Requirements
The AlAdhan API (api.aladhan.com) may be unreachable from some datacenter IPs (e.g., DigitalOcean → Hetzner routing issues).

**Solution:** Use Cloudflare WARP or similar VPN to route traffic through Cloudflare's network.

**Quick fix:**
```bash
# Install Cloudflare WARP
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt update && sudo apt install cloudflare-warp
warp-cli register
warp-cli connect
```

### Accuracy
- Always use country-specific methods when available (e.g., method 21 for Morocco)
- Coordinates provide more accurate results than city names
- Times are in 24-hour format (HH:MM)

### Timezones
The API returns times in **local time** for the queried location. When calculating "time until next prayer", use the appropriate timezone offset.

## API Source
- **Provider:** AlAdhan (Islamic Network)
- **Endpoint:** https://api.aladhan.com
- **Documentation:** https://aladhan.com/prayer-times-api
- **Free tier:** No API key required, rate limited
- **Reliability:** High (99%+ uptime)

## Examples

### Example 1: User asks "What are the prayer times in Mecca?"
```bash
python3 get_prayer_times.py --city Mecca --country "Saudi Arabia"
```

### Example 2: User asks "When is the next prayer?"
```bash
python3 get_prayer_times.py --city Istanbul --country Turkey --next --timezone 3
```

### Example 3: User provides coordinates
```bash
python3 get_prayer_times.py --lat 40.7128 --lon -74.0060 --next --timezone -5
# New York coordinates
```

### Example 4: User wants specific date
```bash
python3 get_prayer_times.py --city Cairo --country Egypt --date 15-03-2026
```

## Testing the Skill

Test the script locally:
```bash
cd scripts/
python3 get_prayer_times.py --city Rabat --country Morocco --next --timezone 1
```

Expected output should show 5 prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha) plus Sunrise, and indicate the next upcoming prayer if `--next` is used.
