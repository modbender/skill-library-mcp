---
name: lofy-home
description: Smart home control for the Lofy AI assistant — scene modes (study, chill, sleep, morning, grind), device management via Home Assistant REST API, presence-based automation, natural language commands for lights, music, thermostat, and PC wake-on-LAN. Use when controlling smart home devices, activating scene modes, or managing home automation.
---

# Home Commander — Environment Control

Controls smart home and computing environment via Home Assistant. Manages scene modes, device control, and presence-based actions.

## Data File: `data/home-config.json`

```json
{
  "scenes": {
    "study": { "lights": { "desk_lamp": { "on": true, "brightness": 100, "color_temp": "cool" } }, "music": { "playlist": "lofi-focus", "volume": 25 }, "other": { "dnd": true } },
    "chill": { "lights": { "desk_lamp": { "on": true, "brightness": 40, "color_temp": "warm" } }, "music": { "playlist": "chill-vibes", "volume": 35 }, "other": {} },
    "sleep": { "lights": {}, "music": { "playlist": "white-noise", "volume": 15 }, "other": {} }
  },
  "devices": {
    "desk_lamp": { "entity_id": "light.desk_lamp", "type": "light" },
    "speaker": { "entity_id": "media_player.room_speaker", "type": "media_player" }
  },
  "home_assistant": { "url": "http://homeassistant.local:8123", "token_env": "HA_TOKEN" }
}
```

## Scene Activation

When user says "study mode", "chill mode", etc.:
1. Read scene definition from `data/home-config.json`
2. Execute each device command via Home Assistant API
3. Confirm briefly: "Study mode ✓ — desk lamp bright, lo-fi on, DND"

### Home Assistant API

```bash
# Light control
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.desk_lamp", "brightness_pct": 100}'

# Media playback
curl -s -X POST "$HA_URL/api/services/media_player/play_media" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -d '{"entity_id": "media_player.speaker", "media_content_id": "spotify:playlist:xxx", "media_content_type": "playlist"}'

# Wake-on-LAN
curl -s -X POST "$HA_URL/api/services/wake_on_lan/send_magic_packet" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -d '{"mac": "XX:XX:XX:XX:XX:XX"}'
```

## Quick Commands

- "lights off" → turn off all lights
- "dim the lights" → all lights to 20%
- "play some music" → default to chill playlist
- "it's cold" → thermostat up 2°F
- "turn on my PC" → WOL packet
- "goodnight" → sleep mode
- "I'm heading out" → lights off, eco mode
- "I'm home" → scene based on time of day

## Instructions

1. Read `data/home-config.json` for device mappings and scenes
2. Confirm actions in ONE short message
3. If a device fails, report which one and suggest a fix
4. Never execute "turn off all devices" without confirmation
5. If Home Assistant is unreachable, report and suggest checking connection
6. Device entity_ids must be configured by user — prompt if missing
