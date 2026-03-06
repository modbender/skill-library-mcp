# Glitch Dashboard v3

Cross-platform system management dashboard for OpenClaw agents.

## Features

- **Cross-Platform**: Windows, macOS, Linux
- **System Monitoring**: CPU, Memory, Load, Uptime
- **ZeroTier Integration**: Network status, IP management
- **Task Queue**: Task management with subtasks
- **Token Manager**: API token management
- **Mihomo/Clash**: Proxy node management
- **Real-time Logs**: System activity monitoring

## Quick Install

### Linux (Ubuntu/Debian/CentOS/Arch)

```bash
curl -fsSL https://raw.githubusercontent.com/chris6970barbarian-hue/glitch-skills/main/dashboard/scripts/install-linux.sh | sudo bash
```

### macOS

```bash
curl -fsSL https://raw.githubusercontent.com/chris6970barbarian-hue/glitch-skills/main/dashboard/scripts/install-macos.sh | bash
```

### Windows (PowerShell Admin)

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/chris6970barbarian-hue/glitch-skills/main/dashboard/scripts/install-windows.ps1" -OutFile "install.ps1"
powershell -ExecutionPolicy Bypass -File install.ps1
```

## Manual Install

1. Clone the repository:
```bash
git clone https://github.com/chris6970barbarian-hue/glitch-skills.git
cd glitch-skills/dashboard
```

2. Install dependencies (Node.js 18+ required)

3. Run:
```bash
node main.js
```

## Usage

After installation, access the dashboard at:
- Local: http://localhost:3853
- ZeroTier: http://172.26.21.18:3853

### CLI Commands

**Linux/macOS:**
```bash
glitch-dashboard start     # Start service
glitch-dashboard stop      # Stop service
glitch-dashboard restart   # Restart service
glitch-dashboard status    # Check status
glitch-dashboard logs      # View logs
```

**Windows:**
```cmd
glitch-dashboard start
glitch-dashboard stop
glitch-dashboard logs
```

## Navigation

| Icon | Page | Description |
|------|------|-------------|
| ⌂ | Overview | System status summary |
| ⚙ | System | CPU, Memory, Load monitoring |
| 🌐 | Network | ZeroTier configuration |
| ☰ | Tasks | Task queue management |
| 🔑 | Tokens | API token management |

## Configuration

Edit `~/.glitch-dashboard/config.json`:

```json
{
  "port": 3853,
  "theme": "dark",
  "services": {
    "zerotier": { "enabled": true },
    "tokenManager": { "enabled": true, "port": 3847 },
    "mihomo": { "enabled": false }
  }
}
```

## Platform Support

| Platform | Status | Tested On |
|----------|--------|-----------|
| Ubuntu 20.04+ | ✅ Full | 22.04 LTS |
| Debian 11+ | ✅ Full | 12 (bookworm) |
| CentOS 8+ | ✅ Full | Rocky Linux 9 |
| Arch Linux | ✅ Full | 2024.01 |
| macOS 12+ | ✅ Full | Sonoma 14 |
| Windows 10/11 | ✅ Full | Windows 11 23H2 |

## Troubleshooting

### Linux
```bash
# Check service status
sudo systemctl status glitch-dashboard

# View logs
sudo journalctl -u glitch-dashboard -f

# Manual restart
sudo systemctl restart glitch-dashboard
```

### macOS
```bash
# Check service
launchctl list | grep glitch

# View logs
tail -f ~/.glitch-dashboard/output.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.glitch.dashboard.plist
launchctl load ~/Library/LaunchAgents/com.glitch.dashboard.plist
```

### Windows
```powershell
# Check service
sc query GlitchDashboard

# View logs
Get-Content $env:USERPROFILE\.glitch-dashboard\dashboard.log -Tail 50

# Restart
Restart-Service GlitchDashboard
```

## Development

```bash
# Install dev dependencies
npm install

# Run in development mode
npm run dev

# Build binary (optional)
npm run build
```

## License

MIT

## Author

Glitch - OpenClaw Agent
