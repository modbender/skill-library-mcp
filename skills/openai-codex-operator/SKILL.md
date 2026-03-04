---
name: openai-codex-operator
description: Run OpenAI Codex CLI from OpenClaw for coding tasks in a target project directory. Use when the user asks OpenClaw to use Codex for implementation, debugging, refactoring, review, or scripted coding workflows.
---

# OpenAI Codex Operator

Use this skill to reliably call Codex CLI from OpenClaw.

## Core rules

1. Verify Codex CLI exists (`codex --version`) before first task.
2. Always run Codex through OpenClaw `exec` with `pty:true`.
3. Always set explicit `workdir` to the target repository.
4. For long tasks, use `background:true` and track via `process`.
5. Report clear milestones: started, waiting-input, finished/failed.

## Execution patterns

### One-shot coding task

Use:
- `exec.command`: `codex exec "<task>"`
- `exec.pty`: `true`
- `exec.workdir`: `<repo path>`

### Interactive session

Use:
- `exec.command`: `codex`
- `exec.pty`: `true`
- `exec.workdir`: `<repo path>`

### Long-running background task

1. Start with `exec(background:true, pty:true, workdir, command:"codex exec ...")`
2. Record returned `sessionId`.
3. Poll with `process action:poll`.
4. Read output with `process action:log`.
5. If Codex asks for input, use `process action:submit`.

## Recommended prompts

- "Implement <feature> with tests, run tests, and summarize changed files."
- "Find root cause for failing CI in this repo and propose minimal fix."
- "Review current branch diff and list high-risk issues first."

## Guardrails

- Do not claim files were changed unless logs show completion.
- If `codex` is missing or auth fails, return exact remediation steps.
- Keep OpenClaw tool config (`pty/workdir/background`) separate from CLI args.

## References

- `references/codex-doc-summary.md`
- `references/codex-usage-recipes.md`
- `scripts/run-codex-example.sh`
