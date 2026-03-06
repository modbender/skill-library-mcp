# Compaction Survival Guide

Context compaction is when OpenClaw summarises older conversation to save tokens. It preserves facts but loses tone, flow, and sometimes critical instructions. This is the #1 cause of "my agent forgot everything."

This guide covers what actually works to survive it.

---

## The Problem

When your context window fills up, OpenClaw compacts (summarises) older messages. What gets lost:
- Conversational tone and flow
- Instructions given mid-conversation ("don't touch that file")
- Nuance and reasoning behind decisions
- Safety rules that were only stated verbally, not written to files

What survives:
- Files in your workspace (AGENTS.md, MEMORY.md, etc.)
- Tool results and their outputs
- The compaction summary (facts, but not personality)

**The rule:** If it's not in a file, assume it will be lost.

---

## Fix 1: The Anchor File

Create `anchor.md` in your workspace root (template included in `assets/anchor.md`).

This is a tiny file (~300-500 tokens) containing your absolute non-negotiable rules, current constraints, and active projects. Your agent re-reads it before any risky action.

Add this to your AGENTS.md:
```
Before any external action (sending messages, running destructive commands, 
posting content), re-read anchor.md to confirm current constraints.
```

Why it works: Files are loaded fresh. They don't get compacted. The anchor acts as a safety net when conversation-based instructions get summarised away.

---

## Fix 2: Write It Down Immediately

When you tell your agent something important mid-conversation:

**Bad:** "Don't deploy to production this week"
(Lives only in conversation → will be compacted away)

**Good:** "Don't deploy to production this week — write this to anchor.md under Current Constraints"
(Now it's in a file → survives everything)

Train yourself to say "write that down" for anything that matters.

---

## Fix 3: Keep Files Lean

The more tokens your files consume, the less room for actual conversation before compaction kicks in.

**Targets:**
- AGENTS.md: under 150 lines
- SOUL.md: under 50 lines
- MEMORY.md: under 500 lines (prune regularly)
- anchor.md: under 30 lines
- Daily notes: archive anything older than 2 weeks

**Total workspace file budget:** aim for under 10K tokens loaded per session. Every token of file content is a token less of conversation before compaction.

---

## Fix 4: Structure AGENTS.md for Survival

Put the most critical instructions at the **top** of AGENTS.md, not buried in the middle. LLMs pay most attention to the beginning and end of context — the middle is an attention dead zone.

```markdown
# AGENTS.md

## CRITICAL (read first, always)
[Your most important rules here]

## Memory
[Memory protocols]

## Everything Else
[Less critical stuff]
```

---

## Fix 5: Use Memory Flush

OpenClaw has a built-in pre-compaction memory flush — before compaction happens, the agent is prompted to save important context to files. Make sure this is enabled (it is by default).

To support this, add to AGENTS.md:
```
When you sense context is getting large or before any session reset,
proactively save important recent context to memory/YYYY-MM-DD.md.
Don't wait to be asked.
```

---

## Fix 6: Session Resets Done Right

Before running `/new` or resetting a session:
1. Ask your agent to save current conversation state to today's daily note
2. Confirm anchor.md is up to date
3. Confirm MEMORY.md reflects any new long-term info
4. Then reset

After reset, your agent reads all workspace files on boot and picks up where it left off — minus the conversational flow, but with all the facts.

---

## What NOT to Do

- **Don't make MEMORY.md a dumping ground.** If it's 2000 lines of everything that ever happened, it's useless. Curate ruthlessly.
- **Don't rely on conversation for persistent instructions.** If you wouldn't write it on a post-it note on your monitor, don't expect your agent to remember it after compaction.
- **Don't panic about compaction.** It's a feature, not a bug. It keeps costs down. The goal is to make your important stuff survive it, not prevent it.
