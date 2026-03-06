# AGENTS.md

This repository is an **AgentSkill** for OpenClaw / Clawdbot: **Freedcamp**.

It uses Node.js built-in `fetch` (or `https`) and `crypto` with zero external dependencies, designed to work in sandboxed environments.

If you are a coding agent working in this repo, follow the guidance below.

## Project overview

Goal: provide a robust Node.js CLI (`scripts/freedcamp.mjs`) that lets an agent:

- Authenticate with **Freedcamp HMAC-SHA1 secured credentials** (API Key + API Secret)
- Discover the **organization hierarchy** (groups, projects, apps)
- Support both:
  - **Personal task management** (my tasks, quick capture, triage, notifications)
  - **Project workflows** (task creation, status updates, comments, task lists)

Non-goals:

- Do not add Invoice/Invoices Plus features unless explicitly requested.
- Do not bake "bot personality" into the skill; keep it generic and configurable by the user/bot prompt.

## Repo layout

- `SKILL.md` -- skill definition + agent-facing usage guide
- `README.md` -- human-facing quickstart (install/config/run)
- `AGENTS.md` -- agent-facing development guide (this file)
- `scripts/freedcamp.mjs` -- the only executable; dependency-free Node ESM CLI
- `references/REFERENCE.md` -- API notes, links, and gotchas
- `_meta.json` -- OpenClaw/ClawHub metadata

## Local config files

The CLI stores session cache (session token, user ID) in:

- Default: `~/.openclaw/skills/freedcamp-session.json`
- Override: `FREEDCAMP_SESSION_PATH=/path/to/file.json`

## Setup commands

OpenClaw config can be edited non-interactively via `openclaw config get|set|unset` (useful for enabling the skill and injecting credentials).

No package manager required.

- Ensure Node.js **18+** (needs built-in `fetch` and ESM).
- Smoke test (requires `FREEDCAMP_API_KEY` and `FREEDCAMP_API_SECRET` in env):

  - Who am I:
    - `node scripts/freedcamp.mjs me`

  - List groups and projects:
    - `node scripts/freedcamp.mjs groups-projects`

## How to run checks

There is no test suite yet. If you change behavior, run at least:

- `node scripts/freedcamp.mjs me`
- `node scripts/freedcamp.mjs groups-projects`
- `node scripts/freedcamp.mjs tasks --project <project_id> --limit 5`
- A write-path check: create-task + update-task + comment on a throwaway task

## Conventions & patterns

### CLI behavior

- Always output **JSON** to stdout for machine parsing.
- Exit non-zero with a clear error message on failures.
- Preserve backwards compatibility of command names/flags where possible.

### API calls

- Freedcamp uses `limit` + `offset` pagination (max 200 per page).
- Authentication is HMAC-SHA1: `hash = HMAC-SHA1(apiKey + timestamp, apiSecret)`, sent as query parameters.
- Once a session is established, use `X-Freedcamp-API-Token` and `X-Freedcamp-User-Id` headers instead.
- Handle 401 by refreshing the session automatically.

### Code style

- Node ESM (`.mjs`), standard library only.
- Use small, testable functions (request helpers, parsing helpers, storage helpers).
- Keep "business logic" separate from transport (HTTP request) functions.

## Security

- **Never** commit API keys, secrets, or user config.
- Do not print secrets in logs or error messages.
- The `.env` file and `session.json` should be in `.gitignore`.

## Comments and rich text

- Freedcamp comments use HTML formatting.
- Plain text should be wrapped in `<p>` tags before sending (there is a known Freedcamp bug where omitting `<p>` tags breaks formatting).
- The CLI auto-wraps plain `--text` input in `<p>` tags.

## Release & publishing

- This skill can be published to **ClawHub** directly from the skill folder.
- First-time publish example:

  `clawhub publish . --slug freedcamp --name "Freedcamp" --version 1.0.0 --tags latest --changelog "Initial release"`

- When preparing a release:
  - Update `README.md` / `SKILL.md` docs if the command surface changed
  - Bump the semver version used during `clawhub publish`
  - Validate install into a clean workspace via `clawhub install <slug>`

## When unsure

Prefer minimal, composable primitives over many narrow "shortcut" commands.
Add helpers only when they reduce multi-step orchestration or statefulness (e.g., session caching).
