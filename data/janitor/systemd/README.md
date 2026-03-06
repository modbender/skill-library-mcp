# Systemd Service Setup

This guide shows how to set up Janitor as a systemd service on Linux for automatic background monitoring.

## Service Files

Below are the systemd service files you'll need to create manually. Copy the content into the appropriate files.

### 1. Janitor Monitor Service

This service runs Janitor monitoring in the background, checking context usage every 5 minutes and performing automatic cleanup when needed.

**File:** `/etc/systemd/system/janitor-monitor@.service`

```ini
[Unit]
Description=OpenClaw Janitor Session Monitoring Service
Documentation=https://github.com/openclaw/janitor
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory=/home/%i/.openclaw/workspace/openclaw-janitor/skill
ExecStart=/usr/bin/node /home/%i/.openclaw/workspace/openclaw-janitor/skill/index.js monitor start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="NODE_ENV=production"
Environment="OPENCLAW_HOME=/home/%i/.openclaw"

# Resource limits
MemoryLimit=256M
CPUQuota=25%

[Install]
WantedBy=multi-user.target
```

### 2. OpenClaw Gateway with Janitor (Optional)

Enhanced OpenClaw gateway service that runs pre-start cleanup before OpenClaw starts, preventing context issues from the beginning.

**File:** `/etc/systemd/system/openclaw@.service`

```ini
[Unit]
Description=OpenClaw Gateway with Janitor Pre-Start Cleanup
Documentation=https://docs.openclaw.ai
After=network.target janitor-monitor.service

[Service]
Type=simple
User=%i
WorkingDirectory=/home/%i/.openclaw

# Pre-start cleanup script
ExecStartPre=/home/%i/.openclaw/workspace/openclaw-janitor/skill/scripts/pre-start-cleanup.sh

# Main OpenClaw gateway
ExecStart=/home/%i/.npm-global/bin/openclaw gateway

# Graceful stop
ExecStop=/bin/kill -SIGTERM $MAINPID
TimeoutStopSec=30

# Restart policy
Restart=always
RestartSec=10
StartLimitInterval=200
StartLimitBurst=5

# Output
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw

# Environment
Environment="NODE_ENV=production"
Environment="OPENCLAW_HOME=/home/%i/.openclaw"
Environment="PATH=/home/%i/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"

# Resource limits
MemoryLimit=2G
CPUQuota=75%

# Security (optional - adjust as needed)
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

## Installation

### Quick Install (via install.sh)
```bash
cd /path/to/janitor/skill
./install.sh
# Follow the prompts to install systemd service
```

### Manual Install

#### 1. Install Janitor Monitor Service
```bash
# Create service file
sudo nano /etc/systemd/system/janitor-monitor@.service
# Paste the content from above

# Reload systemd
sudo systemctl daemon-reload

# Enable service for your user
sudo systemctl enable janitor-monitor@$USER

# Start service
sudo systemctl start janitor-monitor@$USER

# Check status
sudo systemctl status janitor-monitor@$USER
```

#### 2. Install Enhanced OpenClaw Service (Optional)
This replaces your existing OpenClaw service with one that includes pre-start cleanup.

⚠️ **Warning**: This will replace your existing OpenClaw systemd service!

```bash
# Backup existing service (if any)
sudo cp /etc/systemd/system/openclaw.service /etc/systemd/system/openclaw.service.backup

# Create new service file
sudo nano /etc/systemd/system/openclaw@.service
# Paste the content from above

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable openclaw@$USER

# Start service
sudo systemctl start openclaw@$USER

# Check status
sudo systemctl status openclaw@$USER
```

## Service Management

### View Logs
```bash
# Janitor monitor logs
sudo journalctl -u janitor-monitor@$USER -f

# OpenClaw logs (with cleanup)
sudo journalctl -u openclaw@$USER -f
```

### Start/Stop Services
```bash
# Start
sudo systemctl start janitor-monitor@$USER
sudo systemctl start openclaw@$USER

# Stop
sudo systemctl stop janitor-monitor@$USER
sudo systemctl stop openclaw@$USER

# Restart
sudo systemctl restart janitor-monitor@$USER
sudo systemctl restart openclaw@$USER
```

### Disable Services
```bash
# Disable
sudo systemctl disable janitor-monitor@$USER
sudo systemctl disable openclaw@$USER

# Remove service files
sudo rm /etc/systemd/system/janitor-monitor@.service
sudo rm /etc/systemd/system/openclaw@.service

# Reload systemd
sudo systemctl daemon-reload
```

## Configuration

### Environment Variables
Edit the service files to customize:

```ini
[Service]
Environment="OPENCLAW_HOME=/path/to/.openclaw"
Environment="MAX_SESSIONS=20"
Environment="MAX_SESSION_AGE_DAYS=7"
```

### Resource Limits
Adjust CPU and memory limits:

```ini
[Service]
MemoryLimit=256M
CPUQuota=25%
```

## Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status janitor-monitor@$USER

# View logs
sudo journalctl -u janitor-monitor@$USER -n 50

# Check file permissions
ls -la ~/.openclaw/workspace/openclaw-janitor/skill/
```

### Pre-Start Script Fails
```bash
# Test script manually
~/.openclaw/workspace/openclaw-janitor/skill/scripts/pre-start-cleanup.sh

# Check script permissions
ls -la ~/.openclaw/workspace/openclaw-janitor/skill/scripts/pre-start-cleanup.sh

# Make executable if needed
chmod +x ~/.openclaw/workspace/openclaw-janitor/skill/scripts/pre-start-cleanup.sh
```

### Monitoring Not Working
```bash
# Check if service is running
sudo systemctl is-active janitor-monitor@$USER

# Restart service
sudo systemctl restart janitor-monitor@$USER

# Check Node.js path
which node

# Update ExecStart path in service file if needed
sudo nano /etc/systemd/system/janitor-monitor@.service
```

## Notes

- Service files use `%i` placeholder for username (systemd template syntax)
- Install with `@` syntax: `janitor-monitor@username.service`
- Logs are sent to systemd journal (use `journalctl` to view)
- Services auto-restart on failure
- Resource limits prevent runaway processes
- Adjust paths in service files if your Janitor installation is in a different location

## Alternative: Cron Job

If you don't want to use systemd, you can use cron instead:

```bash
# Edit crontab
crontab -e

# Add line to run every 5 minutes
*/5 * * * * cd ~/.openclaw/workspace/openclaw-janitor/skill && node index.js monitor check >> ~/.openclaw/logs/janitor-cron.log 2>&1
```

## Support

For issues with systemd services:
1. Check journalctl logs
2. Verify file paths in service files
3. Ensure scripts are executable
4. Check Node.js installation
5. Review OpenClaw installation

For more help, see the main README.md
