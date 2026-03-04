# Network Security

Tork Guardian's network governance layer protects OpenClaw agents from network-level threats: port hijacking, SSRF, reverse shells, and data exfiltration.

## What It Protects Against

| Threat | How Guardian Stops It |
|---|---|
| **Port hijacking** | Tracks which skill owns each port; blocks another skill from rebinding it |
| **Privileged port binding** | Blocks binding to ports below 1024 (HTTP, SSH, DNS, etc.) |
| **SSRF** | Blocks egress to private networks (127.x, 10.x, 192.168.x, 169.254.x) |
| **Reverse shells** | Detects `bash -i /dev/tcp`, `nc -e`, python/perl/ruby socket patterns in shell history |
| **Data exfiltration** | Domain allowlists and rate limiting restrict where and how fast data can leave |
| **Raw IP C2 channels** | DNS validation flags raw IP addresses used instead of hostnames |

## Policies

### Default Policy

Balanced security suitable for development and production.

```
Inbound ports:   3000-3999, 8000-8999
Outbound ports:  80, 443, 8080
Domain filter:   None (all domains allowed)
Rate limit:      60 connections/min
Privileged:      Blocked (< 1024)
Private nets:    Blocked
Reverse shells:  Detected
Port hijacking:  Detected
```

### Strict Policy

Enterprise lockdown for regulated environments.

```
Inbound ports:   3000-3010 only
Outbound ports:  443 only (TLS required)
Domain filter:   Explicit allowlist only
                 (api.openai.com, api.anthropic.com, tork.network,
                  registry.npmjs.org, github.com)
Rate limit:      20 connections/min
Privileged:      Blocked
Private nets:    Blocked
Reverse shells:  Detected
Port hijacking:  Detected
```

### Custom Policy

Override any setting from the default policy:

```typescript
const guardian = new TorkGuardian({
  apiKey: 'tork_...',
  networkPolicy: 'custom',
  allowedInboundPorts: [3000, 3001, 4000],
  allowedOutboundPorts: [443, 8443],
  allowedDomains: ['api.myservice.com', 'tork.network'],
  blockedDomains: ['evil.com'],
  maxConnectionsPerMinute: 30,
});
```

## Configuration Reference

| Option | Type | Default | Description |
|---|---|---|---|
| `networkPolicy` | `'default' \| 'strict' \| 'custom'` | `'default'` | Base policy preset |
| `allowedInboundPorts` | `number[]` | `3000-3999, 8000-8999` | Ports skills may bind to |
| `allowedOutboundPorts` | `number[]` | `80, 443, 8080` | Ports for outbound connections |
| `allowedDomains` | `string[]` | `[]` (no restriction) | If non-empty, only these domains are allowed |
| `blockedDomains` | `string[]` | `[]` | Domains always blocked |
| `maxConnectionsPerMinute` | `number` | `60` | Per-skill outbound rate limit |

## Reading Network Compliance Receipts

Every network decision is logged with a timestamp, skill ID, action type, and outcome:

```json
{
  "timestamp": "2026-02-06T12:00:00.000Z",
  "skillId": "code-assistant",
  "action": "egress",
  "allowed": true,
  "reason": "Egress to api.openai.com:443 allowed"
}
```

Access the log programmatically:

```typescript
const handler = guardian.getNetworkHandler();

// Get all activity
const log = handler.getActivityLog();

// Get a full network report (includes anomalies)
const report = handler.getMonitor().getNetworkReport();
```

The network report includes:
- **activePorts** — currently bound ports and their owners
- **recentConnections** — outbound connections in the last 5 minutes
- **recentShellCommands** — shell commands in the last 5 minutes
- **connectionRatePerMinute** — current egress rate
- **anomalies** — ports opened after startup, high connection rates, reverse shell patterns
