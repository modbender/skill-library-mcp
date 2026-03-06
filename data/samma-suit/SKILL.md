---
name: samma-suit
description: Add 8 security governance layers to your OpenClaw agent — budget controls, permissions, audit logging, kill switch, identity signing, skill vetting, process isolation, and gateway protection.
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      env: ["SAMMA_API_KEY"]
      bins: []
    primaryEnv: "SAMMA_API_KEY"
user-invocable: true
command-dispatch: prompt
---

# Sammā Suit — Security Governance for OpenClaw

You are helping the user install and configure Sammā Suit, an open-source security framework that adds 8 enforced governance layers to OpenClaw as lifecycle hooks.

## What It Does

Sammā Suit intercepts OpenClaw's plugin hooks to enforce:
- **NIRVANA** — Kill switch. Blocks all activity if agent is terminated.
- **DHARMA** — Permissions. Checks tools against allowed permission set.
- **SANGHA** — Skill vetting. Blocks unapproved skills via allowlist + AST scanning.
- **KARMA** — Budget controls. Per-agent monthly spending caps with hard ceiling.
- **BODHI** — Isolation. Injects timeout, token, and resource limits per agent.
- **METTA** — Identity. Ed25519 cryptographic signing on outbound messages.
- **SILA** — Audit trail. Logs every tool call, message, and session event.

## Installation

Run:
