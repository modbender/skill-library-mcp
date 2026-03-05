---
name: chief-feature
description: >
  Create and implement new features in Chief-managed projects using the Chief CLI.
  Use when asked to create a new PRD, implement a feature with Chief, set up a
  worktree and branch for a new feature, or open a PR for a Chief-implemented feature.
  Triggers on phrases like "create a new PRD", "implement this feature with Chief",
  "run Chief for a feature", "new feature request", or any workflow involving
  Chief's interactive PRD creation and AI-driven implementation loop.
---

# Chief Feature Workflow

Chief is an AI-driven development loop: reads a `prd.json`, implements user stories one by one via Claude Code, commits each, and tracks progress.

## Full Workflow

### 1. Clone / verify repo

Confirm the project is cloned locally.

### 2. Create a new PRD

Run interactively in the project root:

```bash
cd <project>
chief new <prd-name>
```

Chief launches Claude Code in PRD-writer mode. It will ask clarifying questions with lettered options. Provide:
- The full feature description / spec
- Answers to clarifying questions (e.g. "1A, 2C, 3D")

When Chief asks **"Do you want to create prd.md?"** — approve (option 1 or 2).

Chief converts `prd.md` → `prd.json` on `/exit`. Watch for:
```
✓ PRD converted successfully
```

Files land at: `.chief/prds/<prd-name>/prd.md` and `prd.json`

### 3. Create a worktree + branch

```bash
git worktree add ../<project>-<prd-name> -b feat/<prd-name>
mkdir -p ../<project>-<prd-name>/.chief/prds/<prd-name>
cp .chief/prds/<prd-name>/prd.{md,json} ../<project>-<prd-name>/.chief/prds/<prd-name>/
```

### 4. Commit the PRD

```bash
cd ../<project>-<prd-name>
git add .chief/prds/<prd-name>/prd.md
git commit -m "docs: add <prd-name> PRD"
```

Only commit `prd.md` — `prd.json` is typically gitignored.

### 5. Delegate to a subagent (recommended for long runs)

Instead of running Chief manually and polling, spawn a subagent to handle the full implementation autonomously:

```
Spawn a subagent with this task:
- Working directory: ~/<project>-<prd-name>
- Run `chief <prd-name>` with pty:true
- Press `s` to start the loop
- Approve bash prompts with `1` + Enter (or `2` to always allow)
- If stuck on a prompt, send hex `0d` (Enter)
- Poll until all stories show ✓ (100%)
- Commit progress.md, push, open PR
- Announce the PR URL when done
```

The subagent runs fully isolated and auto-announces on completion. You can spawn **multiple subagents in parallel** — one per PRD/worktree — for concurrent feature development.

**Parallel runs:** 2–3 concurrent subagents is the practical sweet spot. Each Chief run is API-heavy (runs Claude Code under the hood), so more than 3 parallel runs risks rate limits and high cost.

### 5b. Run Chief manually (alternative)

If you prefer to supervise directly:

```bash
chief <prd-name>
```

Press **`s`** in the TUI to start. Chief works through stories in priority order, runs verification (`make test`, `pnpm typecheck`, etc.), commits each passing story, and updates `progress.md`.

Monitor via `process(action=poll)` on the PTY session. Watch for `**US-00X is complete**`.

### 6. Commit progress + push

```bash
git add .chief/prds/<prd-name>/progress.md
git commit -m "docs: add <prd-name> progress"
git push -u origin feat/<prd-name>
```

### 7. Open a PR

```bash
gh pr create \
  --title "feat: <prd-name>" \
  --body "Implements the <prd-name> PRD. See .chief/prds/<prd-name>/prd.md for spec." \
  --base main
```

### 8. Clean up the worktree

After the PR is merged:

```bash
cd <project>
git worktree remove ../<project>-<prd-name>
git branch -d feat/<prd-name>
```

> Use `git worktree remove --force` if the directory has uncommitted changes.

## Tips

- TUI bash prompts: use `1` (Yes) or `2` (Yes, always allow)
- If stuck on a permission prompt, send `hex: ["0d"]` via `process(send-keys)`
- If a story fails, Chief retries or logs the failure in `progress.md`
- `prd.json` is typically gitignored — only commit `prd.md` and `progress.md`
- Chief resumes automatically from the last completed story if restarted

## Reference

See `references/chief-commands.md` for CLI commands, TUI keyboard shortcuts, and official links.

## About Chief

Chief is an open-source AI-driven development loop built by minicodemonkey.
- Website: https://chiefloop.com/
- GitHub: https://github.com/minicodemonkey/chief
