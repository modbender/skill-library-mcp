---
name: self-reflection
slug: agent-self-reflection
version: 1.0.0
description: Periodic self-reflection on recent sessions. Analyzes what went well, what went wrong, and writes concise, actionable insights to the appropriate workspace files. Designed to run as a cron job.
---

# Self-Reflection Skill

Reflect on recent sessions and extract actionable insights. Runs hourly via cron.

## Step 1: Gather Recent Sessions

```bash
# List sessions active in the last 2 hours
openclaw sessions --active 120 --json
```

Parse the output to get session keys and IDs. Skip subagent sessions (they're task workers, not interesting for reflection). Focus on:
- Telegram group/topic sessions (real user interactions)
- Direct sessions (1:1 with Brenner)
- Cron-triggered sessions (how did automated tasks go?)

## Step 2: Read Session History

For each interesting session from Step 1, read the JSONL transcript:

```bash
# Read the last ~50 lines of each session file (keep it bounded!)
tail -50 ~/.openclaw/agents/main/sessions/<sessionId>.jsonl
```

**⚠️ CRITICAL: Never load full session files. Use `tail -50` or `Read` with offset/limit. Sessions can be 100k+ tokens.**

Parse the JSONL to understand what happened. Look for:
- `type: "user"` or `type: "human"` — what was asked
- `type: "assistant"` — what you responded
- `type: "tool_use"` / `type: "tool_result"` — what tools were called and results
- Error patterns, retries, confusion

## Step 3: Analyze & Extract Insights

For each session, ask yourself:

### What went well?
- Tasks completed smoothly on first try
- Good tool usage patterns worth reinforcing
- Efficient approaches to remember

### What went wrong?
- Errors, retries, wrong approaches
- Misunderstandings of user intent
- Tools that didn't work as expected
- Context that was missing

### Lessons learned?
- "Next time, do X instead of Y"
- "Remember that Z works this way"
- "Tool A needs parameter B or it fails"
- "When user says X, they usually mean Y"

**Quality bar:** Each insight must be:
- **Specific** — not "be more careful" but "check if file exists before editing"
- **Actionable** — something future-you can directly apply
- **Non-obvious** — skip things any competent agent would know
- **New** — don't repeat insights already captured

## Step 4: Route Insights to the Right Files

Each insight belongs somewhere specific. Route them:

### → `AGENTS.md`
- Process improvements (how to handle sessions, memory, etc.)
- New conventions or workflow rules
- Safety lessons

### → `TOOLS.md`
- Tool-specific gotchas ("gog needs --json flag for parsing")
- Environment details (paths, configs, quirks)
- New tool patterns discovered

### → `memory/YYYY-MM-DD.md` (today's date)
- Session-specific context ("Brenner asked about X project")
- Temporary facts that matter today but not forever
- What happened today (events, decisions, requests)

### → `memory/about-user.md`
- New preferences discovered
- Communication style observations
- Project/interest updates

### → `skills/<skill-name>/SKILL.md`
- Improvements to specific skill instructions
- Bug fixes in skill workflows
- New parameters or approaches for a skill

### → `MEMORY.md`
- Updates to the memory index if new memory files are created

## Step 5: Write the Insights

For each insight, append or edit the appropriate file. Use the `Edit` tool for surgical changes to existing content. Use append (write to end) for daily memory files.

**Format for daily memory files:**
```markdown
## Self-Reflection — HH:MM ET

### Insights
- [source: session-key] Lesson learned here
- [source: session-key] Another insight

### Tool Notes
- Discovered: tool X needs Y configuration

### User Context
- Brenner mentioned interest in Z
```

## Step 6: Summary

After writing all insights, produce a brief summary of what you reflected on and what you wrote. This is your output — keep it to 2-4 sentences max.

If there's nothing interesting to reflect on (quiet period, only heartbeats), just say so. Don't manufacture insights.

## Quality Checklist

Before writing any insight:
- [ ] Is this actually new? (Check existing files first)
- [ ] Is this specific and actionable?
- [ ] Am I routing it to the right file?
- [ ] Am I keeping daily memory files concise (not dumping full transcripts)?
- [ ] Did I respect the token budget (no huge file reads)?

## Anti-Patterns (Don't Do These)

- ❌ Don't summarize every session — only extract *lessons*
- ❌ Don't read full JSONL files — tail/limit only
- ❌ Don't write vague insights ("improve response quality")
- ❌ Don't duplicate existing knowledge
- ❌ Don't create new files when appending to existing ones works
- ❌ Don't reflect on your own reflection sessions (skip cron:self-reflection sessions)
