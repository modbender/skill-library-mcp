---
name: apple-watch
description: |
  Apple Watch health data sync via Health Auto Export app.
  Use when querying sleep, heart rate, steps, workouts, or any health metrics.
  Also use when setting up or troubleshooting the health data pipeline.
metadata: {"openclaw":{"requires":{"bins":["python"]}}}
---

# Agent Instructions

This skill has TWO parts: PC setup (automated) and Phone setup (requires user action).
Do NOT just run setup.py and say "done". You MUST walk the user through the full flow.

## Before setup: confirm prerequisites with user

Ask the user to confirm ALL of these before proceeding:

- [ ] Do you have an Apple Watch?
- [ ] Do you have an iPhone paired with it?
- [ ] Have you installed [Health Auto Export](https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069) app?
- [ ] Are your iPhone and PC on the same Wi-Fi?

If any is missing, help them resolve it first. Do NOT run setup.py until all are confirmed.

## Setup flow

### Step 1: Run setup.py
Run `python scripts/setup.py` - generates server, dashboard, API key, and phone templates.
setup.py does NOT start the server. You must start it yourself in step 2.

### Step 2: Start server as a persistent background service

The server MUST run independently of any agent session. Do NOT start it in an exec session
that will get killed by heartbeat or session recycling.

**Windows** - register as a startup task:
```powershell
$action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "server.py" -WorkingDirectory "<health-sync-dir>"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "HealthSyncServer" -Action $action -Trigger $trigger -RunLevel Highest -Force
Start-ScheduledTask -TaskName "HealthSyncServer"
```

**macOS** - use launchd plist:
```bash
cat > ~/Library/LaunchAgents/com.health-sync.server.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.health-sync.server</string>
  <key>ProgramArguments</key><array>
    <string>python3</string><string>server.py</string>
  </array>
  <key>WorkingDirectory</key><string>HEALTH_SYNC_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>HEALTH_SYNC_DIR/server.log</string>
  <key>StandardErrorPath</key><string>HEALTH_SYNC_DIR/server.log</string>
</dict>
</plist>
EOF
# replace HEALTH_SYNC_DIR with actual path, then:
launchctl load ~/Library/LaunchAgents/com.health-sync.server.plist
```

**Quick start (if you just need it running now, not persistent):**
```bash
# Windows
start /B pythonw.exe server.py
# macOS / Linux
nohup python3 server.py > server.log 2>&1 &
```

Before starting, kill anything already on port 3001:
```powershell
# Windows
(Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue).OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```
```bash
# macOS / Linux
lsof -ti:3001 | xargs kill -9 2>/dev/null
```

Verify it's running:
```bash
curl.exe -s -H "api-key: <key>" http://localhost:3001/api/summary
```
Note: on Windows use `curl.exe` (not `curl` which is a PowerShell alias for Invoke-WebRequest).

### Step 3: Phone side (YOU MUST GUIDE THE USER STEP by STEP，once confirm one step is ready then move on to the another)
After server is running, walk the user through phone configuration.
Read the API key from .env.json first - you will need to tell the user. SEND THE FILE TO USER.

1. Send the template JSON from `templates/` to the user's iPhone. If your IM channel supports file attachments, send the file directly. Otherwise, paste the key settings as text.
2. Tell the user to open the file on iPhone to import into Health Auto Export. SEND `tutorial_imgs/step1.png` with your message TO USER
   - This auto-fills URL, metrics, format, and sync settings.
3. **CRITICAL**: Tell the user to manually add the API key header after import. SEND `tutorial_imgs/step2.png`.with your message TO USER
   - Open the imported automation -> scroll to Headers -> tap "Add Header"
   - Key (left field): `api-key`
   - Value (right field): the API key from .env.json
   - Template import does NOT set headers. The user MUST do this step manually.(format: Key：xxx, Value：sk-xxx)
4. Tell the user to tap "Manual Export" to test. SEND `tutorial_imgs/step3.png`with your message TO USER
5. Verify data arrives: check /api/summary or /dashboard.
6. Only after data is confirmed arriving, tell the user setup is complete.

Fallback: if the user is confused by the template import flow, fall back to fully manual setup (Automations -> + -> REST API -> enter URL and header by hand). Only use this fallback when necessary.

### If already set up
If server.py and .env.json already exist:
1. Check if server is running on port 3001.
2. If running, check if data is flowing (/api/summary).
3. If yes, skip setup. If no, troubleshoot (server running? correct API key? phone on same WiFi?).

## Querying health data for the user

When the user asks about their health (sleep, heart rate, steps, etc.):

1. Read the API key from .env.json.
2. Query the API using `curl.exe` (NOT `curl` on Windows):
```bash
curl.exe -s -H "api-key: <KEY>" "http://localhost:3001/api/latest/metrics/sleep_analysis?n=3"
curl.exe -s -H "api-key: <KEY>" "http://localhost:3001/api/latest/metrics/heart_rate?n=5"
curl.exe -s -H "api-key: <KEY>" http://localhost:3001/api/summary
```
3. Summarize the data in a readable format for the user.

## Dashboard screenshots

When the user wants to see their health stats visually, or you want to proactively show a summary:
1. Open http://localhost:3001/dashboard in a browser or take a screenshot.
2. The dashboard shows cards for each metric with latest values and record counts.
3. Screenshot the dashboard and send it to the user as a visual health summary.

## Heartbeat integration

You can use your native heartbeat capability to periodically check the user's health data (e.g. detect wake-up, monitor heart rate). Add health check tasks to HEARTBEAT.md.

Example HEARTBEAT.md entry:
```markdown
## Health Check
- Query: curl.exe -s -H "api-key: <KEY>" "http://localhost:3001/api/latest/metrics/sleep_analysis?n=1"
- Query: curl.exe -s -H "api-key: <KEY>" "http://localhost:3001/api/latest/metrics/heart_rate?n=1"
- If sleep ended within last 2 hours: send wake-up greeting with sleep duration
- If no data or server not responding: reply HEARTBEAT_OK (do NOT try to restart server)
```

IMPORTANT for heartbeat:
- Use `curl.exe` not `curl` on Windows (avoid PowerShell alias issues).
- Do NOT start/restart the server from heartbeat. Server should be a persistent background service.
- Keep heartbeat health checks lightweight: 1-2 API calls max per heartbeat.

# Health Sync

Sync Apple Watch health data to your PC in real time.

## What you need

**Hardware:**
- Apple Watch (any model with watchOS 9+)
- iPhone (paired with the Apple Watch)
- A PC/Mac on the same Wi-Fi as your iPhone

**Software (phone side):**
- [Health Auto Export](https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069) app ($24.99 lifetime, one-time purchase)
  - This is the bridge: it reads Apple HealthKit data and pushes it over HTTP to your server
  - Free tier only does manual export; Premium enables automatic background sync

**Software (PC side):**
- Python 3.8+ (that's it, setup handles the rest)

## How it works

```
Apple Watch -> iPhone HealthKit -> Health Auto Export app -> HTTP POST -> Python server -> JSONL files
```

Your iPhone periodically sends health data as JSON to a lightweight Python server running on your PC.
The server stores everything as append-only JSONL files, queryable via REST API.

## One Click Setup

```bash
python scripts/setup.py
```

No git account needed. No Docker needed. Flask is auto-installed if missing.

Setup will:
1. Auto-install flask (if not already installed)
2. Generate a random API key -> .env.json (gitignored)
3. Download upstream repo (reference + optional Grafana dashboards)
4. Generate lightweight Python server
5. Generate web dashboard
6. Let you pick data types, generate phone automation templates
7. Print step-by-step phone configuration

## Phone Setup (after running setup.py)

1. Send the template JSON from `templates/` to your iPhone (AirDrop, email, etc.)
2. Open the file on iPhone -> import into Health Auto Export
   - This sets URL, metrics, format, sync interval etc. automatically
3. **Manually add the API key header** (template import does NOT set headers):
   - Open the imported automation -> scroll to Headers -> tap "Add Header"
   - Key (left field): `api-key`
   - Value (right field): your API key from `.env.json` (setup.py prints this)
4. Tap **Manual Export** to test
5. Check http://localhost:3001/dashboard for data

## Keep server running

The server must stay running to receive data from your phone.

**Windows** - scheduled task (survives reboot):
```powershell
$action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "server.py" -WorkingDirectory "<health-sync-dir>"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask -TaskName "HealthSyncServer" -Action $action -Trigger $trigger -RunLevel Highest -Force
```

**macOS** - launchd (survives reboot):
```bash
# create plist at ~/Library/LaunchAgents/com.health-sync.server.plist
# see Agent Instructions section for full plist template
launchctl load ~/Library/LaunchAgents/com.health-sync.server.plist
```

**Quick (non-persistent):**
```bash
# Windows
start /B pythonw.exe server.py
# macOS / Linux
nohup python3 server.py > server.log 2>&1 &
```

## Directory Structure

```
health-sync/
  SKILL.md           <- this file
  scripts/setup.py   <- one click setup
  server.py          <- receiver server (generated)
  dashboard.html     <- web dashboard (generated)
  .env.json          <- API key (auto-generated, gitignored)
  .gitignore         <- ignores .env.json, data/, upstream/
  data/              <- received health data
    metrics/         <- heart_rate.jsonl, sleep_analysis.jsonl, ...
    workouts/        <- workouts.jsonl
  templates/         <- phone automation config JSONs (importable)
  upstream/          <- original repo (Grafana dashboards, Docker setup)
```

## Server

```bash
python server.py
```

- Receives JSON POST on port 3001
- Dashboard at http://localhost:3001/dashboard
- API key: auto-generated on first setup, stored in .env.json

## Query data

API key is in .env.json (generated by setup.py). Use `curl.exe` on Windows:

```bash
# get your api key
python -c "import json; print(json.load(open('.env.json'))['api_key'])"

# summary of all data
curl.exe -s -H "api-key: YOUR_KEY" http://localhost:3001/api/summary

# latest N records
curl.exe -s -H "api-key: YOUR_KEY" "http://localhost:3001/api/latest/metrics/sleep_analysis?n=5"
curl.exe -s -H "api-key: YOUR_KEY" "http://localhost:3001/api/latest/metrics/heart_rate?n=10"
curl.exe -s -H "api-key: YOUR_KEY" "http://localhost:3001/api/latest/metrics/step_count?n=10"
```

## Key metrics

- sleep_analysis (sleep start/end, deep/rem/core/awake)
- heart_rate (min/avg/max bpm)
- resting_heart_rate
- step_count
- active_energy / basal_energy_burned
- heart_rate_variability
- blood_oxygen_saturation
- time_in_daylight
- headphone_audio_exposure

## Visualization

- Dashboard: http://localhost:3001/dashboard (auto-refresh every 30s, dark theme, card layout)
- Can screenshot the dashboard to send to user as visual health summary
- Grafana (optional, heavy): see upstream/README.md (requires Docker + MongoDB)

## Limitations

- iPhone must be unlocked for background auto-sync (iOS restriction)
- Phone and PC must be on the same Wi-Fi / LAN
- Server must be running on PC to receive data
- Health Auto Export Premium required for automatic sync ($24.99 lifetime), but they have a trail version
