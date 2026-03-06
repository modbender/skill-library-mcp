---
name: opportunity-scout
description: >
  Find profitable business opportunities in any niche by scanning Twitter, web, Reddit,
  and Product Hunt for unmet needs and pain points. Scores each opportunity on Demand,
  Competition, Feasibility, and Monetization (1-5 each, max 20). Generates a ranked report
  with actionable recommendations. Use when asked to find business ideas, market gaps,
  product opportunities, or "what should I build" questions. Also triggers on: market research,
  niche analysis, opportunity hunting, trend scouting, competitive analysis for new products.
---

# AI Opportunity Scout

Find what people need → evaluate if you can build it → decide if it's worth it.

## Quick Start

When the user specifies a niche (e.g. "AI agents", "crypto trading", "SaaS tools"):

1. Run the scout pipeline below
2. Score each finding with `scripts/scout.py`
3. Present the ranked report

## Scout Pipeline

### Step 1: Gather Data (use your built-in tools)

Run these searches, adapting queries to the user's niche:

**Twitter** (via exec):
```bash
bird search "[niche] need OR wish OR looking for OR frustrated" --limit 20
bird search "[niche] tool OR plugin OR solution" --limit 20
```

**Web** (via web_search tool):
- `"[niche] pain points 2026"`
- `"[niche] tools people want"`
- `"site:reddit.com [niche] need OR wish OR looking for"`
- `"site:producthunt.com [niche]"`

**ClawHub** (if niche is AI/agent related):
```bash
clawdhub search "[niche keyword]"
```

### Step 2: Identify Opportunities

From the raw data, extract distinct opportunities. Each opportunity = a specific unmet need that could become a product. Look for:

- Repeated complaints/requests (same problem mentioned 3+ times)
- Gaps between what exists and what people want
- Problems with existing solutions (too expensive, too complex, missing features)
- Emerging trends without established solutions

### Step 3: Score Each Opportunity

Run the scoring script:
```bash
python3 scripts/scout.py score --input opportunities.json --output report.md
```

Or score manually using these criteria (1-5 each):

| Criterion | 5 (Best) | 3 (Medium) | 1 (Worst) |
|-----------|----------|------------|-----------|
| **Demand** | 50+ people asking | 10-20 mentions | 1-2 mentions |
| **Competition** | No solutions exist | Some solutions, all flawed | Saturated market |
| **Feasibility** | Build MVP in 1-2 days | 1-2 weeks | Months of work |
| **Monetization** | People actively paying for similar | Freemium possible | Hard to charge |

**Total Score interpretation:**
- **16-20**: 🔥 BUILD IT NOW
- **12-15**: 👍 Strong opportunity, worth pursuing
- **8-11**: 🤔 Monitor, not urgent
- **4-7**: ❌ Skip

Detailed scoring examples: see `references/scoring-guide.md`

### Step 4: Generate Report

Format results as:

```
# Opportunity Scout: [Niche] — [Date]

## 🏆 Top 3 Opportunities

### 1. [Name] (Score: X/20)
- **Problem:** [What people need]
- **Evidence:** [Links/quotes from research]
- **Scores:** D:[X] C:[X] F:[X] M:[X]
- **Action:** [What to build, how long, how to monetize]

### 2. [Name] (Score: X/20)
...

## All Findings

| # | Opportunity | D | C | F | M | Total | Verdict |
|---|------------|---|---|---|---|-------|---------|
| 1 | ... | | | | | | |

## Recommendation
[Which to build first and why]
```

## Depth Modes

- `--depth quick`: 2 Twitter + 2 web searches. Fast scan, ~2 min.
- `--depth normal`: 4 Twitter + 4 web + ClawHub. Standard, ~5 min.
- `--depth deep`: 6 Twitter + 8 web + ClawHub + Reddit deep dive. Thorough, ~10 min.

## Tips

- Focus on problems people PAY to solve, not just complain about
- "I wish..." and "Does anyone know a tool for..." = strongest signals
- Check if existing solutions are abandoned/unmaintained — easy to replace
- Crypto/finance niches: high monetization but also high competition
- Niche down: "AI agent for dentists" beats "AI agent" every time
