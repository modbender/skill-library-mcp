---
name: "Skill: Nexus-Orchestrator (V1.1)"
description: Intelligent SRE Bridge for AI-driven system diagnosis and recovery.
---

# Skill: Nexus-Orchestrator (V1.1)

Intelligent SRE Bridge for AI-driven system diagnosis and recovery.

## 🛡️ Security & Privacy Protocols
- **Log Redaction**: The orchestrator includes a redaction engine that masks passwords, tokens, and emails in logs before sending them to the reasoning service.
- **Generic Binary Support**: No longer relies on root-home paths. It searches for `opencode` in your system PATH or local user directory.
- **Privacy Notice**: This skill sends redacted log snippets to your configured AI reasoning service (e.g., OpenCode/Codex). Ensure your AI provider complies with your data policy.

## 📋 Capabilities
- **Reasoning-First Recovery**: Blocks blind restarts. Analyzes logs to differentiate between code bugs (alert user) and infra failures (restart service).
- **Log Contextualization**: Automatically fetches and redacts relevant logs for the AI.

## ⚙️ Logic & Safeguards
- **Manual Oversight**: Critical actions still require `/approve` if configured in OpenClaw.
- **Diagnostic Step**: The agent is forced to perform an analysis via `bridge.py` before any recovery action.

## 🚀 Installation
1. `pip install psutil`
2. Ensure `docker`, `pm2`, and `opencode` are installed.
