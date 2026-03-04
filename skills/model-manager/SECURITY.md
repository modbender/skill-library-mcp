# Security Policy for OpenClaw Model Manager

This document outlines the permissions and security considerations for the `model-manager` skill.

## Required Permissions

This skill performs the following operations to enable dynamic model routing:

1.  **Read/Write Configuration**: Modifies `~/.openclaw/openclaw.json` to update model fallbacks and enable new models dynamically. This is the core functionality.
2.  **Network Access**: Connects to `https://openrouter.ai/api/v1/models` (HTTPS only) to fetch current pricing and model lists. No user data is sent.
3.  **Process Execution**: Spawns sub-processes via `openclaw sessions spawn` to orchestrate multi-agent workflows (Planner/Executor/Reviewer).

## Data Privacy

- **No Telemetry**: This skill does not collect or transmit usage data to the author or third parties (other than the necessary API calls to OpenRouter).
- **Local Execution**: All logic runs locally on the user's machine.

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it via GitHub Issues on the repository.
