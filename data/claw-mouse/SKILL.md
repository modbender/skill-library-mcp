---
name: claw-mouse
description: Control a Linux X11 desktop by taking screenshots and moving/clicking/typing via xdotool + scrot.
homepage: https://github.com/rylena/claw-mouse
metadata:
  openclaw:
    requires:
      bins: [python3, xdotool, scrot]
---

# claw-mouse

This skill provides a small, scriptable **desktop GUI control** helper for Linux **X11**.

It’s intended for “vision loop” automation:
1) take a screenshot
2) decide where to click
3) move/click/type
4) repeat

Under the hood it wraps:
- `scrot` for screenshots
- `xdotool` for mouse/keyboard/window control

## Files

- `desktopctl.py` — the CLI script

## Requirements

- Linux running **X11** (not Wayland-only)
- `python3`
- `xdotool`
- `scrot`

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y xdotool scrot
```

## Usage

From this skill directory:

```bash
python3 desktopctl.py screenshot
python3 desktopctl.py click 500 300
python3 desktopctl.py type "hello"
python3 desktopctl.py key ctrl+l
python3 desktopctl.py windows
python3 desktopctl.py activate "Chromium"
```

### DISPLAY / XAUTHORITY

If you’re running from a daemon/headless shell where `DISPLAY` isn’t set:

```bash
DISPLAY=:0 XAUTHORITY=$HOME/.Xauthority python3 desktopctl.py screenshot
```

Or use flags:

```bash
python3 desktopctl.py --display :0 --xauthority $HOME/.Xauthority screenshot
```

## Safety notes

This can click/type into your real desktop session. Use carefully.

## Changelog

- 0.1.0: Initial published skill.
