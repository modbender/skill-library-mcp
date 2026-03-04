# astrill-watchdog

> Auto-reconnect Astrill VPN on Ubuntu — for the standard deb GUI package. No sudo required.

Monitors your Astrill VPN and automatically reconnects when it drops, using
Astrill's own built-in mechanisms. Discovered through reverse engineering:
Astrill ships `/reconnect` and `/autostart` arguments that aren't documented
anywhere, and killing just the main process causes root-owned children to die
cleanly without needing sudo.

---

## Who is this for?

- You run **Ubuntu Linux x86_64** (tested on 25.10; expected to work on 22.04+)
- You have the **Astrill deb GUI package** installed (`/usr/local/Astrill/`)
- Your VPN occasionally drops and you want automatic recovery

---

## Quick start

```bash
# Install via clawhub
clawhub install astrill-watchdog

# Run setup once — creates systemd user service for auto-start on login
bash ~/.openclaw/workspace/skills/astrill-watchdog/setup.sh
```

That's it. The watchdog starts automatically when you log in and survives reboots.

---

## What it does

Every 30 seconds, checks:
1. Is `tun0` up? (VPN tunnel active)
2. Can we ping `8.8.8.8`? (traffic flows)

If either fails, runs a 3-attempt escalating reconnect:

| Attempt | Method | Wait |
|---------|--------|------|
| 1 | `astrill /reconnect` — built-in command | 20s |
| 2 | Kill `asovpnc` + `asproxy` child processes — parent respawns them | 20s |
| 3 | Kill Astrill + relaunch with `/autostart` — connects to last server | 45s |

**No sudo needed.** Killing the main Astrill process (which runs as your user)
causes the root-owned children to die automatically — no elevated privileges required.

---

## What it does NOT do

- ❌ Switch servers (Astrill encrypts its config — server list not accessible)
- ❌ Work with the CLI `.sh` installer (different install layout)
- ❌ Work headlessly without a desktop session (Method 3 needs DISPLAY/DBUS)
- ❌ Require sudo at any point

---

## Commands

```bash
# Via systemd (recommended)
systemctl --user start astrill-watchdog
systemctl --user stop astrill-watchdog
systemctl --user status astrill-watchdog

# Direct script
bash astrill-watchdog.sh start    # start daemon
bash astrill-watchdog.sh stop     # stop daemon
bash astrill-watchdog.sh status   # full diagnostics
bash astrill-watchdog.sh once     # single check/reconnect

# Live log
tail -f ~/.local/state/astrill-watchdog/watchdog.log
```

---

## What we discovered during development

- Astrill deb installs to `/usr/local/Astrill/` (not `/opt/astrill/`)
- `astrill` is NOT on PATH — full path required
- Astrill ships `/etc/systemd/system/astrill-reconnect.service` which uses
  `/usr/local/Astrill/astrill /reconnect` for post-sleep recovery — we reuse this
- `/autostart` is the argument used by the desktop autostart entry and causes
  Astrill to connect to the last used server automatically on launch
- The OpenVPN management port (3221) requires an internal password — not accessible
- `~/.config/astrill/Astrill.ini` is encrypted binary — server list not extractable
- Root-owned child processes (`asovpnc`, `asproxy`) die automatically when the
  parent Astrill process is killed — no sudo needed for full restart

---

## Troubleshooting

**Method 3 doesn't reconnect**
Ensure Astrill was previously connected (it reconnects to the last used server).
If Astrill has never connected on this machine, it has no server to reconnect to.

**`tun0` shows UP but internet fails**
Normal during reconnection — traffic drops briefly while the tunnel re-establishes.

**Double log entries**
Two watchdog instances are running. Run `stop` then `start` (or re-run `setup.sh`).

**Where are the logs?**
Logs are written to `~/.local/state/astrill-watchdog/watchdog.log` (private, mode 700 — not world-readable).

**Service fails on boot**
The systemd user service requires `loginctl enable-linger` to start before login:
```bash
loginctl enable-linger $USER
```

---

## License

MIT
