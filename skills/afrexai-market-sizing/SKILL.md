# Market Sizing — TAM/SAM/SOM Calculator

Build defensible market sizing for any product, pitch deck, or business case. Top-down and bottom-up methodologies combined.

## What You Get

- **TAM** (Total Addressable Market) — entire market if you had 100% share
- **SAM** (Serviceable Addressable Market) — segment you can actually reach
- **SOM** (Serviceable Obtainable Market) — realistic capture in 12-36 months
- **Bottom-up validation** — unit economics × reachable customers
- **Source citations** — government data, industry reports, public filings

## How to Use

Tell me your product/service and target customer. I'll build the full sizing.

**Example prompts:**
- "Size the market for AI-powered contract review for mid-market law firms in the US"
- "TAM/SAM/SOM for a SaaS helpdesk targeting e-commerce brands doing $1M-$50M revenue"
- "Market size for automated bookkeeping for UK SMBs"

## Methodology

### Top-Down
1. Start with total industry revenue (cite source)
2. Filter by geography, segment, company size
3. Apply technology adoption rates
4. Result = SAM

### Bottom-Up
1. Count reachable customers (databases, directories, LinkedIn)
2. Multiply by realistic ACV (annual contract value)
3. Apply conversion rates at each funnel stage
4. Result = SOM

### Triangulation
Compare top-down and bottom-up. If they're within 2-3x of each other, the sizing holds. If wildly different, investigate assumptions.

## Output Format

```
## Market Sizing: [Product/Service]

### TAM — $X.XB
[Total market calculation with sources]

### SAM — $XXM
[Filtered by geography + segment + tech adoption]

### SOM (12-month) — $X.XM
[Bottom-up: customers × ACV × conversion]

### Key Assumptions
- [Assumption 1 + source]
- [Assumption 2 + source]

### Risks to Sizing
- [What could make this smaller]
- [What could make this bigger]
```

## When to Use This

- Pitch decks and investor presentations
- Go-to-market strategy planning
- New product feasibility analysis
- Board presentations and business cases
- Competitive positioning

## Pro Tip

Most founders oversize their TAM and undersize their SOM. Investors see through inflated numbers instantly. A tight, well-sourced $50M SAM beats a hand-wavy $10B TAM every time.

---

Need the full business context pack for your industry? **[Browse AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/)** — pre-built agent configs for Fintech, Healthcare, Legal, SaaS, and 6 more verticals ($47 each).

Calculate what AI automation could save your business: **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)**
