# KKClaw Server

Optimized OpenClaw client for Ubuntu/Raspbian as remote server.

## Overview

KKClaw Server is a headless version of KKClaw designed for Ubuntu and Raspbian servers. It runs without GUI, perfect for Raspberry Pi or cloud instances.

## Features

### 1. Heartbeat Mechanism
- Configurable heartbeat interval (default: 30s)
- Status reporting to gateway
- Memory and uptime monitoring
- Automatic connection monitoring

### 2. Auto Reconnect
- Exponential backoff reconnection
- Max retry limit with configurable attempts
- Persistent connection monitoring
- Graceful degradation

### 3. Auto Recovery
- Automatic session recovery
- Queue restoration after disconnect
- Model auto-rollback on failure
- Max restart attempts

### 4. Queue Management
- Message queuing when disconnected
- Automatic retry with backoff
- Queue size limits
- FIFO processing

### 5. Model Switching
- Hot model switching without restart
- Fallback model support
- Auto-rollback on failure
- Timeout protection

## Quick Start

```bash
# Initialize config
kkclaw-server init

# Start server
kkclaw-server start

# Check status
kkclaw-server status

# Switch model
kkclaw-server model minimax-portal/MiniMax-M2.5
```

## Configuration

Edit `~/.kkclaw/config.json`:

```json
{
  "gateway": {
    "url": "http://your-gateway:18789",
    "apiKey": "your-api-key"
  },
  "heartbeat": {
    "enabled": true,
    "interval": 30000
  },
  "reconnect": {
    "enabled": true,
    "maxRetries": 10,
    "baseDelay": 1000
  },
  "recovery": {
    "enabled": true,
    "maxRestarts": 5
  },
  "queue": {
    "maxSize": 100,
    "maxRetries": 3
  },
  "models": {
    "default": "claude-opus-4-6",
    "fallback": "minimax-portal/MiniMax-M2.5"
  }
}
```

## Systemd Service (Raspbian/Ubuntu)

Create `/etc/systemd/system/kkclaw.service`:

```ini
[Unit]
Description=KKClaw Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/kkclaw
ExecStart=/usr/bin/node /home/pi/kkclaw/main.js start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kkclaw
sudo systemctl start kkclaw
```

## Features Detail

### Heartbeat
- Sends periodic heartbeats to gateway
- Reports: status, model, queue length, memory, uptime
- Detects connection issues early

### Auto Reconnect
- Exponential backoff: 1s, 2s, 4s, 8s... up to 60s
- Max 10 retries by default
- Manual reconnect available

### Auto Recovery
- Clears failed session state
- Restores queued messages
- Auto-rollback to previous model on failure

### Queue Management
- Queues messages when disconnected
- Automatic retry with exponential backoff
- Removes failed messages after max retries

### Model Switching
- Hot switch without restart
- Timeout: 30s default
- Auto fallback to default model on failure

## CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Create default config |
| `start` | Start server |
| `status` | Show current status |
| `connect` | Manual connect |
| `model <name>` | Switch model |
| `queue` | Show queue info |

## Author

Glitch (OpenClaw agent)
