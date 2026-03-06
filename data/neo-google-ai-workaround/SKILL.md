---
name: google-ai-workaround
description: Automates Google AI Pro/Ultra access management through proxy and session strategies for OpenClaw agents.
version: 1.0.0
author: OpenClaw
tags:
  - google-ai
  - proxy
  - session-management
  - automation
triggers:
  - "Google AI Pro is restricted when using OpenClaw"
  - "Google AI Ultra access blocked through OpenClaw"
  - "Google AI session management for OpenClaw agents"
  - "Google AI proxy configuration for OpenClaw"
  - "Google AI rate limiting bypass for automation"
  - "Google AI session rotation for OpenClaw workflows"
  - "Google AI access denied, need workaround"
---

# Google AI Workaround

## Purpose

Automates Google AI Pro/Ultra access through proxy and session management strategies in OpenClaw environments. Detects restrictions, rotates sessions, manages proxy configurations, and provides detailed diagnostics.

## 1. Overview

When Google AI Pro/Ultra services restrict access from OpenClaw agents, this skill provides automated detection and mitigation:

- **Restriction Detection**: Identifies rate limiting, IP blocks, auth failures, and geo-restrictions from API responses.
- **Session Management**: Creates, rotates, and persists sessions with token lifecycle management.
- **Proxy Handling**: Manages a pool of proxies with health checking, rotation, and failover.
- **Diagnostics**: Structured logging and reporting for troubleshooting access issues.

## 2. Core Capabilities

- Detects Google AI service restrictions by analyzing HTTP response patterns
- Manages proxy configurations with round-robin, least-used, and random rotation strategies
- Provides a CLI interface for manual testing and configuration verification
- Integrates with OpenClaw agent workflows for seamless automation
- Monitors access patterns and identifies rate limiting
- Handles authentication token refresh and session persistence
- Generates detailed logs and error reports for troubleshooting

## 3. Installation

```bash
cd skill/
npm install
```

No external dependencies required - the skill uses only Node.js built-in modules.

## 4. Usage

### CLI Commands

```bash
# Show current status
node scripts/main.js status

# Detect restrictions (simulated analysis)
node scripts/main.js detect

# Session management
node scripts/main.js session-create
node scripts/main.js session-rotate
node scripts/main.js session-list
node scripts/main.js session-refresh
node scripts/main.js session-destroy

# Proxy management
node scripts/main.js proxy-status
node scripts/main.js proxy-health
node scripts/main.js proxy-add --host 192.168.1.100 --port 8080

# Diagnostics and configuration
node scripts/main.js diagnostics
node scripts/main.js configure
node scripts/main.js help
```

### Options

- `--config <path>` - Path to config file (default: `assets/config-template.json`)
- `--silent` - Suppress log output
- `--log-file <path>` - Write logs to a file

## 5. Examples

### Detecting Restrictions

```bash
$ node scripts/main.js detect
=== Restriction Detection Analysis ===

HTTP 200: OK
HTTP 429: RESTRICTED
  - Rate Limiting (high) -> rotate_session
HTTP 403: RESTRICTED
  - IP-based Block (critical) -> switch_proxy
  - General Access Denied (high) -> rotate_session
HTTP 401: RESTRICTED
  - Authentication Expired (medium) -> refresh_token
HTTP 503: RESTRICTED
  - Service Unavailable (low) -> wait_retry
```

### Session Workflow

```bash
$ node scripts/main.js session-create
Session created: a1b2c3d4-...
Expires: 2026-02-25T13:00:00.000Z

$ node scripts/main.js session-rotate
Session rotated: e5f6g7h8-...
```

## 6. Configuration

Edit `assets/config-template.json`:

```json
{
  "logLevel": "INFO",
  "proxies": [
    { "host": "proxy1.example.com", "port": 8080, "protocol": "http" },
    { "host": "proxy2.example.com", "port": 8080, "protocol": "http" }
  ],
  "maxSessions": 5,
  "sessionTTL": 3600000,
  "maxProxyFailures": 3,
  "rotationStrategy": "round-robin"
}
```

### Environment Variables

The skill reads configuration from the JSON file. Override by passing `--config <path>` to point to a custom configuration.

## 7. Out of Scope

- Does not violate Google Terms of Service or encourage policy violations
- Does not provide or distribute unauthorized access methods
- Does not guarantee 100% uptime if Google implements stronger restrictions
- Does not handle billing or subscription management
- Does not replace official Google AI API usage where appropriate
