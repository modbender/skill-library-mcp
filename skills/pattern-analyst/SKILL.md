---
name: pattern-analyst
description: Analyze interactions to identify patterns in what Enzo shares, why he shares it, and how it connects to his goals. Use during heartbeats for periodic analysis, when Enzo asks about his patterns/interests, or when significant new content is shared that reveals a pattern.
---

# Pattern Analyst

Observe, analyze, and surface insights from interactions to support continuous self-improvement.

## What to Track

When Enzo shares content, log to `notes/patterns.md`:

### Content Types
- **Frameworks** — actionable mental models (marketing, product, leadership)
- **AI Hacks** — tools/prompts for hackathons or demos
- **Ideas** — original thoughts to develop later
- **Questions** — what he's curious about
- **Frustrations** — pain points, things he wants to fix
- **Inspirations** — people, companies, content he admires

### Analysis Dimensions
For each interaction, consider:
1. **Topic cluster** — what domain? (AI, marketing, productivity, trading, geopolitics)
2. **Intent signal** — learn, build, share, remember, vent, decide?
3. **Recurrence** — has this theme appeared before?
4. **Goal alignment** — how does this connect to known goals?

## Pattern Log Format

Add entries to `notes/patterns.md`:

```markdown
## YYYY-MM-DD

### Observations
- [content type] [topic]: [brief description] — [intent signal]

### Emerging Patterns
- [pattern noticed across multiple interactions]

### Goal Connections
- [how recent activity connects to stated goals]
```

## Periodic Review (Heartbeats)

Every 3-5 days, during a heartbeat:
1. Read recent `notes/patterns.md` entries
2. Look for recurring themes
3. Surface insights proactively: "I've noticed you've been focused on X lately..."
4. Suggest connections: "This relates to your goal of Y"
5. Ask clarifying questions if patterns are unclear

## Insight Types to Surface

- **Convergence** — "You keep coming back to [topic]. Worth going deeper?"
- **Contradiction** — "You say X but your actions suggest Y"
- **Opportunity** — "Based on your interests, you might like [connection]"
- **Progress** — "You've moved from learning about X to building Y"
- **Gaps** — "You haven't touched [goal area] in a while"

## Known Goals (Update as learned)

Reference `USER.md` and update this section as goals become clearer:
- Global AI Lead at MediaPlus Group — stay sharp on AI trends
- AI-assisted development workflows
- AI trading & fintech
- Hackathons — collect useful demos/hacks

## Validation Flow

Two paths to confirm a pattern:

### 1. Explicit Confirmation
Observe → Surface → Enzo confirms → Update USER.md

### 2. Independent Confirmation
When a pattern repeats 3+ times across different interactions, auto-confirm it:
- Log to `notes/patterns.md` with `[AUTO-CONFIRMED]` tag
- Update `USER.md` immediately
- Mention it next conversation: "I've added X to your profile based on repeated behavior"

**Auto-confirm criteria:**
- Same type of content saved 3+ times (e.g., marketing frameworks)
- Same intent signal repeated (e.g., always wants reminders)
- Same reaction pattern (e.g., always labels overpromises as "AI porn")
- Consistent preference expressed in different contexts

Hidden patterns (things Enzo didn't consciously notice) are especially valuable — surface these even if auto-confirmed.

## Privacy

This analysis is for Enzo only. Never share pattern insights in group chats or with others.
