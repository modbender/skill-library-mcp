# inference-optimizer

**An OpenClaw skill that audits token usage, purges stale sessions, and optimizes inference speed.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

![banner](social-preview.png)

Ask your bot to run a baseline audit, purge old session files, or get optimization recommendations. Instead of guessing where tokens go, you get workspace sizes, session counts, and actionable next steps.

```
> /optimize
> purge stale sessions
> audit workspace tokens
```

## Before installing

1. Inspect the scripts (`openclaw-audit.sh`, `purge-stale-sessions.sh`, `setup.sh`, `verify.sh`) and confirm behavior.
2. Back up `~/.openclaw` and your workspace so you can restore sessions and config if needed.
3. Run the audit manually first (`bash .../openclaw-audit.sh`) and review output before letting an agent run it.
4. Do not run purge with `--delete` until you have inspected archive contents; prefer manual archive-and-review.
5. Do not grant broad exec allowlist or automated permission for `setup --apply` or `purge --delete`; run setup with `--apply` manually after reviewing snippets.
6. If the agent must run purge, use path-specific exec approvals and monitor the archive directory.
7. Consider running these scripts on an isolated or test host first.

## Why

Every OpenClaw instance loads workspace files, session history, and tool schemas on every request. Stale sessions pile up. Daily memory stubs accumulate. The model gets slower and more expensive without obvious cause.

This skill fixes that. Run `/optimize` to get a token audit. Approve a purge to clear stale sessions and stub files. No manual SSH, no guessing.

## Install

**ClawHub (recommended):**
```bash
clawhub install https://github.com/vitalyis/inference-optimizer
```

**Manual:**
```bash
git clone https://github.com/vitalyis/inference-optimizer.git ~/clawd/skills/public/inference-optimizer
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh        # preview first
# Review output, then:
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh --apply
```

## Setup

After install, run the setup script. By default it previews changes only; use `--apply` to modify workspace files:

```bash
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh        # preview
bash ~/clawd/skills/public/inference-optimizer/scripts/setup.sh --apply  # apply
```

This makes scripts executable and, with `--apply`, appends command snippets to `AGENTS.md` and `TOOLS.md`.

## Commands

| Command | What it does |
|---------|--------------|
| `/optimize` | Run token audit (workspace files, sessions, config); script outputs metadata |
| `/audit` | Same as `/optimize` |
| purge sessions | After audit, if user approves, run purge script (archives by default; `--delete` for immediate removal) |

## Verify

Confirm installation and script enablement:

```bash
bash ~/clawd/skills/public/inference-optimizer/scripts/verify.sh
```

Expected output:
- `optimization-agent.md` found
- `openclaw-audit.sh` executable
- `purge-stale-sessions.sh` executable
- Workspace paths resolvable
- AGENTS.md has `/optimize` (or manual step required)

## How It Works

```
SKILL.md (triggers + workflow)
    ↓
optimization-agent.md  ← agent reads for full Task 1–5 flow
scripts/
├── openclaw-audit.sh      ← baseline token audit
├── purge-stale-sessions.sh ← removes stale sessions + stub memory
├── setup.sh               ← wires commands into workspace
└── verify.sh              ← confirms install
    ↓
/optimize in chat → exec audit script → return output
purge approved    → exec purge script → archives to ~/openclaw-purge-archive/ by default
```

## Paths

Scripts auto-detect session and workspace paths:

- **Sessions:** `~/.openclaw/agents/main/sessions` or `~/.clawdbot/agents.main/sessions`
- **Workspace:** `~/clawd` or `~/.openclaw/workspace-whatsapp`
- **Memory:** `~/clawd/memory` or `~/.openclaw/workspace-whatsapp/memory`

## Script reference (for review)

- **openclaw-audit.sh:** Reads workspace file sizes, session counts, config size; outputs metadata only (no file contents). Lines 10–54.
- **purge-stale-sessions.sh:** Archive vs delete logic; `--delete` flag. Lines 22–66. Archives to `~/openclaw-purge-archive/<timestamp>/` by default.
- **setup.sh:** Appends to AGENTS.md and TOOLS.md only when `--apply` is passed. Lines 52–74.

## Security

- **Audit** outputs only metadata (file sizes, token estimates); it does not echo config or workspace contents. Config and workspace paths may contain secrets; the audit reports character counts only.
- **Purge** moves files to a timestamped archive by default (`~/openclaw-purge-archive/`). Verify archive contents before removing. Use `--delete` only when you want immediate deletion without archive.
- **Setup** modifies `AGENTS.md` and `TOOLS.md`. Run without `--apply` first to preview. Revert by removing the appended sections.
- **Allowlist:** Prefer running purge manually (`bash purge-stale-sessions.sh`) so no exec allowlist changes are needed. If purge must run via agent, add path-specific patterns rather than broad wildcards (`find *`, `rm **`).

## Limitations

- Run on the same host as OpenClaw (VPS or local)
- Workspace layout must match OpenClaw defaults

## License

MIT
