---
name: mac-control
description: Control Mac via mouse/keyboard automation using cliclick and AppleScript. Use for clicking UI elements, taking screenshots, getting window bounds, handling coordinate scaling on Retina displays, and automating UI interactions like clicking Chrome extension icons, dismissing dialogs, or toolbar buttons.
---

# Mac Control

Automate Mac UI interactions using cliclick (mouse/keyboard) and system tools.

## Tools

- **cliclick**: `/opt/homebrew/bin/cliclick` - mouse/keyboard control
- **screencapture**: Built-in screenshot tool
- **magick**: ImageMagick for image analysis
- **osascript**: AppleScript for window info

## Coordinate System (Eason's Mac Mini)

**Current setup**: 1920x1080 display, **1:1 scaling** (no conversion needed!)

- Screenshot coords = cliclick coords
- If screenshot shows element at (800, 500), click at (800, 500)

### For Retina Displays (2x)

If screenshot is 2x the logical resolution:
```bash
# Convert: cliclick_coords = screenshot_coords / 2
cliclick c:$((screenshot_x / 2)),$((screenshot_y / 2))
```

### Calibration Script

Run to verify your scale factor:
```bash
/Users/eason/clawd/scripts/calibrate-cursor.sh
```

## cliclick Commands

```bash
# Click at coordinates
/opt/homebrew/bin/cliclick c:500,300

# Move mouse (no click) - Note: may not visually update cursor
/opt/homebrew/bin/cliclick m:500,300

# Double-click
/opt/homebrew/bin/cliclick dc:500,300

# Right-click
/opt/homebrew/bin/cliclick rc:500,300

# Click and drag
/opt/homebrew/bin/cliclick dd:100,100 du:200,200

# Type text
/opt/homebrew/bin/cliclick t:"hello world"

# Press key (Return, Escape, Tab, etc.)
/opt/homebrew/bin/cliclick kp:return
/opt/homebrew/bin/cliclick kp:escape

# Key with modifier (cmd+w to close window)
/opt/homebrew/bin/cliclick kd:cmd t:w ku:cmd

# Get current mouse position
/opt/homebrew/bin/cliclick p

# Wait before action (ms)
/opt/homebrew/bin/cliclick -w 100 c:500,300
```

## Screenshots

```bash
# Full screen (silent)
/usr/sbin/screencapture -x /tmp/screenshot.png

# With cursor (may not work for custom cursor colors)
/usr/sbin/screencapture -C -x /tmp/screenshot.png

# Interactive region selection
screencapture -i region.png

# Delayed capture
screencapture -T 3 -x delayed.png  # 3 second delay
```

## Workflow: Screenshot → Analyze → Click

**Best practice for reliable clicking:**

1. **Take screenshot**
   ```bash
   /usr/sbin/screencapture -x /tmp/screen.png
   ```

2. **View screenshot** (Read tool) to find target coordinates

3. **Click at those coordinates** (1:1 on 1920x1080)
   ```bash
   /opt/homebrew/bin/cliclick c:X,Y
   ```

4. **Verify** by taking another screenshot

### Example: Click a button

```bash
# 1. Screenshot
/usr/sbin/screencapture -x /tmp/before.png

# 2. View image, find button at (850, 450)
# (Use Read tool on /tmp/before.png)

# 3. Click
/opt/homebrew/bin/cliclick c:850,450

# 4. Verify
/usr/sbin/screencapture -x /tmp/after.png
```

## Window Bounds

```bash
# Get Chrome window bounds
osascript -e 'tell application "Google Chrome" to get bounds of front window'
# Returns: 0, 38, 1920, 1080  (left, top, right, bottom)
```

## Common Patterns

### Chrome Extension Icon (Browser Relay)

Use AppleScript to find exact button position:

```bash
# Find Clawdbot extension button position
osascript -e '
tell application "System Events"
    tell process "Google Chrome"
        set toolbarGroup to group 2 of group 3 of toolbar 1 of group 1 of group 1 of group 1 of group 1 of group 1 of window 1
        set allButtons to every pop up button of toolbarGroup
        repeat with btn in allButtons
            if description of btn contains "Clawdbot" then
                return position of btn & size of btn
            end if
        end repeat
    end tell
end tell
'
# Output: 1755, 71, 34, 34 (x, y, width, height)

# Click center of button
# center_x = x + width/2 = 1755 + 17 = 1772
# center_y = y + height/2 = 71 + 17 = 88
/opt/homebrew/bin/cliclick c:1772,88
```

### Clicking by Color Detection

If you need to find a specific colored element:

```bash
# Find red (#FF0000) pixels in screenshot
magick /tmp/screen.png txt:- | grep "#FF0000" | head -5

# Calculate center of colored region
magick /tmp/screen.png txt:- | grep "#FF0000" | awk -F'[,:]' '
  BEGIN{sx=0;sy=0;c=0}
  {sx+=$1;sy+=$2;c++}
  END{printf "Center: (%d, %d)\n", sx/c, sy/c}'
```

### Dialog Button Click

1. Screenshot the dialog
2. Find button coordinates visually
3. Click (no scaling on 1920x1080)

```bash
# Example: Click "OK" button at (960, 540)
/opt/homebrew/bin/cliclick c:960,540
```

### Type in Text Field

```bash
# Click to focus, then type
/opt/homebrew/bin/cliclick c:500,300
sleep 0.2
/opt/homebrew/bin/cliclick t:"Hello world"
/opt/homebrew/bin/cliclick kp:return
```

## Helper Scripts

Located in `/Users/eason/clawd/scripts/`:

- `calibrate-cursor.sh` - Calibrate coordinate scaling
- `click-at-visual.sh` - Click at screenshot coordinates
- `get-cursor-pos.sh` - Get current cursor position
- `attach-browser-relay.sh` - Auto-click Browser Relay extension

## Keyboard Navigation (When Clicks Fail)

**Google OAuth and protected pages block synthetic mouse clicks!** Use keyboard navigation:

```bash
# Tab to navigate between elements
osascript -e 'tell application "System Events" to keystroke tab'

# Shift+Tab to go backwards
osascript -e 'tell application "System Events" to key code 48 using shift down'

# Enter to activate focused element
osascript -e 'tell application "System Events" to keystroke return'

# Full workflow: Tab 3 times then Enter
osascript -e '
tell application "System Events"
    keystroke tab
    delay 0.15
    keystroke tab
    delay 0.15
    keystroke tab
    delay 0.15
    keystroke return
end tell
'
```

**When to use keyboard instead of mouse:**
- Google OAuth / login pages (anti-automation protection)
- Popup dialogs with focus trapping
- When mouse clicks consistently fail after verification

## Chrome Browser Relay & Multiple Windows

**Problem**: Browser Relay may list tabs from multiple Chrome windows, causing `snapshot` to fail on the desired tab.

**Solution**:
1. Close extra Chrome windows before automation
2. Or ensure only the target window has relay attached

**Check tabs visible to relay**:
```bash
# In agent code
browser action=tabs profile=chrome
```

If target tab missing from list → wrong window attached.

**Verify single window**:
```bash
osascript -e 'tell application "Google Chrome" to return count of windows'
```

## Verify-Before-Click Workflow

**Critical**: Always verify coordinates BEFORE clicking important buttons.

```bash
# 1. Take screenshot
osascript -e 'do shell script "/usr/sbin/screencapture -x /tmp/before.png"'

# 2. View screenshot (Read tool), note target position

# 3. Move mouse to verify position (optional)
python3 -c "import pyautogui; pyautogui.moveTo(X, Y)"
osascript -e 'do shell script "/usr/sbin/screencapture -C -x /tmp/verify.png"'

# 4. Check cursor is on target, THEN click
/opt/homebrew/bin/cliclick c:X,Y

# 5. Take screenshot to confirm action worked
osascript -e 'do shell script "/usr/sbin/screencapture -x /tmp/after.png"'
```

## Troubleshooting

**Click lands wrong**: Verify scale factor with calibration script

**cliclick m: doesn't move cursor visually**: Use `c:` (click) instead, or check with `cliclick p` to confirm position changed

**Permission denied**: System Settings → Privacy & Security → Accessibility → Add `/opt/homebrew/bin/node`

**Window not found**: Check exact app name:
```bash
osascript -e 'tell application "System Events" to get name of every process whose background only is false'
```

**Clicks ignored on OAuth/protected pages**: These pages block synthetic events. Use keyboard navigation (Tab + Enter) instead.

**pyautogui vs cliclick coordinates differ**: Stick with cliclick for consistency. pyautogui may have different coordinate mapping.

**Quartz CGEvent clicks don't work**: Some pages (Google OAuth) block low-level mouse events too. Keyboard is the only reliable method.
