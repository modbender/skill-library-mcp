---
name: minecraft-monitor
description: Monitor Minecraft servers by checking online status, player counts, latency, and version info using the Server List Ping protocol. Use when the user asks to check Minecraft server status, monitor a Minecraft server, verify if a server is online, get player counts, or mentions Minecraft server monitoring. Example servers include corejourney.org.
---

# Minecraft Server Monitoring

Quickly check Minecraft server status without installing any external dependencies.

## Quick Check

Check if a server is online:

```bash
python3 ~/.openclaw/workspace/skills/public/minecraft-monitor/scripts/minecraft-status.py corejourney.org
```

```
🟢 corejourney.org:25565 - ONLINE (45ms)
   Version: 1.20.4
   Players: 3/20
   Online: Steve, Alex, CreeperHunter
   MOTD: Welcome to Core Journey!
```

## Usage

```bash
python3 ~/.openclaw/workspace/skills/public/minecraft-monitor/scripts/minecraft-status.py <host[:port]> [timeout]
```

- **host**: Server hostname or IP address (e.g., `corejourney.org`, `192.168.1.10`)
- **port**: Optional, defaults to `25565`
- **timeout**: Optional connection timeout in seconds (default: 5)

### Examples

```bash
# Check default port
python3 ~/.openclaw/workspace/skills/public/minecraft-monitor/scripts/minecraft-status.py corejourney.org

# Check custom port
python3 ~/.openclaw/workspace/skills/public/minecraft-monitor/scripts/minecraft-status.py corejourney.org:25566

# Check IP with longer timeout
python3 ~/.openclaw/workspace/skills/public/minecraft-monitor/scripts/minecraft-status.py 192.168.1.10 10
```

## Output

**Online server:**
- 🟢 Green (good ping) / 🟡 Yellow (moderate) / 🟠 Orange (slow)
- Server address and port
- Response time in milliseconds
- Minecraft version
- Current/maximum player count
- List of online players (up to 5 shown)
- Server MOTD (message of the day)

**Offline server:**
- 🔴 Red indicator
- Error message (timeout, connection refused, etc.)

## What's Being Monitored

- ✅ Online/offline status
- ✅ Player count (current/max)
- ✅ Response time/latency
- ✅ Server version
- ✅ Online player list (if available)
- ✅ Server MOTD

## Notes

- Uses Minecraft Server List Ping (SLP) protocol - works with all modern Minecraft servers
- No server-side plugins or RCON access required
- Exit code 0 if online, 1 if offline (useful for scripts/automation)
- SRV records are not automatically resolved - use the actual server address

## Integration Ideas

- Add to a cron job for periodic health checks
- Wrap in a monitoring script that alerts if server goes offline
- Use in automation pipelines that depend on server availability
- Create a dashboard showing server status history