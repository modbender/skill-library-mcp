---
name: codexmonitor
version: 0.2.1
description: >
  List/inspect/watch local OpenAI Codex sessions (CLI + VS Code) using the
  CodexMonitor Homebrew formula. Reads sessions from ~/.codex/sessions by default
  (or via CODEX_SESSIONS_DIR / CODEX_HOME overrides). Requires the cocoanetics/tap
  Homebrew tap.
homepage: https://github.com/Cocoanetics/CodexMonitor
metadata:
  moltbot:
    emoji: "🧾"
    os: ["darwin"]
    requires:
      bins: ["codexmonitor"]
    install:
      - id: brew
        kind: brew
        formula: cocoanetics/tap/codexmonitor
        bins: ["codexmonitor"]
        label: "Install codexmonitor (brew)"
  openclaw:
    requires:
      bins: ["codexmonitor"]
    install:
      - id: brew
        kind: brew
        formula: cocoanetics/tap/codexmonitor
        bins: ["codexmonitor"]
        label: "Install codexmonitor via Homebrew"
---

# codexmonitor

Use `codexmonitor` to browse local OpenAI Codex sessions.

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Common commands

- List sessions (day): `codexmonitor list 2026/01/08`
- List sessions (day, JSON): `codexmonitor list --json 2026/01/08`
- Show a session: `codexmonitor show <session-id>`
- Show with ranges: `codexmonitor show <session-id> --ranges 1...3,26...28`
- Show JSON: `codexmonitor show <session-id> --json`
- Watch all: `codexmonitor watch`
- Watch specific: `codexmonitor watch --session <session-id>`

## Notes
- Sessions live under `~/.codex/sessions/YYYY/MM/DD/` by default.
- If your sessions live somewhere else, set `CODEX_SESSIONS_DIR` (preferred) or `CODEX_HOME`.
- Sessions can be resumed/appended by id via Codex: `codex exec resume <SESSION_ID> "message"`.
