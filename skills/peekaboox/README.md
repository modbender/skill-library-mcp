# linux-desktop — OpenClaw Linux GUI Automation Skill

Full GUI automation for Linux X11 desktops. This skill gives OpenClaw the ability to capture screenshots, inspect windows, click, type, send hotkeys, scroll, and manage windows.

## Requirements

- Linux with X11 session (XFCE, GNOME on X11, KDE on X11, i3, openbox, etc.)
- `DISPLAY` environment variable set (usually `:0`)

## Installation

```bash
bash install.sh
```

This installs system dependencies (`xdotool`, `wmctrl`, `scrot`, `x11-utils`, `imagemagick`, Python).

Supported package managers: apt (Debian/Ubuntu), dnf (Fedora/RHEL), pacman (Arch).

## Tools

| Script | Purpose |
|--------|---------|
| `capture.sh` | Take screenshots (full screen or specific window) |
| `inspect.sh` | List windows, get window details (JSON output) |
| `click.sh` | Mouse click at coordinates (left/right/middle, single/double) |
| `type.sh` | Type text into the focused window |
| `hotkey.sh` | Send keyboard shortcuts (ctrl+c, alt+F4, etc.) |
| `scroll.sh` | Scroll up/down at current or specified position |
| `window.sh` | Window management (focus, minimize, maximize, close, move, resize) |

## Quick Start

```bash
# Take a screenshot
bash capture.sh

# List all open windows
bash inspect.sh

# Click at coordinates
bash click.sh --x 500 --y 300

# Type text
bash type.sh "Hello world"

# Send Ctrl+C
bash hotkey.sh "ctrl+c"
```

Preferred workflow: capture screenshot, interpret it directly in your OpenClaw chat, then act with coordinates.

## Testing

```bash
bash test.sh
```

## OpenClaw Integration

Because this repo is dedicated to this single skill, use the repo root as the skill folder:

```bash
cp -r <this-repo> ~/.openclaw/workspace/skills/linux-desktop/
```

Restart the OpenClaw gateway; the agent will read `SKILL.md`.

## Limitations

- **X11 only** — does not work on Wayland sessions
- Some applications with custom rendering may resist automation
