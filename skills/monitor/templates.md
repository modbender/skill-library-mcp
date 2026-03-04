# Monitor Templates

Examples of monitor definitions. User defines what to check, these are common patterns.

## HTTP Endpoint

```json
{
  "name": "api-health",
  "description": "Check API returns 200",
  "checks": [
    {"type": "http", "target": "https://api.example.com/health", "expect": 200}
  ],
  "interval": "5m",
  "requires": []
}
```

Agent runs: `curl -s -o /dev/null -w "%{http_code}" --max-time 10 URL`

## SSL Certificate

```json
{
  "name": "api-ssl",
  "description": "Check SSL cert not expiring soon",
  "checks": [
    {"type": "ssl", "target": "api.example.com", "warn_days": 14}
  ],
  "interval": "24h",
  "requires": []
}
```

Agent runs: `openssl s_client` + parse expiry

## Process Running

```json
{
  "name": "postgres-up",
  "description": "Check postgres is running",
  "checks": [
    {"type": "process", "target": "postgres"}
  ],
  "interval": "1m",
  "requires": []
}
```

Agent runs: `pgrep -x postgres`

## Disk Space

```json
{
  "name": "disk-root",
  "description": "Check disk not full",
  "checks": [
    {"type": "disk", "target": "/", "warn_percent": 80}
  ],
  "interval": "1h",
  "requires": []
}
```

Agent runs: `df -h /`

## Custom Check (User-Defined)

```json
{
  "name": "custom-check",
  "description": "User's custom check",
  "checks": [
    {"type": "custom", "command": "user-provided-command", "expect": "success"}
  ],
  "interval": "15m",
  "requires": ["user-granted-access"]
}
```

User provides the command, agent runs it.

## Remote Server (Requires SSH)

```json
{
  "name": "server-disk",
  "description": "Check remote server disk",
  "checks": [
    {"type": "disk", "target": "/", "host": "server1"}
  ],
  "interval": "1h",
  "requires": ["ssh:server1"]
}
```

User must explicitly grant SSH access to server1.
