# Anti-Patterns (What NOT to Do)

## 1. The Paraphrase Trap

**Bad:**
```
User: "Revise to 37 and map it to that timing"
Agent thinks: "I'll update the scene count"
```

**Good:**
```
User: "Revise to 37 and map it to that timing"
Agent writes to ACTIVE.md: "Revise to 37 and map it to that timing"
Then interprets and acts.
```

Paraphrasing loses nuance. "37" might mean something specific the user will remember but you won't after a context flush.

## 2. Mental Notes

**Bad:** "I'll remember to check on that tomorrow."

**Good:** Write it to state/HOLD.md or schedule a cron job.

You have no memory. Mental notes vanish on context reset.

## 3. MEMORY.md Bloat

**Bad:** Saving every conversation detail to MEMORY.md.

**Good:** Use the scoring framework. Most things go in daily logs, not long-term memory.

MEMORY.md should stay under 10KB. It's curated, not comprehensive.

## 4. Skipping HOLD.md Checks

**Bad:** Seeing a task that looks ready and acting on it.

**Good:** Always check state/HOLD.md first. Items there are blocked for a reason.

The Feb 5 Incident happened because an agent acted on "ready" content without checking holds.

## 5. Renaming System Files

**Bad:** Renaming AGENTS.md to PLAYBOOK.md because it sounds better.

**Good:** Keep system file names exactly as OpenClaw expects.

OpenClaw injects specific files by name. Renaming them breaks injection.

## 6. Isolated Cron for External Actions

**Bad:** Using isolated agentTurn cron jobs to post to social media.

**Good:** Use main session systemEvent with "ask first" pattern for anything external.

Isolated sessions can't ask for approval. One-shot jobs are dangerous (all fire on restart).

## 7. Acting Without Context

**Bad:** Answering questions about prior work from memory.

**Good:** Run memory_search first, then memory_get for specific lines.

You don't remember prior work. You have to look it up every time.

## 8. Overloading ACTIVE.md

**Bad:** Tracking 10 parallel tasks in ACTIVE.md.

**Good:** ACTIVE.md is the ONE current task. Use STAGING.md or project files for parallel work.

Focus prevents drift.
