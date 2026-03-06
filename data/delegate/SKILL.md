---
name: Delegate
description: Route tasks to sub-agents with optimal model selection, error recovery, and result verification.
---

## Core Rule

Spawn cost < task cost → delegate. Otherwise, do it yourself.

## Model Tiers

| Tier | Models | Cost | Use for |
|------|--------|------|---------|
| Small | Haiku, GPT-4o-mini, Gemini Flash | ~$0.25/1M | Search, summarize, format, classify |
| Medium | Sonnet, GPT-4o, Gemini Pro | ~$3/1M | Code, analysis, synthesis |
| Large | Opus, o1, Gemini Ultra | ~$15/1M | Architecture, complex reasoning |

**Rule of thumb:** Start with smallest tier. Escalate only if output quality insufficient.

## Spawn Checklist

Every spawn must include:
```
1. TASK: Single clear deliverable (not "help with X")
2. MODEL: Explicit tier choice
3. CONTEXT: Only files/info needed (never full history)
4. OUTPUT: Expected format ("return JSON with...", "write to file X")
5. DONE: How to signal completion
```

Check `templates.md` for copy-paste spawn templates.

## Error Recovery

| Error Type | Action |
|------------|--------|
| Sub-agent timeout (>5 min no response) | Kill and retry once |
| Wrong output format | Retry with stricter instructions |
| Task too complex for tier | Escalate: Small→Medium→Large |
| Repeated failures (3x) | Abort, report to user |

Check `errors.md` for recovery patterns and escalation logic.

## Verification

Never trust "done" without checking:
- **Code:** Run tests, check syntax
- **Files:** Verify they exist and have content
- **Data:** Spot-check 2-3 items
- **Research:** Confirm sources exist

## Don't Delegate

- Quick tasks (<30 seconds to do yourself)
- Tasks needing conversation context
- Anything requiring user clarification mid-task
