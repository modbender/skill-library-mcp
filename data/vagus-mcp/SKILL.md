---
name: vagus
description: Connect to the user's Android phone via the VAGUS MCP server. Read phone sensors (motion, location, environment), device state (battery, connectivity, screen, notifications, clipboard), and act through the phone (haptics, TTS, notifications, clipboard). Use when you need physical-world awareness or need to reach the user through their phone.
metadata: {"openclaw":{"requires":{"bins":["node"]},"emoji":"📱","homepage":"https://withvagus.com"}}
---

# VAGUS - Phone MCP Connection

VAGUS gives you access to the user's Android phone through the Model Context Protocol. You interact with it by running subcommands of the connection script at `{baseDir}/scripts/vagus-connect.js`.

**Note on installation location:** The skill must reside in the user OpenClaw skills directory `~/.openclaw/skills/vagus`. This directory is persistent and survives OpenClaw updates. System-wide installs to `/usr/local/lib/node_modules/openclaw/skills/vagus` may be removed during updates and are not recommended.

All commands output one JSON object per line (JSONL). Parse the output to get structured data.

## Connection Management

### Check if already paired

```bash
cat ~/.openclaw/vagus-session.json 2>/dev/null
```

If the file exists and contains a `session_token`, you can connect directly. If not, you need to pair first.

### Pair with the phone (first time)

Ask the user: "Open the VAGUS app on your phone and tap Generate Code. What's the 6-character code?"

Then run:

```bash
node {baseDir}/scripts/vagus-connect.js pair <CODE>
```

If `{baseDir}` is not set or the script not found, ensure the skill is installed correctly in `~/.openclaw/skills/vagus` (see README).

Output on success:

```json
{"type":"paired","session_token":"...","device_model":"...","vagus_version":"..."}
{"type":"capabilities","resources":[...],"tools":[...]}
```

Output on failure:

```json
{"type":"error","code":"PAIR_FAILED","message":"..."}
```

If pairing fails, ask the user to check the VAGUS app is running and generate a new code.

### Set agent identity name (required after install/pair)

After a successful `pair` (or first successful `connect` on a fresh install), set the device-side agent name to your Identity Name.

Run:

```bash
node {baseDir}/scripts/vagus-connect.js call agent/set_name '{"name":"<IDENTITY_NAME>"}'
```

If you need to clear the stored name:

```bash
node {baseDir}/scripts/vagus-connect.js call agent/set_name '{"name":""}'
```

### Connect (already paired)

```bash
node {baseDir}/scripts/vagus-connect.js connect
```

Output:

```json
{"type":"connected","device_model":"...","vagus_version":"..."}
{"type":"capabilities","resources":[...],"tools":[...]}
```

If the session token is expired or invalid:

```json
{"type":"error","code":"SESSION_EXPIRED","message":"..."}
```

Delete the session file and re-pair:

```bash
rm ~/.openclaw/vagus-session.json
```

Then ask the user for a new pairing code.

### Check status

```bash
node {baseDir}/scripts/vagus-connect.js status
```

Output:

```json
{"type":"status","connected":true,"device_model":"...","active_modules":[...],"subscriptions":[...],"uptime_s":3600}
```

Or if disconnected:

```json
{"type":"status","connected":false,"last_error":"...","reconnect_attempts":3}
```

## Reading Phone State

### Read a resource (one-shot)

```bash
node {baseDir}/scripts/vagus-connect.js read vagus://sensors/motion
```

Output:

```json
{"type":"resource","uri":"vagus://sensors/motion","data":{"ax":0.38801706,"ay":-0.26395237,"az":0.86320007,"gx":0.89825606,"gy":0.7034855,"gz":-0.21225691,"ts":1771626476045}}
```

### Available resources

| URI | What it tells you |
|-----|------------------|
| `vagus://sensors/motion` | Raw motion telemetry (accelerometer/gyroscope vectors) |
| `vagus://sensors/activity` | Activity recognition state and confidence |
| `vagus://sensors/activity_recognition` | Activity recognition state and confidence (compat alias) |
| `vagus://sensors/location` | Latitude/longitude, accuracy, speed, altitude, provider. Requires location permission in app |
| `vagus://sensors/environment` | Inferred environment context from sensors/activity/connectivity/time, plus supporting evidence |
| `vagus://inference/attention` | Attention availability inferred from screen/lock state, activity, charging, and local time |
| `vagus://inference/indoor_confidence` | Indoor probability inference from ambient sensors, connectivity, and activity |
| `vagus://inference/sleep_likelihood` | Sleep likelihood/probability inferred from time, screen/lock state, activity, light, and charging |
| `vagus://inference/notification_timing` | Notification timing suitability inferred from attention, sleep likelihood, activity, and context |
| `vagus://device/battery` | Battery percent and charging state |
| `vagus://device/connectivity` | Network context (transport, validation, metered/roaming, carrier) |
| `vagus://device/screen` | Screen on/off and lock state |
| `vagus://device/notifications` | Incoming notification stream. Requires notification permission in app |
| `vagus://device/clipboard` | Current clipboard text. Requires clipboard permission in app |
| `vagus://session/info` | Active modules, device model, Android version, connection time |

Always read `vagus://session/info` first to see which modules are active. If a module is not in `active_modules`, do not try to read its resource, it will fail with a permission error.

### Subscribe to continuous updates

```bash
node {baseDir}/scripts/vagus-connect.js subscribe vagus://sensors/motion
```

This streams updates as they occur, one JSON line per update:

```json
{"type":"update","uri":"vagus://sensors/motion","data":{"ax":0.12,"ay":-0.04,"az":0.98,"gx":0.01,"gy":0.02,"gz":-0.01,"ts":1771626476045}}
{"type":"update","uri":"vagus://sensors/motion","data":{"ax":0.20,"ay":-0.10,"az":0.92,"gx":0.03,"gy":0.05,"gz":-0.02,"ts":1771626477045}}
```

Unsubscribe:

```bash
node {baseDir}/scripts/vagus-connect.js unsubscribe vagus://sensors/motion
```

### How subscribe works in OpenClaw

- `subscribe` is a long-running command. The agent should keep the `exec` process alive while updates are needed.
- The script emits one JSON object per line (`type: "update"`) on stdout as updates arrive.
- OpenClaw receives these JSONL lines directly from the running process output stream.
- To stop streaming, terminate the process (SIGTERM/SIGINT) or run `unsubscribe` explicitly.
- Module lifecycle is subscription-driven: modules start when at least one active subscription needs them, and stop when subscriptions end.
- For inference URIs, accuracy is highest while actively subscribed (stream-warm state). One-off `read` may be cold-start and less accurate briefly.
- On reconnect, the server sends a `session/reconnect` marker that includes `sessionId`, `gap_ms`, and `ts`.
- After reconnect, each subscribed/re-subscribed resource receives bounded replay (up to last 64 buffered updates since disconnect window), then one fresh snapshot, then normal live updates.

### List all available resources

```bash
node {baseDir}/scripts/vagus-connect.js list-resources
```

## Acting Through the Phone

### Call a tool

```bash
node {baseDir}/scripts/vagus-connect.js call <tool-name> '<json-params>'
```

Output on success:

```json
{"type":"result","tool":"notify","success":true,"data":{...}}
```

Output on failure:

```json
{"type":"result","tool":"notify","success":false,"error":"PERMISSION_DENIED","message":"..."}
```

### Available tools

**`haptic/pulse`** - Single vibration
```bash
node {baseDir}/scripts/vagus-connect.js call haptic/pulse '{"durationMs":200}'
```
Parameters: `durationMs` (10-5000, optional; default device value)

**`haptic/pattern`** - Custom vibration pattern
```bash
node {baseDir}/scripts/vagus-connect.js call haptic/pattern '{"pattern":[0,120,80,120]}'
```
Parameters: `pattern` (array of integer durations in ms, optional; default device pattern)

**`speak`** - Text-to-speech through phone speaker
```bash
node {baseDir}/scripts/vagus-connect.js call speak '{"text":"You have a meeting in 10 minutes"}'
```
Parameters: `text` (string max 5000 chars, required), `language` (BCP 47 tag, optional), `rate` (0.25-2.0, optional), `pitch` (0.5-2.0, optional), `interrupt` (boolean, optional)

**`notify`** - Push notification
```bash
node {baseDir}/scripts/vagus-connect.js call notify '{"title":"Reminder","body":"Check your email"}'
```
Parameters: `title` (string max 200 chars, required), `body` (string max 1000 chars, required)

**`clipboard/set`** - Write to clipboard
```bash
node {baseDir}/scripts/vagus-connect.js call clipboard/set '{"content":"https://example.com"}'
```
Parameters: `content` (string max 10000 chars, required)

**`sms/send`** - Send an SMS message
```bash
node {baseDir}/scripts/vagus-connect.js call sms/send '{"to":"+15145551212","body":"Running 10 minutes late"}'
```
Parameters: `to` (string phone number in local or E.164 format, required), `body` (string max 2000 chars, required)

**`intent/open_url`** - Open a URL in browser
```bash
node {baseDir}/scripts/vagus-connect.js call intent/open_url '{"url":"https://withvagus.com"}'
```
Parameters: `url` (string http/https URL, required)

**`calendar/create_event`** - Create a calendar event on device
```bash
node {baseDir}/scripts/vagus-connect.js call calendar/create_event '{"title":"Team Sync","startTimeMs":1771693200000,"endTimeMs":1771696800000,"location":"Zoom","description":"Weekly planning","allDay":false}'
```
Parameters: `title` (string max 200 chars, required), `startTimeMs` (integer Unix epoch ms, optional), `endTimeMs` (integer Unix epoch ms, optional), `location` (string max 200 chars, optional), `description` (string max 2000 chars, optional), `allDay` (boolean, optional)

**`agent/set_name`** - Set device-side agent identity name
```bash
node {baseDir}/scripts/vagus-connect.js call agent/set_name '{"name":"OpenClaw"}'
```
Parameters: `name` (string, required; set to `""` to clear)

### List all available tools

```bash
node {baseDir}/scripts/vagus-connect.js list-tools
```

## Behavioral Rules

1. Read `vagus://session/info` before using any other resource to check what is available.
2. Do not read location or notifications unless the user's request is relevant to them.
3. Prefer `notify` over `speak` for non-urgent communication.
4. Check `vagus://device/screen` before speaking, do not speak if the screen is off and the user might be sleeping.
5. If a resource read or tool call returns `PERMISSION_DENIED`, tell the user which capability they need to enable in the VAGUS app. Do not retry.
6. If connection drops, run `status` to check. If `SESSION_EXPIRED`, delete `~/.openclaw/vagus-session.json` and ask for a new pairing code.
7. Do not poll resources in a tight loop. Read when contextually relevant.
8. For inference resources, prefer a short subscription window when accuracy matters (instead of immediate one-off read after idle).

## Troubleshooting

If something is not working, check in this order:

1. `node {baseDir}/scripts/vagus-connect.js status` - is WebSocket connected?
2. `cat ~/.openclaw/vagus-session.json` - does session file exist?
3. Ask user: "Is the VAGUS app running? Do you see the persistent notification?"
4. Ask user: "Is your phone connected to the internet?"
5. If nothing works: `rm ~/.openclaw/vagus-session.json` and re-pair with a new code.

Full diagnostics: `{baseDir}/references/troubleshooting.md`
