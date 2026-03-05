---
name: transcript-triage
description: "Parses long transcripts into topics under ordered lists, to triage in your notes system"
type: public
version: 0.1.0
status: published
dependencies: []
author: nonlinear
license: MIT
---

## Transcript Triage

**Parse AI conversation transcripts → numbered topics → groom into positions.**

### Flow

1. **Trigger:** User provides transcript (MD format)
2. **Parse:** AI extracts topics, decisions, action items
3. **Triage:** Classify by urgency/importance:
   - **NOW** - Current epic (immediate)
   - **LATER** - Future epics (planned)
   - **BACKLOG** - Ideas (someday/maybe)
   - **DECISIONS** - What was agreed (log)
4. **Groom:** User positions topics in correct places (ROADMAP, epic-notes, memory)

### Triggers

- "triage transcript"
- "parse conversation"
- "organize chat"
- "extract action items from [file/paste]"

### Output Format

```markdown
## Triage Results

### NOW (v1.1.0 Contract Diagram)
1. [Topic] - [Brief description]
2. [Topic] - [Brief description]

### LATER (Future Epics)
3. [Topic] - [Brief description]
4. [Topic] - [Brief description]

### BACKLOG (Ideas)
5. [Topic] - [Brief description]

### DECISIONS (Log to Memory)
- [Decision] - [Context]
- [Decision] - [Context]
```

### Integration Points

- **Backstage:** Auto-add NOW items to current epic-notes/
- **ROADMAP:** Suggest LATER items as new epics
- **Memory:** Log DECISIONS to memory/YYYY-MM-DD.md

---

## Notes

**Why this skill?**
- External AI chats (Claude, ChatGPT, etc.) generate valuable insights
- Transcripts are hard to parse manually
- Need systematic way to extract → classify → act

**Similar skills:**
- Backstage (epic management, checks)
- Roadmap (epic planning, grooming)
- Memory (decision logging)

**Unique value:**
- Bridges external conversations → internal workflow
- Automates triage (urgency + importance)
- Preserves context (decisions logged, not lost)
