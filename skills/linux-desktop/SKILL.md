---
name: linux-desktop
description: "Linux desktop automation and control. Use when: (1) taking screenshots of the screen or windows, (2) controlling mouse and keyboard, (3) managing windows, (4) automating desktop tasks, or (5) any Linux desktop interaction needs. Supports screenshot capture, mouse movement, typing, and window management."
---

# Linux Desktop Control

Automate and control your Linux desktop using command-line tools. Capture screenshots, control mouse/keyboard, and manage windows.

## When to Use

- Take screenshots of screen or specific windows
- Automate mouse movements and clicks
- Simulate keyboard input
- Manage and interact with windows
- Build desktop automation workflows

## Prerequisites

Install required tools:

```bash
sudo apt-get install scrot xdotool xclip x11-utils x11-apps
```

## Quick Start

### Take Screenshot
```bash
python3 scripts/linux-desktop.py screenshot
# Output: ~/screenshot_20240224_203901.png
```

### List Windows
```bash
python3 scripts/linux-desktop.py list
```

### Move Mouse and Click
```bash
python3 scripts/linux-desktop.py move 500 300
python3 scripts/linux-desktop.py click
```

### Type Text
```bash
python3 scripts/linux-desktop.py type "Hello World"
```

## Commands

### `screenshot [path]`
Capture a screenshot of the entire screen.

**Examples:**
```bash
# Save to default location (/tmp/screenshot_YYYYMMDD_HHMMSS.png)
python3 scripts/linux-desktop.py screenshot

# Save to custom path
python3 scripts/linux-desktop.py screenshot ~/desktop.png
```

### `window [window_id] [path]`
Capture a screenshot of a specific window.

**Examples:**
```bash
# Screenshot active window
python3 scripts/linux-desktop.py window

# Screenshot specific window
python3 scripts/linux-desktop.py window 0x12345678 ~/window.png
```

### `active`
Get information about the currently active window.

```bash
python3 scripts/linux-desktop.py active
# Output: 🖥️ Active Window
#         ID: 0x12345678
#         Title: Terminal
```

### `list`
List all visible windows.

```bash
python3 scripts/linux-desktop.py list
# Output: 🪟 Found 5 windows:
#         1. 0x12345678 - Terminal
#         2. 0x87654321 - Chrome
```

### `move <x> <y>`
Move mouse cursor to specified coordinates.

**Examples:**
```bash
python3 scripts/linux-desktop.py move 100 200
# Moves mouse to (100, 200)

python3 scripts/linux-desktop.py move 500 300
# Moves mouse to center of 1000x600 area
```

### `click [button]`
Click mouse button at current cursor position.

**Button values:**
- `1` - Left button (default)
- `2` - Middle button
- `3` - Right button

**Examples:**
```bash
python3 scripts/linux-desktop.py click
# Left click

python3 scripts/linux-desktop.py click 3
# Right click
```

### `type <text>`
Type text at current cursor position (must be in focused window).

**Examples:**
```bash
python3 scripts/linux-desktop.py type "Hello World"

python3 scripts/linux-desktop.py type "ls -la"

python3 scripts/linux-desktop.py type "sudo apt update"
```

### `key <keyspec>`
Press keyboard keys.

**Common keys:**
- `Return` - Enter key
- `Escape` - Escape key
- `Tab` - Tab key
- `BackSpace` - Backspace
- `Delete` - Delete
- `Up`, `Down`, `Left`, `Right` - Arrow keys
- `Home`, `End`, `Page_Up`, `Page_Down`
- `F1` through `F12`
- `Ctrl+c`, `Ctrl+v`, `Ctrl+a`, `Ctrl+z` - Key combinations

**Examples:**
```bash
python3 scripts/linux-desktop.py key Return

python3 scripts/linux-desktop.py key Escape

python3 scripts/linux-desktop.py key Ctrl+a

python3 scripts/linux-desktop.py key F5
```

### `screen`
Get screen information.

```bash
python3 scripts/linux-desktop.py screen
# Output: 🖥️ Screen Info
#         Resolution: 1920x1080
```

## Automation Examples

### Basic Automation
```bash
# Move mouse, click, type, and press enter
python3 scripts/linux-desktop.py move 100 100
python3 scripts/linux-desktop.py click
python3 scripts/linux-desktop.py type "ls -la"
python3 scripts/linux-desktop.py key Return
```

### Web Search Automation
```bash
# Open browser, navigate to Google, search
python3 scripts/linux-desktop.py move 100 50
python3 scripts/linux-desktop.py click
python3 scripts/linux-desktop.py type "https://www.google.com"
python3 scripts/linux-desktop.py key Return
sleep 2
python3 scripts/linux-desktop.py type "how to make money online"
python3 scripts/linux-desktop.py key Return
```

### Screenshot Workflow
```bash
# Take screenshot before and after action
python3 scripts/linux-desktop.py screenshot /tmp/before.png
python3 scripts/linux-desktop.py key F5  # Refresh
sleep 1
python3 scripts/linux-desktop.py screenshot /tmp/after.png
```

## Tips

- Always check the active window before typing
- Use `sleep` commands between actions for reliability
- Take screenshots to verify state changes
- Test commands one by one before building complex workflows
- Use window list to find specific window IDs for targeting

## Troubleshooting

**"Command not found" errors:**
```bash
sudo apt-get install scrot xdotool xclip x11-utils x11-apps
```

**Permission denied:**
- Ensure you're running in a graphical session (X11 or Wayland)
- Some actions require focus on the target window

**Mouse doesn't move:**
- Check if another application is grabbing the mouse
- Try moving the mouse manually to see if it's responsive

## Security Notes

- This skill can control your desktop - use with caution
- Don't automate sensitive actions without verification
- Always review automation scripts before running
