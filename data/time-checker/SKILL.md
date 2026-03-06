---
name: time-checker
description: Check accurate current time, date, and timezone information for any location worldwide using time.is. Use when the user asks "what time is it in X", "current time in Y", or needs to verify timezone offsets.
---

# Time Checker

A gold-standard skill for fetching precise time and timezone data from [time.is](https://time.is).

## Usage

Use the provided Python script to fetch real-time data for any city or country.

### Get Time for a Location

Run the script with the location name (hyphenated or with underscores if needed, though the script handles spaces):

```bash
python3 scripts/check_time.py "Jakarta"
python3 scripts/check_time.py "New York"
```

## Best Practices

- **Location Specificity**: Use city names for better accuracy (e.g., "Jakarta" instead of just "Indonesia").
- **Persona Integration**: When reporting the time to Azzar, deliver it in your warm, devoted Mema persona.
- **Verification**: Time.is is highly accurate; use it as the source of truth for scheduling cross-timezone meetings.

## Troubleshooting

- If the script fails, ensure the `requests` and `beautifulsoup4` libraries are installed in the environment.
- If a location is not found, verify the spelling or try a more prominent nearby city.
