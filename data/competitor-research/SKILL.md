---
name: Competitor Research
slug: competitor-research
version: 1.0.0
homepage: https://clawic.com/skills/competitor-research
description: Deep competitor audits with market positioning, gap analysis, and actionable insights for winning strategies.
changelog: Initial release with analysis frameworks, depth levels, and iterative workflow.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":[],"paths":["~/competitor-research/"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs deep competitor analysis. Agent conducts thorough research on competitors in a niche, identifies gaps and opportunities, and delivers actionable strategies. Supports both new market entry and existing business competitive analysis.

## Architecture

Memory lives in `~/competitor-research/`. See `memory-template.md` for structure.

```
~/competitor-research/
├── memory.md              # Status + research preferences + niche context
├── niches/                # Research by market/niche
│   └── {niche}/           # One folder per niche
│       ├── overview.md    # Market landscape
│       └── {company}.md   # Individual competitor deep dives
└── insights/              # Cross-cutting findings
    └── {date}-{topic}.md  # Strategic insights and recommendations
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Research frameworks | `frameworks.md` |

## Core Rules

### 1. Define Scope Before Research
Never start without clarity on:

| Question | Why It Matters |
|----------|----------------|
| What decision will this inform? | Shapes depth and focus |
| New market entry or existing competition? | Different analysis needs |
| Direct competitors only, or substitutes too? | Defines research boundaries |
| Time constraint? | Determines depth level |

If user is vague, ask. Bad scope = wasted research.

### 2. Use Depth Levels

| Level | Time | Output | Best For |
|-------|------|--------|----------|
| **Quick Scan** | 15-30 min | Top 5 competitors, key differentiators, obvious gaps | Initial exploration |
| **Standard** | 1-2 hours | Full landscape, pricing matrix, positioning map, opportunities | Business planning |
| **Deep Dive** | Half day+ | Individual competitor audits, detailed SWOT, strategic playbook | Serious competition |

Always confirm depth level before starting. Default to Standard if unsure.

### 3. Structure Every Competitor Analysis

For each competitor, cover:

```
BASICS
- What they do (one sentence)
- Target customer
- Pricing model and range
- Founding date, funding, size indicators

PRODUCT
- Core features
- Key differentiators
- Weaknesses/gaps
- Recent changes

POSITIONING  
- How they describe themselves
- Who they compare against
- Messaging tone and style

TRACTION SIGNALS
- Reviews/ratings (G2, Capterra, etc.)
- Social proof they highlight
- Customer logos/testimonials
- Growth indicators
```

### 4. Always Find Gaps and Opportunities

End every research session with:

**GAP ANALYSIS**
- What do customers complain about that nobody solves?
- What segments are underserved?
- What's overpriced in the market?
- What's missing that should exist?

**OPPORTUNITIES**
- Where can user win? (price, features, positioning, audience)
- What would be the wedge to enter?
- What's the unfair advantage potential?

Research without actionable gaps is just a report. Make it strategic.

### 5. Iterate and Build Knowledge

Each research session builds on previous ones:
- **First session:** Establish landscape, identify key players
- **Follow-up sessions:** Deep dive individual competitors
- **Return visits:** Update with new findings, track changes

Before researching a niche again, check `niches/{niche}/` for prior work.

### 6. Cite and Date Everything

Mark all findings with:
- **Source:** Where you found it (website, G2, LinkedIn, etc.)
- **Date:** When observed (pricing changes, features evolve)
- **Confidence:** High (direct source) / Medium (inferred) / Low (speculation)

Undated intelligence becomes unreliable fast.

### 7. Deliver Actionable Recommendations

Every research deliverable ends with:

```
STRATEGIC RECOMMENDATIONS
1. [Specific action] because [finding supports it]
2. [Another action] based on [gap identified]
3. [What to avoid] given [competitor strength]

WHAT TO WATCH
- [Signal that would change this analysis]
- [Competitor move to monitor]
```

## Research Frameworks

### Market Landscape
Start broad, then narrow:
1. List all players (direct, indirect, substitutes)
2. Categorize by segment (enterprise, SMB, prosumer, etc.)
3. Map by positioning (premium vs budget, generalist vs niche)
4. Identify white space

### Competitive Matrix
Compare on dimensions that matter:

| Competitor | Price | Feature X | Feature Y | Target | Differentiator |
|------------|-------|-----------|-----------|--------|----------------|
| Player A   | $$$   | ✅        | ❌        | Enterprise | Security |
| Player B   | $     | ❌        | ✅        | SMB    | Simplicity |
| (User)     | $$    | ✅        | ✅        | Mid-market | Best of both |

### Win/Lose Analysis
For each competitor, answer:
- Why would a customer choose them over user?
- Why would a customer choose user over them?
- What type of customer is a slam-dunk for each?

### Positioning Audit
Analyze how competitors position:
- Homepage headline and subhead
- Three main value props
- Social proof strategy
- Pricing presentation
- Comparison pages (if any)

Look for positioning gaps nobody owns.

## Iterative Research Workflow

**Session 1: Landscape**
```
"I want to research competitors in [niche]"
→ Quick scan of market
→ Identify 5-10 key players
→ Create overview.md for the niche
→ Ask: want to deep dive any specific competitor?
```

**Session 2+: Deep Dives**
```
"Let's analyze [Company X]"
→ Load niche overview for context
→ Full competitor analysis
→ Save to niches/{niche}/{company}.md
→ Update overview with new findings
```

**Return Visit**
```
"What do we know about [niche/company]?"
→ Load existing research
→ Note what might be outdated
→ Offer to refresh specific sections
```

## Common Traps

- **No scope = bad research** → Always clarify what decision this informs before starting
- **Feature obsession** → Business model and positioning often matter more than features
- **Outdated pricing** → Check pricing pages directly, don't trust cached data
- **Missing substitutes** → Direct competitors aren't the only threat. What else solves the same job?
- **Analysis paralysis** → Set time limits. Good-enough research beats perfect research never delivered
- **No recommendations** → A list of competitors isn't strategy. What should user DO with this?
- **Forgot to save** → Update memory and niche files after every session

## Security & Privacy

**Data that stays local:**
- All research stored in `~/competitor-research/`
- Niche analyses and competitor profiles
- User preferences and context

**This skill does NOT:**
- Access private competitor systems
- Create fake accounts for research
- Scrape content violating ToS
- Send your research externally
- Store any credentials

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `market-research` — broader market analysis
- `business` — strategic frameworks
- `competitor-monitoring` — ongoing tracking after research

## Feedback

- If useful: `clawhub star competitor-research`
- Stay updated: `clawhub sync`
