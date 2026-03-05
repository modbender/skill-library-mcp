---
name: xdotool-control
description: "Mouse and keyboard automation using xdotool. Use when clicking Chrome extension icons, typing into GUI apps, switching browser tabs, automating desktop UI, or running screenshot-verify-click loops without a browser relay. Triggers on: 'click extension icon', 'click coordinates', 'type in window', 'switch tab', 'automate mouse', 'screenshot and click', 'xdotool', 'desktop automation', 'GUI automation without relay'."
---

# xdotool-control

Automate mouse, keyboard, and window operations on the Linux desktop. Primary use: clicking Chrome extension icons, interacting with GUI apps when browser CDP isn't connected.

## Quick Start

```bash
# Find a window
xdotool search --name "Google Chrome"

# Click at screen coordinates
xdotool mousemove 1800 56 click 1

# Type text into focused window
xdotool type "hello world"

# Screenshot current state
scrot /tmp/snap.png
```

---

## Core Patterns

### 1. Find + Focus + Click

```bash
# Find Chrome window, focus it, click at position
WIN=$(xdotool search --name "Google Chrome" | head -1)
xdotool windowactivate --sync "$WIN"
sleep 0.3
xdotool mousemove X Y click 1
```

### 2. Screenshot → Verify → Click Loop

Use this when you need to click an element but don't know its exact position:

```bash
bash ~/.openclaw/workspace/skills/xdotool-control/scripts/snap_verify_click.sh \
  "Google Chrome" \    # Window name pattern
  "extension_icon" \   # What to look for (label for your snap files)
  1830 56              # Coordinates to click
```

Or use the full loop script for unknown positions:

```bash
bash ~/.openclaw/workspace/skills/xdotool-control/scripts/find_and_click.sh \
  "Google Chrome" \
  /tmp/target_icon.png \  # Template image to match (ImageMagick compare)
  10                       # Max attempts
```

### 3. Click Chrome Extension Icon

```bash
bash ~/.openclaw/workspace/skills/xdotool-control/scripts/click_extension.sh "OpenClaw"
# or
bash ~/.openclaw/workspace/skills/xdotool-control/scripts/click_extension.sh "Dawn"
```

This focuses Chrome and clicks the extensions puzzle-piece area, then scans for the named extension.

### 4. Tab Switching

```bash
# Switch to next tab
WIN=$(xdotool search --name "Google Chrome" | head -1)
xdotool windowactivate --sync "$WIN"
xdotool key ctrl+Tab

# Switch to specific tab (1-indexed)
xdotool key ctrl+2   # Tab 2
xdotool key ctrl+3   # Tab 3

# Open new tab
xdotool key ctrl+t

# Type a URL into address bar
xdotool key ctrl+l
sleep 0.2
xdotool type "https://example.com"
xdotool key Return
```

### 5. Type Into Window

```bash
WIN=$(xdotool search --name "Terminal" | head -1)
xdotool windowactivate --sync "$WIN"
sleep 0.2
xdotool type --clearmodifiers "command to type here"
xdotool key Return
```

### 6. Approve tmux Prompt (for Clawdy daemon)

```bash
SESSION=$(tmux ls | grep claude-session | head -1 | cut -d: -f1)
tmux send-keys -t "$SESSION" "Yes" Enter
```

---

## Window Management

```bash
# List all windows with names
xdotool search --name "" | while read wid; do
  name=$(xdotool getwindowname "$wid" 2>/dev/null)
  [ -n "$name" ] && echo "$wid $name"
done | head -20

# Get window geometry (position + size)
xdotool getwindowgeometry $WIN_ID

# Move window to front
xdotool windowraise $WIN_ID

# Resize window
xdotool windowsize $WIN_ID 1280 800

# Move window
xdotool windowmove $WIN_ID 0 0
```

---

## Screenshot Utilities

```bash
# Full desktop screenshot
scrot /tmp/desktop.png

# Specific window
scrot -u /tmp/active_window.png  # Currently active window

# Crop a region (x,y,width,height)
scrot -a 1400,0,480,60 /tmp/toolbar.png

# With delay
scrot -d 2 /tmp/delayed.png
```

Read screenshots with Claude's Read tool — it renders images inline.

---

## Chrome-Specific Patterns

```bash
# Chrome toolbar extension icons are typically at:
# y ≈ 56 (vertical center of toolbar)
# x varies by number of pinned extensions, roughly:
#   Last icon:       screen_width - 30
#   Second-to-last:  screen_width - 60
#   Puzzle piece:    screen_width - 90 (unpinned extensions menu)
```

### Clicking a Pinned Extension Icon

```bash
# Always auto-detect screen width — never hardcode
read SCREEN_W SCREEN_H <<< $(xdotool getdisplaygeometry)
TOOLBAR_Y=56

# Take a toolbar snapshot first to verify positions
scrot -a "$((SCREEN_W-300)),0,300,70" /tmp/toolbar_snap.png
# Read /tmp/toolbar_snap.png to see icon positions visually

# Then click
xdotool mousemove $((SCREEN_W - 60)) $TOOLBAR_Y click 1
```

---

## Dependencies

```bash
# Required
sudo apt-get install xdotool scrot

# Optional — enables template matching in find_and_click.sh
sudo apt-get install imagemagick

# Check all deps at once:
for dep in xdotool scrot convert; do
  command -v "$dep" &>/dev/null && echo "✓ $dep" || echo "✗ $dep (missing)"
done
```

## Tips & Gotchas

- **Always `windowactivate --sync` before clicking** — without `--sync`, the click may fire before focus lands
- **Add `sleep 0.3`** after focus change before interacting with Chrome
- **Coordinates are screen-absolute**, not window-relative — factor in window position from `getwindowgeometry`
- **`xdotool type` vs `xdotool key`**: use `type` for text strings, `key` for special keys (ctrl+t, Return, Escape)
- **`--clearmodifiers`** on `type` prevents Shift/Ctrl state from leaking into typed text
- **scrot -u** captures only the currently active window — make sure to activate the right window first
- **ImageMagick compare** can do pixel-level template matching for verify loops (see `find_and_click.sh`)
