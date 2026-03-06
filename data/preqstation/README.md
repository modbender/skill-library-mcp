# preqstation-openclaw

OpenClaw skill package for running `claude`, `codex`, or `gemini` CLI with a fixed execution template.

This repository is skill-only. It does not ship HTTP servers, webhook handlers, or messenger integration code.

## How to use

Just talk to OpenClaw in natural language.

You do not need to write fixed flags or a `preqstation:` prefix.

OpenClaw should use this skill when your request is about PREQSTATION task execution or running work in a mapped project.

If your message includes `preq` or `preqstation`, this skill should be prioritized.

## Execution mode

Worktree-first execution is the default.

- resolve `project_cwd` from user input or `MEMORY.md`
- create a per-task git worktree and use it as execution `<cwd>`
- launch engine commands with `pty:true` and explicit `workdir:<cwd>`
- use `background:true` only when asynchronous execution is needed
- monitor background sessions with `process action:poll` and `process action:log`

## Natural language examples

1. `Start PRJ-284 in the example project using Claude.`
2. `Use Codex to fix README command examples in the example project.`
3. `Use Gemini to draft notes for DOC-12 in the example project.`
4. `Update the example project path to /<absolute-path>/projects/example-project.`
5. `Implement API pagination and add tests in the example project.`
6. `What is currently running in OpenClaw sessions?`
7. `Show progress for session openclaw-claude-20260221-131240.`

## Engine selection rules

- explicit engine in message: use it (`claude`, `codex`, `gemini`)
- if omitted: default to `claude`

## Workspace path resolution

Execution needs two paths:

- `project_cwd`: primary checkout path
- `cwd`: per-task worktree path used for actual engine execution

Resolve in this order:

1. absolute path directly mentioned in message
2. project key from `MEMORY.md` (for example `example`)
3. task prefix key match in `MEMORY.md` (when available)

If path cannot be resolved, ask user for project key or absolute path.

After `project_cwd` is resolved, create task worktree `cwd`:

- default root: `${OPENCLAW_WORKTREE_ROOT:-/tmp/openclaw-worktrees}`
- branch naming: `codex/<project_key>/<task_or_purpose>`
- run all coding-agent commands inside this worktree `cwd` (never in primary checkout)

## MEMORY.md usage

`MEMORY.md` stores reusable project path mappings.

- keep keys short and stable
- use absolute paths only
- update this file through normal OpenClaw conversation when paths change

## Expected output

Success:

`completed: <task or N/A> via <engine> at <cwd>`

Failure:

`failed: <task or N/A> via <engine> at <cwd or N/A> - <short reason>`

## Background session controls

When using `background:true`, use process actions:

- `process action:list`
- `process action:poll sessionId:<id>`
- `process action:log sessionId:<id>`
- `process action:write sessionId:<id> data:"..."`
- `process action:submit sessionId:<id> data:"..."`
- `process action:kill sessionId:<id>` (only when required)

## ClawHub import

Use GitHub import with this repository URL:

`https://github.com/sonim1/preqstation-openclaw`

ClawHub should detect `SKILL.md` from repository root.

## Responsibility boundary

- OpenClaw: messenger routing, permissions, webhook/channel integration
- This repo: CLI execution instructions and prompt template only
