# clawfi

Install the ClawFi skill so your agent knows how to call the ClawFi API. The skill is installed into every supported platform present on your machine (Cursor, Claude Code, and Codex).

## Supported platforms

The skill runs on these AI coding agents:

- **Cursor** — [Cursor](https://cursor.com) IDE. The skill is loaded from `~/.cursor/skills/clawfi/SKILL.md` and lets the Cursor agent read/write ClawFi context, observations, and signals.
- **Claude Code** — [Claude Code](https://claude.com/code) (Anthropic’s Claude in VS Code / JetBrains). The skill is loaded from `~/.claude/skills/clawfi/SKILL.md` so the agent can call the ClawFi API.
- **Codex** — [Codex](https://codex.com) (OpenAI’s coding agent). The skill is loaded from `$CODEX_HOME/skills/clawfi/SKILL.md` (default `~/.codex/skills/clawfi/SKILL.md`).

After install, restart the agent so it picks up the skill.

## Usage

```bash
npx clawfi@latest install clawfi
```

This writes the ClawFi skill to each platform’s skills directory:

- **Cursor:** `~/.cursor/skills/clawfi/SKILL.md`
- **Claude Code:** `~/.claude/skills/clawfi/SKILL.md`
- **Codex:** `$CODEX_HOME/skills/clawfi/SKILL.md` (defaults to `~/.codex`)

Restart your agent after installing.

## Publishing

From this directory:

```bash
npm publish
```

Publish the first time (and when you want the website’s `npx clawfi@latest install clawfi` to use the new version).
