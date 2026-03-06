---
name: prayer-times
version: 1.0.0
description: Get instant, accurate Islamic prayer times for any location worldwide. Auto-detects your city or accepts any city/country name globally. Handles typos with smart fuzzy search. Shows Fajr, Sunrise, Dhuhr, Asr, Maghrib, and Isha times in 12-hour format. Works anywhere - UK, USA, Middle East, Asia, Europe, Australia, Africa. Uses ISNA calculation method via Aladhan API. Perfect for Muslims worldwide checking daily salah times.
---

# Prayer Times (Global)

Get instant, accurate Islamic prayer times for any location worldwide. Auto-detects your city or accepts any city/country name. Handles typos with smart fuzzy search. Perfect for Muslims anywhere in the world.

## Usage

**Auto-detect your location:**
```
prayer times
prayer times today
what time is prayer?
```

**Any city worldwide:**
```
prayer times Makkah
prayer times Madinah
prayer times Dubai
prayer times London
prayer times New York
prayer times Karachi
prayer times Jakarta
prayer times Istanbul
prayer times Sydney
```

**Specific prayers:**
```
Asr in Dubai
Maghrib in Makkah
Fajr in Cairo
Dhuhr in New York
Isha in Kuala Lumpur
```

Works with typos: "Meca", "Dubay", "Istanbol" - fuzzy search finds it!

## Features

✅ Auto-detects your location (via IP)
✅ Works for ANY city worldwide
✅ Handles typos and misspellings
✅ Shows location clearly at top of results
✅ 12-hour format (AM/PM)
✅ Uses ISNA calculation method

## Examples
```bash
python prayer_times.py
# Auto-detects and shows times

python prayer_times.py Makkah
# Shows times for Makkah, Saudi Arabia

python prayer_times.py "New York"
# Shows times for New York, USA

python prayer_times.py Dubai
# Shows times for Dubai, UAE

python prayer_times.py Istanbul
# Shows times for Istanbul, Turkey
```

## Supported Locations

**Anywhere in the world!** Examples:

- **Middle East:** Makkah, Madinah, Dubai, Riyadh, Jeddah, Cairo, Jerusalem, Amman, Doha, Kuwait City
- **Asia:** Karachi, Lahore, Dhaka, Jakarta, Kuala Lumpur, Singapore, Mumbai, Delhi, Islamabad
- **Europe:** London, Paris, Berlin, Amsterdam, Brussels, Rome, Madrid, Istanbul
- **UK:** Birmingham, Manchester, Leicester, Glasgow, Bradford, Leeds
- **Americas:** New York, Toronto, Chicago, Los Angeles, Houston, Montreal
- **Africa:** Cairo, Casablanca, Tunis, Nairobi, Johannesburg
- **Australia:** Sydney, Melbourne, Perth, Brisbane

## Data Sources

- **Location Detection:** ipapi.co (auto-detect from IP)
- **Geocoding:** OpenStreetMap Nominatim (global coverage)
- **Prayer Times:** Aladhan API (ISNA method)

## Permissions

- Internet access (to fetch location and prayer times)
- No file system access
- No personal data stored

## Output Format
```
============================================================
🕌 PRAYER TIMES - MAKKAH, SAUDI ARABIA
📅 08 Feb 2026
============================================================

Fajr:    05:12 AM
Sunrise: 06:34 AM
Dhuhr:   12:28 PM
Asr:     03:42 PM
Maghrib: 06:21 PM
Isha:    07:51 PM

============================================================
```

Location is displayed clearly at top with country name.

## Perfect For

- Muslims worldwide checking daily prayer times
- Travelers needing local times anywhere
- Expats checking times for home country
- Hajj/Umrah travelers (Makkah/Madinah times)
- Anyone planning travel to Muslim countries
- Students studying abroad
- Business travelers

## Version

1.0.0 - Initial release (Global coverage)