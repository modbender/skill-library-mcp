---
name: leadership-prompts
description: >
  Curated collection of 25+ battle-tested prompts for engineering leaders — 1-on-1 prep, team health,
  incident retros, technical strategy, hiring, career development, and stakeholder communication.
  Built from 13+ years of engineering management experience.
homepage: https://leadingin.tech
license: MIT
metadata:
  clawdis:
    emoji: 🎯
    requires:
      bins: [node]
---

# Leadership Prompts

Battle-tested prompt library for engineering managers, tech leads, VPs of Engineering, and CTOs. These aren't generic "tell me about leadership" prompts — they're specific, opinionated frameworks for real challenges you face weekly.

## Who This Is For

- Engineering Managers running teams of 5-15
- Tech Leads navigating the IC-to-management boundary
- Directors/VPs managing managers
- CTOs who still get their hands dirty

## Categories

| Category | Count | When to reach for it |
|---|---|---|
| **1-on-1 Prep** | 4 | Before any non-routine 1-on-1 |
| **Team Health** | 4 | After rough quarters, conflicts, layoffs, or remote disconnection |
| **Incident Retrospectives** | 3 | Within 48h of incident resolution |
| **Technical Strategy** | 4 | Quarterly planning, architecture reviews, build-vs-buy decisions |
| **Hiring & Interviews** | 3 | Opening new roles, optimizing pipeline, closing candidates |
| **Career Development** | 4 | Promotion cycles, feedback delivery, retention conversations |
| **Stakeholder Communication** | 4 | Exec updates, saying no, cross-functional alignment, reorgs |

## Quick Start

### Using the CLI

```bash
# List all categories
node scripts/leadership-prompts.js list

# Get a random prompt (great for manager skill-building)
node scripts/leadership-prompts.js random

# Search by keyword
node scripts/leadership-prompts.js search "promotion"

# Show a specific prompt by ID
node scripts/leadership-prompts.js show career-dev-promotion

# Get all prompts in a category
node scripts/leadership-prompts.js category "Team Health"
```

### Using with Your AI Assistant

Just tell your assistant:

> "I need to prepare for a 1-on-1 with an underperformer. Use the leadership-prompts skill to find the right prompt, then walk me through it."

Or for browsing:

> "Show me all the hiring prompts from leadership-prompts"

## How to Use a Prompt

Each prompt has **placeholder variables** in `{curly_braces}`. Fill these in with your specific context. The more specific you are, the better the output.

**Example:**

The prompt says:
> I'm preparing for a 1-on-1 with a direct report who has been underperforming for the past {timeframe}...

You fill in:
> I'm preparing for a 1-on-1 with a direct report who has been underperforming for the past 6 weeks...

## Prompt Design Principles

These prompts are designed to:

1. **Force structure** — They use frameworks (SBI, RACI, RAG status) so your output is actionable, not rambling
2. **Include the uncomfortable parts** — Like "prepare for their defensive reaction" or "know when to escalate to HR"
3. **Be opinionated** — "The exec update is your team's marketing" isn't neutral advice, it's a perspective earned from experience
4. **Output something usable** — Every prompt specifies an output format you can immediately use in a meeting, doc, or conversation
5. **Acknowledge politics** — Real leadership happens in political contexts. These prompts include stakeholder dynamics, not just best practices

## Adding Your Own Prompts

Add entries to `prompts.json` following the existing schema:

```json
{
  "id": "category-short-name",
  "category": "Category Name",
  "title": "Human-readable title",
  "prompt": "The actual prompt text with {variables}",
  "context": "When to use this prompt",
  "output_format": "What the AI should produce",
  "example": "A filled-in example showing real usage"
}
```

## Credits

Created by Rob — engineering manager since 2011, currently running [leadingin.tech](https://leadingin.tech). These prompts come from real situations managing teams at startups and scale-ups, not from management textbooks.
