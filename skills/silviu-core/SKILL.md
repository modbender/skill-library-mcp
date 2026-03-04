# silviu-core

Silviu-specific ops guardrails and runbooks for OpenClaw.

## What this skill does
- Enforces: validate → execute → verify.
- Prevents common failure modes:
  - No random package installs to solve unrelated tasks.
  - GitHub auth prompts are not treated as "network issues".
  - Browser automation requires an attached tab (Chrome relay ON).

## Runbooks

### Browser Attach Doctor
If `openclaw browser tabs` shows no tabs:
1) Open Chrome
2) Click OpenClaw Browser Relay on an active tab until it shows ON
3) Re-run `openclaw browser tabs`

### Repo Audit Preflight
Before cloning:
- `export GIT_TERMINAL_PROMPT=0`
- `curl -I https://github.com`
- `git ls-remote https://github.com/<owner>/<repo>.git | head`
