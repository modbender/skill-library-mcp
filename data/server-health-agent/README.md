# Server Health Agent (OpenClaw Skill)

Production-ready OpenClaw skill to monitor VPS health metrics including CPU, RAM, disk usage, and Docker container status.

## Features

- Real-time CPU monitoring
- RAM usage monitoring
- Disk usage monitoring
- Docker container detection
- Structured JSON output
- Compatible with OpenClaw Docker environment
- Node.js 18–22 compatible
- CLI testing supported

## Installation

Copy this folder into:

~/.openclaw/workspace/skills/

Restart OpenClaw:

docker compose restart

## Usage

Ask OpenClaw:

Check server health

or

Run server-health-agent

## Example Output

```json
{
  "success": true,
  "skill": "server-health-agent",
  "timestamp": "2026-02-20T12:00:00Z",
  "server_health": {
    "cpu_percent": "12.44",
    "ram_percent": "21.33",
    "disk_usage": "51%",
    "docker_status": "openclaw-openclaw-gateway-1: Up 2 hours"
  }
}
```
