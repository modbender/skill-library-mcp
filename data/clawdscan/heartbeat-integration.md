# Clawdscan Heartbeat Integration

This file contains code snippets for integrating clawdscan into Clawdbot's heartbeat monitoring system.

## HEARTBEAT.md Integration

Add this to your workspace `HEARTBEAT.md` file:

```markdown
### Session Health Monitoring (Every 6 Hours)
- Check clawdbot session health
- Alert if bloated sessions exceed threshold
- Alert if total storage exceeds limits
- Track growth trends

**Last scan:** {{clawdscan_last_scan}}
**Action needed:** {{clawdscan_action_needed}}
```

## Heartbeat Check Script

Create this as a periodic check in your heartbeat routine:

```python
def heartbeat_clawdscan_check():
    """Periodic clawdscan health check for heartbeat system."""
    import subprocess
    import json
    import tempfile
    from datetime import datetime
    
    try:
        # Run scan and capture JSON output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
            result = subprocess.run(
                ['python3', '/path/to/clawdscan.py', 'scan', '--json', tmp.name],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                tmp.seek(0)
                data = json.load(tmp)
                
                # Check thresholds
                bloated_sessions = len(data.get('bloated_sessions', []))
                total_size_mb = data.get('total_size_bytes', 0) / (1024 * 1024)
                zombie_sessions = len(data.get('zombie_sessions', []))
                
                alerts = []
                action_needed = False
                
                # Bloated sessions alert
                if bloated_sessions > 5:
                    alerts.append(f"🔥 {bloated_sessions} bloated sessions found")
                    action_needed = True
                
                # Storage size alert  
                if total_size_mb > 100:
                    alerts.append(f"💾 Sessions using {total_size_mb:.1f}MB storage")
                    action_needed = True
                
                # Zombie sessions alert
                if zombie_sessions > 3:
                    alerts.append(f"💀 {zombie_sessions} zombie sessions detected")
                    action_needed = True
                
                # Update heartbeat state
                heartbeat_state = {
                    'clawdscan_last_scan': datetime.now().isoformat(),
                    'clawdscan_action_needed': 'Yes' if action_needed else 'No',
                    'clawdscan_alerts': alerts
                }
                
                return heartbeat_state, alerts
            else:
                return None, [f"⚠️ Clawdscan failed: {result.stderr}"]
                
    except Exception as e:
        return None, [f"⚠️ Clawdscan error: {str(e)}"]
```

## Auto-cleanup Script

For automatic cleanup of zombie sessions:

```python
def heartbeat_clawdscan_cleanup():
    """Automatic cleanup of zombie sessions if enabled."""
    import subprocess
    import os
    
    # Only run if auto-cleanup is enabled
    auto_cleanup = os.environ.get('CLAWDSCAN_AUTO_CLEANUP', 'false').lower() == 'true'
    
    if not auto_cleanup:
        return "Auto-cleanup disabled"
    
    try:
        # Clean zombies (dry run first)
        result = subprocess.run(
            ['python3', '/path/to/clawdscan.py', 'clean', '--zombies'],
            capture_output=True, text=True, timeout=30
        )
        
        if "would remove" in result.stdout:
            # Actually execute cleanup
            result = subprocess.run(
                ['python3', '/path/to/clawdscan.py', 'clean', '--zombies', '--execute'],
                capture_output=True, text=True, timeout=30
            )
            return f"Cleaned up zombie sessions: {result.stdout.strip()}"
        else:
            return "No zombie sessions to clean"
            
    except Exception as e:
        return f"Cleanup failed: {str(e)}"
```

## Integration in Main Heartbeat Function

```python
def process_heartbeat():
    """Main heartbeat processing function."""
    
    # ... other heartbeat checks ...
    
    # Clawdscan health check (every 6 hours)
    last_clawdscan = get_last_check_time('clawdscan')
    if hours_since(last_clawdscan) >= 6:
        heartbeat_state, alerts = heartbeat_clawdscan_check()
        
        if alerts:
            for alert in alerts:
                notify_user(alert)
        
        # Auto-cleanup if configured
        if heartbeat_state and heartbeat_state.get('clawdscan_action_needed') == 'Yes':
            cleanup_result = heartbeat_clawdscan_cleanup()
            if cleanup_result and "Cleaned up" in cleanup_result:
                notify_user(f"🧹 {cleanup_result}")
        
        update_last_check_time('clawdscan')
    
    # ... rest of heartbeat processing ...
```

## Environment Configuration

Set these environment variables to control behavior:

```bash
# Enable automatic cleanup of zombie sessions
export CLAWDSCAN_AUTO_CLEANUP=true

# Clawdscan path (if not in PATH)
export CLAWDSCAN_PATH="/path/to/clawdscan.py"

# Alert thresholds
export CLAWDSCAN_BLOAT_THRESHOLD=5
export CLAWDSCAN_SIZE_THRESHOLD_MB=100
export CLAWDSCAN_ZOMBIE_THRESHOLD=3

# Check interval (hours)
export CLAWDSCAN_CHECK_INTERVAL=6
```

## Notification Templates

```python
CLAWDSCAN_TEMPLATES = {
    'bloated_alert': "🔥 ClawdBot Health Alert: {count} bloated sessions detected. Consider running `clawdscan clean --stale-days 7`",
    'storage_alert': "💾 ClawdBot Storage Alert: {size}MB used. Run `clawdscan disk` for breakdown.",
    'zombie_alert': "💀 ClawdBot Zombie Alert: {count} unused sessions found. Run `clawdscan clean --zombies --execute`",
    'cleanup_success': "🧹 Auto-cleaned {count} zombie sessions, freed {size}",
    'weekly_summary': "📊 Weekly ClawdBot Health: {total_sessions} sessions, {total_size}, {issues_found} issues"
}
```

## Cron Integration (Alternative)

If not using Clawdbot's heartbeat system, you can use cron:

```bash
# Check every 6 hours
0 */6 * * * cd /path/to/clawdscan && python3 clawdscan.py scan --json /tmp/clawdscan.json && python3 /path/to/process_scan_results.py

# Weekly cleanup on Sunday at 2 AM  
0 2 * * 0 cd /path/to/clawdscan && python3 clawdscan.py clean --stale-days 14 --execute

# Daily zombie cleanup at 3 AM
0 3 * * * cd /path/to/clawdscan && python3 clawdscan.py clean --zombies --execute
```

## Sample process_scan_results.py

```python
#!/usr/bin/env python3
"""Process clawdscan results and send notifications."""

import json
import subprocess
import sys

def send_notification(message):
    """Send notification via your preferred method."""
    # Example: Discord webhook
    # subprocess.run(['curl', '-X', 'POST', webhook_url, '-d', json.dumps({'content': message})])
    print(f"ALERT: {message}")

def main():
    try:
        with open('/tmp/clawdscan.json', 'r') as f:
            data = json.load(f)
        
        bloated = len(data.get('bloated_sessions', []))
        total_mb = data.get('total_size_bytes', 0) / (1024 * 1024)
        zombies = len(data.get('zombie_sessions', []))
        
        if bloated > 5:
            send_notification(f"🔥 {bloated} bloated ClawdBot sessions need attention")
        
        if total_mb > 100:
            send_notification(f"💾 ClawdBot using {total_mb:.1f}MB - cleanup recommended")
            
        if zombies > 3:
            send_notification(f"💀 {zombies} zombie ClawdBot sessions found")
            
    except Exception as e:
        send_notification(f"❌ ClawdScan check failed: {e}")

if __name__ == "__main__":
    main()
```

## Usage Examples

### Manual Integration
```bash
# Add to your daily workflow
clawdscan scan && clawdscan history --days 7

# Weekly maintenance
clawdscan clean --zombies --execute && clawdscan clean --stale-days 14 --execute

# Growth tracking
clawdscan history --days 30 > weekly-growth-report.txt
```

### Programmatic Integration
```python
# In your agent code
import subprocess
result = subprocess.run(['clawdscan', 'scan', '--json', '/tmp/scan.json'])
# Process results...
```

This integration ensures your Clawdbot sessions stay healthy and performant with minimal manual intervention.