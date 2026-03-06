---
name: FACEPALM
displayName: FACEPALM
description: Crosscheck OpenClaw console logs with chat history (last 5 mins) and use Codex 5.3 to troubleshoot issues. Standalone troubleshooting tool that can be invoked manually or integrated with other skills.
version: 1.0.0
---

# FACEPALM

## Description

Crosscheck OpenClaw console logs with chat history (last 5 mins) and use Codex 5.3 to troubleshoot issues. Standalone troubleshooting tool that can be invoked manually or integrated with other skills.

# FACEPALM

**Crosscheck console logs with chat history to troubleshoot issues intelligently.**

FACEPALM analyzes OpenClaw console logs (`gateway.log`) and chat history from the last 5 minutes, then uses Codex 5.3 to diagnose and troubleshoot issues. It's automatically invoked by Agent Swarm when troubleshooting loops are detected.


## Usage

- **Automatic:** Invoked by Agent Swarm when a troubleshooting loop is detected (repeated errors, failed attempts)
- **Manual:** Run directly when you need intelligent troubleshooting analysis

```bash
python3 workspace/skills/FACEPALM/scripts/facepalm.py [--minutes N] [--json]
```


## Features

- Reads `gateway.log` from the last 5 minutes
- Extracts chat history from active session transcripts
- Crosschecks console errors with chat context
- Uses Codex 5.3 (`openrouter/openai/gpt-5.3-codex`) for intelligent troubleshooting
- Returns actionable diagnosis and fixes


## Requirements

- OpenClaw with `gateway.log` and session transcripts
- OpenRouter API key configured (for Codex 5.3 access)
- `openclaw` CLI on PATH (for invoking Codex via `openclaw agent`)


## Links

- **GitHub:** https://github.com/RuneweaverStudios/FACEPALM
- **ClawHub:** Update base URL when new instance is live. Current: https://clawhub.ai/skills/FACEPALM (when published)
- **Related:** [Agent Swarm](https://clawhub.ai/skills/agent-swarm) - Automatically invokes FACEPALM
