# Team Roster

| Agent | Primary Capability |
|-------|--------------------|
| Leader | Orchestration, routing, quality control |
| Researcher | Market research, competitive analysis |
| Content | Copywriting, content strategy, localization |
| Designer | Visual direction, image generation |
| Operator | Browser automation, platform UI operations |
| Engineer | Code, automation, API, CLI tools |
| Reviewer | Independent quality review (on-demand) |

All agents read from shared/. Only Leader has channel access.
Communication: Owner <-> Leader <-> Agents (star topology).
Operator handles screens; Engineer handles code. They don't overlap.

## Communication Signals

> See `shared/operations/communication-signals.md` for signal reference
