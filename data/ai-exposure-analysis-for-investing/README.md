# AI Exposure Analyzer

Analyze any public company's AI exposure using an 8-dimension framework. Fetches 10-K filings, earnings transcripts, patent data, and O*NET workforce mappings to score vulnerability and adaptive capacity—classifying companies as **AI Fortified**, **AI Transformer**, **AI Bystander**, or **AI Endangered** with a valuation overlay.

## What It Does

- **8-Dimension AI Exposure Index** — Scores companies across Labor Automation Vulnerability, Revenue Model Disruption, AI Adoption Maturity, Competitive Moat Durability, Operational AI Leverage, Regulatory Risk, Industry Transformation Velocity, and Data & Ecosystem Strength
- **Real Data** — Fetches last 4 10-K filings (or international equivalents), earnings transcripts, and patent data
- **Workforce Mapping** — Maps company job categories to O*NET occupations for AI exposure scoring
- **Investment Classification** — Produces a 2×2 matrix (Vulnerability × Adaptive Capacity) with valuation overlay
- **Scenario Sensitivity** — Evaluates impact of Agentic AI, Physical AI/Robotics, Energy Constraints, and Open-Source Acceleration

## When to Use

The agent automatically applies this skill when you ask about:

- AI exposure, AI vulnerability, or AI risk for a company
- "How will AI affect [company]?" or "Is [company] ready for AI?"
- AI analysis of a stock or ticker
- Workforce automation risk or competitive moat durability
- Any company evaluation through an AI lens

You can also invoke manually: `/ai-exposure-analyzer` or "Analyze AI exposure for [ticker]"

## Installation

### From SkillsMP

If you use the SkillsMP MCP server or marketplace, search for `ai-exposure-analyzer` and install.

### From GitHub

```bash
# Clone or copy this repo into your skills directory
# Project-level (shared with repo):
cp -r AI-exposure-analysis-for-investing .cursor/skills/ai-exposure-analyzer

# Or personal (all projects):
cp -r AI-exposure-analysis-for-investing ~/.cursor/skills/ai-exposure-analyzer
```

Restart Cursor to load the skill.

## Requirements

- **Web access** — The agent uses `web_search` and `web_fetch` to retrieve SEC filings, earnings transcripts, and patent data
- **O*NET data** (optional) — For workforce-to-occupation mapping, place O*NET datasets in `data/`. See [O*NET Resource Center](https://www.onetcenter.org/database.html) for downloads. The skill works without them but with reduced precision on Dimension 1

## Structure

```
ai-exposure-analyzer/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── references/
│   ├── framework_dimensions.md # Scoring rubrics for all 8 dimensions
│   ├── data_collection_guide.md# How to fetch 10-K, transcripts, patents
│   ├── onet_mapping_guide.md   # O*NET workforce mapping
│   └── scoring_calculations.md # Composite score formulas
├── scripts/
│   ├── onet_lookup.py          # O*NET occupation lookup & exposure
│   └── calculate_scores.py    # Score calculation utilities
└── data/                       # O*NET datasets (user-provided)
```

## Output

Each analysis produces a structured report with:

- Executive summary and classification
- Dimension scores (1–5) with evidence-based explanations
- AI Vulnerability and Adaptive Capacity composite scores
- 2×2 matrix classification (AI Fortified / Transformer / Bystander / Endangered)
- Valuation overlay vs. sector medians
- Scenario sensitivity table
- Key risks and catalysts

