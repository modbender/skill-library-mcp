---
name: pomoclaw
description: Control the PomoClaw pomodoro timer on the Mac. Use when the user asks to start, stop, pause a pomodoro/pomoclaw/focus timer, check timer status, or when a pomodoro webhook fires (system event containing "Pomodoro finished").
---

# PomoClaw 🍅

A minimal pomodoro timer for your macOS menu bar. Control via URL scheme, perfect for OpenClaw integration.

**GitHub:** https://github.com/vkozlovskyi/PomoClaw
**Download:** https://github.com/vkozlovskyi/PomoClaw/releases/latest

## Commands

Run via `nodes.run` on the Mac node using `bash -c "open 'pomoclaw://...'"`:

```
pomoclaw://start                     # Start timer with default duration (25 min)
pomoclaw://start?minutes=N           # Start timer for N minutes (1-99)
pomoclaw://pause                     # Pause/resume toggle
pomoclaw://stop                      # Stop and reset
pomoclaw://status                    # Write status to ~/.pomoclaw/status.json
pomoclaw://break?minutes=N           # Start break timer for N minutes
pomoclaw://skip                      # Skip current break
```

## Configuration

All config via single `pomoclaw://config` command:

```
pomoclaw://config?workMinutes=25     # Set default work duration
pomoclaw://config?shortBreak=5       # Set short break duration
pomoclaw://config?longBreak=15       # Set long break duration
pomoclaw://config?sound=Glass        # Set work completion sound
pomoclaw://config?breakSound=Purr    # Set break completion sound
pomoclaw://config?launchAtLogin=true # Enable launch at login
pomoclaw://config?count=0            # Set completed pomodoro count
```

Multiple params can be combined:
```
pomoclaw://config?workMinutes=25&shortBreak=5&longBreak=15
```

### Valid sounds
Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink

### Defaults
- Work: 25 min, Short break: 5 min, Long break: 15 min (every 4th pomodoro)
- Work sound: Glass, Break sound: Purr

## Check Status

After `pomoclaw://status`, read the file:

```
cat ~/.pomoclaw/status.json
```

Returns: `{"state": "running|paused|idle", "remaining": <seconds>, "total": <seconds>, "startedAt": "<ISO8601>", "completedCount": N, "mode": "work|break|break_ready|idle"}`

## Webhooks

- Work complete: `🍅 Pomodoro finished! N min focus session complete.`
- Break complete: `☕ Break finished! N min break complete.`

On work complete:
- Acknowledge the completed session to the user
- Break timer will auto-appear (green arc). User clicks to start.
- Long break (15 min) after every 4th pomodoro, short break (5 min) otherwise.

## Notes

- Timer range: 1–99 minutes
- App must be running on Mac for commands to work
- No dock icon — lives in menu bar only (LSUIElement)
- Use `bash -c "open 'pomoclaw://...'"` via nodes.run (more reliable than array format with URL encoding)
- Break state is NOT restored on app restart — only meaningful right after work
