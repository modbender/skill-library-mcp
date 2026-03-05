---
name: clawdscan
version: 0.3.0
description: "Diagnose Clawdbot/OpenClaw health — session bloat, zombies, stale files, AND skill dependency validation. Zero dependencies, single Python file."
user-invocable: true
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: ["python3"]
---

# ClawdScan — Session Health Analyzer

> 🔍 Diagnose bloat, find zombies, reclaim disk space

ClawdScan is a zero-dependency Python CLI that analyzes Clawdbot/OpenClaw session JSONL files to identify bloated sessions, zombies, stale files, and provides actionable cleanup recommendations.

## Features

- **Session Health Analysis** - Detect bloated sessions, high message counts, disk usage patterns
- **Zombie Detection** - Find sessions created but never used
- **Stale Session Identification** - Identify sessions inactive for configurable periods  
- **Tool Usage Analytics** - Track which tools are being used and how frequently
- **Model Usage Patterns** - Monitor model switching and usage trends
- **Disk Space Management** - Breakdown of storage usage by agent and session
- **Automatic Cleanup** - Safe archive and deletion of problematic sessions
- **Trend Tracking** - Historical analysis of session health over time
- **Heartbeat Integration** - Automated monitoring and alerts

## Installation

### As Clawdbot Skill
```bash
clawdbot skill install clawdscan
```

### Standalone
```bash
chmod +x clawdscan.py
./clawdscan.py --help
```

## Quick Start

```bash
# Full health scan
clawdscan scan

# Top 10 largest sessions
clawdscan top -n 10

# Clean up zombie sessions
clawdscan clean --zombies --execute

# View recent trends
clawdscan history --days 7
```

## Commands

### `scan` - Full Health Scan
Comprehensive analysis of all Clawdbot sessions.

```bash
clawdscan scan [--json output.json]

# Examples
clawdscan scan                    # Console output
clawdscan scan --json report.json # Save as JSON
```

**Output includes:**
- Total sessions and disk usage
- Bloated sessions (>1MB or >300 messages)
- Zombie sessions (created but unused)
- Stale sessions (inactive >7 days)
- Top sessions by size and messages
- Cleanup recommendations

### `top` - Top Sessions
Show largest sessions by size or message count.

```bash
clawdscan top [-n COUNT] [--sort {size|messages}]

# Examples
clawdscan top                     # Top 15 by size
clawdscan top -n 20               # Top 20 by size
clawdscan top --sort messages     # Top 15 by message count
clawdscan top -n 10 --sort messages # Top 10 by messages
```

### `inspect` - Deep Session Analysis
Detailed analysis of a specific session.

```bash
clawdscan inspect <session-id>

# Example
clawdscan inspect chhotu-agent-20240109
```

**Shows:**
- Session metadata (created, last activity, size)
- Message count breakdown by type
- Tool usage within the session
- Model usage patterns
- Large messages or potential issues

### `tools` - Tool Usage Analytics
Aggregate statistics across all sessions.

```bash
clawdscan tools
```

**Analysis includes:**
- Most frequently used tools
- Tool usage by agent
- Average tool call frequency
- Tools that may be causing bloat

### `models` - Model Usage Patterns
Track model usage and switching patterns.

```bash
clawdscan models
```

**Shows:**
- Model usage distribution
- Model switching frequency
- Cost implications (if token data available)
- Model preference by agent

### `disk` - Storage Analysis
Breakdown of disk usage by agent and session type.

```bash
clawdscan disk
```

**Provides:**
- Total storage usage
- Usage by agent
- Largest directories
- Growth trends
- Cleanup potential

### `clean` - Session Cleanup
Safe cleanup of problematic sessions with preview mode.

```bash
clawdscan clean [--zombies] [--stale-days N] [--execute]

# Examples
clawdscan clean --zombies           # Preview zombie cleanup
clawdscan clean --zombies --execute # Execute zombie cleanup
clawdscan clean --stale-days 28     # Preview cleanup of 28+ day old sessions
clawdscan clean --stale-days 28 --execute # Execute stale cleanup
```

**Safety features:**
- Preview mode by default (no destructive actions)
- Backup creation before deletion
- Confirmation prompts for large cleanups
- Detailed logs of all actions

### `history` - Trend Analysis *(New)*
View session health trends over time.

```bash
clawdscan history [--days N]

# Examples
clawdscan history               # Last 30 days
clawdscan history --days 7     # Last week
clawdscan history --days 90    # Last 3 months
```

**Tracks:**
- Session count over time
- Storage growth trends
- Bloat accumulation patterns
- Cleanup effectiveness

## Configuration

### Environment Variables
- `CLAWDBOT_DIR` - Override default Clawdbot directory
- `NO_COLOR` - Disable colored output

### Thresholds (customizable in skill.json)
- **Bloat Size**: 1 MB (sessions larger than this)
- **Bloat Messages**: 300 messages
- **Stale Threshold**: 7 days without activity  
- **Zombie Threshold**: 48 hours created but unused

## Heartbeat Integration

ClawdScan can run automatically as part of Clawdbot's heartbeat system:

```markdown
### In HEARTBEAT.md
- Check session health every 6 hours
- Alert if >5 bloated sessions found
- Alert if total usage >100MB
- Auto-cleanup zombies (if enabled)
```

### Heartbeat Configuration
```json
{
  "heartbeat": {
    "enabled": true,
    "interval": "6h",
    "auto_cleanup": false,
    "alert_thresholds": {
      "bloated_sessions": 5,
      "total_size": "100MB"
    }
  }
}
```

## Output Examples

### Scan Output
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

### History Output
```
📈 Session Health Trends (Last 30 Days)

Week 1 (Jan 1-7):   12 sessions,  8.4 MB
Week 2 (Jan 8-14):  18 sessions, 15.7 MB  📈 +87% growth
Week 3 (Jan 15-21): 22 sessions, 19.3 MB  📈 +23% growth  
Week 4 (Jan 22-28): 28 sessions, 23.4 MB  📈 +21% growth

🔥 Bloat Trend: 0 → 1 → 2 → 3 sessions
💀 Zombie Trend: 1 → 1 → 2 → 2 sessions

💡 Growth Rate: +38% sessions/week, +44% storage/week
```

## Troubleshooting

### Common Issues

**"No sessions found"**
- Check `--dir` parameter points to correct Clawdbot directory
- Verify sessions exist in `agents/*/sessions/`

**"Permission denied"**
- Ensure read access to `~/.clawdbot` directory
- Check file ownership and permissions

**"JSON parsing error"**
- Some session files may be corrupted
- Use `--verbose` flag for detailed error info

### Debug Mode
```bash
clawdscan scan --verbose --debug
```

## Integration Examples

### Cron Job
```bash
# Daily health check at 2 AM
0 2 * * * /usr/local/bin/clawdscan scan --json /var/log/clawdscan.json
```

### Shell Script
```bash
#!/bin/bash
# Weekly cleanup script
clawdscan clean --zombies --execute
clawdscan clean --stale-days 14 --execute
clawdscan scan --json /var/log/weekly-scan.json
```

### Python Integration
```python
import subprocess
import json

# Run scan and get JSON output
result = subprocess.run(['clawdscan', 'scan', '--json', '/tmp/scan.json'])
with open('/tmp/scan.json') as f:
    data = json.load(f)
    
# Process results
if data['bloated_sessions'] > 5:
    notify_admin("ClawdBot cleanup needed")
```

## Development

### Adding New Commands
1. Add command handler to `clawdscan.py`
2. Update `skill.json` tools array
3. Add documentation to `SKILL.md`
4. Update `--help` text

### Contributing
- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure backward compatibility

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/jugaad-lab/clawdscan/issues)
- Documentation: This file and `clawdscan.py --help`