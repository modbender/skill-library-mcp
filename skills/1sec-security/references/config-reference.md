# 1-SEC Configuration Reference

Quick reference for the main configuration sections in `1sec.yaml`.

## Server

```yaml
server:
  host: "0.0.0.0"
  port: 1780
  api_keys: ["your-secret-key"]       # Secure the REST API
  read_only_keys: ["dashboard-key"]    # Read-only access for dashboards
  cors_origins: ["https://your-domain.com"]
  tls_cert: "/path/to/cert.pem"       # Optional HTTPS
  tls_key: "/path/to/key.pem"
```

## Event Bus

```yaml
bus:
  embedded: true          # NATS JetStream runs inside the binary
  data_dir: "./data/nats"
  port: 4222
```

## Modules

All 16 modules are enabled by default. Disable or tune individually:

```yaml
modules:
  network_guardian:
    enabled: true
    settings:
      max_requests_per_minute: 1000
  auth_fortress:
    enabled: true
    settings:
      max_failures_per_minute: 10
      lockout_duration_seconds: 300
  llm_firewall:
    enabled: true
  # ... all 16 modules follow the same pattern
```

## Enforcement

```yaml
enforcement:
  enabled: true
  dry_run: true                    # Start in dry-run, go live when ready
  preset: "safe"                   # lax, safe, balanced, strict, vps-agent
  global_allow_list: ["10.0.0.1"]  # IPs never blocked
  approval_gate:
    enabled: false                 # Human approval for destructive actions
    require_approval: ["kill_process", "quarantine_file"]
    auto_approve_above: "CRITICAL"
    ttl: 30m
```

## Escalation

```yaml
escalation:
  enabled: false       # Auto-escalate unacknowledged alerts
  timeouts:
    CRITICAL:
      timeout: 5m
      escalate_to: "CRITICAL"
      re_notify: true
      max_escalations: 3
    HIGH:
      timeout: 15m
      escalate_to: "CRITICAL"
      re_notify: true
      max_escalations: 2
```

## Archive (Cold Storage)

```yaml
archive:
  enabled: false
  dir: "./data/archive"
  rotate_bytes: 104857600    # 100MB
  rotate_interval: "1h"
  compress: true
```

## Cloud Dashboard

```yaml
cloud:
  enabled: false
  api_url: "https://api.1-sec.dev"
  api_key: "your-cloud-api-key"
  heartbeat_interval: 60
  command_poll_interval: 15
```

## AI Analysis

```yaml
modules:
  ai_analysis_engine:
    enabled: true
    settings:
      triage_model: "gemini-flash-lite-latest"
      deep_model: "gemini-flash-latest"
```

Keys are read from environment variables: `GEMINI_API_KEY`, `GEMINI_API_KEY_2`, etc.

## Notification Templates

Supported webhook templates: `generic`, `pagerduty`, `slack`, `teams`, `discord`, `telegram`.

```yaml
# In enforcement policy actions:
- action: webhook
  params:
    url: "https://hooks.slack.com/services/YOUR/WEBHOOK"
    template: "slack"
```

For Telegram, also provide `chat_id` in params.
