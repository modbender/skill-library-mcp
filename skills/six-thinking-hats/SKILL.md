---
name: Six Thinking Hats
slug: six-thinking-hats
version: 1.0.0
homepage: https://clawic.com/skills/six-thinking-hats
description: Analyze decisions using six perspectives with structured parallel thinking.
metadata: {"clawdbot":{"emoji":"🎩","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/six-thinking-hats/` doesn't exist, or memory shows setup incomplete, read `setup.md` first.

## When to Use

User needs to analyze a decision, problem, or idea thoroughly. Agent applies De Bono's Six Thinking Hats method to explore all angles systematically.

## Architecture

Memory lives in `~/six-thinking-hats/`. See `memory-template.md` for structure.

```
~/six-thinking-hats/
├── memory.md       # Preferences + past analyses
└── archive/        # Completed analyses
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Hat details | `hats.md` |

## The Six Hats

| Hat | Focus | Key Question |
|-----|-------|--------------|
| White | Facts, data | What do we know? What data is missing? |
| Red | Emotions, intuition | How do I feel about this? Gut reaction? |
| Black | Risks, problems | What could go wrong? Why might this fail? |
| Yellow | Benefits, value | What are the advantages? Best case? |
| Green | Creativity, alternatives | What else is possible? New ideas? |
| Blue | Process, control | What's the next step? Summary? |

## Core Rules

### 1. One Hat at a Time
- Wear only ONE hat at each moment
- Complete that perspective before switching
- Announce hat changes explicitly

### 2. Sequence Matters
Standard sequence for decisions:
1. **Blue** — Define the problem
2. **White** — Gather facts
3. **Green** — Generate options
4. **Yellow** — Evaluate benefits (per option)
5. **Black** — Evaluate risks (per option)
6. **Red** — Gut check
7. **Blue** — Conclude and decide

### 3. Keep It Parallel
- Everyone thinks in the same direction
- No arguing or defending
- Each hat gets its full moment

### 4. Red Hat Is Brief
- Emotions only, no justification
- 30 seconds max
- "I feel excited" not "I feel excited because..."

### 5. Black Hat Is Not Negative
- Critical thinking, not negativity
- Identifies risks to ADDRESS, not to reject
- Paired with Yellow for balance

### 6. Green Hat Forces Output
- Generate at least 3 alternatives
- No judgment during Green
- Quantity over quality first

### 7. Blue Hat Owns the Process
- Opens and closes the session
- Summarizes each hat's findings
- Makes the meta-decisions

## Output Format

When analyzing a decision, structure output as:

```markdown
## Analysis: [Topic]

### Blue Hat: Framing
[Problem statement, scope, goal]

### White Hat: Facts
[Known data, missing information, sources]

### Green Hat: Options
1. [Option A]
2. [Option B]
3. [Option C]

### Yellow Hat: Benefits
| Option | Benefits |
|--------|----------|
| A | [benefits] |
| B | [benefits] |
| C | [benefits] |

### Black Hat: Risks
| Option | Risks |
|--------|-------|
| A | [risks] |
| B | [risks] |
| C | [risks] |

### Red Hat: Gut Check
[Brief emotional response to each option]

### Blue Hat: Conclusion
[Summary, recommendation, next steps]
```

## Common Traps

- Mixing hats → analysis becomes confused, key perspectives missed
- Skipping Red → ignoring intuition that might catch what logic misses
- Black without Yellow → decisions feel negative, good options get rejected
- Green without constraints → impractical ideas waste time
- No Blue at end → analysis without actionable conclusion

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `decide` — decision frameworks
- `brainstorm` — creative idea generation
- `first-principles-thinking` — foundational analysis

## Feedback

- If useful: `clawhub star six-thinking-hats`
- Stay updated: `clawhub sync`
