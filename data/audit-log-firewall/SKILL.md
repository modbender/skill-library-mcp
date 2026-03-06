---
name: audit-log-firewall
description: Policy-based monitoring and command-line enforcement for high-risk agent operations. Intercepts sensitive commands and logs them for human auditing.
---

# Audit Log Firewall

Security is a non-negotiable protocol for autonomous agents. This skill acts as a dynamic guardrail.

## Operational Modes

### 1. Interception Mode
Every command is checked against a local allowlist (`config/allowlist.json`).
- **High Risk**: commands like `rm -rf`, `sudo`, or direct `curl` to unknown external IPs.
- **Protocol**: If a high-risk command is detected, the agent triggers a mandatory 'Pause and Ask' state.

### 2. Forensic Logging
All terminal activity is hashed and stored in `.logs/SECURITY.json`.
- **Fields**: Timestamp, Command, User, Working Directory, and Hash.
- **Utility**: Allows humans to reconstruct the agent's actions in case of a breach or error.

## Installation
```bash
clawhub install audit-log-firewall
```
