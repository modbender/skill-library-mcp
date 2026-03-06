---
name: birdbuddy
description: Query your Bird Buddy smart bird feeder - check status, battery, food level, and see recent bird visitors with species identification.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - BIRDBUDDY_EMAIL
        - BIRDBUDDY_PASSWORD
      bins:
        - python3
    primaryEnv: BIRDBUDDY_EMAIL
    emoji: "🐦"
    homepage: https://github.com/jhansche/pybirdbuddy
---

# Bird Buddy Skill

Query your Bird Buddy smart bird feeder. Check feeder status, see recent bird visitors with species names, and fetch sighting photos.

## Requirements
- `pybirdbuddy` Python package: `pip install pybirdbuddy`
- `BIRDBUDDY_EMAIL` and `BIRDBUDDY_PASSWORD` environment variables (email/password login only — Google SSO not supported)

## Commands

### Check feeder status (battery, food, signal)
```bash
python3 {skillDir}/run.py status
```

### Get recent bird sightings with species names
```bash
python3 {skillDir}/run.py recent [hours=24] [limit=5]
```

### Get raw postcard feed
```bash
python3 {skillDir}/run.py feed [hours=24]
```

### Get full details and photo URLs for a specific postcard
```bash
python3 {skillDir}/run.py sighting <postcard_id>
```

## Example agent interactions
- "What birds visited my feeder today?" → `recent 24 10`
- "How is my Bird Buddy doing?" → `status`
- "Show me photos from the last visit" → `recent 24 1` then `sighting <id>`
- "What was the last bird at my feeder?" → `recent 1 1`
