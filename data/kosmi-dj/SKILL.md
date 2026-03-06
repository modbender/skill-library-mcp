---
name: kosmi-dj
description: This skill should be used when the user asks to "play a video in Kosmi", "queue a video", "DJ in Kosmi", "start the video DJ", "loop videos in Kosmi", "connect to Kosmi room", "play YouTube in Kosmi", "stop the DJ loop", "add a video to the queue", "be my video DJ", or needs guidance on controlling a Kosmi watch party room via agent-browser automation.
---

# Kosmi Video DJ — agent-browser Automation Skill

This skill turns the agent into a video DJ for Kosmi watch party rooms. It uses `agent-browser` (Chromium automation via accessibility-tree snapshots) to navigate to a Kosmi room, queue videos by URL, and auto-loop playback.

## Prerequisites

- `agent-browser` CLI installed and on PATH (`npm install -g agent-browser` or available in the environment)
- A `.env` file at `${CLAUDE_PLUGIN_ROOT}/.env` containing room URL and credentials
- Persistent session support via `AGENT_BROWSER_SESSION_NAME` env var (keeps cookies/localStorage between runs)

## Environment Variables

Load from `${CLAUDE_PLUGIN_ROOT}/.env` before any agent-browser calls:

| Variable | Required | Description |
|---|---|---|
| `KOSMI_ROOM_URL` | Yes | Full URL to the Kosmi room (e.g. `https://app.kosmi.io/room/XXXXX`) |
| `KOSMI_EMAIL` | No | Login email (skip if using persistent session) |
| `KOSMI_PASSWORD` | No | Login password (skip if using persistent session) |
| `KOSMI_BOT_NAME` | No | Display name in room (default: `clawdbot`) |
| `AGENT_BROWSER_SESSION_NAME` | Yes | Session persistence key (default: `kosmi-dj-session`) |
| `AGENT_BROWSER_ENCRYPTION_KEY` | No | Hex key to encrypt stored session data |

## Core Workflow

### 1. Connect to Room

Execute `${CLAUDE_PLUGIN_ROOT}/skills/kosmi-dj/scripts/kosmi-connect.sh` to:

1. Open the Kosmi room URL in agent-browser
2. Wait for page load (800ms settle)
3. Take an accessibility snapshot to detect the current UI state
4. If a nickname/name prompt appears → fill with `KOSMI_BOT_NAME` and click Join
5. If a login prompt appears and credentials exist → fill email/password and submit
6. Verify connection by confirming room UI elements are present

### 2. Play a Video by URL

Execute `${CLAUDE_PLUGIN_ROOT}/skills/kosmi-dj/scripts/kosmi-play.sh <VIDEO_URL>` to:

1. Ensure connected (runs connect idempotently)
2. Open the Apps/media modal in Kosmi
3. Select the URL/link input mode
4. Fill the URL textbox with the provided video URL
5. Click Play (or press Enter as fallback)
6. Verify playback started by checking for player UI elements

### 3. Auto-Loop DJ Mode

Execute `${CLAUDE_PLUGIN_ROOT}/skills/kosmi-dj/scripts/kosmi-loop.sh` to:

1. Connect to the room
2. Enter a fetch→play→wait→repeat cycle:
   a. Retrieve a video URL (from a provided list, or agent finds one)
   b. Play the video
   c. Poll the room periodically to detect when the video ends (snapshot the player state)
   d. When ended, play the next video
3. Continue until interrupted or a stop signal is received

The loop script writes a PID file at `/tmp/kosmi-dj-loop.pid` for stop/status commands.

## agent-browser CLI Reference (Quick)

All browser automation goes through the `agent-browser` CLI. Key commands:

| Command | Usage | Purpose |
|---|---|---|
| `open <url>` | `agent-browser open "$URL"` | Navigate to URL |
| `snapshot` | `agent-browser snapshot -i -C --json` | Get interactive elements as JSON |
| `click <ref>` | `agent-browser click @ref123` | Click an element by ref ID |
| `fill <ref> <text>` | `agent-browser fill @ref123 "text"` | Fill a textbox |
| `press <key>` | `agent-browser press Enter` | Press a keyboard key |
| `wait <ms>` | `agent-browser wait 1000` | Wait/settle delay |

Snapshot output is JSON with `data.refs` — a map of `refId → { role, name }`. Use role + name matching to find UI elements. Always use the `-i` (interactive-only) and `-C` (cursor-interactive) flags for cleaner snapshots.

For detailed command reference, see `references/agent-browser-commands.md`.

## Snapshot-Based Element Discovery

Kosmi's UI is dynamic. Element ref IDs change between page loads. The correct approach:

1. Take a snapshot: `agent-browser snapshot -i -C --json`
2. Parse refs from `data.refs`
3. Find the target element by matching `role` (button, textbox, link) and `name` (case-insensitive substring match)
4. Use the ref ID (prefixed with `@`) for click/fill actions

For the Kosmi-specific UI element map (button names, modal flow), see `references/kosmi-ui-map.md`.

## Debug / Inspect

Run `${CLAUDE_PLUGIN_ROOT}/skills/kosmi-dj/scripts/kosmi-snapshot-debug.sh` to dump a human-readable snapshot of all interactive elements currently visible. Use this to discover exact button names and textbox labels in the Kosmi room.

## Error Handling

- If `agent-browser` is not installed, install it: `npm install -g agent-browser`
- If snapshot returns no refs, the page may still be loading — add a `wait 1500` and retry
- If the URL textbox is not found after opening the modal, Kosmi may have updated its UI — run the debug snapshot script and update `references/kosmi-ui-map.md`
- If login fails, check credentials in `.env` or delete the session to force re-auth:
  `agent-browser session delete kosmi-dj-session`

## Token Efficiency

For long-running DJ loops, minimize token burn:

- Use cron-style scheduling (`crontab` or `watch`) instead of agent idle-polling
- The loop script sleeps between polls (configurable interval, default 30s)
- The agent only wakes to: check if video ended → queue next → sleep again
- For fully hands-off operation, use the `/dj-start` command which launches the loop as a background process

## Additional Resources

### Reference Files

- **`references/agent-browser-commands.md`** — Full agent-browser CLI reference with examples
- **`references/kosmi-ui-map.md`** — Kosmi room UI element names, modal flows, and snapshot patterns

### Scripts

- **`scripts/kosmi-connect.sh`** — Connect/join a Kosmi room
- **`scripts/kosmi-play.sh`** — Play a single video by URL
- **`scripts/kosmi-loop.sh`** — Auto-loop DJ mode (background process)
- **`scripts/kosmi-snapshot-debug.sh`** — Dump interactive elements for debugging
