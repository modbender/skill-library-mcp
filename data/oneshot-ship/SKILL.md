---
name: oneshot-ship
description: Ship code autonomously with oneshot CLI -- a single command that plans, executes, reviews, and opens a PR. Runs over SSH or locally. Use when the user wants to ship code changes, automate PRs, or run an autonomous coding pipeline with Claude and Codex.
license: MIT
metadata:
  author: ADWilkinson
  version: "0.0.1"
  repository: "https://github.com/ADWilkinson/oneshot-cli"
compatibility: Requires Bun, Claude Code CLI, Codex CLI, and GitHub CLI. SSH access to a server optional (can run locally with --local)
---

# oneshot CLI

Ship code with a single command. oneshot CLI runs a full autonomous pipeline: plan (Claude) -> execute (Codex) -> review (Codex) -> PR (Claude). Works over SSH to a remote server or locally with `--local`.

## When to use this skill

- User wants to ship a code change to a repository without manual coding
- User wants to automate the plan/implement/review/PR workflow
- User mentions "oneshot" or "oneshot CLI" or wants autonomous code shipping
- User wants to delegate a coding task to run on a remote server or locally

## Installation

```bash
bun install -g oneshot-ship
```

## Setup

Run `oneshot init` to configure SSH host, workspace path, API keys, and model preferences. Config is saved to `~/.oneshot/config.json`.

Repos on the server should be organized as `<org>/<repo>` under the workspace path:

```
~/projects/
  my-org/my-app/
  my-org/my-api/
```

### Server prerequisites

- [Bun](https://bun.sh)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
- [Codex CLI](https://github.com/openai/codex)
- [GitHub CLI](https://cli.github.com) (authenticated)
- `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` in environment

## Usage

### Basic usage

```bash
oneshot <repo> "<task>"
```

### With Linear ticket

```bash
oneshot <repo> <linear-url>
```

Fetches the ticket as context and updates its status after the PR is created.

### Local mode

```bash
oneshot <repo> "<task>" --local
```

Runs the pipeline directly on the current machine instead of SSH-ing to a server. Requires Claude Code CLI, Codex CLI, and GitHub CLI installed locally.

### Background mode

```bash
oneshot <repo> "<task>" --bg
```

Fire and forget -- runs detached on the server (SSH mode only).

### Dry run

```bash
oneshot <repo> --dry-run
```

Validates the repo exists without running the pipeline.

### Override model

```bash
oneshot <repo> "<task>" --model sonnet
```

## Pipeline steps

1. **Validate** -- checks the repo exists, fetches latest from origin
2. **Worktree** -- creates a temp git worktree from `origin/main`, auto-detects and installs deps (bun/pnpm/yarn/npm)
3. **Plan** -- Claude reads the codebase and CLAUDE.md conventions, outputs an implementation plan
4. **Execute** -- Codex implements the plan
5. **Review** -- Codex reviews its own diff for bugs, types, and security issues
6. **PR** -- Claude creates a branch, commits, pushes, and opens a PR

The worktree is cleaned up after every run.

## Configuration

`~/.oneshot/config.json`:

```json
{
  "host": "user@100.x.x.x",
  "basePath": "~/projects",
  "anthropicApiKey": "sk-ant-...",
  "linearApiKey": "lin_api_...",
  "claude": { "model": "opus", "timeoutMinutes": 180 },
  "codex": { "model": "gpt-5.3-codex", "reasoningEffort": "xhigh", "timeoutMinutes": 180 },
  "stepTimeouts": {
    "planMinutes": 20,
    "executeMinutes": 60,
    "reviewMinutes": 20,
    "prMinutes": 20
  }
}
```

Only `host` is required. Everything else has defaults.

## Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--model` | `-m` | Override Claude model |
| `--dry-run` | `-d` | Validate only |
| `--local` | | Run locally instead of over SSH |
| `--bg` | | Run in background (SSH mode only) |
| `--help` | `-h` | Help |
| `--version` | `-v` | Version |

## Customization

- Drop a `CLAUDE.md` in any repo root to enforce conventions -- oneshot passes it as context to both Claude and Codex
- Edit `prompts/plan.txt`, `execute.txt`, `review.txt`, `pr.txt` to change pipeline behavior

## Tips

- Use `--bg` for long-running tasks so you can fire and forget
- Linear integration auto-moves tickets to "In Review" and adds a PR comment
- Per-step timeouts prevent runaway processes (defaults: plan 20min, execute 60min, review 20min, PR 20min)
- oneshot CLI creates isolated worktrees so your main branch is never affected
