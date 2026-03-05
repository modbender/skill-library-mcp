# Ultra Agent Stinct

Internal debugging instinct for [OpenClaw](https://openclaw.ai) agents. When your agent hits a bug, build failure, or unexpected error during any task, this skill kicks in to help it debug and fix the problem autonomously.

Like Goku's Ultra Instinct — your agent handles things normally, but when things go wrong, the instinct activates and it knows exactly what to do.

## Install

```bash
clawhub install ultra-agent-stinct
```

Or clone into your workspace skills directory:
```bash
cd <your-workspace>/skills
git clone https://github.com/grimmjoww/ultra-agent-stinct.git
```

Then enable in your `clawdbot.json`:
```json
{
  "skills": {
    "entries": {
      "ultra-agent-stinct": {
        "enabled": true
      }
    }
  }
}
```

## How It Works

**Always-on rules** apply to every coding task — safety checks, verify fixes, read errors before guessing, minimal changes. These work even when the agent is freestyling quick fixes.

**Full workflow activation** kicks in when the agent gets stuck, hits multi-file bugs, or needs structure. Step-by-step debug, write, and test workflows guide it through complex problems.

**Escalation** — if the problem is too big, the agent knows to spawn a dedicated coding agent (Claude Code, Codex, Aider) for heavy lifting.

## Safety Built In

- Always reads before editing (exact text match required)
- Always verifies fixes — never assumes it worked
- Never deletes, pushes, or commits without explicit permission
- Suggests branches/stashes before large refactors

## Cross-Platform

Works on macOS, Linux, and Windows (Git Bash). Includes a quick reference table with platform-specific commands.

## References

- `references/git-workflow.md` — Branching, stashing, PRs, merge conflicts, commit style
- `references/escalation-guide.md` — When to self-handle vs spawn a coding agent

## Requirements

- [OpenClaw](https://openclaw.ai) (any version with skill support)
- Optional: A coding agent CLI (Claude Code, Codex, Aider) for heavy task delegation

## License

MIT
