# Hammerspoon Setup Guide

## What is Hammerspoon?

Hammerspoon is an open-source macOS automation tool that bridges Lua scripting with native macOS APIs. It's the engine behind Desktop Guardian's window management and dialog dismissal.

## Installation

### Via Homebrew (recommended)
```bash
brew install --cask hammerspoon
```

### Manual
Download from https://www.hammerspoon.org/

## First-Time Setup

### 1. Launch Hammerspoon
```bash
open -a Hammerspoon
```
A menubar icon (🔨) appears.

### 2. Grant Accessibility
Hammerspoon will prompt for Accessibility access on first launch. If it doesn't:
1. System Settings → Privacy & Security → Accessibility
2. Click + and add `/Applications/Hammerspoon.app`
3. Toggle ON

### 3. Enable IPC (for `hs` CLI)
Open Hammerspoon Console (click menubar icon → Console) and run:
```lua
hs.ipc.cliInstall()
```

Or add to `~/.hammerspoon/init.lua`:
```lua
require("hs.ipc")
```

### 4. Verify
```bash
hs -c '"hello"'
# Should print: hello
```

## Desktop Guardian Spoon

The DesktopGuardian Spoon is installed to `~/.hammerspoon/Spoons/DesktopGuardian.spoon/`.

### Verify it's loaded
```bash
hs -c 'spoon.DesktopGuardian.version()'
# Returns: {"version":"2.0.0","name":"DesktopGuardian"}
```

### Test queries
```bash
hs -c 'spoon.DesktopGuardian.queryAll()'
hs -c 'spoon.DesktopGuardian.listApps()'
hs -c 'spoon.DesktopGuardian.listDialogs()'
```

## Troubleshooting

### `hs: command not found`
Run in Hammerspoon Console: `hs.ipc.cliInstall()`
Or check `/opt/homebrew/bin/hs` or `/usr/local/bin/hs`.

### Accessibility denied
- Check System Settings → Privacy & Security → Accessibility
- Try removing and re-adding Hammerspoon
- Restart Hammerspoon after granting

### Spoon not loading
- Check `~/.hammerspoon/init.lua` contains `hs.loadSpoon("DesktopGuardian")`
- Click menubar icon → Reload Config
- Check Console for errors
