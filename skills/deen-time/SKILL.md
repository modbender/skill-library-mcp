---
name: deen-time
description: Get daily Islamic prayer (Salah) times, Iftar, and Suhoor schedules for any location worldwide. Supports 15+ calculation methods, Hijri dates, and Ramadan calendars.
metadata:
  openclaw:
    requires:
      bins:
        - curl
      env: []
    homepage: https://aladhan.com/prayer-times-api
user-invokable: true
disable-model-invocation: false
---

# Deen Time

Your daily Islamic prayer companion. Provides accurate Salah times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha) for any city or coordinates worldwide. During Ramadan, also provides Suhoor (pre-dawn meal) and Iftar (fast-breaking) schedules with full monthly calendars.

## When to Use This Skill

Use this skill when the user asks about:
- Prayer times for a specific location
- Iftar or Suhoor times
- Ramadan schedule or timetable
- When to break fast or start fasting
- Fajr, Dhuhr, Asr, Maghrib, or Isha times
- Islamic prayer schedule

## How It Works

This skill uses the **Aladhan Prayer Times API** (`https://aladhan.com/prayer-times-api`), a free and reliable public API that requires no authentication.

### Fetching Prayer Times by City

```bash
curl -L "https://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method={METHOD}"
```

Replace `{CITY}`, `{COUNTRY}`, and `{METHOD}` with actual values. URL-encode spaces (e.g., `New%20York`). Always use `-L` to follow redirects.

### Fetching Prayer Times by Coordinates

```bash
curl -L "https://api.aladhan.com/v1/timings/{DD-MM-YYYY}?latitude={LAT}&longitude={LNG}&method={METHOD}"
```

Use this when the user provides latitude/longitude or when a city name is ambiguous.

### Fetching a Full Monthly Calendar

```bash
curl -L "https://api.aladhan.com/v1/calendarByCity/{YEAR}/{MONTH}?city={CITY}&country={COUNTRY}&method={METHOD}"
```

Use this for Ramadan schedules. `{MONTH}` is the Gregorian month number (1-12).

## Calculation Methods

The `method` parameter controls prayer time calculation. Pick the most appropriate one based on the user's region:

| Method | Organization | Best For |
|--------|-------------|----------|
| 1 | University of Islamic Sciences, Karachi | Pakistan, Bangladesh, India |
| 2 | Islamic Society of North America (ISNA) | North America |
| 3 | Muslim World League (MWL) | Europe, Far East |
| 4 | Umm Al-Qura University, Makkah | Saudi Arabia, Gulf |
| 5 | Egyptian General Authority of Survey | Africa, Syria, Lebanon |
| 7 | Institute of Geophysics, University of Tehran | Iran |
| 8 | Gulf Region | UAE, Kuwait, Qatar |
| 9 | Kuwait | Kuwait |
| 10 | Qatar | Qatar |
| 11 | Majlis Ugama Islam Singapura | Singapore |
| 12 | Union Organization Islamic de France | France |
| 13 | Diyanet Isleri Baskanligi | Turkey |
| 14 | Spiritual Administration of Muslims of Russia | Russia |
| 15 | Moonsighting Committee Worldwide | Global (moonsighting-based) |

**Defaults**: Use method `2` for North America, `4` for Saudi/Gulf, `3` for Europe, `5` for Africa, `13` for Turkey, `1` for South Asia. If the user doesn't specify a preference, select based on their location.

## API Response Structure

The API returns JSON. The key fields to extract:

```json
{
  "data": {
    "timings": {
      "Fajr": "05:12",
      "Sunrise": "06:30",
      "Dhuhr": "12:15",
      "Asr": "15:30",
      "Maghrib": "18:00",
      "Isha": "19:20",
      "Imsak": "05:02"
    },
    "date": {
      "readable": "19 Feb 2026",
      "hijri": {
        "date": "02-09-1447",
        "month": { "number": 9, "en": "Ramadan" },
        "year": "1447"
      }
    }
  }
}
```

For the calendar endpoint, `data` is an array of day objects with the same structure.

## Presenting Results

### Daily Prayer Times

Display as a clean table:

```
Prayer Times for {City}, {Country}
Date: {Gregorian Date} | {Hijri Date}

| Prayer   | Time   |
|----------|--------|
| Fajr     | 05:12  |
| Sunrise  | 06:30  |
| Dhuhr    | 12:15  |
| Asr      | 15:30  |
| Maghrib  | 18:00  |
| Isha     | 19:20  |

Suhoor: Stop eating before 05:12 (Fajr). Recommended: 05:02 (Imsak).
Iftar: Break fast at 18:00 (Maghrib).
```

### Ramadan Monthly Schedule

For monthly requests, present a condensed table:

```
Ramadan Schedule for {City} — {Year}

| Day | Date       | Suhoor (Imsak) | Fajr  | Iftar (Maghrib) |
|-----|------------|-----------------|-------|-----------------|
| 1   | 17 Feb     | 05:02           | 05:12 | 17:45           |
| 2   | 18 Feb     | 05:01           | 05:11 | 17:46           |
| ... | ...        | ...             | ...   | ...             |
```

### Important Notes to Convey

- **Suhoor** must be completed before Fajr. The Imsak time (typically 10 min before Fajr) is the recommended cutoff.
- **Iftar** is at Maghrib (sunset).
- All times are in the **local timezone** of the requested location.
- If the user doesn't specify a location, ask for their city and country.
- If the user doesn't specify a date, use today's date.

## Example Interactions

**User**: "What are the prayer times for London today?"
→ Call: `curl -L "https://api.aladhan.com/v1/timingsByCity?city=London&country=United%20Kingdom&method=3"`
→ Display all prayer times in a formatted table with both Gregorian and Hijri dates.

**User**: "When is Iftar in Dubai?"
→ Call: `curl -L "https://api.aladhan.com/v1/timingsByCity?city=Dubai&country=United%20Arab%20Emirates&method=4"`
→ Highlight the Maghrib time as the Iftar time.

**User**: "Give me the Ramadan schedule for Istanbul"
→ Determine the Gregorian months that overlap with Ramadan for the current year.
→ Call: `curl -L "https://api.aladhan.com/v1/calendarByCity/2026/2?city=Istanbul&country=Turkey&method=13"` (and March if Ramadan spans two months)
→ Filter to only Ramadan days (check Hijri month = 9 / Ramadan) and present the Suhoor/Iftar table.

**User**: "Suhoor time for New York?"
→ Call: `curl -L "https://api.aladhan.com/v1/timingsByCity?city=New%20York&country=United%20States&method=2"`
→ Show the Imsak and Fajr times. Recommend stopping eating at Imsak (10 min before Fajr).

**User**: "Prayer times for coordinates 21.4225, 39.8262"
→ Call: `curl -L "https://api.aladhan.com/v1/timings/19-02-2026?latitude=21.4225&longitude=39.8262&method=4"`
→ Display full prayer times (these coordinates are Makkah, so use Umm Al-Qura method).

## Privacy and Data Handling

This skill makes **read-only HTTPS requests** to the [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api), a well-known, free, public Islamic prayer times service.

- **Data sent**: Only the city/country name or coordinates provided by the user, plus a calculation method number. No personal data, credentials, or device information is transmitted.
- **Data received**: Prayer times (JSON) for the requested location and date. No tracking, cookies, or user profiling.
- **No authentication**: The API requires no API keys, tokens, or accounts.
- **No data storage**: This skill does not write to disk, store user data, or maintain any state between invocations.
- **Single domain**: All network requests go exclusively to `api.aladhan.com` over HTTPS. No other external endpoints are contacted.
