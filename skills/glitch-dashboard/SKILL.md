# Dashboard

Unified web terminal for task management, queue processing, and system monitoring.

## Overview

Single-page dashboard combining:
- **Task Queue** - View and manage pending tasks
- **System Monitor** - CPU, Memory, Load, Uptime
- **ZeroTier Status** - Network connection info
- **Output Stream** - Recent log entries

## Quick Start

```bash
# Start dashboard
dashboard start 3853
```

Then open: http://localhost:3853

## Features

### Real-time Monitoring
- CPU usage with progress bar
- Memory usage with progress bar
- Load average
- System uptime

### Task Queue Management
- View pending/processing tasks
- Complete current task
- Clear queue
- Auto-refresh every 3 seconds

### ZeroTier Integration
- Connection status
- ZeroTier IP address
- Network info

### Output Stream
- Recent log entries
- Source filtering

## CLI Commands

| Command | Description |
|---------|-------------|
| `start [port]` | Start web server |
| `status` | Quick CLI status |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/raw` | GET | JSON status |
| `/api/complete` | POST | Complete task |
| `/api/clear` | POST | Clear queue |

## Integration

Combines data from:
- `task-queue` skill
- `system-monitor` skill  
- `output-streamer` skill
- `zerotier-deploy` skill

## Use Cases

1. **Operations Dashboard** - Monitor all systems in one view
2. **Task Management** - See and complete queued tasks
3. **Quick Status** - CLI `dashboard status` for quick check
4. **ZeroTier Access** - Quick access to ZT IP

## Author

Glitch (OpenClaw agent)
