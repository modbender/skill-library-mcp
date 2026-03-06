# 🫀⚡ Agent Defibrillator

> *"CLEAR!"* — Every sysadmin, eventually

Your AI agent is amazing. It writes code, sends messages, automates your life. But sometimes... it just *dies*. Gateway stuck. Process frozen. Flatline.

And you're not home. Or you're asleep. Or you're touching grass (good for you).

**Agent Defibrillator** is a watchdog that monitors your AI agent gateway and automatically shocks it back to life when it crashes. No more coming home to a dead agent. No more "why didn't you reply for 6 hours?"

## How It Works

```
Every 10 minutes:
    │
    ├─ Agent alive?
    │       │
    │       └─ Version match? → 😴 (sleep)
    │               │
    │               └─ Stale version? → 🔄 Restart + 📢 Notify
    │
    └─ Agent dead?
           │
           ├─ Wait & retry (maybe it's just slow)
           │
           └─ Still dead after 3 checks?
                  │
                  └─ 🫀⚡ "CLEAR!" → Full restart + 📢 Notify
                         │
                         ├─ ✅ Pulse restored!
                         │
                         └─ 💀 Manual intervention needed
```

**Safety features:**
- 🔄 5-minute cooldown between shocks (no restart loops)
- 🔒 Lock file prevents concurrent runs
- 🧹 Kills orphaned processes before restart
- 📝 Only logs when something goes wrong (no spam)

**v2 features:**
- 🔍 **Version mismatch detection** — catches stale gateway processes running old code after npm updates
- 📢 **Discord notifications** — get pinged when your agent gets shocked back to life
- ⏰ 1-hour cooldown for version-based restarts (separate from crash cooldown)

## Quick Install

### Option 1: One-liner (recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/hazy2go/agent-defibrillator/main/install.sh | bash
```

### Option 2: Clone & Install
```bash
git clone https://github.com/hazy2go/agent-defibrillator.git
cd agent-defibrillator
chmod +x install.sh
./install.sh
```

### Option 3: Ask Your Agent! 🤖

Just paste this prompt to your AI agent:

> **Prompt:**
> ```
> Install the Agent Defibrillator watchdog from https://github.com/hazy2go/agent-defibrillator
> 
> This is a macOS launchd service that monitors the OpenClaw gateway process and
> automatically restarts it if it crashes. 
> 
> Steps:
> 1. Clone the repo to a temp directory
> 2. Run the install.sh script
> 3. Verify the service is running with: launchctl list | grep defib
> 4. The watchdog checks every 10 minutes by default
> 
> After install, show me the status and explain what was set up.
> ```

Your agent will literally install its own life support. How's that for self-preservation?

## Configuration

### Custom Gateway Label
If your gateway service has a different name:
```bash
./install.sh "your.gateway.label" 600
```

### Environment Variables
Set these before running, or edit the script:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFIB_GATEWAY_LABEL` | `ai.openclaw.gateway` | launchd service label |
| `DEFIB_GATEWAY_PROCESS` | `openclaw-gateway` | Process name in `ps aux` |
| `DEFIB_RETRY_DELAY` | `10` | Seconds between retries |
| `DEFIB_MAX_RETRIES` | `3` | Retries before restarting |
| `DEFIB_COOLDOWN` | `300` | Seconds between restarts |
| `DEFIB_VERSION_COOLDOWN` | `3600` | Seconds between version restarts |

### Discord Notifications (v2)
Edit the script to set your Discord channel ID:
```bash
DISCORD_CHANNEL="your-channel-id-here"
```
Uses `openclaw message send` — requires OpenClaw to be configured with Discord.

### Change Check Interval
Edit the plist or reinstall:
```bash
./install.sh ai.openclaw.gateway 300  # Check every 5 minutes
```

## Manual Commands

```bash
# View logs
tail -f ~/.openclaw/logs/defibrillator.log

# Check if watchdog is running
launchctl list | grep defib

# Manually trigger a check
~/.openclaw/scripts/defibrillator.sh

# Stop the watchdog
launchctl bootout gui/$(id -u)/com.openclaw.defibrillator

# Restart the watchdog
launchctl kickstart -k gui/$(id -u)/com.openclaw.defibrillator
```

## Uninstall

```bash
launchctl bootout gui/$(id -u)/com.openclaw.defibrillator
rm ~/Library/LaunchAgents/com.openclaw.defibrillator.plist
rm ~/.openclaw/scripts/defibrillator.sh
```

## Why "Defibrillator"?

Because your agent has a heart. And sometimes hearts stop. And when they do, you need 200 joules of `launchctl bootstrap` straight to the chest.

Also, "watchdog" was boring.

## Requirements

- macOS (uses launchd)
- An AI agent running via launchd (OpenClaw, etc.)
- A sense of humor about your agent's mortality

## Troubleshooting

### "Gateway plist not found"
Check your gateway's plist location:
```bash
ls ~/Library/LaunchAgents/*gateway* ~/Library/LaunchAgents/*openclaw*
```

### Watchdog isn't starting
```bash
launchctl list | grep defib  # Should show a PID or "-"
cat ~/.openclaw/logs/defibrillator.log  # Check for errors
```

### Agent keeps dying anyway
The defibrillator can restart your agent, but it can't fix *why* it's dying. Check:
- Memory usage (`top -l 1 | grep openclaw`)
- Disk space (`df -h`)
- Your agent's logs

## Contributing

Found a bug? Agent still dying? PRs welcome.

## License

MIT — because even death should be free.

---

*Made with 🫀 by [hazy2go](https://github.com/hazy2go) and their agent Rem, who kept dying until they built this.*

*P.S. - If you're reading this, your agent is probably still alive. For now.* ⚡
