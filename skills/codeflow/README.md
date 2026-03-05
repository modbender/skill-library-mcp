# Codeflow

English | [简体中文](README.zh-CN.md)

Codeflow runs your coding-agent CLI and relays a structured activity feed to Discord or Telegram.

It parses structured outputs locally (Claude Code `stream-json`, Codex CLI `--json`) and posts tool calls, file writes, shell commands, and results — without any extra LLM calls.

## Features

- Discord: webhook delivery, optional thread posting (`--thread`)
- Telegram: Bot API delivery (chat + optional topic/thread)
- Supported inputs: Claude Code (`--output-format stream-json`), Codex CLI (`--json`), and raw mode for other CLIs
- Robust delivery: message splitting (Discord code fences), Telegram 429 backoff, end-of-run summary
- Per-run artifacts: `stream.jsonl` (events) + `delivery-summary.json` (delivery stats)
- Non-goal: remote control — the optional Discord bridge is intentionally read-only

## Requirements

- Python >= 3.10 (`python3`)
- Claude Code structured output: `unbuffer` from `expect` (see `references/setup.md`)
- Core relay has no third-party Python dependencies (bridge mode is optional)

## Setup

Follow `references/setup.md` to:
- make `scripts/codeflow` executable
- configure Discord (webhook, optional bot token for `--thread`) or Telegram credentials
- run the smoke test

## Quick start

From this directory:

```bash
# Codex CLI (structured JSON)
bash scripts/codeflow run -w ~/projects/myapp -- codex exec --json --full-auto 'fix tests'

# Claude Code (structured JSON stream)
bash scripts/codeflow run -w ~/projects/myapp -- claude -p --output-format stream-json --verbose 'your task'
```

If you installed this as a skill, replace `bash scripts/codeflow` with `bash {baseDir}/scripts/codeflow`.

## CLI

Public entrypoint:

```bash
bash scripts/codeflow <command> [...]
```

Core commands:
- `run` — start a relay session
- `resume` — replay from a relay directory (`stream.jsonl`)
- `guard` — `activate|deactivate|status` (prevents running sessions without explicit activation)
- `review` — PR review mode
- `parallel` — run multiple sessions from a tasks file
- `bridge` — optional Discord gateway bridge (read-only)
- `smoke` — prereq/config validation
- `check` — local sanity checks (syntax + unit tests)

See `bash scripts/codeflow --help` for the canonical contract.

## Safety

By default Codeflow forwards:
- file write previews
- command output bodies

That is great for debugging and terrible for secrets. For shared channels:

```bash
export CODEFLOW_SAFE_MODE=true
```

Safe mode suppresses file previews and command output bodies (metadata only) and applies stricter redaction. It reduces risk; it does not make an unsafe workflow safe.

## Common configuration

- `CODEFLOW_SAFE_MODE=true|false`: suppress file previews + command output bodies
- `CODEFLOW_OUTPUT_MODE=minimal|balanced|verbose`: channel verbosity (default `balanced`)
- `CODEFLOW_STREAM_LOG=full|redacted|off`: what gets written into `stream.jsonl`
- `CODEFLOW_DISCORD_ALLOW_MENTIONS=true|false`: allow mentions/pings (default deny)
- `CODEFLOW_COMPACT=auto|true|false`: Telegram compact updates (default `auto`, Telegram → `true`)

Run flags and advanced modes are documented in `references/advanced-modes.md` and `references/discord-output.md`.

## Docs

- `references/setup.md`: install + credentials + smoke test
- `references/discord-output.md`: output format, artifacts, env vars, architecture
- `references/advanced-modes.md`: resume, PR review, parallel tasks, Discord bridge

## Feedback

Bug reports and feature requests: https://github.com/subjadeites/Skills/issues

## License

MIT (see `LICENSE`).

## Acknowledgements

- Upstream inspiration: `https://clawhub.ai/allanjeng/codecast`
- This repository is an OpenClaw-focused rewrite/refactor for multi-agent parsing and hardening.
