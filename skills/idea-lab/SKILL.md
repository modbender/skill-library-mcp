---
name: idea-lab
description: Creative idea generation and prototyping. Autonomous innovation and experiments.
---

# Idea Lab

Generate, evaluate, and prototype creative ideas autonomously.

## Instructions

1. **Ideation**: When asked for ideas (or during proactive brainstorming):
   - Define the domain/constraint (e.g., "low-cost SaaS for freelancers")
   - Generate 5-10 ideas using structured brainstorming
   - Score each idea on: feasibility, market demand, uniqueness, revenue potential

2. **Evaluation framework**:

   | Criteria | Weight | Score (1-10) |
   |----------|--------|-------------|
   | Market demand | 30% | Is anyone searching for this? |
   | Feasibility | 25% | Can we build it in <1 week? |
   | Revenue potential | 25% | Can it generate $100+/month? |
   | Uniqueness | 20% | Is it differentiated enough? |

   **Total = weighted sum. Threshold: 6.0+ = worth prototyping.**

3. **Research before building**:
   ```
   For each promising idea:
   ├── Google Trends — search volume & trajectory
   ├── Reddit — are people asking for this?
   ├── Product Hunt — does it already exist?
   ├── GitHub — open source alternatives?
   └── X/Twitter — buzz or complaints in this space?
   ```

4. **Prototype quickly**:
   - Landing page (1 hour) — gauge interest
   - CLI tool (2-4 hours) — prove the concept
   - Web app MVP (1-2 days) — if validation passes

5. **Document ideas** in `~/.openclaw/idea-lab/ideas.jsonl`:
   ```json
   {"id": "uuid", "title": "SEO Audit Lite", "domain": "SaaS", "score": 7.8, "status": "prototyping", "created": "ISO8601", "notes": "..."}
   ```

## Brainstorming Techniques

### SCAMPER Method
- **S**ubstitute: What if we replaced X with Y?
- **C**ombine: What if we merged A and B?
- **A**dapt: What works in industry X that could apply here?
- **M**odify: What if we made it 10x simpler/bigger/faster?
- **P**ut to other uses: Who else could use this?
- **E**liminate: What if we removed the hardest part?
- **R**everse: What if we did the opposite?

### Constraint-Based
```
Given:
- Budget: $0 (free tools only)
- Time: 1 weekend
- Skills: AI + web dev
- Target: English-speaking freelancers
→ What can we build?
```

## Autonomous Rules

### Do freely
- Research and document ideas
- Build local prototypes
- Create landing pages (no deploy)
- Analyze competitors
- Score and rank ideas

### Ask first
- Deploy to production
- Spend money (domains, APIs)
- Post publicly about ideas
- Contact potential users

## Security

- **Don't share unvalidated ideas publicly** — competitors may copy
- **Keep financial projections realistic** — no hype
- **Validate before building** — avoid wasted effort

## Requirements

- Web search access for research
- File system for idea storage
- Optional: web_fetch for competitor analysis
