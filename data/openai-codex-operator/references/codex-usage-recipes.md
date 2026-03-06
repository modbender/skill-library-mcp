# Codex usage recipes in OpenClaw

## 1) Quick implementation

- Tool: `exec`
- Params:
  - `pty:true`
  - `workdir:/path/to/repo`
  - `command:"codex exec \"Implement X and add tests\""`

## 2) Code review pass

- Tool: `exec`
- Params:
  - `pty:true`
  - `workdir:/path/to/repo`
  - `command:"codex exec \"Review current changes and list critical issues\""`

## 3) Long task with monitoring

- Start:
  - `exec(background:true, pty:true, workdir, command:"codex exec \"...\"")`
- Monitor:
  - `process list`
  - `process poll <sessionId>`
  - `process log <sessionId>`
- Interact:
  - `process submit <sessionId> "yes"`
- Stop if needed:
  - `process kill <sessionId>`

## Common failures

- `codex: command not found`
  - Install: `npm i -g @openai/codex`
- auth/login errors
  - Re-run `codex` and complete login flow (ChatGPT account or API key).
- wrong repo modified
  - Ensure `exec.workdir` points to intended project.
