# Usage Examples

```bash
# Enable local baseline config
token-optimize --enable

# Analyze last 7 days
token-optimize --analyze --period 7d

# Export analysis JSON
token-optimize --analyze --period 30d --format json --output /tmp/token-opt-report.json

# Generate compressed session context
token-optimize --compress --session agent:main:main --threshold 0.8

# Health check and cleanup planning
token-optimize --health-check --active-minutes 120
token-optimize --cleanup

# Apply cleanup (gateway restart when stuck sessions detected)
token-optimize --cleanup --apply
```
