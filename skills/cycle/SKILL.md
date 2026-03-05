---
name: Cycle
description: Design custom workflow cycles for any domain. Create structured, repeatable processes that become persistent skills.
---

## What is a Cycle?

A structured workflow optimized for a specific goal. Examples:
- **code** — Request → Plan → Execute → Verify → Deliver
- **research** — Question → Search → Synthesize → Report
- **content** — Idea → Draft → Critique → Refine → Publish

## When to Propose

- User repeats similar multi-step processes
- Current workflow has inefficiencies or skipped steps
- User asks "how should I approach X every time?"

## Design Process

1. **Goal** — What does this cycle produce? Be specific.
2. **Map** — How does user currently do it? Where do they get stuck?
3. **Phases** — 3-6 sequential steps with clear input/output each
4. **Handoffs** — Automatic, gated (needs user), or conditional
5. **Memory** — Preferences, patterns, things to avoid

Check `discovery.md` for questions to ask users when designing.

## Phase Structure

Each phase needs: clear input → output, validation before proceeding, can delegate to sub-agent.

Check `implementation.md` for how to structure cycle skills.

## Cycle vs Loop

| Cycle | Loop |
|-------|------|
| Different phases in sequence | Same action repeated |
| Produces complete output | Refines until criteria |
| Design once, use many times | Created per task |

They combine: cycles can use loops within phases. Check `examples.md` for cycle patterns.

---

**Related:** For iterating until success criteria are met (same action repeated), see the `loop` skill.
