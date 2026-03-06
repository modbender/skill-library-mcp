---
name: lametric-cli
description: Control LaMetric TIME/SKY smart displays from the command line. Use when sending notifications, controlling device brightness/volume, managing timers, or displaying data on LaMetric devices. Triggers on "LaMetric", "smart display", "notification to device", "set timer", "send alert to clock".
license: MIT
homepage: https://github.com/dedene/lametric-cli
metadata:
  author: dedene
  version: "1.1.0"
  openclaw:
    primaryEnv: LAMETRIC_API_KEY
    requires:
      bins:
        - lametric
    install:
      - kind: brew
        tap: dedene/tap
        formula: lametric
        bins: [lametric]
      - kind: go
        package: github.com/dedene/lametric-cli/cmd/lametric
        bins: [lametric]
---

# LaMetric CLI

CLI tool for controlling LaMetric TIME/SKY devices. Send notifications, control settings, manage timers, and stream content.

## Prerequisites

### Installation

```bash
# Homebrew (macOS/Linux)
brew install dedene/tap/lametric

# Or Go install
go install github.com/dedene/lametric-cli/cmd/lametric@latest
```

### Setup

1. Get API key from LaMetric mobile app: Device Settings > API Key
2. Run setup wizard:

```bash
lametric setup
```

Or configure manually:

```bash
# Store API key securely
lametric auth set-key --device=living-room

# Or use environment variables
export LAMETRIC_API_KEY=your-api-key
export LAMETRIC_DEVICE=192.168.1.100
```

Config file location: `~/.config/lametric-cli/config.yaml`

## Core Workflows

### Sending Notifications

**Simple notification:**
```bash
lametric notify "Hello World"
```

**With icon and sound:**
```bash
lametric notify "Build passed" --icon=checkmark --sound=positive1
```

**Critical alert (wakes device, plays alarm):**
```bash
lametric notify "ALERT: Server down" --priority=critical --sound=alarm1
```

**Progress indicator:**
```bash
lametric notify "Upload progress" --goal=75/100 --icon=upload
```

**Sparkline chart:**
```bash
lametric notify "CPU Usage" --chart=10,25,50,30,45,80,60
```

**From stdin (for pipelines):**
```bash
echo "Build complete" | lametric notify
git log -1 --format="%s" | lametric notify --icon=github
```

**Wait for user dismissal:**
```bash
lametric notify "Confirm deployment?" --wait
```

### Device Control

**Get device info:**
```bash
lametric device
```

**Display brightness:**
```bash
lametric display get
lametric display brightness 50      # Set to 50%
lametric display mode auto          # Auto brightness
```

**Audio volume:**
```bash
lametric audio get
lametric audio volume 30            # Set to 30%
```

**Bluetooth:**
```bash
lametric bluetooth get
lametric bluetooth on
lametric bluetooth off
```

### Built-in Apps

**Timer:**
```bash
lametric app timer set 5m           # Set 5 minute timer
lametric app timer set 1h30m        # Set 1 hour 30 minutes
lametric app timer start
lametric app timer pause
lametric app timer reset
```

**Stopwatch:**
```bash
lametric app stopwatch start
lametric app stopwatch pause
lametric app stopwatch reset
```

**Radio:**
```bash
lametric app radio play
lametric app radio stop
lametric app radio next
lametric app radio prev
```

**App navigation:**
```bash
lametric app list                   # List installed apps
lametric app next                   # Switch to next app
lametric app prev                   # Switch to previous app
```

### Streaming

Stream images or video to the display:

```bash
lametric stream start               # Start streaming session
lametric stream image logo.png      # Send static image
lametric stream gif animation.gif   # Send animated GIF
lametric stream stop                # End streaming
```

**Pipe from ffmpeg:**
```bash
ffmpeg -i video.mp4 -vf "scale=37:8" -f rawvideo -pix_fmt rgb24 - | lametric stream pipe
```

### Discovery

Find LaMetric devices on your network:

```bash
lametric discover
lametric discover --timeout=10s
```

## Common Patterns

### Build/CI Notifications

```bash
# Success
lametric notify "Build #123 passed" --icon=checkmark --sound=positive1

# Failure
lametric notify "Build #123 failed" --icon=error --sound=negative1 --priority=warning

# Deployment
lametric notify "Deployed to prod" --icon=rocket --sound=positive2
```

### System Monitoring

```bash
# CPU alert
lametric notify "High CPU: 95%" --priority=warning --icon=warning

# Disk space
lametric notify "Disk: 85% full" --goal=85/100 --icon=harddrive
```

### Pomodoro Timer

```bash
lametric app timer set 25m && lametric app timer start
```

### Meeting Reminder

```bash
lametric notify "Meeting in 5 min" --icon=calendar --sound=alarm3 --priority=warning
```

## Quick Reference

### Popular Icons

| Alias | Description |
|-------|-------------|
| `checkmark` | Success/complete |
| `error` | Error/failure |
| `warning` | Warning/caution |
| `info` | Information |
| `rocket` | Deploy/launch |
| `github` | GitHub |
| `slack` | Slack |
| `mail` | Email |
| `calendar` | Calendar/meeting |
| `download` | Download |
| `upload` | Upload |

Run `lametric icons` for full list.

### Popular Sounds

| Sound | Category |
|-------|----------|
| `positive1-5` | Success sounds |
| `negative1-5` | Error sounds |
| `alarm1-13` | Alarm sounds |
| `notification1-4` | Gentle notifications |

Run `lametric sounds` for full list.

### Global Flags

| Flag | Description |
|------|-------------|
| `-d, --device` | Device name or IP |
| `-j, --json` | Output JSON |
| `--plain` | Output TSV (for scripting) |
| `-v, --verbose` | Verbose logging |

## Troubleshooting

### Connection Failed

1. Verify device IP: `lametric discover`
2. Check device is on same network
3. Ensure API key is correct: `lametric auth get-key --device=NAME`

### Authentication Error

```bash
# Re-set API key
lametric auth set-key --device=living-room

# Or use environment variable
export LAMETRIC_API_KEY=your-api-key
```

### Device Not Found

```bash
# Discover devices
lametric discover --timeout=10s

# Add to config
lametric setup
```


## Installation

```bash
brew install dedene/tap/lametric
```
