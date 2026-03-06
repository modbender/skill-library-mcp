---
name: pomodoro
description: Use this skill when a user wants to run timed focus sessions (Pomodoro technique) from the terminal.
---

# Pomodoro Timer

## When to use

- User asks to start a focus session, work timer, or pomodoro.

## How it works

Run a 25-minute focus block followed by a 5-minute break. After 4 blocks, take a 15-minute break.

## Start a session

```bash
echo "🍅 Focus started at $(date +%H:%M)" && sleep 1500 && osascript -e 'display notification "Time for a break!" with title "Pomodoro"' && echo "Break time at $(date +%H:%M)"
```

## Custom duration (minutes)

```bash
MINS=15 && echo "Focus: ${MINS}m started at $(date +%H:%M)" && sleep $((MINS * 60)) && echo "Done at $(date +%H:%M)"
```

## Log completed sessions

```bash
echo "$(date +%Y-%m-%d) $(date +%H:%M) - 25min focus" >> ~/pomodoro.log
```

## Review today's log

```bash
grep "$(date +%Y-%m-%d)" ~/pomodoro.log 2>/dev/null || echo "No sessions today."
```
