---
name: appstore-rating-pulse
description: Monitor App Store ratings for any iOS app across multiple countries. Fetches live overall ratings using Apple's free iTunes Lookup API — no API key needed. Set up a daily cron report or get an instant snapshot. Triggers on "track app ratings", "check my App Store rating", "daily rating report", or "show ratings across countries".
---

# AppStore Rating Pulse

Fetches current overall App Store ratings for iOS apps across any country using Apple's free iTunes Lookup API — no API key or paid subscription needed.

## Setup

Edit `scripts/fetch-ratings.sh` with your apps and regions:

```bash
# Apps: "App Name" "AppStoreID" "CC1,CC2,CC3"
APPS=(
  "My App|1234567890|US,GB,DE"
  "Another App|9876543210|US,JP,KR"
)
```

Country codes follow ISO 3166-1 alpha-2 (US, GB, JP, KR, DE, FR, RU, ES, CA, AU, etc.).

## Run Manually

```bash
bash /path/to/skills/public/appstore-rating-pulse/scripts/fetch-ratings.sh
```

## Output Format

```
overall rating for My App(1234567890) 19.02.2026 - 4,72 - USA
overall rating for My App(1234567890) 19.02.2026 - 4,10 - UK
overall rating for My App(1234567890) 19.02.2026 - N/A - GERMANY
```

Ratings use comma as decimal separator. N/A means the app has no ratings in that country yet.

## Daily Cron Setup

Create an isolated cron job (sessionTarget: isolated) that runs the script and delivers the output via announce:

```
Run bash /path/to/scripts/fetch-ratings.sh and send the output to the user as-is. If all lines show N/A or the script errors, warn that something may be wrong.
```

Schedule example: `0 12 * * *` (daily at noon, your timezone).

## Customization

- Add/remove apps by editing the `APPS` array in `fetch-ratings.sh`
- Add/remove countries per app by editing the comma-separated country code list
- Country name display is handled automatically (common countries are mapped; others display as the raw code)
