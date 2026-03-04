# Disk Usage Watcher

## Description
Monitors disk space and inode usage on specified paths, sending alerts when thresholds are exceeded. Essential for preventing disk-full incidents.

## Usage
The agent can call this skill directly or it runs automatically via cron every 15 minutes.

### Example Prompts:
- "Check disk space on root partition"
- "Monitor all mount points and alert at 85%"
- "Show me disk usage statistics"

## Inputs
- `threshold_percent`: number — Alert when usage exceeds this percentage (default: 85)
- `inode_threshold`: number — Alert when inode usage exceeds this percentage (default: 85)
- `paths`: array — Specific paths to monitor (default: all mounted partitions)
- `alert_on_failure`: boolean — Send alert if check fails (default: true)

## Outputs
- `status`: string — "success" or "failure"
- `details`: object — Contains disk_usage array with mount points, usage percentages, and any triggered alerts

## Dependencies
- `openclaw/exec` - For running df commands
- `openclaw/notify` - For sending alerts

## Testing
```bash
openclaw call disk-usage-watcher --params '{"paths": ["/"]}'
```
