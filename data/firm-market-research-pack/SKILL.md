---
name: firm-market-research-pack
version: 1.0.0
description: >
  Market research and competitive intelligence pack.
  Competitive analysis, market sizing, financial benchmarking, web research,
  report generation, and competitive monitoring. 6 market research tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.1.0
tags:
  - market-research
  - competitive-intelligence
  - analysis
  - strategy
  - finance
---

# firm-market-research-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Provides a complete market research and competitive intelligence toolkit for the firm.
Enables structured competitive analysis, market sizing (TAM/SAM/SOM), financial
benchmarking, web-based intelligence gathering, professional report generation accessible
to all departments, and continuous competitive monitoring.

Designed to produce professional documents readable by every department:
CEO (strategic decisions), CFO (financial projections), CTO (tech landscape),
Marketing (positioning), Commercial (battlecards), Legal (regulatory landscape),
HR (salary benchmarks).

## Tools (6)

| Tool | Description | Category |
|------|-------------|----------|
| `openclaw_market_competitive_analysis` | Full competitive landscape analysis with feature matrix, SWOT, and positioning map | strategy |
| `openclaw_market_sizing` | TAM/SAM/SOM calculation with top-down and bottom-up approaches | strategy |
| `openclaw_market_financial_benchmark` | Financial benchmarking — unit economics, pricing analysis, revenue comparisons | finance |
| `openclaw_market_web_research` | Structured web research and OSINT intelligence gathering | research |
| `openclaw_market_report_generate` | Generate a complete professional market research report (Markdown) | export |
| `openclaw_market_research_monitor` | Continuous competitive monitoring — track competitor moves and market shifts | strategy |

## Usage

```yaml
skills:
  - firm-market-research-pack

# Full competitive analysis:
openclaw_market_competitive_analysis sector="SaaS project management" geography="France" competitors='["Monday.com","Asana","Notion"]'

# Market sizing:
openclaw_market_sizing sector="SaaS project management" geography="France" target_segment="PME 10-250" horizon_years=5

# Financial benchmarking:
openclaw_market_financial_benchmark sector="SaaS project management" metrics='["CAC","LTV","churn","ARPU"]'

# Web research on a specific competitor:
openclaw_market_web_research query="Monday.com competitive analysis 2026" sources='["crunchbase","g2","linkedin"]'

# Generate full report from collected data:
openclaw_market_report_generate title="Étude de Marché SaaS Gestion de Projet France" sections='["executive_summary","market_overview","competitive_landscape","financial_analysis","segmentation","positioning","recommendations"]'

# Set up monitoring:
openclaw_market_research_monitor action="add" competitor="Monday.com" watch='["pricing","features","funding","headcount"]'
```

## Cross-Department Integration

| Department | What they get | Tool |
|------------|--------------|------|
| **CEO** | Executive brief with strategic recommendations | `report_generate` |
| **CFO** | Financial benchmarks, unit economics, pricing data | `financial_benchmark` |
| **CTO** | Tech stack intelligence, feature comparison | `competitive_analysis` |
| **Marketing** | Positioning map, ICP insights, messaging angles | `competitive_analysis` + `market_sizing` |
| **Commercial** | Competitive battlecards | `competitive_analysis` |
| **Legal** | Regulatory landscape notes | `web_research` |
| **HR** | Salary benchmarks, headcount trends | `web_research` |

## Requirements

- `mcp-openclaw-extensions >= 3.1.0`
