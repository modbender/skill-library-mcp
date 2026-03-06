# coding-pm

[English](README.md) | [中文](README_zh.md)

[![GitHub release](https://img.shields.io/github/v/release/horacehxw/coding-pm?include_prereleases&style=for-the-badge)](https://github.com/horacehxw/coding-pm/releases)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-8A2BE2?style=for-the-badge)](https://github.com/openclaw/openclaw)

> PM/QA skill for [OpenClaw](https://github.com/openclaw/openclaw) that manages Claude Code as a background engineer. Complements [coding-agent](https://github.com/openclaw/openclaw): agent executes, PM manages.

**PM** (Project Manager) ensures requirements are covered, process is followed, and results meet quality standards. **QA** (Quality Assurance) validates deliverables through automated tests, functional checks, and visual inspection. coding-pm plays both roles — managing the coding-agent's work from plan to merge, so you don't have to.

```
You (IM)  →  coding-pm (PM/QA)  →  coding-agent (Engineer, background)
```

## Features

- **5-phase workflow**: preprocessing → plan review → execution monitoring → acceptance testing → merge & cleanup
- **Non-blocking**: coding-agent runs in background, your chat stays responsive
- **PM manages people, not tech**: reviews requirements coverage, process compliance, and result quality — coding-agent owns all technical decisions
- **Event-driven monitoring**: responds to wake events, parses structured markers, pushes progress to you
- **3-layer acceptance testing**: automated tests + functional integration + screenshot analysis
- **Git worktree isolation**: each task gets its own branch and worktree
- **Concurrency**: multiple tasks run simultaneously with independent isolation
- **Human-in-the-loop**: plan approval gate, decision escalation, error retry (up to 3 rounds)
- **Task lifecycle**: pause, resume, cancel — full control over background tasks
- **Pure SKILL.md**: zero scripts, uses OpenClaw platform tools

## Quick Start

### Prerequisites

- [OpenClaw](https://github.com/openclaw/openclaw) installed and configured
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 2.1.0+ (`claude auth status`)
- `git` installed

### Install

```bash
# From ClawdHub
clawdhub install coding-pm

# Or manually
cd ~/.openclaw/workspace/skills/
git clone https://github.com/horacehxw/coding-pm.git
```

### Setup

```bash
# Allow agent to access files outside workspace (for worktrees)
openclaw config set tools.fs.workspaceOnly false
openclaw gateway restart
```

### Security

coding-pm uses a **3-tier permission model** to minimize risk at each phase:

| Phase | Permissions | What the agent can do |
|-------|------------|----------------------|
| Planning (Phase 1-2) | Read-only tools via `--allowedTools` (best-effort) | Research codebase, read files, search — writes restricted but not sandboxed |
| Execution (Phase 3) | Full access via `--dangerously-skip-permissions` | Write code, run tests, commit changes |
| Testing (Phase 4) | PM runs tests directly | Coding-agent only receives targeted fix prompts |

**Why `--dangerously-skip-permissions`?** Claude Code requires this flag for non-interactive (background) execution where no TTY is available for permission prompts. This is the standard approach for any Claude Code automation or CI/CD integration.

**Why `tools.fs.workspaceOnly = false`?** Each task runs in an isolated git worktree at `~/.worktrees/<task>/`, which is outside the OpenClaw workspace directory. The agent needs filesystem access to these worktree paths.

**Additional guardrails:**
- Supervisor Protocol (`references/supervisor-prompt.md`) requires the coding-agent to ask before deleting files or modifying credentials
- PM scans coding-agent output for dangerous patterns (`rm -rf`, `DROP TABLE`, `chmod 777`, `--force`, `--no-verify`, credential file modifications)
- Human-in-the-loop: plan approval gate before execution begins, decision escalation during execution
- Skill is user-invocable only — only runs when you explicitly send `/dev <request>`

**Recommendation**: Review the Supervisor Protocol in `references/supervisor-prompt.md` before use. Run on non-production codebases first.

### Usage

In your IM (Feishu/Slack/etc.):

```
/dev Add JWT support to the auth module
```

The agent will:
1. Explore project context and compose a structured prompt for coding-agent
2. Coding-agent researches and produces a plan → PM reviews → presents for your approval
3. Execute in a git worktree → active monitoring with progress updates
4. Run acceptance tests (automated + functional + visual) → report results
5. Merge on your approval → clean up

Task commands:

```
/task list              — Show all tasks with phase and status
/task status jwt-auth   — Show task details and recent checkpoints
/task cancel jwt-auth   — Kill and clean up
/task approve jwt-auth  — Approve pending plan
/task pause jwt-auth    — Pause task, preserve state
/task resume jwt-auth   — Resume paused task
/task progress jwt-auth — Show recent checkpoints
/task plan jwt-auth     — Show approved plan
```

## How coding-pm Differs from coding-agent

| | coding-agent | coding-pm |
|--|-------------|-----------|
| Role | Cookbook (teaches you how to use agents) | PM/QA (manages agents for you) |
| Plan review | None | PM reviews requirements + user approval gate |
| Monitoring | None | Active loop: markers, commits, anomaly detection |
| Test validation | None | 3-layer: automated + functional + visual |
| Reporting | Manual | Structured progress pushes per checkpoint |
| Error handling | User handles manually | Auto-retry (3 rounds) + smart escalation |
| Concurrency | Single task | Multiple independent tasks |
| Worktree | Manual management | Automatic create/merge/cleanup |

## Architecture

```
coding-pm/
  SKILL.md                          # PM brain — 5-phase workflow logic
  references/
    supervisor-prompt.md            # Appended to coding-agent system prompt
  CLAUDE.md                         # Developer guide
```

No custom scripts. Uses OpenClaw's built-in `bash` (pty/background/workdir) and `process` (poll/log/kill/list/write) tools.

## Requirements

| Component | Version |
|-----------|---------|
| OpenClaw | 2026.2.19+ |
| git | 2.20+ (worktree support) |
| Claude Code | 2.1.0+ |

## License

[MIT](LICENSE)
