# Context & Prompts — Agentic Engineering

## Prompt Length

Modern agents (GPT-5, Claude) need less context than you think.

| Situation | Prompt Style |
|-----------|--------------|
| Clear task, familiar codebase | 1-2 sentences |
| New area or complex logic | Paragraph + screenshot |
| Architecture decision | Discussion mode |

## Screenshots Are Essential

50%+ of prompts should include screenshots:
```
1. Take screenshot (Cmd+Shift+4 on Mac)
2. Drag into terminal
3. Agent matches visual to code
```

Benefits:
- More precise than text descriptions
- Agent finds exact elements/strings
- Faster than explaining location

No annotation needed — agents are excellent at visual matching.

## Discussion Mode

For uncertain changes:
```
"Let's discuss before making changes"
"Give me options"
"What approaches would work here?"
```

Agent presents options, you choose, then execute.

## Queue Messages

When agent is working on task A and you have tasks B, C:
```
[Agent working on A...]
You: "Next: add loading state to submit button"
You: "Then: update error messages"
[Agent finishes A, starts B, then C]
```

Queue up related tasks. Agent works through them.

## Steering Mid-Work

If agent drifts:
1. Press Escape (stops thinking)
2. Enter to send redirect message
3. Agent adjusts course

Don't wait for wrong output. Steer early.

## Context Efficiency

Keep context clean:
- Don't waste on lengthy setup explanations
- Skip obvious instructions agent already knows
- Reference docs/files instead of pasting content

```
❌ "First, let me explain how our API works..."
✅ "Check src/api/README.md, then add new endpoint"
```

## AGENTS.md / CLAUDE.md

Keep concise. Agent files are scar tissue from lessons learned.

Good entries:
```markdown
## Patterns
- Use zod for validation
- Error responses: { error: string, code: number }
- Tests: colocate with source files

## Tools
- Logs: vercel cli or axiom
- DB: psql (see .env for connection)
```

Skip:
- Obvious instructions
- Long explanations
- Things model already knows

## Fresh Context vs. Continuing

| Situation | Action |
|-----------|--------|
| New feature, clean slate | Fresh context |
| Iteration on recent work | Continue session |
| Context getting long | Summarize key points, start fresh |
| Debugging same issue | Continue (history helps) |

GPT-5/Codex handles large context well. Don't restart prematurely.

## Recovery Phrases

When stuck:
```
"Take your time"
"Be comprehensive" 
"Read all related code first"
"Create possible hypotheses"
```

Trigger deeper thinking on hard problems.
