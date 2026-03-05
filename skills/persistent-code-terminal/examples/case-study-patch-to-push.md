# Case Study: One sentence → Patch → Build/Test → Commit → Push

**Goal:** From a phone (SSH), ask Codex to add a small feature, verify, and push — while keeping full visibility and takeover ability.

## Setup

From repo root:

```bash
chmod +x skills/persistent-code-terminal/bin/*.sh
./skills/persistent-code-terminal/bin/persistent-code-terminal-start.sh
```

## One-sentence instruction to Codex (closed loop)

```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-codex-exec.sh "Add a /health endpoint that returns JSON {status:'ok'}. Add tests. Ensure build and tests pass. Commit with 'feat: add health endpoint' and push to current branch. Do NOT force push."
```

This uses the script defaults:
- `codex exec --full-auto --sandbox workspace-write --cd <current-dir> ...`

Optional (for automation logs):
```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-codex-exec.sh --json -o /tmp/codex-run.json "Add a /health endpoint that returns JSON {status:'ok'}. Add tests. Ensure build and tests pass. Commit with 'feat: add health endpoint' and push to current branch. Do NOT force push."
```

## Observe & intervene if needed

Attach to the session:

```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-attach.sh
```

If Codex gets stuck or fails tests, you can either:

1) **Give Codex a follow-up one-liner** (same repo, same session):
```bash
./skills/persistent-code-terminal/bin/persistent-code-terminal-codex-exec.sh "Fix the failing test output above with minimal changes. Rerun tests until green. Then push."
```

2) Or **take over manually** in the attached session (run build/test, edit files, etc.).

## Why this works well on mobile

- Your SSH connection can drop; the tmux session stays alive.
- Output is preserved; you can attach later and see the full history.
- You keep control: you can interrupt, inspect diffs, or stop before push.
