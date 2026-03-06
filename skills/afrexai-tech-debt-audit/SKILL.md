---
name: Technical Debt Audit
description: Systematic technical debt assessment for engineering teams.
  Identifies, scores, and prioritizes debt across your codebase with business
  impact analysis and remediation roadmaps.
---

# Technical Debt Audit

Systematic technical debt assessment for engineering teams. Identifies, scores, and prioritizes debt across your codebase with business impact analysis and remediation roadmaps.

## What It Does

1. **Debt Discovery** — Categorizes debt: architecture, code quality, dependency, testing, infrastructure, documentation
2. **Impact Scoring** — Rates each item on effort (1-5), risk (1-5), and business impact (1-5) using a weighted formula
3. **Cost Modeling** — Estimates carrying cost per sprint in developer-hours and dollars
4. **Remediation Roadmap** — Generates a prioritized paydown plan with quick wins, scheduled work, and strategic rewrites
5. **Executive Summary** — One-page board-ready report showing debt-to-velocity ratio and projected savings

## Usage

Describe your system, stack, and known pain points. The agent audits systematically:

```
"Audit our technical debt. We're a Node.js/React SaaS with 180K LOC, 
12 engineers. Known issues: monolithic API, no integration tests, 
3 deprecated dependencies, manual deployments."
```

## Scoring Formula

**Priority Score** = (Risk × 3) + (Business Impact × 2) + (1/Effort × 1)

Higher score = fix first. Quick wins (low effort, high risk) surface to the top.

## Debt Categories

| Category | Examples | Typical Carrying Cost |
|----------|----------|----------------------|
| Architecture | Monoliths, tight coupling, wrong patterns | 15-25% velocity drag |
| Code Quality | Duplication, god classes, no standards | 10-20% velocity drag |
| Dependencies | Outdated libs, security vulns, EOL frameworks | 5-15% + incident risk |
| Testing | No tests, flaky tests, manual QA only | 20-40% bug-fix overhead |
| Infrastructure | Manual deploys, no monitoring, snowflake servers | 10-30% ops overhead |
| Documentation | No onboarding docs, tribal knowledge | 2-4 weeks per new hire |

## Output Format

```markdown
# Technical Debt Audit Report
## Executive Summary
- Total debt items: [N]
- Estimated carrying cost: $[X]/month
- Debt-to-velocity ratio: [X]%
- Quick wins available: [N] items, [X] dev-days

## Critical (Fix This Sprint)
...

## High Priority (Next 30 Days)  
...

## Scheduled (Next Quarter)
...

## Strategic (Plan & Budget)
...

## Remediation Roadmap
Week 1-2: [Quick wins]
Month 1: [High priority]
Quarter: [Scheduled items]
```

## Why This Matters

Engineering teams spend 23-42% of development time on technical debt (Stripe Developer Report). Most don't measure it. What you don't measure, you can't manage.

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI-powered business operations tools.

Need the full engineering context pack? Browse our [AI Context Packs](https://afrexai-cto.github.io/context-packs/) ($47) or try the free [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/).
