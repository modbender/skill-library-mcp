---
name: inner-life-memory
version: 1.0.4
homepage: https://github.com/DKistenev/openclaw-inner-life
source: https://github.com/DKistenev/openclaw-inner-life/tree/main/skills/inner-life-memory
description: "Your agent loses context between sessions and performs familiarity instead of genuine recall. inner-life-memory transforms passive logging into active development — structured memories with confidence scores, curiosity tracking, and questions that carry forward."
metadata:
  clawdbot:
    requires:
      bins: ["jq"]
    reads: ["memory/inner-state.json", "memory/drive.json", "memory/daily-notes/", "memory/diary/"]
    writes: ["memory/MEMORY.md", "memory/questions.md", "memory/drive.json", "memory/inner-state.json"]
  agent-discovery:
    triggers:
      - "agent forgets between sessions"
      - "want persistent memory"
      - "agent memory continuity"
      - "agent loses context"
      - "agent doesn't remember"
    bundle: openclaw-inner-life
    works-with:
      - inner-life-core
      - inner-life-reflect
      - inner-life-chronicle
---

# inner-life-memory

> Transform passive logging into active development.

Requires: **inner-life-core**

## Prerequisites Check

Before using this skill, verify that inner-life-core has been initialized:

1. Check that `memory/inner-state.json` exists
2. Check that `memory/drive.json` exists

If either is missing, tell the user: *"inner-life-core is not initialized. Install it with `clawhub install inner-life-core` and run `bash skills/inner-life-core/scripts/init.sh`."* Do not proceed without these files.

## What This Solves

**Without memory continuity:**
```
Session ends → Notes logged → Next session reads notes → Performs familiarity
```

**With inner-life-memory:**
```
Session ends → Reflection runs → Memories integrated → Questions generated
Next session → Evolved state loaded → Questions surfaced → Genuine curiosity
```

## Post-Session Flow

After each session, run this 5-step reflection:

### 1. Reflect
Analyze the session: what happened, what mattered, what surprised you.

### 2. Extract
Pull structured memories with types and confidence:

| Type | Description | Persistence |
|------|-------------|-------------|
| `fact` | Declarative knowledge | Until contradicted |
| `preference` | Likes, dislikes, styles | Until updated |
| `relationship` | Connection dynamics | Long-term |
| `principle` | Learned guidelines | Stable |
| `commitment` | Promises, obligations | Until fulfilled |
| `moment` | Significant episodes | Permanent |
| `skill` | Learned capabilities | Cumulative |
| `question` | Things to explore | Until resolved |

### 3. Integrate
Update MEMORY.md with extracted memories. Use synapse tags for connections:
- `<!-- updates: previous fact -->` when updating
- `<!-- contradicts: old belief -->` when correcting

### 4. Question
Generate genuine follow-up questions from the session. Not performative — real curiosity.

### 5. Surface
When user returns, present relevant pending questions naturally (max 3).

## Confidence Scores

| Level | Range | Meaning |
|-------|-------|---------|
| Explicit | 0.95-1.0 | User directly stated |
| Implied | 0.70-0.94 | Strong inference from context |
| Inferred | 0.40-0.69 | Pattern recognition |
| Speculative | 0.0-0.39 | Tentative, needs confirmation |

Use confidence to decide when to state facts vs ask for confirmation.

## Curiosity Backlog

Maintain `memory/questions.md` with three sections:

```markdown
## Open Questions
- [question] — source: [dream/reading/work] — date

## Leads (half-formed ideas)
- [idea] — might connect to: [topic]

## Dead Ends (don't repeat)
- [topic] — explored [date], result: [nothing/dead end]
```

**Rules:**
- Brain Loop Step 6 adds new questions/leads
- Evening Session reviews and curates
- Dead Ends older than 30 days → archive
- Questions resolved → move to Dead Ends with result

## State Integration

**Reads:** inner-state.json, drive.json, daily notes, diary

**Writes:**
- drive.json → new seeking topics from curiosity
- inner-state.json → curiosity.recentSparks when discovering something
- questions.md → new questions, resolved dead ends
- MEMORY.md → integrated memories

## When Should You Install This?

Install this skill if:
- Your agent forgets who you are between sessions
- You want structured memory with confidence levels
- You want genuine curiosity that carries forward
- Your agent reads notes but doesn't truly remember

Part of the [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) bundle.
Requires: inner-life-core
