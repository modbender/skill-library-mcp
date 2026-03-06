# Deen Time

Your daily Islamic prayer companion for OpenClaw. Get accurate Salah times, Iftar/Suhoor schedules, and full Ramadan calendars for any location worldwide.

## Features

- **Daily Salah times**: Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha — works year-round
- **Suhoor & Iftar times**: With Imsak (recommended cutoff) for fasting days
- **City or coordinates**: Look up by city name or lat/lng
- **Monthly Ramadan calendar**: Full month Suhoor/Iftar schedule in one query
- **15+ calculation methods**: ISNA, MWL, Umm Al-Qura, Egyptian, Diyanet, and more — auto-selected by region
- **Hijri dates**: Displays both Gregorian and Islamic calendar dates

## Usage

Once installed, just ask your OpenClaw agent:

- "What are the prayer times for London?"
- "When is Maghrib in Calgary?"
- "Iftar time for Dubai"
- "Give me the Ramadan schedule for Istanbul"
- "Suhoor time for New York?"

## Installation

```bash
clawhub install deen-time
```

## API

Powered by the [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api) — free, public, and requires no API key.

## Security and Privacy

- All API calls are **read-only HTTPS** requests to `api.aladhan.com`
- Only city/country names or coordinates are sent — **no personal data**
- No API keys, authentication, or credentials required
- No data is stored or written to disk

## License

MIT
