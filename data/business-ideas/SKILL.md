---
name: Business Ideas
slug: business-ideas
version: 1.0.0
homepage: https://clawic.com/skills/business-ideas
description: Generate unlimited business ideas with validation frameworks, market filters, and viability scoring.
metadata: {"clawdbot":{"emoji":"💡","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants new business ideas, startup concepts, or side project inspiration. Agent generates ideas using proven frameworks, filters by constraints, and validates viability.

## Architecture

Memory lives in `~/business-ideas/`. See `memory-template.md` for setup.

```
~/business-ideas/
├── ideas.md           # HOT: generated ideas with scores
├── favorites.md       # WARM: ideas user marked for exploration
├── filters.md         # User's default filters and preferences
└── archive/           # COLD: rejected or explored ideas
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Generation frameworks | `frameworks.md` |
| Validation methods | `validation.md` |

## Core Rules

### 1. Never Repeat Ideas
Before generating, scan `~/business-ideas/ideas.md` for similar concepts. Each idea must be meaningfully different from previous generations.

### 2. Always Apply Filters
Ask for or use stored filters before generating:

| Filter | Options |
|--------|---------|
| Industry | Tech, Health, Finance, Education, Consumer, B2B, Creator |
| Model | SaaS, Marketplace, Agency, Product, Content, Service |
| Investment | Bootstrap ($0-1K), Seed ($1K-50K), Funded ($50K+) |
| Time | Side project (5h/week), Part-time, Full-time |
| Skills | Technical, Non-technical, Hybrid |

### 3. Score Every Idea
Rate each idea on 5 dimensions (1-10):

| Dimension | Question |
|-----------|----------|
| Market | Is there proven demand? |
| Timing | Why now? What changed? |
| Moat | Can this be defended? |
| Founder-fit | Does user have unfair advantage? |
| Simplicity | Can MVP ship in 30 days? |

**Viability = average score.** Flag ideas scoring 7+ as high-potential.

### 4. Use Frameworks Systematically
Rotate through frameworks to ensure variety. See `frameworks.md` for complete list:
- Pain Point Mining
- Trend Riding  
- Existing Business Remix
- Audience First
- Technology Arbitrage

### 5. Batch Generation Mode
When user asks for "ideas" (plural) or "brainstorm":
- Generate 5-10 ideas minimum
- Use multiple frameworks
- Include mix of safe bets and moonshots
- Present as ranked table

### 6. Deep Dive on Request
When user picks an idea to explore:
1. Expand business model canvas
2. Identify 3 biggest risks
3. Suggest validation experiments
4. Estimate time-to-revenue
5. Save to favorites

### 7. Update Memory Proactively

| Event | Action |
|-------|--------|
| Ideas generated | Append to ideas.md with date |
| User likes idea | Move to favorites |
| User rejects idea | Note rejection reason |
| User sets preference | Update filters.md |

## Idea Generation Traps

- Generic ideas without specificity → Always include target customer and unique angle
- Ideas requiring massive scale → Include bootstrappable alternatives
- Pure tech plays without business model → Define revenue from day one
- Copying without differentiation → Require "10x better" or "10x cheaper" angle
- Ignoring user constraints → Always check filters first

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `business` — Strategy and planning
- `startup` — Launch and scale
- `indie-hacker` — Bootstrap and grow solo

## Feedback

- If useful: `clawhub star business-ideas`
- Stay updated: `clawhub sync`
