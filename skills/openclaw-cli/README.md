# OpenClaw CLI Skill

A Codex skill for operating and troubleshooting the OpenClaw CLI safely and quickly.

This skill helps route requests to the correct `openclaw` command family, apply profile isolation correctly (`--dev`, `--profile`), and verify outcomes after each operation.

## Highlights

- Command-family routing for setup, runtime, channels, messaging, agents, models, plugins, and system health.
- Built-in triage flow for "OpenClaw not working" incidents.
- Safety-first guidance for destructive commands (`reset`, `uninstall`, `--force`).
- Verification-first workflow (`status`, `health`, `doctor`, `--json` when available).

## Command Coverage

- Runtime and services: `gateway`, `daemon`, `node`, `nodes`
- Diagnostics: `status`, `health`, `doctor`, `logs`
- Messaging and channels: `channels`, `message`, `pairing`, `devices`, `qr`
- Agent workflows: `agent`, `agents`, `skills`
- Setup and config: `setup`, `configure`, `config`, `onboard`
- Extensions and system: `plugins`, `models`, `system`, `update`
- Security and policy: `security`, `approvals`, `sandbox`

## Installation

Clone this repo into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/ramensushi2026/openclaw-cli-skill.git ~/.codex/skills/openclaw-cli
```

If you already cloned it elsewhere, copy the folder so the final path is:

```text
~/.codex/skills/openclaw-cli
```

## Usage

Ask Codex with the skill name:

```text
Use $openclaw-cli to diagnose why my channels are disconnected.
Use $openclaw-cli to send a WhatsApp message from the dev profile.
Use $openclaw-cli to restart gateway and verify health.
```

## Safety Model

The skill is designed to avoid accidental destructive actions:

- Confirms intent before `reset`, `uninstall`, or forceful flows.
- Prefers diagnostics before restarts.
- Keeps profile context consistent across a workflow.
- Uses explicit post-checks after each operation.

## Repository Structure

- `SKILL.md`: Skill definition, workflow, triage sequence, and guardrails.
- `references/command-map.md`: OpenClaw command routing, recipes, and caution commands.
- `agents/openai.yaml`: Agent-facing display metadata and prompt defaults.

## References

- OpenClaw CLI docs: https://docs.openclaw.ai/cli
