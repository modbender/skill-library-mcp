---
name: skill-father
description: Authoritative skill-creation standards (Boss). Use when creating or updating OpenClaw skills so they are portable, reproducible, include prerequisites checks, and have a guided installation/onboarding flow that persists machine-specific config in skill-local config files.
---

# Skill Father

This skill is Boss’s opinionated, **authoritative** standard for creating/updating skills.

It is based on the upstream `skill-creator` guidance, with extra requirements:

- Always include **Prerequisites** checks (fail fast).
- Keep skills **portable/shareable**: do not bake machine-specific settings into `SKILL.md`.
- Always include **Initialization / Installation / Onboarding** that prompts the user when needed.
- Make skills **reproducible** for other people/machines.

## Core principles (from skill-creator)

- **Concise is key**: minimize context bloat.
- **Progressive disclosure**: keep SKILL.md short; put big docs in `references/`, deterministic code in `scripts/`.
- Avoid extra docs (README/CHANGELOG/etc.).

## Required sections in every skill

### 1) Prerequisites

Include a short section with concrete checks/commands.

Examples:

- 1Password-backed workflows:
  - `op whoami` must succeed (or, if service accounts are used, required env vars like `OP_SERVICE_ACCOUNT_TOKEN` must be set).
- External CLIs:
  - `command -v <tool>` must exist; include install guidance if missing.

### 2) Configuration (portable)

Rules:

- Never hardcode machine/user-specific paths, usernames, tenant IDs, tokens, etc. inside `SKILL.md`.
- Prefer skill-local config files stored next to `SKILL.md`, e.g.:
  - `config.env` (dotenv-style KEY="VALUE")
  - `config.json` (structured)
- **Config must be split into two files**:
  - `config.env.example` (or `config.json.example`) — checked-in/shareable example; never mutated by onboarding
  - `config.env` (or `config.json`) — real machine-specific values written/updated during onboarding
- `SKILL.md` documents:
  - where config lives
  - required keys + defaults
  - which file is the example vs real
  - how to run onboarding to generate/update the real config

### 3) Initialization / Installation / Onboarding

Provide a guided first-run flow.

- If setup is trivial and safe: can be silent.
- Otherwise: **ask the user** for choices + confirmation.
- Persist outcomes into the **real** skill-local config file (not into SKILL.md; do not modify the example file).
- Prefer discovery + confirmation over assumptions.

**Prefer an onboarding helper script** when setup touches real machine state.

### Chat-first onboarding (Telegram-friendly)

When the primary interface is chat (e.g. Telegram), do not rely on TTY-style interactive prompts.

**Requirement:** Every child skill should explicitly document a **“Preferred (chat-first)”** onboarding path.

Preferred pattern:

1. Agent asks the user the required onboarding questions in chat.
2. Agent writes/updates the real skill-local config file.
3. Agent runs a smoke test and reports results.

If you do ship an interactive script, treat it as an optional convenience for users running it in a real terminal (document as “Optional (terminal)”).

Recommended onboarding script behaviors:

- Generate/update the real config file from prompts and/or auto-discovery.
- If editing an existing system config file (e.g. `~/.config/openclaw/env`, `~/.ssh/config`):
  - detect whether the target file exists; create if missing
  - for each key/entry that would change, show current vs new
  - prompt the user per item: keep / override / skip
  - for secrets/tokens, mask values in prompts
- If a restart/reload is required:
  - first detect whether the service manager is available (e.g. `systemctl --user status <svc>`)
  - ask the user for confirmation before restarting
  - if not detectable/available, print clear manual instructions

Examples of onboarding steps:

- Detect candidate paths/resources.
- Present options.
- Ask for confirmation.
- Write config.
- Validate config by running a quick self-test.

### 4) Reproducibility

- The skill should work for other people with minimal edits.
- Prefer parameterization/config + prompts.
- Avoid environment-specific assumptions unless explicitly documented.

### 5) Executables / bin placement

- Any executable scripts/binaries required by the skill should live **inside the skill folder** (or inside the relevant plugin’s folder).
- For convenience, you may create a **symlink** into a common PATH location (e.g. `~/.local/bin/<name>`), but the canonical copy should remain in the skill/plugin directory.

## Resource layout

Use the standard skill layout:

```
skill-name/
├── SKILL.md
├── config.env.example    # example (shareable)
├── config.env            # real machine-specific config (generated/updated by onboarding)
├── scripts/              # deterministic code
└── references/           # optional docs, loaded on demand
```

## Process checklist (for the agent)

1. Understand the task and collect concrete usage examples.
2. Plan resources (`scripts/`, `references/`, `assets/`) only if they reduce repetition or increase reliability.
3. Create/confirm required sections: Prerequisites, Config, Installation/Onboarding.
4. Implement the smallest working version.
5. Validate with a smoke test.
6. Iterate.

## Example expectations: ssh-op skill

- **Prereqs**: confirm `op whoami` works (or service account env is set) and `ssh/ssh-add/ssh-agent` exist.
- **Onboarding**: proactively discover/confirm:
  - vault name
  - SSH key item
  - host + host aliases stored in the 1Password item
- **Integration**: check whether aliases exist in `~/.ssh/config`; if missing, offer to add/update entries.
- **Config**: store vault/item/host/aliases in a skill-local config file.
