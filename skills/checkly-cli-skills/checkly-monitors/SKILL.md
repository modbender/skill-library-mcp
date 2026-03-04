---
name: checkly-monitors
description: Create simple health monitoring checks including heartbeat, TCP, DNS, and URL monitors. Use for basic uptime monitoring, infrastructure health checks, DNS validation, and service availability without code execution. Triggers on heartbeat, TCP monitor, DNS monitor, URL monitor, health check, uptime monitoring.
---

# checkly monitors

Simple health checks without code execution.

## Monitor types

| Monitor | Use Case | Checks |
|---------|----------|--------|
| **Heartbeat** | Periodic ping expected | Inbound webhook calls |
| **TCP** | Port connectivity | Socket connection |
| **DNS** | Domain resolution | DNS records |
| **URL** | HTTP availability | Status code only |

## Heartbeat Monitors

Expect periodic pings from your application.

```typescript
import { HeartbeatMonitor } from 'checkly/constructs'

new HeartbeatMonitor('app-heartbeat', {
  name: 'App Heartbeat',
  period: 300, // seconds
  periodUnit: 'seconds',
  grace: 60,
})
```

**Usage:**
```bash
# Your app pings this URL
curl -X POST https://ping.checklyhq.com/heartbeats/{YOUR_ID}
```

## TCP Monitors

Check TCP port connectivity.

```typescript
import { TcpMonitor } from 'checkly/constructs'

new TcpMonitor('database-tcp', {
  name: 'Database TCP Check',
  host: 'db.example.com',
  port: 5432,
  frequency: 5,
})
```

## DNS Monitors

Validate DNS records.

```typescript
import { DnsMonitor } from 'checkly/constructs'

new DnsMonitor('dns-check', {
  name: 'DNS A Record',
  host: 'example.com',
  recordType: 'A',
  expectedValues: ['93.184.216.34'],
})
```

## URL Monitors

Simple HTTP availability checks.

```typescript
import { UrlMonitor } from 'checkly/constructs'

new UrlMonitor('url-check', {
  name: 'Homepage URL Check',
  url: 'https://example.com',
  method: 'GET',
})
```

## Related Skills

- See `checkly-checks` for more advanced monitoring
- See `checkly-groups` for organizing monitors
