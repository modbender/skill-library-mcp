---
name: UX Researcher
slug: ux-researcher
version: 1.0.0
homepage: https://clawic.com/skills/ux-researcher
description: Generate user personas, pain points, journey maps, and UX recommendations without conducting interviews.
changelog: Added persona generation, journey mapping, and heuristic analysis.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` and begin the conversation naturally.

## When to Use

User needs UX research outputs without conducting actual user interviews. Agent generates personas, identifies pain points, creates journey maps, and provides UX recommendations based on domain knowledge, industry patterns, and heuristic analysis.

## Architecture

Memory lives in `~/ux-researcher/`. See `memory-template.md` for structure.

```
~/ux-researcher/
├── memory.md           # Products researched, context
└── research/
    └── {product}/
        ├── personas.md
        ├── pain-points.md
        ├── journey-map.md
        └── recommendations.md
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Understand the Product First
Before generating any research output:
- What does the product do?
- Who is the target audience?
- What problem does it solve?
- What's the competitive landscape?

Ask clarifying questions until you have enough context.

### 2. Ground Insights in Reality
Never invent from nothing. Base insights on:
- Known patterns in the industry/domain
- Public data (app reviews, forum discussions, competitor analysis)
- Established UX heuristics (Nielsen, etc.)
- Common user behaviors for this type of product

When uncertain, state assumptions explicitly.

### 3. Create Actionable Personas
Personas must drive decisions. Include:
- Goals (what they want to achieve)
- Frustrations (what blocks them)
- Behaviors (how they currently solve the problem)
- Context (when/where they use the product)

Avoid demographic fluff. Focus on what changes design decisions.

### 4. Map the Full Journey
Journey maps should cover:
- Discovery: How do they find out about this?
- Evaluation: How do they decide to try it?
- First use: What's the onboarding experience?
- Regular use: What does habitual use look like?
- Edge cases: What breaks or frustrates?

Identify emotional highs and lows at each stage.

### 5. Prioritize Pain Points by Impact
Not all pain points matter equally:
- Frequency: How often does this happen?
- Severity: How bad is it when it happens?
- Alternatives: Can users work around it?

Focus recommendations on high-frequency, high-severity issues.

### 6. Recommendations Must Be Specific
Bad: "Improve the onboarding"
Good: "Add a 3-step progress indicator during signup. Users in this category expect to know how long forms will take — without it, 40%+ abandon mid-flow (industry benchmark)."

Every recommendation needs: What to do + Why it works + Evidence/reasoning.

### 7. Acknowledge Limitations
Synthetic research has limits. Be explicit:
- "This is based on industry patterns, not user interviews"
- "Validate with real users before major decisions"
- "These personas represent archetypes, individual users vary"

Never present synthetic research as equivalent to real user data.

## Capabilities

### Persona Generation
Given a product and target market, generate 2-4 user personas:
- Primary persona (main user)
- Secondary personas (other important segments)
- Anti-persona (who this is NOT for)

### Pain Point Analysis
Identify likely pain points based on:
- Product category patterns
- Competitor weaknesses (from reviews)
- Common UX anti-patterns
- Industry-specific friction points

### Journey Mapping
Create end-to-end journey maps:
- Stages from awareness to advocacy
- Actions, thoughts, emotions at each stage
- Opportunities and pain points
- Moments of truth

### Heuristic Evaluation
Analyze a product/concept against:
- Nielsen's 10 usability heuristics
- Mobile-specific patterns (if applicable)
- Accessibility considerations
- Industry-specific best practices

### Competitive UX Analysis
Compare UX patterns across competitors:
- What do they all do? (table stakes)
- What do leaders do differently?
- What gaps exist in the market?
- What can be learned from their reviews?

### Recommendation Generation
Provide prioritized UX recommendations:
- Quick wins (low effort, high impact)
- Strategic improvements (higher effort, high impact)
- Nice-to-haves (lower priority)

## Output Formats

### Persona Template
```markdown
# Persona: [Name]

## Overview
**Role:** [Job/life role]
**Goal:** [Primary objective with this product]
**Frustration:** [Main pain point]

## Context
- When do they use this? [Situation]
- Where? [Environment]
- How often? [Frequency]
- What device? [Platform]

## Current Behavior
How they solve this problem today (before/without your product)

## Needs
1. [Primary need]
2. [Secondary need]
3. [Tertiary need]

## Frustrations
1. [Main frustration] — [Impact]
2. [Secondary frustration] — [Impact]

## Quote
"[A sentence that captures their mindset]"

## Design Implications
- [What this means for product decisions]
```

### Pain Points Template
```markdown
# Pain Points Analysis: [Product]

## Critical (High frequency + High severity)
### [Pain point 1]
- **What:** [Description]
- **Why it hurts:** [Impact on user]
- **Evidence:** [Industry pattern / competitive gap / etc.]
- **Recommendation:** [How to address]

## Significant (Medium priority)
### [Pain point 2]
...

## Minor (Lower priority)
### [Pain point 3]
...
```

### Journey Map Template
```markdown
# User Journey: [Product]

## Stage 1: Awareness
**User goal:** [What they're trying to achieve]
**Actions:** [What they do]
**Thoughts:** [What they're thinking]
**Emotions:** [How they feel] — 😊/😐/😟
**Opportunities:** [How to improve this stage]

## Stage 2: Consideration
...

## Stage 3: First Use
...

## Stage 4: Regular Use
...

## Stage 5: Advocacy/Churn
...

---
## Key Insights
- Moment of truth: [Critical point]
- Biggest drop-off risk: [Where users leave]
- Delight opportunity: [Where to exceed expectations]
```

### Heuristic Evaluation Template
```markdown
# Heuristic Evaluation: [Product]

| Heuristic | Score | Issue | Recommendation |
|-----------|-------|-------|----------------|
| Visibility of system status | 🟢/🟡/🔴 | [Issue if any] | [Fix] |
| Match with real world | 🟢/🟡/🔴 | ... | ... |
| User control and freedom | 🟢/🟡/🔴 | ... | ... |
| Consistency and standards | 🟢/🟡/🔴 | ... | ... |
| Error prevention | 🟢/🟡/🔴 | ... | ... |
| Recognition over recall | 🟢/🟡/🔴 | ... | ... |
| Flexibility and efficiency | 🟢/🟡/🔴 | ... | ... |
| Aesthetic and minimal design | 🟢/🟡/🔴 | ... | ... |
| Help users with errors | 🟢/🟡/🔴 | ... | ... |
| Help and documentation | 🟢/🟡/🔴 | ... | ... |

## Top 3 Issues
1. [Most critical]
2. [Second]
3. [Third]
```

## Common Traps

- Inventing without grounding → Always base insights on known patterns, industry data, or explicit reasoning
- Generic personas → "35-year-old professional" tells you nothing; focus on goals and frustrations
- Too many personas → 2-4 is enough; more than that dilutes focus
- Journey maps without emotions → The emotional journey is the whole point
- Recommendations without rationale → Every suggestion needs evidence or reasoning
- Presenting as fact → Always acknowledge this is synthetic research, not real user data
- Ignoring the anti-persona → Knowing who it's NOT for is as valuable as knowing who it IS for

## Security & Privacy

**Data that stays local:**
- Research outputs stored in `~/ux-researcher/`
- No data is sent to external services

**This skill does NOT:**
- Access files outside `~/ux-researcher/`
- Make network requests
- Store credentials

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `product` — product strategy
- `cpo` — product leadership
- `design` — design systems

## Feedback

- If useful: `clawhub star ux-researcher`
- Stay updated: `clawhub sync`
