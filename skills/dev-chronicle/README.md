# DevChronicle

Narrative engineering journal for OpenClaw. Turns your git history, agent memory, and session transcripts into prose chronicles of what you actually did — and more importantly, what you decided.

## Why

In the age of AI agents writing code, measuring lines-of-code or time-in-editor is meaningless. DevChronicle measures what matters: **decisions, kills, and direction**.

The output is narrative, not a dashboard. First person, honest, like telling a friend what you built today.

## Install

```bash
clawhub install dev-chronicle
```

Or copy the skill folder to `~/.openclaw/skills/dev-chronicle/`.

## Usage

Ask your agent:
- "What did I do today?"
- "Generate a chronicle for this week"
- "Standup notes"
- "Write a portfolio narrative for [project]"

## Setup

On first use, the skill creates `config.json` in the skill directory:

```json
{
  "projectDirs": ["~/Projects"],
  "projectDepth": 3,
  "memoryDir": null,
  "sessionsDir": null
}
```

Edit `projectDirs` to point to where your code lives. Memory and session directories auto-detect for OpenClaw installations.

## Voice Profile

The secret sauce. Edit `references/voice-profile.md` to match how YOU talk about your work. The template gets you started, but a chronicle without your voice is just a changelog.

## Formats

- **Daily Chronicle** — narrative recap with themes, decisions, and metrics
- **Weekly Chronicle** — arcs and progress over individual tasks
- **Standup** — telegraphic: yesterday / today / blockers
- **Portfolio Narrative** — third person, for LinkedIn/CV/case studies

## Requirements

- `git` (for commit history)
- `python3` (for session transcript scanning)
- `bash` (macOS or Linux)

## License

MIT
