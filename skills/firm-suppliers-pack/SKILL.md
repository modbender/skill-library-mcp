---
name: firm-suppliers-pack
version: 1.0.0
description: >
  Procurement and supplier management pack.
  Supplier sourcing, multi-criteria evaluation, TCO analysis,
  contract management, and supply chain risk monitoring. 5 procurement tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.2.0
tags:
  - procurement
  - suppliers
  - sourcing
  - supply-chain
  - vendor-management
---

# firm-suppliers-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Provides a complete procurement and supplier management toolkit for the firm.
Enables structured supplier sourcing (SaaS, services, industrial), multi-criteria
evaluation with scoring matrices, total cost of ownership analysis, contract clause
recommendations, and continuous supply chain risk monitoring.

Designed to produce professional documents readable by every department:
CEO (strategic sourcing decisions), CFO (procurement budget and TCO), CTO (tech vendor
selection), Legal (contract clauses), Operations (delivery and logistics).

## Tools (5)

| Tool | Description | Category |
|------|-------------|----------|
| `openclaw_supplier_search` | Market-wide supplier sourcing — identification, filtering, shortlisting | procurement |
| `openclaw_supplier_evaluate` | Multi-criteria supplier evaluation with 15+ weighted criteria scoring | procurement |
| `openclaw_supplier_tco_analyze` | Total Cost of Ownership analysis over 3-5 years including hidden costs | finance |
| `openclaw_supplier_contract_check` | Contract clause analysis — SLA, penalties, reversibility, compliance | legal |
| `openclaw_supplier_risk_monitor` | Continuous supplier risk monitoring — financial, dependency, geopolitical | procurement |

## Usage

```yaml
skills:
  - firm-suppliers-pack

# Search for SaaS project management tools:
openclaw_supplier_search category="SaaS project management" budget_max=1000 users=50

# Evaluate shortlisted suppliers:
openclaw_supplier_evaluate suppliers='["Monday.com","ClickUp","Notion"]' criteria='{"price":20,"features":25,"support":15}'

# TCO analysis:
openclaw_supplier_tco_analyze suppliers='["Monday.com","ClickUp"]' volume=50 horizon_years=3

# Contract clause check:
openclaw_supplier_contract_check supplier="ClickUp" contract_type="SaaS" requirements='["SLA 99.9%","RGPD DPA","reversibility"]'

# Risk monitoring:
openclaw_supplier_risk_monitor action="add" supplier="ClickUp" watch='["financial","service_level","security"]'
```

## Cross-Department Integration

| Department | What they get | Tool |
|------------|--------------|------|
| **CEO** | Strategic sourcing recommendations | `supplier_evaluate` |
| **CFO** | TCO analysis, budget projections | `supplier_tco_analyze` |
| **CTO** | Tech vendor evaluation and comparison | `supplier_search` + `supplier_evaluate` |
| **Legal** | Contract clause recommendations | `supplier_contract_check` |
| **Operations** | Supply chain risk alerts | `supplier_risk_monitor` |

## Requirements

- `mcp-openclaw-extensions >= 3.2.0`
