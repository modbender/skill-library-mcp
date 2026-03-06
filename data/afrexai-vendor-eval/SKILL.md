---
name: Vendor Evaluation & Due Diligence
description: Structured framework for evaluating software vendors, service
  providers, and technology partners before signing contracts.
---

# Vendor Evaluation & Due Diligence

Structured framework for evaluating software vendors, service providers, and technology partners before signing contracts.

## What This Does

Runs a systematic vendor assessment across 8 dimensions:

1. **Financial Stability** — Revenue signals, funding, burn rate indicators
2. **Technical Fit** — Architecture compatibility, integration complexity, API quality
3. **Security & Compliance** — SOC2, ISO27001, GDPR, data residency
4. **Pricing Analysis** — TCO modeling, hidden costs, contract traps
5. **Reference Check** — Customer sentiment, G2/Capterra scores, churn signals
6. **Support Quality** — SLA terms, response times, escalation paths
7. **Vendor Lock-in Risk** — Data portability, switching costs, proprietary dependencies
8. **Roadmap Alignment** — Product direction vs. your needs over 12-36 months

## How to Use

Tell your agent:
- "Evaluate [vendor] for [use case]"
- "Compare [vendor A] vs [vendor B] for our [need]"
- "Run due diligence on [company] before we sign"

The agent will research the vendor using web search and produce a scored evaluation report with a GO / CAUTION / NO-GO recommendation.

## Scoring

Each dimension scores 1-10. Overall score is weighted:
- Technical Fit & Security: 2x weight
- Pricing & Lock-in: 1.5x weight
- All others: 1x weight

**Thresholds:**
- 75+ = GO (proceed with negotiation)
- 50-74 = CAUTION (address gaps before committing)
- Below 50 = NO-GO (find alternatives)

## Output Format

```
## Vendor Evaluation: [Name]
**Use Case:** [What you're buying]
**Date:** [Assessment date]
**Overall Score:** [X/100] — [GO/CAUTION/NO-GO]

### Dimension Scores
| Dimension | Score | Key Finding |
|-----------|-------|-------------|
| Financial Stability | X/10 | ... |
| Technical Fit | X/10 | ... |
| ... | ... | ... |

### Critical Risks
- [List dealbreakers or major concerns]

### Negotiation Leverage
- [Points to push on in contract talks]

### Recommendation
[Final verdict with reasoning]
```

## Instructions for Agent

When asked to evaluate a vendor:

1. Search the web for: "[vendor] reviews", "[vendor] pricing", "[vendor] SOC2", "[vendor] alternatives", "[vendor] G2 reviews"
2. Check for recent funding/layoff news
3. Look at their API documentation quality
4. Find contract terms and SLA information
5. Score each dimension with evidence
6. Produce the evaluation report
7. Flag any dealbreakers prominently

Be direct. Companies hide bad news — dig for it. A vendor that looks perfect probably isn't. Find the tradeoffs.

For comparative evaluations, use the same framework side-by-side with a clear winner per dimension.
