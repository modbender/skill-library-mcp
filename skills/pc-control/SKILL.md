---
name: pc-control
description: "Remote Windows desktop control from WSL/Linux via screenshot + mouse/keyboard simulation. Use when: user asks to control their PC, click something, open an app, interact with a GUI program, take a screenshot, or perform any desktop automation that has no CLI alternative. NOT for: tasks with command-line alternatives (prefer CLI/PowerShell), reading files, or running scripts."
---

# PC Control — Remote Desktop Control

Control a Windows desktop from WSL/Linux via screenshots (mss) + mouse/keyboard simulation (pyautogui). A FastAPI server runs on Windows; a Python client calls it from WSL.

## Setup

### 1. Configure `config.json`

Edit `config.json` in the skill directory. Set `python_path` to a Windows Python with pip:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 18888,
    "python_path": "C:\\Python312\\python.exe"
  },
  "powershell": "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
  "auto_shutdown_minutes": 10,
  "screenshot": {
    "default_scale": 0.5,
    "default_quality": 50
  }
}
```

### 2. Install dependencies

```bash
python3 scripts/install.py
```

Installs `fastapi uvicorn mss pyautogui pillow` into the Windows Python.

## Usage

### Start the server

```bash
python3 scripts/launcher.py start
```

### Take a screenshot and analyze

```python
import sys; sys.path.insert(0, 'skills/pc-control/scripts')
from client import PCControl
pc = PCControl()
img_path = pc.screenshot(scale=0.5, quality=50)
# Use image analysis tool to understand the screen
```

**Important:** Screenshots are scaled. When clicking, divide target coordinates by the scale factor to get actual screen coordinates. E.g., if scale=0.5 and target is at (400, 300) in the image, click at (800, 600).

### Execute actions

```python
pc.click(x, y)                # Left click
pc.double_click(x, y)         # Double click
pc.right_click(x, y)          # Right click
pc.move(x, y)                 # Move cursor
pc.scroll(x, y, clicks)       # Scroll (negative = down)
pc.drag(x1, y1, x2, y2)      # Drag
pc.type_text("hello")         # Type text
pc.press("enter")             # Press key
pc.hotkey("ctrl", "c")        # Key combo
```

### Verify after each action

Always screenshot after an action to confirm it worked before proceeding.

### Stop the server

```bash
python3 scripts/launcher.py stop
```

## Interaction Loop

```
screenshot → analyze → decide action → execute → screenshot verify → continue or done
```

## Notes

- Server listens on localhost only with token auth (token auto-generated per session)
- `Win+R` → type app name → Enter is more reliable than clicking taskbar icons
- Wait 1–2 seconds after clicks before re-screenshotting
- Prefer CLI/PowerShell when available — use this only for GUI-only tasks
