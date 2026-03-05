---
name: desktop-guardian
description: "macOS GUI automation and desktop control for OpenClaw, powered by Hammerspoon. Gives your agent full access to interact with the Mac desktop — query windows, manage apps, close browser tabs, click dialog buttons, dismiss popups, and send keypresses. Includes an always-on desktop guardian that actively monitors for system dialogs, permission prompts, error popups, and unauthorized apps, taking action automatically or alerting you when human input is needed. Use when: (1) your agent needs to interact with the macOS GUI, (2) monitoring and responding to desktop popups/dialogs/alerts, (3) managing open apps, browser windows, and tabs, (4) enforcing desktop cleanliness policies, (5) any macOS Accessibility automation from OpenClaw."
---

# Desktop Guardian

Full macOS GUI access and desktop automation for OpenClaw, powered by **Hammerspoon**.

## What It Does

### 🖥️ GUI Access
- **Query** all open windows, apps, and dialogs with full detail (titles, buttons, states)
- **Close** specific windows or tabs — not just kill entire apps
- **Click buttons** in system dialogs and popups (with safety guardrails)
- **Send keypresses** to any app
- **Quit or force-quit** apps programmatically
- **Chrome DevTools Protocol** integration for tab-level browser control

### 🛡️ Active Desktop Monitoring
- **Watches** for system dialogs, permission prompts, error popups, and alerts in real-time
- **Auto-dismisses** known-safe dialogs (e.g., "app downloaded from internet")
- **Alerts you** via Telegram/chat when human input is needed (e.g., security prompts)
- **Detects and closes** unauthorized apps and excess browser windows/tabs
- **Enforces** configurable desktop policies via YAML rules
- **Logs** every action for full audit trail

## Requirements

- macOS (Tahoe or later)
- Hammerspoon (installed automatically) + Accessibility permission
- Python 3 + PyYAML (installed automatically)
- Optional: Chrome with `--remote-debugging-port=9222` for tab-level control

## Installation

```bash
bash scripts/install.sh
```

This will:
1. Install Hammerspoon if needed
2. Install the DesktopGuardian Spoon
3. Guide you through Accessibility permission
4. Compile the Swift fallback for degraded mode
5. Set up config, logs, and LaunchAgent

## Configuration

Config file: `~/.openclaw/skills/desktop-guardian/policy.yaml`

See `assets/config.example.yaml` for all options. Key settings:

- **cleanup.enabled**: Master switch for auto-cleanup (default: true)
- **cleanup.apps.whitelist**: Apps allowed to run; others get closed
- **browsers.chrome.max_windows/max_tabs**: Limits before auto-close
- **dialogs.auto_dismiss**: Apps whose dialogs are safe to dismiss
- **dialogs.ignore**: Apps whose dialogs should be silently ignored
- **alerts.notify_on_actions**: Send notification for every auto-action

## Chrome Tab Monitoring

For tab-level granularity, Chrome must run with CDP enabled:

```bash
open -a "Google Chrome" --args --remote-debugging-port=9222
```

Without CDP, only window counts are available.

## Kill Switch

Instantly disable all actions:
```bash
touch ~/.openclaw/skills/desktop-guardian/KILL_SWITCH
```

Remove to re-enable:
```bash
rm ~/.openclaw/skills/desktop-guardian/KILL_SWITCH
```

## Graceful Degradation

Without Hammerspoon, the skill runs in **monitor-only mode** using a Swift fallback binary. It can detect violations but cannot auto-close or dismiss anything.

## helpers.py Subcommands

```
parse_config          — Output config as key=value pairs
validate_config       — Validate config (exit 0/1)
check_quiet           — Exit 0 if NOT in quiet hours
evaluate_snapshot     — Apply policy to snapshot JSON → violations + actions
parse_query           — Convert snapshot to key=value pairs
safe_hs_command       — Generate safe hs -c command string
update_state          — Update alert cooldown state
log_violation         — Append to violation log
daily_summary         — Generate daily summary
list_apps             — List apps from last snapshot
check_cooldown        — Check if alert cooldown has expired
```

## Security

- **Never** interpolates shell variables into `hs -c` commands
- Hardcoded button blacklist: won't click Allow, Delete, Install, etc.
- Hardcoded app blacklist: won't dismiss SecurityAgent, Keychain Access, etc.
- All app names validated against `^[a-zA-Z0-9 ._-]+$`
- Config file mode 600, state uses atomic writes
- Full audit log of every action taken

## Uninstall

```bash
bash scripts/uninstall.sh
```

Removes LaunchAgent, Spoon, and init.lua entries. Preserves config/logs unless you choose to remove them. Does NOT uninstall Hammerspoon.
