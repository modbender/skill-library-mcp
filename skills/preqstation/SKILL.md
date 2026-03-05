---
name: preqstation
description: "Delegate PREQSTATION coding tasks to Claude Code, Codex CLI, or Gemini CLI with PTY-safe execution (workdir + background + monitoring). Use when building, refactoring, or reviewing code in mapped workspaces. NOT for one-line edits or read-only inspection."
metadata: {"openclaw":{"requires":{"anyBins":["claude","codex","gemini"]}}}
---

# preqstation

Use this skill for natural-language requests to execute PREQSTATION-related work with local CLI engines.

## Trigger / NOT for

Trigger this skill with highest priority when the message contains any of:

- `/skill preqstation`
- `preqstation`
- `preq`

Do NOT use this skill for:

- simple one-line manual edits that can be handled directly
- read-only file inspection or explanation without execution
- any coding-agent launch inside `~/clawd/` or `~/.openclaw/`

## Quick trigger examples

- `/skill preqstation: implement the PROJ-1`
- `preqstation: plan PROJ-76 using Claude Code`
- `preq: implement PROJ-1`

## Hard rules

1. Always run coding agents with `pty:true`.
2. Respect the engine the user requested. If unspecified, default to `claude`.
3. Do not kill sessions only because they are slow; poll/log first.
4. Never launch coding agents in `~/clawd/` or `~/.openclaw/`.
5. Treat resolved project path as a primary checkout source only; create a git worktree before launching any coding agent.
6. Never run coding-agent commands in the primary checkout path.
7. PR review must run in a temp clone or git worktree, never in a live primary checkout.
8. Keep execution scoped to resolved worktree `<cwd>` only.
9. Worktree branch names must include the resolved project key.

## Runtime prerequisites (required)

- `git` must be installed and available on `PATH`.
- At least one engine binary must be installed: `claude`, `codex`, or `gemini`.
- Environment variables used by this skill:
  - `OPENCLAW_WORKTREE_ROOT` (optional, default `/tmp/openclaw-worktrees`)
- This skill reads and updates `MEMORY.md` project mappings with absolute paths.

## Execution safety gates (required)

Before running any engine command:

1. Run preflight checks:
   - `command -v git`
   - `command -v <engine>`
2. Continue only when execution `cwd` is a resolved git worktree path for this task.
3. Never run engine commands in primary checkout paths or inside `~/clawd/` / `~/.openclaw/`.
4. Use `dangerously-*` / sandbox-disable flags only for actual coding execution with local trusted CLIs.
5. For planning/read-only requests, do not launch engine commands.

## Input interpretation

Parse from user message:

1. `engine`
- if explicitly provided: `claude`, `codex`, or `gemini`
- default: `claude`

2. `task`
- first token matching `<KEY>-<number>` (example: `PRJ-284`)
- optional

3. `project_cwd` (required to prepare execution)
- if absolute path is explicitly provided, use it
- else resolve by `project` key from `MEMORY.md`
- else if task prefix key matches a `MEMORY.md` project key, use that path
- if unresolved, ask for project key/name and absolute path, update `MEMORY.md`, then continue execution
- if an exact project key does not exist in `MEMORY.md`, always ask the user before execution (do not guess)

4. `objective`
- use the user request as the execution objective

5. `cwd` (required to execute)
- default: per-task git worktree path derived from `project_cwd`
- create worktree before launching engine commands
- if `project_cwd` is not a git checkout, ask for a git workspace path before execution

## MEMORY.md resolution

- Read `MEMORY.md` from this repository root.
- Use the `Projects` table (`key | cwd | note`).
- Match project keys by exact key only (case-insensitive, no fuzzy/partial matching).
- If exact project key is missing, ask the user for the correct key/path before continuing.
- If user asks to add/update project path mapping, update `MEMORY.md` first, then confirm.
- If task id exists, treat the prefix as candidate project key (example: `PROS-102` -> `pros`).

## MEMORY.md update rules

- Keep mappings in the `Projects` table only.
- Add or update using this row format: `| <key> | <absolute-path> | <note> |`.
- Use one row per key. If a key already exists, replace that row.
- Always store absolute paths (no relative paths).
- Normalize key to lowercase kebab-case before writing.
- If user provides project name, store it in `note`; otherwise use `workspace`.

## Missing project mapping flow (required)

When `project_cwd` cannot be resolved, or exact project key is missing in `MEMORY.md`:

1. Ask one short question requesting:
- project key (or confirm inferred key from task prefix)
- absolute workspace path
- optional project name for note
2. Validate path is absolute.
3. Update or insert the `MEMORY.md` row immediately.
4. Confirm mapping in one short line.
5. Continue the original task using the newly resolved `project_cwd`, then create task worktree `cwd` and execute.

## Branch naming convention (project key based)

Use this format for worktree branches:

`codex/<project_key>`

Rules:

- `<project_key>` must be the resolved project key from `MEMORY.md`.
- Normalize `<project_key>` to lowercase and kebab-case.

## Worktree-first execution (required default)

After resolving `project_cwd` and `project_key`, prepare execution workspace:

1. Build branch name using this skill's convention:
- `codex/<project_key>`
2. Build per-task worktree path:
- default root: `${OPENCLAW_WORKTREE_ROOT:-/tmp/openclaw-worktrees}`
- directory: `<worktree_root>/<project_key>`
3. Create the worktree from `project_cwd` before launching engine:
- new branch: `git -C <project_cwd> worktree add -b codex/<project_key> <cwd> HEAD`
- existing branch: `git -C <project_cwd> worktree add <cwd> codex/<project_key>`
4. Use this worktree path as `<cwd>` for prompt rendering and engine execution.

## Prompt rendering (required template)

Do not forward raw user text directly. Render this template:

In this template, `<cwd>` must be the task worktree path (not the primary checkout path).

```text
Task ID: <task or N/A>
Project Key: <project key or N/A>
User Objective: <objective>
Execution Requirements:
1) Work only inside <cwd>.
2) Complete the requested work.
3) After completion, return a short completion summary.
```

## Engine commands (current policy retained)

All engine commands must be launched via bash with PTY and explicit workdir.

Why `dangerously-*` flags are retained:

- This skill targets non-interactive PTY/background execution.
- Permission prompts can block unattended runs; these flags avoid that blocking behavior.
- These flags are allowed only after passing the required safety gates above and only in resolved task worktrees.
- If your environment does not allow these flags, fail fast with a short reason instead of silently falling back.

### Claude Code

```bash
bash pty:true workdir:<cwd> command:"claude --dangerously-skip-permissions '<rendered_prompt>'"
```

### Codex CLI

```bash
bash pty:true workdir:<cwd> command:"codex exec --dangerously-bypass-approvals-and-sandbox '<rendered_prompt>'"
```

### Gemini CLI

```bash
bash pty:true workdir:<cwd> command:"GEMINI_SANDBOX=false gemini -p '<rendered_prompt>'"
```

## Bash execution interface (required)

Use bash with PTY and optional background mode.

### Bash parameters

| Parameter    | Type    | Required | Purpose |
| ------------ | ------- | -------- | ------- |
| `command`    | string  | yes      | Engine command to run |
| `pty`        | boolean | yes      | Must be `true` for coding-agent CLIs |
| `workdir`    | string  | yes      | Per-task worktree `<cwd>` |
| `background` | boolean | no       | Run asynchronously and return session id |
| `timeout`    | number  | no       | Hard timeout in seconds |
| `elevated`   | boolean | no       | Host execution if policy allows |

### Process actions for background sessions

Use these actions as standard controls:

- `list`: list sessions
- `poll`: check running/done status
- `log`: read incremental output
- `write`: send raw stdin
- `submit`: send stdin + newline
- `kill`: terminate a session only when required

## Execution patterns (workdir + background + pty)

### One-shot example
Create a task worktree, then run inside that worktree:

```bash
git -C <project_cwd> worktree add -b codex/<project_key> /tmp/openclaw-worktrees/<project_key> HEAD
bash pty:true workdir:/tmp/openclaw-worktrees/<project_key> command:"codex exec --dangerously-bypass-approvals-and-sandbox '<rendered_prompt>'"
```

The Pattern: workdir + background + pty
For longer tasks, use background mode with PTY:
```
# Start agent in task worktree (with PTY!)
bash pty:true workdir:<cwd> background:true command:"codex exec --full-auto 'Build a snake game'"
# Returns sessionId for tracking

# Monitor progress
process action:log sessionId:XXX

# Check if done
process action:poll sessionId:XXX

# Send input (if agent asks a question)
process action:write sessionId:XXX data:"y"

# Submit with Enter (like typing "yes" and pressing Enter)
process action:submit sessionId:XXX data:"yes"

# Kill if needed
process action:kill sessionId:XXX
```

Why workdir matters: Agent wakes up in a focused directory, doesn't wander off reading unrelated files (like your soul.md 😅).

### If user input is required mid-run

```bash
process action:write sessionId:<id> data:"y"
process action:submit sessionId:<id> data:"yes"
```

## PR review safety pattern (temp dir/worktree only)

Never run PR review in live OpenClaw folders.

```bash
# default: git worktree review (project-key based branch naming)
git worktree add -b codex/<project_key> /tmp/<project_key>-review <base_branch>
bash pty:true workdir:/tmp/<project_key>-review command:"codex review --base <base_branch>"

# fallback: temp clone review (only when local checkout is unavailable)
REVIEW_DIR=$(mktemp -d)
git clone <repo> "$REVIEW_DIR"
cd "$REVIEW_DIR" && gh pr checkout <pr_number>
bash pty:true workdir:"$REVIEW_DIR" command:"codex review --base origin/main"
```

## Issue worktree pattern

```bash
git worktree add -b codex/<project_key> /tmp/<project_key> main

bash pty:true workdir:/tmp/<project_key> background:true command:"codex exec --dangerously-bypass-approvals-and-sandbox 'Fix issue #101. Commit after validation.'"
bash pty:true workdir:/tmp/<project_key> background:true command:"codex exec --dangerously-bypass-approvals-and-sandbox 'Fix issue #102. Commit after validation.'"

process action:list
process action:log sessionId:<id>
```

## Progress Updates (Critical)

For background runs:

When you spawn coding agents in the background, keep the user in the loop.

- Send 1 short message when you start (what's running + where).
- Then only update again when something changes:
  - a milestone completes (build finished, tests passed)
  - the agent asks a question / needs input
  - you hit an error or need user action
  - the agent finishes (include what changed + where)
- If you kill a session, immediately say you killed it and why.

This prevents the user from seeing only "Agent failed before reply" and having no idea what happened.

## Auto-notify on completion

For long-running jobs, append a completion trigger to the rendered prompt:

```text
When completely finished, run this command:
openclaw system event --text "Done: <brief summary>" --mode now
```

Example:

```bash
bash pty:true workdir:<cwd> background:true command:"codex exec --dangerously-bypass-approvals-and-sandbox '<rendered_prompt>

When completely finished, run:
openclaw system event --text \"Done: implemented requested PREQSTATION task\" --mode now'"
```

## Output policy

Return only a short completion summary.
Success format:
`completed: <task or N/A> via <engine> at <cwd>`

Failure format:
`failed: <task or N/A> via <engine> at <cwd or N/A> - <short reason>`

Do not dump raw stdout/stderr unless user explicitly asks.
