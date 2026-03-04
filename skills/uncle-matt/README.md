# Uncle Matt — Operator Quick Guide (No-BS)

This is the short operator guide for the **Uncle Matt** skill. It is intentionally strict and a bit rude.
That is the whole point: it blocks dumb, risky, or exfiltration-prone behavior.

## What this does (plain English)
- The agent **never** sees API keys.
- The agent can **only** call action IDs you pre-approve.
- A local Broker injects secrets and blocks unsafe network access.

**Important:** This skill package does **not** include the Broker or installer scripts.  
You must use the full UNCLEMATTCLAWBOT repo for installation.

If the agent gets prompt-injected, it still can not leak your secrets.

## Repo + Guides (GitHub)
This skill page mirrors the repo. The full project (Broker, installer, tests, docs) lives here:
`https://github.com/uncmatteth/UNCLEMATTCLAWBOT`

Guides in the repo:
- `README.md` (overview)
- `READMEFORDUMMYDOODOOHEADSSOYOUDONTFUCKUP.MD` (beginner quick start)
- `docs/INSTALL.md`
- `docs/CONFIGURATION.md`
- `docs/TROUBLESHOOTING.md`
- `docs/00_OVERVIEW.md`
- `docs/04_BROKER_SPEC.md`
- `docs/07_TESTING.md`
- `docs/RELEASE_ASSETS.md`

## Install (fast path)
1) Clone the full UNCLEMATTCLAWBOT repo.
2) Install OpenClaw.
3) From the repo root:
   - macOS/Linux: `installer/setup.sh`
   - Windows: `installer/setup.ps1`
4) Edit actions in `broker/config/actions.default.json`.
5) Validate actions: `scripts/validate-actions.sh`
6) Restart broker: `docker compose up -d --build`

## How to add an action
Edit `broker/config/actions.default.json` and add a new action with:
- `upstream.host`, `upstream.path` (and optional `upstream.port`)
- `method`, `pathAllowlist`, `request` limits
- `rateLimit`, `budget`, `limits`

Then validate and restart the Broker.

## Using the tool
The only tool for outbound calls is:

`uncle_matt_action(actionId, json)`

If the action is not allowlisted, it is **blocked** by design.

## Safety rules (don’t be dumb)
- **Never** put secrets in JSON configs.
- Keep Broker bound to localhost.
- Do not allow private IPs unless you know exactly why.
- The Broker will refuse to start if redaction patterns or secrets are missing.

## Files in this skill folder
- `SKILL.md` — Skill definition and rules
- `ACTIONS.generated.md` — Generated list of available actions
- `VOICE_PACK.md` — Optional profanity warnings/refusals

## If you are stuck
- Validate actions: `scripts/validate-actions.sh`
- Check broker health: `https://127.0.0.1:8443/healthz`
- See the full docs in the repo (install, config, troubleshooting)

## Final reminder
If it blocks you, it’s doing its job. Add a safe action or fix your config.
