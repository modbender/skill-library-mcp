---
name: android_control
description: Control an Android device via command-line tools (uiautomator, screencap, input, am). Automatically attempts non-root execution first and falls back to root if necessary.
homepage: https://developer.android.com/studio/test/uiautomator
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":["sh"],"optional_bins":["su","uiautomator","input","am","screencap"]}}}
---

# Android Control Skill

Control an Android phone directly from Clawdbot using built-in Android CLI tools.  
The skill always tries **normal (non-root)** commands first; if they fail, it automatically retries with **root mode (su)** when available.

## Features

- Get UI hierarchy snapshot via `uiautomator dump`
- Capture screen using `screencap`
- Simulate taps, swipes, and input events via `input`
- Launch apps using `am start`
- Auto retry with root if non-root fails

# Setup

Most Android ROMs include `uiautomator`, `input`, `screencap`, and `am`.

To enable root fallback, install Magisk or run:
```bash
su
````

# Usage

## Get UI Snapshot (uiautomator dump)

```bash
# Try non-root
uiautomator dump /sdcard/ui_dump.xml 2>/dev/null \
  && cat /sdcard/ui_dump.xml \
  || (
    # Fallback to root
    su -c "uiautomator dump /sdcard/ui_dump.xml" && su -c "cat /sdcard/ui_dump.xml"
  )
```

## Take Screenshot (PNG, base64 encoded)

```bash
TMP="/sdcard/ai_screen.png"

# Try non-root
screencap -p "$TMP" 2>/dev/null \
  && base64 "$TMP" \
  || (
    # Root fallback
    su -c "screencap -p $TMP"
    su -c "base64 $TMP"
  )
```

## Tap on Screen

```bash
# Example: tap at (540, 1600)

input tap 540 1600 2>/dev/null \
  || su -c "input tap 540 1600"
```

## Swipe on Screen

```bash
# Example: swipe from (500, 1600) to (500, 600) over 300ms

input swipe 500 1600 500 600 300 2>/dev/null \
  || su -c "input swipe 500 1600 500 600 300"
```

## Launch an App

```bash
# Example: launch Android Settings

am start -n com.android.settings/.Settings 2>/dev/null \
  || su -c "am start -n com.android.settings/.Settings"
```

## Send Text Input

```bash
# Example: send text "Hello"

input text "Hello" 2>/dev/null \
  || su -c "input text 'Hello'"
```
