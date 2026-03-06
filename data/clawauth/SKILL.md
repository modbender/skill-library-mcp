---
name: clawauth
description: Let agents request OAuth access from end users via short links, continue working asynchronously, and later claim reusable third-party API tokens from local keychain storage instead of a centralized SaaS token vault.
metadata: {"openclaw":{"emoji":"🔐","homepage":"https://auth.clawauth.app","requires":{"bins":["clawauth"]},"install":[{"id":"node","kind":"node","package":"clawauth","bins":["clawauth"],"label":"Install clawauth CLI (node)"}]}}
---

# Clawauth OAuth Skill

This skill gives agents a production-safe OAuth handover flow that is async by default and works across chat/session interruptions.

Use this when the agent needs provider credentials from a human user, but must avoid blocking execution and must avoid long-lived token storage on a third-party auth SaaS.

## Why this exists

Most "OAuth gateway" patterns keep user refresh tokens in a central hosted database. clawauth avoids that model:

- Hosted edge service mints short-lived auth sessions.
- User authorizes directly with the provider.
- Token response is encrypted end-to-end to the requesting CLI session.
- CLI claims once and stores token locally in system keychain.
- Server-side session is ephemeral and deleted on claim/expiry.

Result: async UX for agents, minimal operator overhead, and no permanent central token vault by design.

## Runtime prerequisite

`clawauth` must already be preinstalled in the trusted runtime image/environment by the operator.
This skill does not instruct dynamic package installation.

OpenClaw can detect this requirement from frontmatter metadata:

- `metadata.openclaw.requires.bins: ["clawauth"]` gates eligibility.
- `metadata.openclaw.install` can expose an operator-approved install action in OpenClaw UI/Gateway flows.

## How installation is documented and triggered

- Installation intent is declared in frontmatter, not in free-form shell instructions.
- This skill declares a Node installer in `metadata.openclaw.install` for package `clawauth`.
- OpenClaw/Gateway uses that metadata to offer a managed install action when `clawauth` is missing.
- If multiple installer options are present, Gateway selects a preferred one (OpenClaw docs: brew preferred when available, otherwise node manager policy).
- For this skill we publish a single Node installer path to keep behavior deterministic across hosts.
- Reference: https://docs.openclaw.ai/tools/skills
- Reference: https://docs.openclaw.ai/platforms/mac/skills
- Source code (review before install): https://github.com/claw-auth/clawauth

## Manual install (operator fallback)

If OpenClaw/Gateway does not run the install action automatically, install the CLI manually:

```bash
npm i -g clawauth
```

Then verify:

```bash
clawauth --help
openclaw skills check --json
```

## Install policy (recommended)

- Pre-install `clawauth` in the base image/runner and disable ad-hoc package fetches.
- Pin and approve the CLI version in operator-managed tooling policy.
- Keep package source/provenance controls outside this skill (CI image build or internal artifact policy).

## Hosted service endpoint

The published CLI is already wired to:

- `https://auth.clawauth.app`

Agents do not need `CLAWAUTH_WORKER_URL` for normal hosted usage.

## Provider support

Implemented providers in current worker:

- notion
- github
- discord
- linear
- airtable
- todoist
- asana
- trello
- dropbox
- digitalocean
- slack
- gitlab
- reddit
- figma
- spotify
- bitbucket
- box
- calendly
- fathom
- twitch

Always treat server output as source of truth:

```bash
clawauth providers --json
```

## Canonical async flow (non-blocking)

1) Start auth and return immediately:

```bash
clawauth login start <provider> --json
```

2) Extract and forward `shortAuthUrl` to the user.

3) Continue other work. Do not block.

4) Later poll/check:

```bash
clawauth login status <sessionId> --json
```

5) When status is `completed`, claim once:

```bash
clawauth login claim <sessionId> --json
```

6) Claim completion and hand off control to the operator-defined API call layer.
This skill intentionally avoids instructing raw token materialization commands.

## Token exposure boundaries

- `login claim` may return sensitive token payload data in JSON output.
- Do not paste sensitive command output to chat, logs, traces, or telemetry.
- Do not materialize tokens into shell environments from this skill.
- Use operator-controlled secret handling for downstream provider API calls.

## Command map

### Login lifecycle

- `clawauth login start [provider] [--ttl <seconds>] [--scope <scope>] [--json]`
- `clawauth login status <sessionId> [--json]`
- `clawauth login claim <sessionId> [--json]`
- `clawauth login wait <sessionId> [--timeout <ms>] [--interval <ms>] [--json]`

### Session management

- `clawauth sessions [--json]`
- `clawauth session-rm <sessionId> [--json]`

### Token access

- `clawauth token list [--json]`

### Discovery and docs

- `clawauth providers [--json]`
- `clawauth explain`
- `clawauth docs`

## JSON fields agents should parse

### `login start --json`

- `provider`
- `sessionId`
- `expiresIn`
- `shortAuthUrl`
- `authUrl`
- `statusCommand`
- `claimCommand`

### `login status --json`

- `status` (`pending | completed | error`)
- `provider`
- `error`

### `login claim --json`

- `status` (`pending | completed | error`)
- `provider`
- `tokenData`
- `storedInKeychain`
- `keychainService`
- `keychainAccount`

## Agent behavior rules

- Prefer `--json` for machine parsing.
- Never block by default; only use `login wait` when explicitly needed.
- On `pending`: schedule retry later.
- On `completed`: run `login claim` once.
- On `error`: surface concise reason and restart with new `login start`.
- If session context is lost, recover using `clawauth sessions --json`.
- If provider unknown, run `clawauth providers --json` and choose supported value.
- Never print raw tokens into user-facing chat.
- Do not run package install/fetch commands from this skill.
- Do not export tokens into shell environment variables from this skill.

## Security model summary

- Short-lived session data in Cloudflare KV (default TTL: 3600s, configurable).
- Signed OAuth `state` binding provider and expiry.
- Signed request verification for status/claim with timestamp + nonce.
- Replay and rate-limit protections during polling.
- End-to-end encrypted token blob (`nacl.box`) from callback to CLI claimant.
- Session blob removed from server on successful claim.
- Tokens stored locally in OS keychain via CLI.

## Failure handling

Provider not implemented:

- `login start` returns error indicating feature request recorded.

Provider misconfigured on backend:

- server returns clear missing secret/config message.

Session expired:

- `status`/`claim` returns not found/expired; start new session.

Lost chat context:

- run `clawauth sessions --json`, then continue with `status`/`claim`.

No token found later:

- run `clawauth token list --json` and select provider/account explicitly.

## Minimal end-to-end example

```bash
# 1) Start
clawauth login start notion --json

# 2) Share shortAuthUrl with user (from JSON output)

# 3) Later check
clawauth login status <sessionId> --json

# 4) Claim when completed
clawauth login claim <sessionId> --json

# 5) Continue with operator-defined downstream API handling
```

## Reference

See `references/commands.md` for compact copy-paste command blocks.
