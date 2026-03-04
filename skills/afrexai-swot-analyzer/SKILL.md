# SWOT Analyzer

Run a structured SWOT analysis for any business, product, or strategic decision.

## Trigger
User asks for a SWOT analysis, competitive assessment, or strategic evaluation.

## Instructions

1. **Gather context** — Ask for (or infer from conversation):
   - Business/product name
   - Industry or market
   - Specific decision or initiative (optional)
   - Key competitors (optional)

2. **Research** — If web_search is available, look up:
   - Recent industry trends and market conditions
   - Competitor moves and positioning
   - Regulatory or macro factors

3. **Build the SWOT matrix**:

### Strengths (Internal, Positive)
- What advantages does this business/product have?
- What do they do better than competitors?
- What unique resources or capabilities exist?

### Weaknesses (Internal, Negative)
- Where are the gaps in capability or resources?
- What do competitors do better?
- What limitations exist (team, tech, capital)?

### Opportunities (External, Positive)
- What market trends favor this business?
- What underserved segments or needs exist?
- What partnerships or channels are untapped?

### Threats (External, Negative)
- What competitive pressures are increasing?
- What regulatory, economic, or tech shifts pose risk?
- What could disrupt the current model?

4. **Score each item** — Rate impact (1-5) and likelihood (1-5). Calculate priority = impact × likelihood.

5. **Strategic recommendations**:
   - **SO strategies** (use Strengths to capture Opportunities)
   - **WO strategies** (address Weaknesses to unlock Opportunities)
   - **ST strategies** (use Strengths to mitigate Threats)
   - **WT strategies** (address Weaknesses to reduce Threat exposure)

6. **Output format**:

```
## SWOT Analysis: [Business/Product]

### Strengths
| # | Factor | Impact | Likelihood | Priority |
|---|--------|--------|------------|----------|
| 1 | ...    | 4      | 5          | 20       |

### Weaknesses
(same format)

### Opportunities
(same format)

### Threats
(same format)

### Strategic Moves
1. **[SO] ...** — leverage X strength to capture Y opportunity
2. **[WO] ...** — fix X weakness to unlock Y opportunity
3. **[ST] ...** — use X strength to defend against Y threat
4. **[WT] ...** — shore up X weakness before Y threat materializes

### Bottom Line
One paragraph: what's the single most important strategic move right now and why.
```

## Tips
- Be specific, not generic. "Strong brand" is weak. "73% unaided brand recall in target demo" is strong.
- Challenge assumptions. If the user says "no weaknesses," push back.
- Prioritize ruthlessly. 3 high-priority items beat 15 medium ones.
- Time-bound where possible. "Opportunity window closes Q3 2026" is actionable.
