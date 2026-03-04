---
name: astrill-watchdog
version: 1.1.0
description: Monitor and auto-reconnect Astrill VPN on Ubuntu Linux (deb GUI package). Detects dropped connections via tun interface + ping, then reconnects using Astrill's built-in /reconnect command or full process restart with /autostart. No sudo required.
metadata: {"openclaw":{"os":["linux"],"emoji":"🔒","homepage":"https://clawhub.ai/LittleJakub/astrill-watchdog","requires":{"bins":["ping","ip","pgrep","pkill"]}}}
---

# Astrill VPN Watchdog

Auto-detects and recovers dropped Astrill VPN connections on Ubuntu Linux.
No sudo required. Works with the standard GUI deb package only.

## Requirements

- **OS:** Ubuntu Linux x86_64 (tested on 25.10; expected to work on 22.04+)
- **Astrill:** deb GUI package — installs to `/usr/local/Astrill/`
- **Not compatible** with the CLI `.sh` installer package
- Standard tools: `ping`, `ip`, `pgrep`, `pkill` (Ubuntu defaults)
- No sudo required

## ⚠️ Limitations

- **No server switching.** Astrill encrypts its config and the OpenVPN management
  port requires an internal password. The watchdog reconnects to the last used server.
- **GUI deb only.** Does not work with the Astrill CLI `.sh` installer.
- **Display session required for Method 3.** Full restart needs an active desktop
  session (DISPLAY, DBUS, XDG vars). Works fine when started via systemd user service
  after login. Does not work headlessly without a desktop session.
- **Must run as the Astrill process owner.** The watchdog enforces that it runs as
  the same user as the Astrill GUI process. No sudo is used at any point — if there
  is a user mismatch, the script logs an error and exits cleanly.

## How it works

Health is checked every 30 seconds (configurable). Both must pass to be healthy:

1. `tun0` interface exists and is UP/UNKNOWN
2. `ping 8.8.8.8` succeeds (traffic actually flows)

### Reconnect cascade (3 attempts, escalating)

| Attempt | Method | Wait |
|---------|--------|------|
| 1 | `astrill /reconnect` — Astrill's built-in command (same one used after sleep/hibernate) | 20s |
| 2 | Kill `asovpnc` + `asproxy` child processes — parent Astrill respawns them | 20s |
| 3 | Kill entire Astrill process + relaunch with `/autostart` — Astrill connects to last server automatically | 45s |

**Key discovery:** killing only the main Astrill process (no sudo) is enough —
the root-owned children (`asovpnc`, `asproxy`) die automatically with the parent.
Relaunching with `/autostart` (the same argument used by the desktop autostart entry)
causes Astrill to connect to the last used server without any GUI interaction.

## Setup

### 1. Install systemd user service (auto-start on login)

Run the setup script once after installing the skill:

```bash
bash {baseDir}/setup.sh
```

This creates and enables a systemd user service that starts the watchdog
automatically when you log in, and restarts it if it ever crashes.

### 2. Verify

```bash
systemctl --user status astrill-watchdog
bash {baseDir}/astrill-watchdog.sh status
```

### Manual start (without systemd)

```bash
bash {baseDir}/astrill-watchdog.sh start
```

## Commands

| Command | Effect |
|---------|--------|
| `start` | Start background watchdog daemon |
| `stop` | Stop the watchdog (also kills orphaned instances) |
| `status` | Full diagnostics: VPN health, process info, recent log |
| `once` | Single check/reconnect and exit |

## Tunable parameters

Edit the top of `astrill-watchdog.sh`:

| Variable | Default | Description |
|----------|---------|-------------|
| `CHECK_INTERVAL` | `30` | Seconds between health checks |
| `MAX_ATTEMPTS` | `3` | Reconnect attempts per drop event |
| `RECONNECT_WAIT_1` | `20` | Wait after attempt 1 (/reconnect) |
| `RECONNECT_WAIT_2` | `20` | Wait after attempt 2 (kill children) |
| `RECONNECT_WAIT_3` | `45` | Wait after attempt 3 (full restart) |
| `PING_HOST` | `8.8.8.8` | Host to ping for connectivity check |
| `LOG_DIR` | `~/.local/state/astrill-watchdog/` | Private log directory (mode 700) |

## Agent trigger phrases

- "check my VPN" / "is Astrill connected?"
- "start the VPN watchdog" / "monitor my VPN"
- "reconnect Astrill" / "VPN dropped"
- "stop the watchdog"
- "show VPN logs"

## Log

```bash
tail -f ~/.local/state/astrill-watchdog/watchdog.log
```
