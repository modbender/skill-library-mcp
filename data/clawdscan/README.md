<p align="center">
  <img src="assets/logo.png" alt="clawdscan logo" width="200" />
</p>

<p align="center">[![ClawHub](https://img.shields.io/badge/ClawHub-clawdscan-teal)](https://clawhub.ai/skills/clawdscan)</p>
<p align="center">**Install via ClawHub:** `clawhub install clawdscan`</p>

# ClawdScan - Clawdbot Session Health Analyzer 🔍

A comprehensive diagnostic tool for Clawdbot sessions. Analyze JSONL session files to identify performance issues, bloated sessions, zombie processes, and get actionable cleanup recommendations.

## Features

- 🔍 **Session Health Analysis** - Detect bloated sessions, high message counts, disk usage patterns
- 💀 **Zombie Detection** - Find sessions created but never used  
- 🗓️ **Stale Session Identification** - Identify sessions inactive for configurable periods
- 📊 **Tool Usage Analytics** - Track which tools are being used and how frequently
- 🤖 **Model Usage Patterns** - Monitor model switching and usage trends
- 💾 **Disk Space Management** - Breakdown of storage usage by agent and session
- 🧹 **Automatic Cleanup** - Safe archive and deletion of problematic sessions
- 📈 **Trend Tracking** - Historical analysis of session health over time
- 💓 **Heartbeat Integration** - Automated monitoring and alerts

## Quick Start

```bash
# Install as Clawdbot skill
clawdbot skill install clawdscan

# Or run standalone
chmod +x clawdscan.py
./clawdscan.py scan
```

## Example Output

```
🔍 ClawdScan v0.1.0 — Clawdbot Session Health Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Overview
  Total Sessions: 42
  Total Size: 23.4 MB
  Agents: main(38), dj(4)

⚠️  Issues Found
  🔥 Bloated: 3 sessions (>1MB or >300 msgs)
  💀 Zombies: 2 sessions (created but unused)  
  🗓️  Stale: 7 sessions (inactive >7 days)

🔝 Top Sessions by Size
  1. main-20240108-143022  4.2 MB  (1,247 msgs)
  2. main-20240107-091534  2.8 MB  (892 msgs)
  3. dj-20240105-220145    1.9 MB  (734 msgs)

💡 Recommendations
  • Archive 2 zombie sessions → save 145 KB
  • Clean 7 stale sessions → save 3.2 MB
  • Consider shorter session lifetimes
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `scan` | Full health scan | `clawdscan scan` |
| `top` | Top sessions by size/messages | `clawdscan top -n 10` |
| `inspect` | Deep-inspect specific session | `clawdscan inspect session-id` |
| `tools` | Tool usage analytics | `clawdscan tools` |
| `models` | Model usage patterns | `clawdscan models` |
| `disk` | Disk usage breakdown | `clawdscan disk` |
| `clean` | Safe session cleanup | `clawdscan clean --zombies` |
| `history` | Health trends over time | `clawdscan history --days 7` |

## Installation

### As Clawdbot Skill

```bash
# Install from skill repository
clawdbot skill install clawdscan

# Or install from local directory
cd /path/to/clawdscan
clawdbot skill link .
```

### Standalone Installation

```bash
# Make executable
chmod +x clawdscan.py

# Add to PATH (optional)
ln -s $(pwd)/clawdscan.py /usr/local/bin/clawdscan

# Test installation
clawdscan --version
```

## Package Structure

```
clawdscan/
├── clawdscan.py              # Main executable
├── skill.json               # Clawdbot skill metadata  
├── SKILL.md                 # Complete documentation
├── LICENSE                  # MIT license
├── heartbeat-integration.md # Heartbeat integration guide
├── TASK.md                 # Development task spec
└── README.md               # This file
```

## Development

### Testing

```bash
# Test against live sessions
clawdscan scan

# Test all commands
clawdscan top -n 5
clawdscan history --days 7
clawdscan disk
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Integration Examples

### Heartbeat Monitoring
```bash
# Add to HEARTBEAT.md
clawdscan scan --json /tmp/health.json
if [[ $(jq '.bloated_sessions | length' /tmp/health.json) -gt 5 ]]; then
  echo "🔥 Bloated sessions detected - cleanup needed"
fi
```

### Cron Jobs
```bash
# Daily health check
0 2 * * * clawdscan scan --json /var/log/clawdscan-$(date +\%Y\%m\%d).json

# Weekly cleanup
0 3 * * 0 clawdscan clean --stale-days 14 --execute
```

### Python Integration
```python
import subprocess
import json

result = subprocess.run(['clawdscan', 'scan', '--json', '/tmp/scan.json'])
with open('/tmp/scan.json') as f:
    data = json.load(f)
    
if len(data['bloated_sessions']) > 5:
    notify_admin("Clawdbot cleanup needed")
```

## Configuration

### Environment Variables
- `CLAWDBOT_DIR` - Override default Clawdbot directory
- `NO_COLOR` - Disable colored output
- `CLAWDSCAN_AUTO_CLEANUP` - Enable automatic cleanup

### Thresholds (customizable)
- Bloat Size: 1 MB
- Bloat Messages: 300
- Stale Threshold: 7 days  
- Zombie Threshold: 48 hours

## Addresses

This tool addresses [GitHub Issue #1808](https://github.com/clawdbot/clawdbot/issues/1808) - Clawdbot session bloat and disk usage management.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📖 Documentation: [SKILL.md](SKILL.md)
- 🐛 Issues: [GitHub Issues](https://github.com/yajatns/clawdscan/issues)  
- 💬 Community: Clawdbot Discord server

---

*Version 0.1.0 - Built with ❤️ for the Clawdbot community*