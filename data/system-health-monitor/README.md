# System Health Monitor Skill

A comprehensive system health monitoring skill for OpenClaw that integrates with the 8-layer monitoring system.

## Overview

This skill provides a unified interface to monitor and manage system health, security, and performance. It integrates with the OpenClaw monitoring infrastructure to provide real-time status, alerts, and historical analysis.

## Features

### Core Monitoring
- **8-Layer Integration**: Full integration with all monitoring layers
- **Real-time Health Scoring**: 0-100 health score calculation
- **Automated Alerts**: Configurable alert thresholds and notifications
- **Historical Analysis**: Trend analysis and performance tracking

### Security Features
- **Security Dashboard**: Consolidated security status view
- **Intrusion Detection**: Integration with fail2ban and UFW
- **Network Monitoring**: Outbound traffic and internal security monitoring
- **Compliance Reporting**: Security configuration verification

### Reporting Capabilities
- **Daily Summaries**: Automated daily health reports
- **Weekly Analysis**: Performance trend analysis
- **Custom Reports**: Ad-hoc report generation

## Installation

### Manual Installation
```bash
# Clone or copy skill to OpenClaw skills directory
cp -r system-health-monitor ~/.openclaw/workspace/skills/

# Make scripts executable
chmod +x ~/.openclaw/workspace/skills/system-health-monitor/scripts/*.sh
```

### Configuration
Edit the configuration file:
```bash
nano ~/.openclaw/workspace/skills/system-health-monitor/config/health-monitor.json
```

Key configuration options:
- `alert_threshold`: Health score threshold for alerts (default: 80)
- `notify_on_critical`: Enable critical alert notifications
- `telegram_channel_id`: Telegram channel for alerts (optional)
- `monitored_services`: List of services to monitor

## Usage

### Basic Commands
```bash
# Get current health status
/health status

# Generate detailed report
/health report

# Check specific monitoring layer
/health layer 2      # Heartbeat monitoring
/health layer 5      # Package integrity monitoring

# Security status
/health security

# View logs
/health logs --alerts
/health logs --monitor
/health logs --all
```

## Monitoring Layers (8-Layer System)

The skill integrates with these 8 monitoring layers:

| Layer | Service | Description | Integration Status |
|-------|---------|-------------|-------------------|
| 1 | SSH Login Monitor | Real-time SSH login tracking | ✅ Full |
| 2 | Heartbeat Monitor | Advanced health checks | ✅ Full |
| 3 | Outbound Traffic Monitor | Network security monitoring | ✅ Full |
| 4 | UFW Firewall | Network layer protection | ✅ Basic |
| 5 | Package Integrity Monitor | Software package security | ✅ Full |
| 6 | Report Monitor | Automated reporting | ✅ Full |
| 7 | Cleanup Monitor | System maintenance | ✅ Full |
| 8 | Internal Security Monitor | Network threat detection | ✅ Full |

## Health Scoring Algorithm

The health score (0-100) is calculated based on:

```
Health Score = (healthy_layers / 8) × 100
```

**Score Interpretation:**
- 90-100: 🟢 Excellent (All systems operational)
- 70-89: 🟡 Good (Minor issues, fully operational)
- 50-69: 🟠 Fair (Some issues, monitoring required)
- 0-49: 🔴 Poor (Critical issues, intervention needed)

## Testing

Run the test suite to verify installation:
```bash
cd ~/.openclaw/workspace/skills/system-health-monitor
./tests/test.sh
```

## Development

### Project Structure
```
system-health-monitor/
├── SKILL.md              # Skill documentation
├── README.md             # This file
├── config/
│   └── health-monitor.json  # Configuration
├── scripts/
│   ├── health-check.sh   # Main health check script
│   └── alert-notify.sh   # Alert notification (future)
├── tests/
│   └── test.sh          # Test suite
└── references/
    └── api-integration.md      # API documentation
```

## Publishing to ClawHub

### Prerequisites
```bash
npm install -g clawhub
clawhub login
```

### Publishing
```bash
cd ~/.openclaw/workspace/skills/system-health-monitor
clawhub publish --version 1.1.1 --description "System Health Monitoring Skill"
```

## Troubleshooting

### Common Issues

#### Skill not recognized by OpenClaw
```bash
# Check skill location
ls -la ~/.openclaw/workspace/skills/system-health-monitor/SKILL.md

# Restart OpenClaw Gateway
openclaw gateway restart
```

#### Script permissions issues
```bash
chmod +x ~/.openclaw/workspace/skills/system-health-monitor/scripts/*.sh
```

#### Configuration errors
```bash
# Validate JSON configuration
jq empty ~/.openclaw/workspace/skills/system-health-monitor/config/health-monitor.json
```

## Security Considerations

- **Permissions**: Requires read access to system logs and services
- **Data Access**: Only reads monitoring data, no modifications
- **Network**: Optional external notifications via Telegram (user-configured)
- **Authentication**: Relies on system authentication mechanisms
- **Script Integrity**: Scripts include SHA256 hashes for verification

## License

This skill is released under the MIT License. See LICENSE file for details.

## Support

- **Issues**: GitHub issue tracker
- **Documentation**: OpenClaw official docs
- **Author**: ZLMbot 🦞

## Version History

- **1.1.1** (2026-03-01): Fixed security scan issues - removed hardcoded paths, sudo usage, fixed 8-layer consistency
- **1.1.0** (2026-03-01): Simplified to 8-layer system (removed Config Monitor and Learning System)
- **1.0.0** (2026-02-28): Initial release

---

**Skill Status**: 🟢 Active  
**Last Updated**: 2026-03-01  
**OpenClaw Compatibility**: 2026.2.26+  
**OS Requirement**: Linux with systemd  
**Dependencies**: systemd, jq
