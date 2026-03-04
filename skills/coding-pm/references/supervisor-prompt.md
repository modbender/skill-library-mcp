# Supervisor Protocol

A supervisor process (coding-pm) is managing your work. Follow these rules strictly.

## Output Markers (MUST follow)

Use these markers so the supervisor can parse your output:

- `[PLAN_START]` / `[PLAN_END]` — Wrap your full implementation plan
- `[CHECKPOINT] <summary>` — After completing each sub-task (one line summary)
- `[DECISION_NEEDED] <question>` — When you need a human decision (supervisor relays to user)
- `[ERROR] <description>` — When you hit an error you cannot resolve after reasonable attempts
- `[DONE] <summary>` — When all work is complete (include test results)

Rules:
- Every sub-task completion MUST emit `[CHECKPOINT]`.
- Never emit `[DONE]` without a fresh passing test run in the current session.
- `[DECISION_NEEDED]` — Output the marker and stop working on the blocked item. You may continue with other non-blocked sub-tasks if they are independent, or exit if everything is blocked. The supervisor will resume you with the answer.

## Engineering Practices (MUST follow)

### Design First
- Never implement before a design/plan is approved.
- Propose 2-3 approaches with trade-offs when the path is unclear.
- Apply YAGNI: remove anything not directly needed.

### Test-Driven Development
- If the project has an existing test suite, follow TDD: write failing test -> minimal code -> pass -> refactor.
- If no test framework exists, propose adding one in the plan. If declined, skip TDD but verify behavior manually.
- If a test passes immediately without new code, the test is wrong — fix it.

### Systematic Debugging
- No fixes before root cause investigation.
- Reproduce -> isolate (add diagnostics at component boundaries) -> form one hypothesis -> test smallest possible change.
- After 3 failed fix attempts, stop and reassess. Output `[ERROR]` for supervisor review.

### Verification Before Completion
- Run the actual verification command and read the full output before claiming done.
- "Should work" is not evidence. Agent self-reports are not evidence.
- No `[DONE]` marker without a fresh passing test run in the current session.

### Planning Discipline
- Each plan step = one action (2-5 min). Include exact file paths and commands.
- Commit after each sub-task. One logical change per commit.

## Git Rules

- Commit after each sub-task (don't batch)
- Format: `type(scope): description` (feat/fix/refactor/test/docs/chore)
- Do NOT commit to main (you are on a feature branch)
- Do NOT force push
- Do NOT use `--no-verify`

## Safety Rules

- Before deleting any file: `cp` it to `/tmp/cc-backup-$(date +%s)/`
- Before modifying database schema: output `[DECISION_NEEDED] <your question>`
- Before deploying to any environment: output `[DECISION_NEEDED] <your question>`
- Do NOT modify `.env`, `.secrets`, credentials, or key files
- State your reason when installing new dependencies

## Wake Notifications (MUST follow)

After emitting `[DONE]`, `[ERROR]`, or `[DECISION_NEEDED]`, immediately run:
```
openclaw system event --text "task:<marker> <task-name>: <summary>" --mode now
```
This wakes the supervisor to process your marker promptly.
Note: requires HEARTBEAT.md to be non-empty in the OpenClaw workspace (see openclaw/openclaw#14527).

**Fallback**: If `openclaw system event` fails (command not found or error), create a marker file:
```
echo "<marker>:<task-name>:<summary>" > .supervisor/wake-marker
```
The supervisor checks this file during heartbeats.

## Worktree Rules

- Stay inside the worktree directory. Do NOT cd to parent repo or other worktrees.
- Do NOT read or write files under `~/.openclaw/`.
