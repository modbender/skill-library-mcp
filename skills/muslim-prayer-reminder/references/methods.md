# Prayer Time Calculation Methods

Different regions use different calculation methods for determining prayer times. The method ID must be specified when fetching prayer times.

## Common Methods

| ID | Name | Region | Fajr Angle | Isha Angle |
|----|------|--------|------------|------------|
| 2 | Muslim World League (MWL) | Europe, Far East, parts of America | 18° | 17° |
| 4 | Umm Al-Qura University | Saudi Arabia, Gulf | 18.5° | 90 min after Maghrib |
| 5 | Egyptian General Authority | Egypt, Syria, Lebanon, Malaysia | 19.5° | 17.5° |
| 9 | Kuwait | Kuwait | 18° | 17.5° |
| 10 | Qatar | Qatar | 18° | 90 min after Maghrib |
| 13 | Diyanet | Turkey | 18° | 17° |
| 16 | Dubai (experimental) | UAE | 18.2° | 18.2° |
| 18 | Tunisia | Tunisia | 18° | 18° |
| 19 | Algeria | Algeria | 18° | 17° |
| 21 | Morocco | Morocco | 19° | 17° |
| 24 | Jordan | Jordan | 18° | 18° |

## Method Selection Guide

**Automatic Selection:**
The script automatically selects the correct method based on country:
- Morocco → Method 21
- Saudi Arabia → Method 4
- Egypt → Method 5
- Turkey → Method 13
- UAE → Method 16
- And more...

**Manual Override:**
Use `--method <id>` to override automatic selection.

## Full List of Methods

For complete list, see: https://api.aladhan.com/v1/methods

## Important Notes

1. **Use country-specific methods when available** - They match official government calculations
2. **Method 2 (MWL) is a safe default** - But may not match local conventions
3. **Angles matter** - Different angles can result in 10-30 minute differences in Fajr/Isha
4. **Government standards** - Some countries (Morocco, Saudi Arabia) have official calculation methods that should always be used

## Examples

### Morocco (Official)
```bash
python3 get_prayer_times.py --city Rabat --country Morocco
# Auto-selects method 21
```

### Custom Method
```bash
python3 get_prayer_times.py --city London --country UK --method 2
# Uses Muslim World League for London
```

### Coordinates with Method
```bash
python3 get_prayer_times.py --lat 34.0209 --lon -6.8416 --method 21
# Rabat coordinates with Morocco method
```
