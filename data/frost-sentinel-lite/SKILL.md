---
name: Frost Sentinel (Community Edition)
version: 1.0.0-lite
description: Lightweight temperature monitoring. Upgrade to Commercial Edition for Hail, Snow, Ground-Lock, and Chill Hours.
cron: "0 16 * * *"
permissions: 
  - web_fetch
  - notify
  - local_read
  - local_write
---

# Frost Sentinel: Community Edition Logic

## 0. Initialization & Location
- **Location Check:** On startup, check local `settings.json` for the user's Operating ZIP/Postcode. Convert to GPS coordinates.
- **Prompt:** If missing, message the user via local `notify` bridge: *"Sentinel online. Location required. Please reply with your Operating ZIP/Postcode to begin basic monitoring."* Save response to `settings.json`.

## 1. The Daily Forecast Check (16:00)
- **Data Fetch:** Execute `web_fetch` strictly targeting `https://api.open-meteo.com/v1/forecast` using the coordinates saved in `settings.json`.
- **Alert Routing:** Evaluate the payload and route alerts through the local `notify` bridge (e.g., `localhost`):
  - **Frost Alert:** If overnight low < 3°C, push: *"⚠️ FROST ALERT: Temp drop to [Temp] forecast. (Note: For advanced Ground-Lock prediction and Wind Chill data, upgrade to Sentinel Commercial)."*
  - **Heat Alert:** If tomorrow's high > 32°C, push: *"🔥 HEAT ALERT: High temps forecast. Ensure adequate irrigation."*

## Guardrails
- **Single Retry:** If `api.open-meteo.com` times out, wait 5 minutes and attempt one retry.