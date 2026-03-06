---
name: openclaw-egress
description: Network DLP for agent workspaces. Scans skills and files for
  outbound URLs, data exfiltration endpoints, and network function calls.
---


# OpenClaw Egress

Network DLP for agent workspaces. Scans skills and files for outbound URLs, data exfiltration endpoints, and network function calls.

## The Problem

Skills can phone home. A compromised skill can POST your workspace contents, API keys, or conversation history to an external server. Nothing monitors what URLs your skills connect to or what data they could send.


## Commands

### Full Scan

Scan workspace for all outbound network risks.

```bash
python3 {baseDir}/scripts/egress.py scan --workspace /path/to/workspace
```

### Skills-Only Scan

```bash
python3 {baseDir}/scripts/egress.py scan --skills-only --workspace /path/to/workspace
```

### Domain Map

List all external domains referenced in workspace.

```bash
python3 {baseDir}/scripts/egress.py domains --workspace /path/to/workspace
```

### Quick Status

```bash
python3 {baseDir}/scripts/egress.py status --workspace /path/to/workspace
```

## What It Detects

| Risk | Pattern |
|------|---------|
| **CRITICAL** | Base64/hex payloads in URLs, pastebin/sharing services, request catchers, dynamic DNS |
| **HIGH** | Network function calls (requests, urllib, curl, wget, fetch), webhook/callback URLs |
| **WARNING** | Suspicious TLDs (.xyz, .tk, .ml), URL shorteners, IP address endpoints |
| **INFO** | Any external URL not on the safe domain list |

## Exit Codes

- `0` — Clean
- `1` — Network calls detected (review needed)
- `2` — Exfiltration risk detected (action needed)

## No External Dependencies

Python standard library only. No pip install. No network calls. Everything runs locally.

## Cross-Platform

Works with OpenClaw, Claude Code, Cursor, and any tool using the Agent Skills specification.
