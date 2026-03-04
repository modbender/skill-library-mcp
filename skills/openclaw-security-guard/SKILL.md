---
name: openclaw-security-guard
description: Security audit CLI + live dashboard for OpenClaw. Scans for secrets, config issues, prompt injections, vulnerable dependencies, and unverified MCP servers. Zero telemetry.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - node
    install:
      - kind: node
        package: openclaw-security-guard
        bins: [openclaw-guard, openclaw-security-guard]
    emoji: "\U0001F6E1"
    homepage: https://github.com/2pidata/openclaw-security-guard
    os:
      - macos
      - linux
      - windows
---

# OpenClaw Security Guard

The missing security layer for your OpenClaw installation.

## What it does

Run `openclaw-guard audit` to scan your OpenClaw setup across 5 categories:

- **Secrets Scanner** -- Detects API keys, tokens, passwords across 15+ formats + entropy analysis
- **Config Auditor** -- Checks sandbox mode, DM policy, gateway binding, rate limiting
- **Prompt Injection Detector** -- 50+ patterns: instruction overrides, role hijacking, jailbreaks
- **Dependency Scanner** -- npm CVE scanning
- **MCP Server Auditor** -- Allowlist-based verification of installed MCP servers

## Quick start

```bash
npm install -g openclaw-security-guard

# Full audit
openclaw-guard audit

# Fix issues automatically (with backup)
openclaw-guard fix --auto

# Launch live dashboard
openclaw-guard dashboard
```

## Features

- **Security Score** (0-100) -- one number for your security posture
- **Auto-hardening** -- interactive, automatic, or dry-run modes
- **Live dashboard** -- real-time monitoring at localhost:18790
- **Pre-commit hooks** -- catch secrets before they're committed
- **Multi-language** -- English, French, Arabic
- **Zero telemetry** -- no tracking, no network requests, 100% local

## Links

- **Repository:** https://github.com/2pidata/openclaw-security-guard
- **Author:** [Miloud Belarebia](https://github.com/miloudbelarebia) / [2PiData](https://2pidata.com)
- **License:** MIT
