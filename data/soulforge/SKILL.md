---
name: soulforge
description: "Run high-signal autonomous coding loops with Soulforge (feature-dev/bugfix/review-loop) using strict worktree isolation, review gates, and scoped fix cycles."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires": { "bins": ["soulforge", "codex", "gh"], "env": [] },
      },
  }
---

# Soulforge (Effective Use Guide)

This is **not** a full engine reference. This is the operating playbook for getting high-quality autonomous coding outcomes with Soulforge.

## Core Operating Model

Use Soulforge when you want: plan → implement → verify/test → PR → review/fix loops with minimal babysitting.

Preferred workflows:
- `feature-dev` for end-to-end feature delivery
- `bugfix` for diagnose-first, surgical fixes
- `review-loop` for tightening an existing PR until clean

## Golden Rules (Most Important)

1. **Never run from repo main checkout.**
   - Soulforge now enforces this guardrail.
2. **Always isolate work in worktrees.**
   - Default base: `<repo>/worktrees/`
3. **Keep tasks tightly scoped.**
   - Specific issue, explicit acceptance criteria, explicit DO-NOT list.
4. **Treat review findings with discipline.**
   - FIX in-scope issues.
   - Mark genuine extras as `SEPARATE`.
5. **Use callback-exec only.**
   - HTTP callback mode is removed.

## Current Behavior You Should Rely On

### Workdir / Worktree safety
- If `--workdir` is omitted, Soulforge can auto-provision a worktree under `<repo>/worktrees/...`.
- Main checkout is blocked (including bare+worktree edge cases).
- Dirty worktrees are rejected for run start.
- Out-of-base workdirs are blocked unless explicitly overridden.

### Checkpoint model
- `approve/reject` is gone.
- Use structured completion via `soulforge complete ...`.
- Pause checkpoints are `type: pause`.

### Callback model
- Use `--callback-exec`.
- Template vars include:
  - `{{run_id}}`, `{{step_id}}`, `{{step_status}}`, `{{status}}`, `{{task}}`
  - `{{callback_message}}` (step-level, preferred)
  - `{{prompt}}` remains for backward compatibility in pause scenarios

## Recommended Command Patterns

### Feature build
```bash
soulforge run feature-dev "Implement <issue-url>.
Constraints: max 2 stories. DO NOT refactor unrelated modules." \
  --workdir /abs/path/to/repo/worktrees/feat-xyz \
  --callback-exec 'openclaw agent --session-key "agent:cpto:slack:channel:c0af7b05h28" --message "Soulforge {{run_id}} {{step_id}} {{step_status}}" --deliver'
```

### Bugfix
```bash
soulforge run bugfix "Fix <issue-url> with failing test first; minimal patch only." \
  --workdir /abs/path/to/repo/worktrees/fix-xyz \
  --callback-exec 'openclaw agent --session-key "agent:cpto:slack:channel:c0af7b05h28" --message "Soulforge {{run_id}} {{step_id}} {{step_status}}" --deliver'
```

### Review-only tightening on an existing PR
```bash
soulforge run review-loop "Review PR #123 and fix only in-scope findings." \
  --workdir /abs/path/to/repo/worktrees/pr-123 \
  --var pr_number=123 \
  --callback-exec 'openclaw agent --session-key "agent:cpto:slack:channel:c0af7b05h28" --message "Soulforge {{run_id}} {{step_id}} {{step_status}}" --deliver'
```

## How to Maximize Autonomous Quality

### 1) Give a tight task contract
Include:
- target issue/PR URL
- explicit in-scope list
- explicit out-of-scope list
- objective success criteria

### 2) Keep iteration loops short
If a PR loops repeatedly:
- create/update `.soulforge-progress.md` in worktree with exact outstanding fixes
- run `review-loop` constrained to remaining findings

### 3) Handle gates like an operator, not a coder
At review gate:
- move in-scope defects to FIX
- separate unrelated ideas into follow-up issues
- avoid “while we’re here” drift

### 4) Expect long fix steps; optimize signal
Long fix steps are normal for real refactors. Your job is quality control at gates, not interrupting active runs.

## Practical Triage Heuristic

When code-review returns findings:
- **High/Medium tied to original issue:** FIX now
- **Low tied to original issue correctness:** usually FIX now
- **Anything outside scope:** SEPARATE

## Anti-Patterns (Avoid)

- Running multiple workflows in the same checkout
- Allowing scope creep in repeated review-fix loops
- Merging with known Highs because “tests pass”
- Treating this skill as generic Soulforge docs instead of an execution playbook

## Minimal Status Workflow for Operator

- Start run
- Wait for review gate
- Triage with strict scope discipline
- Repeat until pass
- Merge
- Pull main + build + npm link + daemon restart (when local runtime should track latest)

## Notes

- If loops hit `max_loops`, spawn a fresh constrained `review-loop` run with a scope lock file.
- For long-running initiatives, keep a brief run ledger in the channel (run id → PR → status).
