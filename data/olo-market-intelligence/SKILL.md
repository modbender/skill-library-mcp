---
name: olo-market-intelligence
version: 1.0.0
description: Competitive landscape and market intelligence for M&A due diligence — TAM/SAM/SOM, competitor mapping, and industry analysis
author: ololand.ai
author_url: https://ololand.ai
license: MIT
triggers:
  - market intelligence
  - competitive landscape
  - tam sam som
  - market sizing
  - industry analysis
  - competitor mapping
  - market research
  - commercial due diligence
tags:
  - finance
  - market-research
  - m-and-a
  - due-diligence
  - competitive-intelligence
---

# Market Intelligence for M&A

Deliver competitive landscape analysis and market sizing for acquisition due diligence.

## Research Framework

### 1. Market Sizing (TAM/SAM/SOM)
- **TAM** (Total Addressable Market): Global market for the product/service category
- **SAM** (Serviceable Addressable Market): Geographic and segment-filtered subset
- **SOM** (Serviceable Obtainable Market): Realistic share given competitive position
- Source from industry reports (Gartner, IDC, Statista), triangulate with bottom-up estimates
- Present as range (low/base/high) with methodology notes
- Include 5-year CAGR forecast for TAM

### 2. Competitive Landscape
- Identify 5-10 direct competitors and 3-5 adjacent players
- For each competitor, capture:
  - Revenue estimate and growth rate
  - Funding history and valuation (if private)
  - Market share estimate
  - Key differentiators and positioning
  - Recent strategic moves (acquisitions, partnerships, product launches)
- Map competitive positioning on 2x2 matrix (e.g., breadth vs. depth, price vs. capability)

### 3. Industry Dynamics
- **Growth drivers**: Regulatory tailwinds, technology shifts, demand trends
- **Headwinds**: Commoditization, regulatory risk, substitute threats
- **Porter's Five Forces** assessment:
  - Supplier power (low/medium/high)
  - Buyer power (low/medium/high)
  - Competitive rivalry (low/medium/high)
  - Threat of substitutes (low/medium/high)
  - Threat of new entrants (low/medium/high)
- **Industry lifecycle stage**: Emerging, Growth, Mature, Declining

### 4. Customer & Channel Analysis
- Customer segmentation (enterprise/mid-market/SMB, by vertical)
- Buyer personas and purchasing decision factors
- Sales channel mix (direct, channel, marketplace, OEM)
- Net revenue retention and churn benchmarks for the sector
- Customer switching costs assessment

### 5. M&A Activity in Sector
- Recent comparable transactions (last 3 years)
- Median and mean EV/Revenue and EV/EBITDA multiples
- Buyer types (strategic vs. financial sponsor)
- Deal volume trend (accelerating, stable, declining)
- Notable failed deals and reasons

## Output Format

```
Market Intelligence Report: [Industry/Sector]
Target: [Company Name]

Market Size:
  TAM: $12.4B (2025) → $18.7B (2030), 8.5% CAGR
  SAM: $4.2B (North America + Europe)
  SOM: $180M (target's realistic capture)

Competitive Position:
  Market Share: ~4.3% of SAM
  Rank: #5 of 12 tracked competitors
  Moat: [proprietary data / switching costs / network effects / none]

Top Competitors:
  1. CompetitorA — $520M rev, 12% share, well-funded
  2. CompetitorB — $310M rev, 7% share, PE-backed
  3. CompetitorC — $190M rev, 4.5% share, recently acquired

Industry Health:
  Growth Stage: Growth → Early Maturity
  Consolidation Trend: Accelerating (12 deals in last 18 months)
  Regulatory Climate: Favorable (no pending restrictive legislation)

Comparable Transactions:
  Median EV/Revenue: 3.2x
  Median EV/EBITDA: 14.5x
  Premium to Public Comps: +25-35% (control premium)
```

## Quality Standards

- Cite sources for all market size estimates
- Distinguish confirmed data from estimates (mark with ~)
- Date-stamp all competitive intelligence (stale data is dangerous)
- Flag low-confidence assessments explicitly
- Cross-reference at least 2 sources for market size claims
