# Provider Matrix — Help Center

Use this matrix to compare vendor platforms and custom builds with the same criteria.

## Quick Comparison

| Option | Best For | Strengths | Trade-offs |
|--------|----------|-----------|------------|
| Zendesk | Mid-large support teams | Mature ticketing, automations, marketplace | Higher cost, admin complexity |
| Freshdesk | Cost-sensitive teams | Fast onboarding, good core workflows | Less extensible for complex enterprise flows |
| Intercom | Product-led SaaS | Strong messenger integration, proactive support | Pricing can scale quickly with usage |
| Help Scout | Smaller service teams | Clean UX, lightweight operations | Fewer deep workflow automations |
| Jira Service Management | Engineering-heavy orgs | Native Jira linking, incident + support alignment | Steeper setup and terminology overhead |
| Custom stack | Unique workflows or sovereignty needs | Full control, flexible integrations, own data model | Highest implementation and maintenance effort |

## Scoring Grid

Score each option from 1 to 5 for each criterion:

| Criterion | Weight | Notes |
|-----------|--------|-------|
| Setup speed | 20% | Time to first stable launch |
| Operating cost | 20% | Licensing + maintenance burden |
| Workflow flexibility | 20% | Automation depth and routing options |
| Data control | 15% | Exportability and lock-in exposure |
| Analytics quality | 15% | Search/ticket insights and reporting depth |
| Team fit | 10% | Match with current staffing and skills |

Formula: `weighted_score = sum(score * weight)`.

## Decision Rule

- Pick the top score only if no blocking constraint exists.
- If two options are within 0.3 points, run a 30-day pilot instead of immediate full migration.
- Document rejected options and reasons in `memory.md`.
