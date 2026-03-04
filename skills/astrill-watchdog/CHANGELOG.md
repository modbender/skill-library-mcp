# Changelog

## 1.1.0

- **Refactor:** `tun_up()` now calls `ip link show tun0` once and captures the
  result — eliminates the duplicate subprocess that existed previously.
- **Refactor:** Desktop session variables (`DISPLAY`, `DBUS`, `XDG`) consolidated
  into a single `DESKTOP_ENV` array; both reconnect methods now use
  `env "${DESKTOP_ENV[@]}"` — impossible to accidentally diverge between them.
- **Refactor:** `reconnect()` replaced the `case` dispatch with parallel `methods`
  and `waits` arrays indexed by attempt number — adding or reordering reconnect
  methods now requires changing one line each.
- **Refactor:** `ASTRILL_USER` auto-detection replaced fragile `ps aux | grep |
  awk | head` pipeline with `pgrep | ps -o user=` — more portable and correct.
- **No functional changes** — all behaviour, log paths, permissions and service
  integration identical to 1.0.8.

## 1.0.7

- **Fix:** Added `default.target` to `After=` in the systemd service unit so the
  watchdog waits for the full user session to be ready before starting. Prevents
  the `Failed to determine supplementary groups: Operation not permitted` error
  seen on Ubuntu 25.10 when the service started before the session was fully
  initialised.
- **Fix:** Increased `RestartSec` from 10s to 15s to give the user session more
  time to stabilise between restart attempts on boot.

## 1.0.6

- **Fix:** PID file now written at the top of `watch_loop` so it is always
  created when the watchdog starts, including when launched directly by systemd
  (which calls `_loop` and bypasses `cmd_start` where the PID was previously written).
  `cmd_stop` and `cmd_status` now reliably find the running process.
- **Fix:** Homepage URL in SKILL.md corrected to the actual published ClawHub
  listing at `https://clawhub.ai/LittleJakub/astrill-watchdog`.

## 1.0.5

- **Fix:** Log and PID files now explicitly created with `touch` and `chmod 600`
  at startup, ensuring they are never world-readable regardless of the process
  umask. Previously only the parent directory was protected (700); the files
  themselves inherited the umask and could be readable by other local users.

## 1.0.4

- **Refactor:** Reduced script from 312 to ~200 lines by compacting verbose
  echo-heavy blocks into concise equivalents — same functionality, fully visible
  in ClawHub's file preview without truncation. Addresses reviewer concern that
  the end of the file was cut off during security assessment.
- **Clarity:** Renamed "Reconnect strategies" section to "Reconnect methods" and
  consolidated inline comments to make each method's intent immediately clear to
  code reviewers.
- **No functional changes** — all reconnect logic, health checks, log paths, and
  user-enforcement behaviour are identical to 1.0.3.

## 1.0.3

- **Security fix:** Moved log and PID files from world-readable `/tmp/` to a
  private directory `~/.local/state/astrill-watchdog/` (XDG_STATE_HOME, mode 700).
  Addresses the ClawHub security assessment flag that logs may contain VPN
  diagnostic info (interface state, ping results) visible to other local users.
- Log file is now at `~/.local/state/astrill-watchdog/watchdog.log`
- PID file is now at `~/.local/state/astrill-watchdog/watchdog.pid`

## 1.0.2

- **Security fix:** Removed `sudo -u` fallback from `run_as_astrill()` — the
  watchdog now enforces that it runs as the same user as the Astrill process and
  logs a clear error if there is a mismatch, rather than silently escalating privileges
- **Docs:** Added explicit limitation to SKILL.md documenting that no sudo is used
  at any point and that a user mismatch results in a clean error

## 1.0.1

- **Fix:** Method 3 now uses `/autostart` argument instead of bare relaunch —
  causes Astrill to connect to last used server automatically (no auto-connect
  setting needed in the GUI)
- **Fix:** Kill pattern changed from `astrill$` to `astrill` — correctly matches
  the running process `/usr/local/Astrill/astrill /autostart`
- **Fix:** Double logging — `log()` now writes only to file (not stdout+file via tee)
- **Fix:** `ASTRILL_USER` auto-detection now uses `|| true` to prevent script exit
  under `set -euo pipefail` when Astrill is not running at startup
- **Fix:** Added `whoami` fallback for `ASTRILL_USER` when auto-detection fails
- **Add:** `setup.sh` — one-command systemd user service install (auto-start on login)
- **Add:** Per-attempt wait times (`RECONNECT_WAIT_1/2/3`) — Method 3 now waits
  45s instead of 15s to give Astrill time to fully initialise
- **Add:** Display environment variables (`DISPLAY`, `DBUS_SESSION_BUS_ADDRESS`,
  `XDG_SESSION_TYPE`) passed to Astrill on relaunch for proper GUI session
- **Add:** Orphaned instance cleanup in `cmd_stop`
- **Docs:** Added limitations, troubleshooting, and discovery notes to README

## 1.0.0

- Initial release
- Health detection via `tun0` + `ping 8.8.8.8`
- 3-attempt reconnect cascade: `/reconnect` → kill children → full restart
- Auto-detection of `ASTRILL_USER` from running process
- Background daemon with PID file
- Tested on Ubuntu 25.10 x86_64 with Astrill deb package version 3.10.0.3073
