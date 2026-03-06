---
name: openclaw-menubar
description: Enable OpenClaw as a native macOS menu bar app with quick access
  popup. **macOS ONLY** - not compatible with Windows or Linux. Use when user
  asks to "enable menubar", "add menu bar", "run in menu bar", "make it
  accessible from menu bar", or wants quick OpenClaw access without opening full
  dashboard.
---


# OpenClaw Menu Bar

> **⚠️ macOS ONLY** - This skill requires macOS. Menu bar apps are not supported on Windows or Linux.

Adds a native macOS menu bar app for quick OpenClaw access - click the crab icon 🦀 in your menu bar to get an instant chat popup.

## Quick Start

### Install & Launch

```bash
scripts/install.sh
scripts/start.sh
```

The crab icon will appear in your menu bar. Click it to open the chat window.

### Stop

```bash
scripts/stop.sh
```

### Check Status

```bash
scripts/status.sh
```

## What It Does

- **Menu bar icon**: Crab 🦀 icon appears in macOS menu bar
- **Quick popup**: Click icon → instant chat window (no browser needed)
- **Keyboard shortcut**: Cmd+Shift+O to toggle popup
- **Native feel**: Proper macOS vibrancy, stays on top when needed
- **Lightweight**: Electron app, ~480x680px popup window

## Icon Setup

The menubar app requires two icon files in `assets/openclaw-menubar/icons/`:
- `icon.png` (22x22 pixels, transparent PNG)
- `icon@2x.png` (44x44 pixels, transparent PNG)

### Option 1: Auto-generate icons

```bash
cd assets/openclaw-menubar
./create-icon.sh
```

This creates a simple crab emoji icon.

### Option 2: Custom icons

Replace the generated icons with your own 22x22 and 44x44 transparent PNGs.

**Note**: macOS menu bar uses monochrome template mode (auto-colorizes your icon).

### Window Size

Edit `assets/openclaw-menubar/main.js`:
```javascript
browserWindow: {
  width: 480,  // Change width
  height: 680  // Change height
}
```

### Keyboard Shortcut

Edit `assets/openclaw-menubar/main.js`:
```javascript
globalShortcut.register('CommandOrControl+Shift+O', () => {
  // Change 'O' to any key
});
```

## Architecture

- **Electron app** using [menubar](https://github.com/maxogden/menubar) package
- **Header**: Custom HTML header (index-webchat.html) with branding
- **Content**: OpenClaw webchat loaded via BrowserView with auth token
- **Auto-auth**: Reads gateway config from `~/.openclaw/openclaw.json`

## Requirements

- macOS (menu bar apps are macOS-specific)
- OpenClaw Gateway running on localhost
- Node.js (for Electron)

## Troubleshooting

### Icon not showing
- Icon must be 22x22 PNG with transparent background
- macOS menu bar uses monochrome template mode (auto-colorizes)

### "OpenClaw Not Running" error
- Ensure OpenClaw Gateway is running: `openclaw gateway status`
- Check config: `cat ~/.openclaw/openclaw.json`

### Window doesn't open
- Check logs in Console.app (search "OpenClaw")
- Try: `scripts/stop.sh && scripts/start.sh`

## Files

- `assets/openclaw-menubar/` - Complete Electron app
- `scripts/install.sh` - Install dependencies (npm install)
- `scripts/start.sh` - Launch the menu bar app
- `scripts/stop.sh` - Kill the app process
- `scripts/status.sh` - Check if app is running
