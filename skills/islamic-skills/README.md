# Islamic Companion Skill

**Unified tool for prayer times, fasting schedules, and Zakat calculations.**

This skill consolidates Islamic utilities into a single CLI with shared configuration and efficient caching.

## Features

- **Prayer Times:** Retrieve daily prayer times (Fajr, Dhuhr, Asr, Maghrib, Isha).
- **Fasting:** Check Imsak and Maghrib times for fasting.
- **Zakat:** Calculate Nisab thresholds for Gold and Silver based on current market prices.
- **Quran:** Search for verses by keyword or fetch specific Surah/Ayah with translation.
- **Calendar:** Generate a monthly prayer schedule for any city.
- **Quotes:** Fetch and display random Islamic quotes or setup daily automation.
- **Scheduler:** Generate OpenClaw cron commands to schedule daily prayer reminders.
- **Caching:** Minimizes API calls by caching daily results locally.

## Usage

Run the CLI using the bash script:

```bash
# Get today's prayer times
./bin/islamic-companion prayer --today

# Setup daily quote automation
./bin/islamic-companion quotes --setup

# Get a random quote
./bin/islamic-companion quotes --random

# Get monthly calendar (Example: Serang, Banten)
./bin/islamic-companion calendar --city "Serang" --month 2 --year 2026

# Sync prayer schedule to cron (generates commands)
./bin/islamic-companion prayer --sync

# Check fasting times (Imsak/Maghrib)
./bin/islamic-companion fasting --today

# Check Zakat Nisab values
./bin/islamic-companion zakat --nisab

# Search Quran for keyword
./bin/islamic-companion quran --search "sabar"

# Get specific Surah (e.g., Al-Fatihah)
./bin/islamic-companion quran --surah 1

# Get specific Ayah (e.g., Al-Baqarah:255)
./bin/islamic-companion quran --surah 2 --ayah 255
```

## Configuration

Edit `skills/islamic-companion/config.json` to set your location and calculation method.
Note: `config.bash` is auto-generated from `config.json` for performance.

```json
{
  "location": {
    "latitude": -6.2088,
    "longitude": 106.8456,
    "name": "Jakarta"
  },
  "calculation": {
    "method": 20,
    "school": 0
  },
  "zakat": {
    "currency": "IDR",
    "gold_gram_threshold": 85,
    "api_key": ""
  },
  "quran_language": "id"
}
```

### Calculation Methods
- **Method 20:** Kemenag RI (Indonesia)
- **School 0:** Standard (Shafi, Maliki, Hanbali)
- **School 1:** Hanafi

## Dependencies

- `bash`
- `curl`
- `jq` (Recommended for best performance, but limited fallback available)
