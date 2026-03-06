# Linux Setup Guide (systemd)

Full Linux support using **user-level systemd** — no `sudo` required.

## ⚡ One-Click Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install.sh | bash
```

The installer auto-detects Linux and runs the Linux-specific setup. You can also call it directly:

```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install-linux.sh | bash
```

Custom workspace:
```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install-linux.sh | bash -s -- --workspace ~/my-openclaw
```

## Supported Distros

| Distro | Package Manager | Status |
|--------|----------------|--------|
| Ubuntu 20.04+ | apt | ✅ |
| Debian 11+ | apt | ✅ |
| Fedora 36+ | dnf | ✅ |
| RHEL/CentOS/Rocky 8+ | dnf | ✅ |
| Arch Linux | pacman | ✅ |
| Pop!_OS / Linux Mint | apt | ✅ |

## Prerequisites

- **systemd** (standard on all major distros)
- **OpenClaw** installed and in PATH
- **tmux** (`apt install tmux` / `dnf install tmux` / `pacman -S tmux`)
- **Claude CLI** (`npm install -g @anthropic-ai/claude-code`)
- **curl** and **jq**

## 🔧 Manual Installation

### 1. Install dependencies

```bash
# Ubuntu/Debian
sudo apt install -y tmux curl jq

# Fedora/RHEL
sudo dnf install -y tmux curl jq

# Arch
sudo pacman -S --noconfirm tmux curl jq
```

### 2. Download scripts

```bash
mkdir -p ~/openclaw/scripts
cd ~/openclaw/scripts

for script in gateway-healthcheck.sh emergency-recovery.sh emergency-recovery-monitor.sh; do
  curl -sSLO "https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/scripts/$script"
  chmod 700 "$script"
done
```

### 3. Install systemd user units

```bash
mkdir -p ~/.config/systemd/user
cd ~/.config/systemd/user

for unit in openclaw-gateway.service openclaw-healthcheck.service openclaw-healthcheck.timer openclaw-emergency-recovery.service; do
  curl -sSLO "https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/systemd/$unit"
done

systemctl --user daemon-reload
```

### 4. Configure environment

```bash
mkdir -p ~/.openclaw
cat > ~/.openclaw/.env << 'EOF'
OPENCLAW_GATEWAY_URL="http://localhost:18789/"
HEALTH_CHECK_MAX_RETRIES=3
HEALTH_CHECK_RETRY_DELAY=30
HEALTH_CHECK_ESCALATION_WAIT=300
EMERGENCY_RECOVERY_TIMEOUT=1800
# DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
EOF
chmod 600 ~/.openclaw/.env
```

### 5. Enable services

```bash
# Enable gateway keepalive
systemctl --user enable openclaw-gateway.service

# Enable health check timer (every 5 min)
systemctl --user enable --now openclaw-healthcheck.timer

# Enable user lingering (services run without active login)
loginctl enable-linger "$USER"
```

### 6. Verify

```bash
# Check timer is active
systemctl --user list-timers | grep openclaw

# Check service status
systemctl --user status openclaw-healthcheck.timer

# View health check logs
journalctl --user -u openclaw-healthcheck -f
```

## Architecture (Linux)

```
┌─────────────────────────────────────────────┐
│ Level 0: systemd Restart=always             │
│   openclaw-gateway.service                  │
│   Process dies → systemd restarts in 10s    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Level 2: systemd timer (5min interval)      │
│   openclaw-healthcheck.timer                │
│   → openclaw-healthcheck.service (oneshot)  │
│   HTTP 200 check → retry → Level 3          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Level 3: Emergency Recovery (on-demand)     │
│   openclaw-emergency-recovery.service       │
│   Claude Code PTY → diagnose → fix          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Level 4: Discord Notification               │
│   Human alert via webhook                   │
└─────────────────────────────────────────────┘
```

## Useful Commands

```bash
# Start/stop gateway
systemctl --user start openclaw-gateway
systemctl --user stop openclaw-gateway

# Trigger emergency recovery manually
systemctl --user start openclaw-emergency-recovery

# View logs
journalctl --user -u openclaw-gateway -f
journalctl --user -u openclaw-healthcheck --since "1 hour ago"

# Check all openclaw units
systemctl --user list-units 'openclaw-*'

# Disable everything
systemctl --user disable --now openclaw-healthcheck.timer
systemctl --user disable openclaw-gateway.service
```

## Troubleshooting

### Services don't start after reboot

Enable user lingering so services persist without login:
```bash
sudo loginctl enable-linger "$USER"
```

### `Failed to connect to bus` error

Ensure `XDG_RUNTIME_DIR` is set:
```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
```

### Health check can't find `openclaw` command

The systemd units set PATH to include `~/.local/bin`. Ensure OpenClaw is installed there, or edit the unit files:
```bash
systemctl --user edit openclaw-healthcheck.service
# Add under [Service]:
# Environment=PATH=/your/custom/path:...
```

### Timer not firing

```bash
# Check timer status
systemctl --user status openclaw-healthcheck.timer

# Check for errors
journalctl --user -u openclaw-healthcheck.timer

# Restart timer
systemctl --user restart openclaw-healthcheck.timer
```

### Permission denied on scripts

```bash
chmod 700 ~/openclaw/scripts/*.sh
```
