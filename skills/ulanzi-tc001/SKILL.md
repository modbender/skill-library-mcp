---
name: ulanzi-tc001
description: Control the Ulanzi TC001 (Pixel Clock) over local HTTP. Use to list tc1/tc001 commands, read status, enable/disable gadgets (time/date/youtube/matrix/etc.), or change settings like brightness, night mode, timezone, switch speed, or scroll speed. Trigger on commands starting with “tc1” or “tc001”.
---

# Ulanzi TC001

Control the Ulanzi TC001 Pixel Clock using its local HTTP endpoints (no browser needed).

## Quick start

1) Set the device IP in `config.json` (preferred):
```json
{ "host": "192.168.1.32" }
```

(Env fallback is supported: `TC001_HOST`)

2) Use the helper script:
```bash
python3 scripts/tc001.py status
python3 scripts/tc001.py gadgets list
python3 scripts/tc001.py gadget on youtube
python3 scripts/tc001.py brightness manual 80
python3 scripts/tc001.py nightmode on
python3 scripts/tc001.py timezone GMT-3
```

## Supported commands (script)

- `status` → JSON summary (sys settings + gadgets on/off)
- `gadgets list|on|off`
- `gadget on|off <name>`
- `brightness auto | manual <0-100>`
- `nightmode on|off | start HH:MM | end HH:MM`
- `timezone GMT-3 | AUTO` (see mapping in script)
- `switch <10|15|20|25|30|35|40|45|50|55|60|noswitch>`
- `scroll <0-10>`

### Full config (sys)
`sys <field> <value>` fields:
- language: `english|chinese`
- autobrightness: `auto|manual`
- brightness: `0-100`
- nightbrightness: `0-100`
- switchspeed: `noswitch|10|15|20|25|30|35|40|45|50|55|60`
- scrollspeed: `0-10`
- timezone: `GMT-3` (or `AUTO`)
- timeformat: `HH:mm|HH:mm:ss`
- dateformat: `DD/MM|MM/DD`
- showweek: `show|hide`
- firstday: `sunday|monday`
- nightmode: `on|off`
- nightstart: `HH:MM`
- nightend: `HH:MM`

### Full config (app)
`app <field> <value>` fields:
- citycode
- bilibili_uid / bilibili_animation / bilibili_color / bilibili_format
- weibo_uid / weibo_animation / weibo_color / weibo_format
- youtube_uid / youtube_apikey / youtube_animation / youtube_color / youtube_format
- douyin_uid / douyin_animation / douyin_color / douyin_format
- awtrix_server / awtrix_port
- showlocalip: `on|off`

Animations: `swipe|scroll` · Colors: `default|red|orange|yellow|green|cyan|blue|purple` · Format: `none|format`

## Gadgets (names)
`time, date, weather, bilibili, weibo, youtube, douyin, scoreboard, chronograph, tomato, battery, matrix, awtrix, localip`

## Notes
- Uses `POST /` and `POST /app_switch` with form data. See `references/tc001-api.md`.
- Keep YouTube API key private (if used).
