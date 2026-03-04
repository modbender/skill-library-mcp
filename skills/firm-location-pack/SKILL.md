---
name: firm-location-pack
version: 1.0.0
description: >
  Location strategy and site selection pack.
  Geo-economic analysis, real estate intelligence, site scoring,
  tax incentive optimization, and TCO simulation. 5 location tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.2.0
tags:
  - location
  - real-estate
  - site-selection
  - geo-economics
  - implantation
---

# firm-location-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Provides a complete location strategy and site selection toolkit for the firm.
Enables structured geo-economic analysis, real estate market intelligence,
multi-criteria site scoring, tax incentive identification, and total cost of
occupation simulation over 3-5 years.

Designed to produce professional documents readable by every department:
CEO (strategic location decisions), CFO (TCO projections), HR (talent pool analysis),
Legal Status (territorial tax implications), Operations (logistics and infrastructure).

## Tools (5)

| Tool | Description | Category |
|------|-------------|----------|
| `openclaw_location_geo_analysis` | Geo-economic analysis — talent pools, transport, ecosystem, quality of life | strategy |
| `openclaw_location_real_estate` | Real estate market intelligence — availability, pricing, trends by zone | real_estate |
| `openclaw_location_site_score` | Multi-criteria site scoring (20+ criteria) with weighted comparison matrix | strategy |
| `openclaw_location_incentives` | Tax incentives and aid programs by territory — ZFU, ZRR, BPI, FEDER | finance |
| `openclaw_location_tco_simulate` | Total Cost of Occupation simulation over 3-5 years | finance |

## Usage

```yaml
skills:
  - firm-location-pack

# Geo-economic analysis of candidate cities:
openclaw_location_geo_analysis cities='["Paris 13e","Lyon Part-Dieu","Nantes"]' sector="tech" headcount=30

# Real estate search:
openclaw_location_real_estate zone="Île-de-France" property_type="bureau" surface_min=200 budget_max=6000

# Multi-criteria scoring:
openclaw_location_site_score sites='["Saint-Denis","Montreuil","Ivry"]' weights='{"transport":15,"talent":15,"price":20}'

# Tax incentives lookup:
openclaw_location_incentives zone="Saint-Denis Pleyel" company_type="startup" headcount=15

# TCO simulation:
openclaw_location_tco_simulate sites='["Paris 13e","Saint-Denis","Nantes"]' surface=250 horizon_years=3
```

## Cross-Department Integration

| Department | What they get | Tool |
|------------|--------------|------|
| **CEO** | Site scoring matrix and strategic recommendation | `site_score` |
| **CFO** | TCO simulations and incentive impact | `tco_simulate` + `incentives` |
| **HR** | Talent pool analysis and quality of life data | `geo_analysis` |
| **Legal Status** | Territorial tax implications | `incentives` |
| **Operations** | Transport and infrastructure assessment | `geo_analysis` |

## Requirements

- `mcp-openclaw-extensions >= 3.2.0`
