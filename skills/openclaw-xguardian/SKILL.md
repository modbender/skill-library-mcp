---
name: openclaw-xguardian
description: Build, configure, and install a 24x7 OpenClaw watchdog on macOS, including scaffolding the Go project, wiring launchd, and tuning health/recovery behavior. Use for requests to create or share the OpenClaw guardian service, deploy it on a Mac, or troubleshoot its recovery/logging behavior.
---

# OpenClaw XGuardian

## Overview
Create a macOS launchd-backed guardian that keeps OpenClaw running, auto-recovers on failure, and logs minimal operational events.

## Workflow
1. Scaffold the project from assets.
2. Configure paths and OpenClaw CLI location.
3. Build the Go binary.
4. Install the LaunchAgent and reload.
5. Validate via logs and a stop/recovery test.

## Steps

### 1) Scaffold from assets
Copy the template project into the target workspace:

```bash
cp -R /Users/xiong/.codex/skills/openclaw-xguardian/assets/guardian/* <TARGET_WORKSPACE>/
```

This copies:
- `go.mod`
- `cmd/openclaw-guardian/main.go`
- `config.sample.json`
- `launchd/com.openclaw.guardian.plist`

### 2) Configure paths
Edit the user config file at `~/.openclaw-guardian/config.json` (create from `config.sample.json`).
Key fields:
- `openclaw_bin`: absolute path from `which openclaw`
- `config_path`: usually `~/.openclaw/openclaw.json`
- `gateway_plist_path`: usually `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
- `log_path`: e.g. `~/.openclaw-guardian/guardian.log`
- `verbose_logs`: `false` by default for concise logs
- `log_health_ok`: `false` by default to avoid spam

### 3) Build

```bash
go build -o bin/openclaw-guardian ./cmd/openclaw-guardian
```

### 4) Install LaunchAgent (guardian)
Edit `launchd/com.openclaw.guardian.plist` and set:
- `ProgramArguments`: binary path + config path
- `EnvironmentVariables/PATH`: include your Node/OpenClaw path
- `StandardOutPath`/`StandardErrorPath`: desired log files

Then install and reload:

```bash
mkdir -p ~/Library/LaunchAgents
cp launchd/com.openclaw.guardian.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.openclaw.guardian.plist
```

### 5) Validate
- Check logs: `tail -n 80 ~/.openclaw-guardian/guardian.log`
- Optional: `openclaw gateway stop` and confirm recovery lines appear.

## Troubleshooting
- `env: node: No such file or directory`: add Node path to LaunchAgent `PATH` and set `openclaw_bin`.
- Repeated `install`: ensure `gateway_plist_path` points to `~/Library/LaunchAgents/ai.openclaw.gateway.plist`; guardian should bootstrap instead of reinstall.
- Too much logging: keep `verbose_logs=false` and `log_health_ok=false`.

## Resources
### assets/
Project template in `assets/guardian/`.
