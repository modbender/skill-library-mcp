# Server Health Skill

Comprehensive server health monitoring for OpenClaw.

## Features

✅ System stats (CPU, RAM, Disk, Uptime)  
✅ Top processes by CPU/RAM  
✅ OpenClaw Gateway status & model config  
✅ Services status (Docker, PostgreSQL, etc.)  
✅ Multiple output formats (standard, JSON, alerts-only)  

## Usage

```bash
# Standard view (default)
./server-health.sh

# JSON output (for automation)
./server-health.sh --json

# Alerts only (warnings/errors)
./server-health.sh --alerts

# Verbose (with temp, network, I/O - coming soon)
./server-health.sh --verbose
```

## Example Output

```
🖥️ SERVER HEALTH
━━━━━━━━━━━━━━━━━━━━

💻 SYSTEM
CPU: ████░░░░░░ 42% (Load: 1.2, 0.8, 0.5)
RAM: ██████░░░░ 1.4GB/8GB (18%)
DISK: ████░░░░░░ 45GB/100GB (45%)
UP: ⏱️ 5d 3h

🔄 TOP PROCESSES
node         35%    450MB
postgres     12%    280MB
openclaw      8%    180MB

⚡ OPENCLAW GATEWAY
Status: ✅ Running (PID: 1639125)
Uptime: 2d 5h | Port: 18789 | v2026.2.6-3

🤖 MODEL CONFIG
Primary: claude-sonnet-4-5
Fallbacks: glm-4.7 → copilot-sonnet → opus-4-5

📊 SESSIONS
Active: 3

🐳 SERVICES
Docker: ✅ 8 containers
PostgreSQL: ✅ Running
```

## Requirements

- bash
- jq (for JSON parsing)
- systemctl (for service status)
- docker (optional, for container status)

## Installation

```bash
# Via ClawHub
clawhub install server-health

# Manual
git clone <repo>
chmod +x server-health.sh
```

## Integration with OpenClaw

Add to SKILL.md in your workspace:

```markdown
### server-health
Quick server monitoring. Use when user asks about system health, resource usage, or OpenClaw status.

Usage: `./skills/server-health/server-health.sh`
```

## License

MIT

## Author

Created for OpenClaw community
