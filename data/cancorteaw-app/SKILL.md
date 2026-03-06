---
name: cancorteaw-app
description: Local Expo / React Native app builder runner for my OpenClaw server.
---

# cancorteaw-app

Local **Expo / React Native** app builder runner for my OpenClaw server.

This skill is a **controlled runner** that only executes an allowlisted script:
`/home/patron/apps/_bin/appctl`  
and that script is restricted to operate under:
`/home/patron/apps/<project>`.

## What it does

This skill wraps `appctl` to provide a safe, repeatable workflow:

- **Create** a new Expo app scaffold under `/home/patron/apps/<name>`
- **Add a screen** file under `/home/patron/apps/<name>/app/<Screen>.tsx`
- **Start a web preview** (`expo start --web`) bound to `127.0.0.1` on a chosen port
- **Check status** of the preview process

## Commands

### 1) Create a new app
**Command:**
- `new <name>`

**Example:**
- `new demoapp`

**Result:**
- Creates `/home/patron/apps/demoapp`
- Initializes git (best-effort)
- Uses `npx create-expo-app` in non-interactive mode

---

### 2) Add a screen
**Command:**
- `add-screen <name> <screenName> <title>`

**Example:**
- `add-screen demoapp Settings "Settings"`

**Result:**
- Writes: `/home/patron/apps/demoapp/app/Settings.tsx`
- Makes a git commit (best-effort)

---

### 3) Start web preview
**Command:**
- `preview <name>`

**Environment:**
- `EXPO_PORT` (optional): override preview port  
  Default: `19006`

**Example:**
- `preview demoapp`
- `EXPO_PORT=19010 preview demoapp`

**Result:**
- Starts `npx expo start --web --port <port>`
- Writes logs to: `/home/patron/apps/_logs/<name>.preview.log`
- Writes pid to: `/home/patron/apps/_state/<name>.pid`
- Writes port to: `/home/patron/apps/_state/<name>.port`

---

### 4) Status
**Command:**
- `status <name>`

**Example:**
- `status demoapp`

**Result:**
- Prints RUNNING with URL if process is alive
- Otherwise prints STOPPED

## Safety / Guardrails

- The runner is **allowlisted**: only `node`, `npm`, `npx`, `git`, `bash`, `python3` can be invoked.
- All project paths are constrained to `/home/patron/apps`.
- Preview binds to `127.0.0.1` (loopback). Expose it externally only via explicit SSH tunnel if desired.
- Telemetry is disabled for Expo in preview (`EXPO_NO_TELEMETRY=1`).

## Troubleshooting

- If `preview` says running but page doesn’t load: check the log file in `/home/patron/apps/_logs/`.
- If a port is busy: set `EXPO_PORT` to a free port and re-run `preview`.
- To stop preview: `kill $(cat /home/patron/apps/_state/<name>.pid)` (if pid exists).

