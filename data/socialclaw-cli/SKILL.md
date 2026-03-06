---
name: socialclaw-cli
description: Run SocialClaw as an agentic control plane for Meta operations through the installed social CLI. Use when the user asks for multi-step execution, approvals, ops automation, or command generation across auth, query, post, Instagram, WhatsApp, Marketing API, agent mode, and gateway/studio workflows. Translate natural-language intents into explicit, risk-gated social commands with confirmation-aware execution.
metadata:
  openclaw:
    homepage: "https://github.com/vishalgojha/social-CLI"
    requires:
      bins:
        - social
    install:
      - id: social-cli-node
        kind: node
        package: "@vishalgojha/social-cli"
        bins:
          - social
        label: Install Social CLI (npm)
---

# SocialClaw CLI

Use this skill to operate SocialClaw as an agentic control plane and produce safe `social` command flows.
Assume `social` is preinstalled, verify availability first, then route to the right domain workflow.

## Core Workflow

1. Validate environment before first command in a session.
2. Parse intent into one primary domain.
3. Start with read-only checks when state is unknown.
4. Propose exact command(s) before execution.
5. Apply risk gating and request confirmation for write actions.
6. Execute minimal command sequence.
7. Recover failures with targeted diagnostics and retry.

### Validate Environment

- Run `social --version`.
- Run `social doctor`.
- If missing or outdated:
  - Verify package source before installing:
    - `https://www.npmjs.com/package/@vishalgojha/social-cli`
    - `https://github.com/vishalgojha/social-CLI`
  - Install or upgrade with `npm install -g @vishalgojha/social-cli`.
  - Re-run `social --version` and `social doctor`.

## Domain Routing

Load only the reference file for the selected domain plus `references/safety-and-risk.md`.

- `auth`, `query`, `post`, `instagram`: `references/workflows-core.md`
- `marketing`, `whatsapp`: `references/workflows-marketing-whatsapp.md`
- `ops`, `agent`, `gateway`, `studio`: `references/workflows-ops-agent-gateway.md`
- command lookup and fallback groups: `references/command-map.md`
- errors and recovery: `references/troubleshooting.md`

## Execution Policy

- Prefer deterministic CLI commands over narration.
- Keep commands profile-aware when the user specifies a client/workspace.
- Never print full tokens or secrets in output.
- Treat unknown write impact as high-risk until proven otherwise.
- Run `social doctor` first when configuration confidence is low.

## Risk Policy

Use `references/safety-and-risk.md` for classification and confirmation wording.

- Read-only actions can execute immediately.
- Low and high write actions require explicit user confirmation.
- High-risk actions must include a spend or delivery warning and a rollback command when available.

## Output Contract

When responding with actions:

1. Show a short plan line.
2. Show executable command block(s).
3. State assumptions (profile, account ID, page ID, region, time window).
4. Request confirmation if the action is not read-only.
