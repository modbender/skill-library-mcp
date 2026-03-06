# Phone OpenClaw Skill

Focused OpenClaw skill for operating the CallMyCall API from chat.

Docs and portal:

- https://api.callmycall.com

## Install (local)

1. Clone or copy this repo into your OpenClaw skills folder.
2. Restart OpenClaw (or refresh skills) so it detects the new skill.

Common locations:

- `<workspace>/skills/openclaw-phone`
- `~/.openclaw/skills/openclaw-phone`

## Usage

Examples:

- "Call +46700000000 and confirm my appointment for Tuesday."
- "Show my recent calls."
- "End call 1."
- "Show results for call 2."

## Files

- `SKILL.md` — primary instructions and workflows
- `references/api.md` — API reference subset
- `examples/prompts.md` — example prompts and expected actions

## API Key

Key lookup order:

1. `CALLMYCALL_API_KEY` environment variable
2. `~/.openclaw/openclaw.json` at `skills.openclaw-phone.apiKey`
3. One-time user prompt, with confirmation before persisting to `~/.openclaw/openclaw.json`

The skill must not store API keys in skill source files or memory/state files.

## Notes

This skill is pull based. It does not rely on webhook callbacks; results are fetched on demand.

See also:

- `docs/auth-config.md` - credential handling details
- `docs/event-updates.md` - options for event-like updates with a pull API
