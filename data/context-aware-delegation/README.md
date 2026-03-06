# Context-Aware Delegation
## (SmartBeat)

Give your isolated sessions (cron jobs, sub-agents, event handlers) full conversation context from your main session.

**SmartBeat** = Background tasks with a heartbeat *and* a brain.

## The Problem

Isolated sessions are cheap (use Haiku at ~$0.003/1K tokens) but blind — they can't see your main session conversation history. Running everything in main session is expensive (Sonnet at ~$0.03/1K tokens).

## The Solution

Use `sessions_history` tool to query main session from isolated sessions. Get Sonnet-level context awareness at Haiku prices.

**Cost savings:** ~10x cheaper than running in main session  
**Context:** Full conversation history  
**Use cases:** Morning reports, sub-agents, event handlers, periodic checks

## Quick Start

1. Read `SKILL.md` for complete documentation
2. Check `examples/` for ready-to-use patterns
3. Adapt to your needs

## Examples Included

- `morning-report-cron.json` - Daily 8 AM report with overnight work summary
- `sub-agent-with-context.sh` - Background tasks that understand your conversation

## Author

**RGBA Research**  
Applied Technology & Innovation  
https://rgbaresearch.com

## License

MIT — Free to use, adapt, and share
