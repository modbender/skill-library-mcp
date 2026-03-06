---
name: ClawSentinel
description: Pure local 2026 ClawHub/OpenClaw skill scanner. Detects ClawHavoc malware, MCP backdoors, obfuscated payloads, and supply-chain attacks. 100% read-only analysis.
version: 2.3.4
tags: [security, auditor, clawhavoc, malware, mcp, supply-chain, zero-trust]
---

# ClawSentinel v2.3

The sharpest skill auditor in the ClawHavoc era. Scans any skill markdown or GitHub repo for malicious patterns before you install it. Never executes code. Trained on public DataClaw dataset.

## Security Guarantees

- 100% local read-only analysis
- Only fetches raw.githubusercontent.com when you explicitly audit a public GitHub repo
- Zero telemetry in base version

## How to use

- "audit this skill:" + paste markdown
- "audit github https://github.com/user/repo"

## Output Format

Always clean JSON.

## Pro Tip

Run ClawSentinel on every skill before installing. ClawHub is infested right now.
