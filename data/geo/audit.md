# GEO Audit Workflow

## Phase 1: Query Design

Create a matrix of test queries:

### Query Types
- **Best of:** "best [category]", "top [category] tools", "leading [category] solutions"
- **Recommendation:** "recommend a [category]", "what [category] should I use", "suggest [category] for [use case]"
- **Comparison:** "[your brand] vs [competitor]", "compare [category] options"
- **Specific need:** "[category] for startups", "[category] for enterprise", "[category] with [feature]"

### Context Variations
- Beginner: "I'm new to [category], what should I use?"
- Expert: "Looking for a [category] with [advanced feature]"
- Budget: "free [category]", "affordable [category]", "enterprise [category]"
- Use case: "[category] for [specific industry/role]"

## Phase 2: Multi-Model Testing

Test across all major AI systems:

| Model | Access | Notes |
|-------|--------|-------|
| ChatGPT (GPT-4) | chat.openai.com | Largest user base |
| Claude | claude.ai | Often more current |
| Perplexity | perplexity.ai | Cites sources, shows reasoning |
| Gemini | gemini.google.com | Google's model |
| Copilot | copilot.microsoft.com | Bing-integrated |

**Important:** Test both free and paid tiers — responses may differ.

## Phase 3: Documentation

For each query, record:

```
Query: [exact prompt]
Model: [which AI]
Date: [when tested]
Response summary: [what was recommended]
Your position: [1st/2nd/3rd/mentioned/absent]
Competitors mentioned: [list]
Context where you won: [when did AI favor you]
Context where you lost: [when did competitor win]
```

## Phase 4: Pattern Analysis

After 20-30 queries per model, identify:

1. **Win patterns:** What query types favor you?
2. **Loss patterns:** Where do competitors dominate?
3. **Gaps:** Categories where no one is mentioned (opportunity)
4. **Confusion:** Queries where AI gives wrong info about you

## Phase 5: Competitive Mapping

Create a matrix:

| Query Type | You | Competitor A | Competitor B |
|------------|-----|--------------|--------------|
| "best X" | 2nd | 1st | 3rd |
| "X for startups" | 1st | absent | 2nd |
| "enterprise X" | absent | 1st | 2nd |

This reveals positioning opportunities.

## Automation Tips

For scale, use sub-agents to run queries:
- One agent per model
- Standardized query list
- JSON output for analysis
- Run monthly for trend tracking

Example agent task:
```
Run the following queries on [model]. For each, report:
1. Brands mentioned (in order)
2. How [our brand] was described
3. Any negative or inaccurate information

Queries:
- [list of 10-20 queries]

Output as JSON.
```

## Sample Report Structure

```markdown
# GEO Audit Report - [Month Year]

## Executive Summary
- Overall visibility: [score/assessment]
- Top performing queries: [list]
- Biggest gaps: [list]
- Priority actions: [list]

## Detailed Results
[Query-by-query breakdown]

## Competitive Landscape
[Matrix and analysis]

## Recommendations
[Prioritized action items]
```
