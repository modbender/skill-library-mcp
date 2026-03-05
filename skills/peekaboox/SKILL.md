---
name: linux-desktop
description: >
  Control and automate the Linux desktop GUI on X11. Use this skill to take screenshots,
  find and click UI elements, type text, send keyboard shortcuts, scroll, manage windows
  (focus, minimize, maximize, close, move, resize), and use your own vision to locate elements
  on screen. Requires X11 (not Wayland). Use for desktop automation, GUI testing,
  remote desktop control, and any task requiring interaction with graphical applications.
metadata:
  clawdbot:
    emoji: "\U0001F5A5"
    os: ["linux"]
    requires:
      bins: ["xdotool", "wmctrl", "scrot"]
      env: ["DISPLAY"]
    install:
      - id: apt
        kind: shell
        command: bash install.sh
        label: Install dependencies (apt/dnf/pacman)
---

# Linux Desktop GUI Automation

Automate any X11 Linux desktop: capture screens, find and click elements, type, use hotkeys,
manage windows.

Preferred screenshot interpretation path: capture with `capture.sh` and interpret the image directly in your OpenClaw chat (existing image-capable model connection).

## Prerequisites

- X11 session running (XFCE, GNOME on X11, KDE on X11, i3, openbox, etc.)
- `DISPLAY` environment variable set (usually `:0`)
- Run `bash install.sh` once to install dependencies
- No extra key needed for screenshot interpretation when using OpenClaw's image-capable chat path

## Quick Reference

| Task | Command |
|------|---------|
| Take screenshot | `bash capture.sh` |
| Screenshot of window | `bash capture.sh --window "Firefox"` |
| List windows | `bash inspect.sh` |
| Active window info | `bash inspect.sh --active` |
| Find window by name | `bash inspect.sh --window "Firefox"` |
| Click at coordinates | `bash click.sh --x 500 --y 300` |
| Right-click | `bash click.sh --x 500 --y 300 --button right` |
| Double-click | `bash click.sh --x 500 --y 300 --double` |
| Click relative to window | `bash click.sh --window "Firefox" --x 200 --y 150` |
| Type text | `bash type.sh "hello world"` |
| Type into window | `bash type.sh --window "Terminal" "ls -la"` |
| Send hotkey | `bash hotkey.sh "ctrl+c"` |
| Send Enter | `bash hotkey.sh "Return"` |
| Scroll down | `bash scroll.sh --direction down --amount 3` |
| Scroll up at position | `bash scroll.sh --x 500 --y 300 --direction up --amount 3` |
| Focus window | `bash window.sh --action focus --window "Firefox"` |
| Minimize window | `bash window.sh --action minimize --window "Firefox"` |
| Maximize window | `bash window.sh --action maximize --window "Firefox"` |
| Close window | `bash window.sh --action close --window "Firefox"` |
| Move window | `bash window.sh --action move --window "Firefox" --x 100 --y 50` |
| Resize window | `bash window.sh --action resize --window "Firefox" --width 1280 --height 800` |

## Typical Automation Workflow

For most GUI automation tasks, follow this pattern:

1. **Capture** a screenshot with `capture.sh` — note the file path printed
2. **Look** at the screenshot yourself to understand what's on screen
3. **Find** the target element by examining the screenshot and estimating its pixel coordinates
4. **Act** using the coordinates: `click.sh --x X --y Y`
5. **Verify** by capturing another screenshot and checking the result

### Example: Click the Save button in a dialog

```bash
# Step 1: Capture the screen
SCREENSHOT=$(bash capture.sh | tail -1)

# Step 2: Look at the screenshot (read the image file with your vision)
# Examine the image and identify the Save button's position

# Step 3: Click at the coordinates you identified
bash click.sh --x 450 --y 320
```

### Example: Type into a specific application

```bash
# Focus the terminal window and type a command
bash type.sh --window "Terminal" "ls -la"
bash hotkey.sh "Return"
```

### Example: Window management

```bash
# Maximize Firefox, then focus a terminal
bash window.sh --action maximize --window "Firefox"
bash window.sh --action focus --window "Terminal"
```

## JSON Output

All tools support a `--json` flag for machine-readable output:

```json
{"success": true, "output": "...", "error": null}
```

On failure:

```json
{"success": false, "output": null, "error": "Error description"}
```

## Environment Setup

If `DISPLAY` is not set (e.g., running over SSH), set it before calling any tool:

```bash
export DISPLAY=:0
```

For headless servers with a virtual display:

```bash
Xvfb :0 -screen 0 1920x1080x24 &
export DISPLAY=:0
```

## Hotkey Reference

Key names follow X11 conventions:

| Key | Name |
|-----|------|
| Enter | `Return` |
| Tab | `Tab` |
| Escape | `Escape` |
| Backspace | `BackSpace` |
| Delete | `Delete` |
| Home | `Home` |
| End | `End` |
| Page Up | `Page_Up` |
| Page Down | `Page_Down` |
| F1-F12 | `F1` through `F12` |
| Super/Win | `super` |
| Ctrl | `ctrl` |
| Alt | `alt` |
| Shift | `shift` |

Combine with `+`: `ctrl+c`, `ctrl+shift+t`, `alt+F4`, `super+d`

## Limitations

- X11 only — does not work on Wayland sessions
- Cannot interact with Wayland-native apps in a Wayland session
- Some apps with custom rendering (games, Electron apps with security flags) may resist automation
- Screenshot quality depends on compositor; disable compositing if captures look wrong
