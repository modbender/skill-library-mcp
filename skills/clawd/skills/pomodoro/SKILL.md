---
name: ClawDoro
description: A beautiful Pomodoro timer with task tracking. Opens a clean, focused timer interface in your browser.
commands:
  clawdoro: node ~/clawd/skills/pomodoro/trigger.js
  pomodoro: node ~/clawd/skills/pomodoro/trigger.js
---

# 🍅 ClawDoro

A beautiful Pomodoro timer with task tracking. Built for focus.

![ClawDoro](https://snail3d.github.io/ClawDoro)

## Usage

```bash
# Start with default 27/5/15 min
clawdoro

# Custom focus time
clawdoro 50

# Full custom (focus/short/long)
clawdoro 50 10 30
```

Or just tell Clawd: **"Start ClawDoro"** or **"ClawDoro 45 minutes"**

## Features

- 🍅 Beautiful, distraction-free timer UI
- ⏱️ Customizable work/break durations (default 27 min - Clawd's pick!)
- 📝 Task list with localStorage persistence
- ⌨️ Keyboard shortcuts (Space = start/pause, R = reset)
- 🔊 3-pulse soothing chime on completion
- ☕ Fun "break time" surprise 😉
- 📱 Mobile responsive
- 💾 Everything persists between sessions

## How It Works

1. Opens a mini HTTP server on port 8765
2. Serves the beautiful ClawDoro UI
3. Auto-opens browser
4. Tasks & settings saved to localStorage

## Files

- `trigger.js` - Entry point that starts server and opens browser
- `timer.html` - The ClawDoro timer UI
- `SKILL.md` - This documentation

---

☕ **Support the work:** [Buy Me a Coffee](https://www.buymeacoffee.com/snail3d)

Built with 💜 by Clawd for Snail
