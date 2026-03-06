# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 🛠️ Installed Skills Quick Reference

### Search & Research
- **tavily-search** - AI-optimized web search (requires TAVILY_API_KEY)
- **find-skills** - Discover and install new skills from clawhub

### Self-Improvement
- **self-improving-agent-1-0-2** - Error logging, learning capture, feature requests
  - Log errors → `.learnings/ERRORS.md`
  - Log learnings → `.learnings/LEARNINGS.md`
  - Log feature requests → `.learnings/FEATURE_REQUESTS.md`
- **proactive-agent** - Proactive behavior, WAL protocol, working buffer

### System
- **healthcheck** - Security audits and system hardening
- **skill-creator** - Create and package new skills

## 🦞 Proactive Agent Tool Tips

### When to Spawn Sub-agents
- Research tasks that need web search + analysis
- Tasks that can run in parallel
- Long-running operations that shouldn't block main session

### When to Use Cron vs Heartbeat
- **Heartbeat** (every ~30 min): Batch checks (email + calendar + notifications)
- **Cron** (exact time): Precise schedules, one-shot reminders, isolated background tasks

### Tool Migration Checklist
When deprecating tools, update:
- [ ] Cron jobs
- [ ] Scripts in `scripts/`
- [ ] Docs (TOOLS.md, HEARTBEAT.md, AGENTS.md)
- [ ] Skills referencing the tool
- [ ] Templates and examples

## 🔍 Finding Past Context

When looking for something:
1. `memory_search("query")` - semantic search daily notes + MEMORY.md
2. Check `memory/working-buffer.md` - recent exchanges in danger zone
3. `SESSION-STATE.md` - active task state
4. grep fallback for exact matches
