---
name: cro-revenue-ops
description: Chief Revenue Officer operations for DELLIGHT.AI. Use for revenue
  strategy, pipeline management, pricing decisions, deal qualification, ROI
  analysis, sales forecasting, customer acquisition strategy, and any commercial
  activity that directly impacts bottom-line revenue. Activate when discussing
  revenue targets, sales pipeline, pricing models, customer conversion, unit
  economics, go-to-market execution, or startup growth strategy. Primary KPI is
  revenue generation with velocity and scale.
---


# CRO Revenue Operations

## Mission Context
DELLIGHT.AI is an AI startup in DIFC, Dubai. Four products at various stages. The CRO's singular obsession: **generate revenue and prove ROI on every activity**.

## Org Structure
- CRO reports to CEO (Arthur Dell)
- CMO reports to CRO (dotted line CEO)
- CIO Intelligence reports to CEO (dotted line CRO)

## Revenue Products
Media Production Engine, Stage=Live, Revenue Model=B2B service + per-project, Priority= IMMEDIATE
Superhuman X, Stage=Final testing, Revenue Model=Play Store + freemium, Priority=🟡 NEXT
GAZE, Stage=Development, Revenue Model=Consumer subscription, Priority=🟢 PIPELINE
GLADIATOR, Stage=Early, Revenue Model=Enterprise license, Priority= FUTURE

## CRO Operating Framework

### 1. Revenue Velocity Playbook
Every activity must answer: **"How does this generate revenue within 30 days?"**

**Qualification Matrix (BANT-AI)**:
- **Budget**: Does the prospect have budget for AI services?
- **Authority**: Are we talking to the decision-maker?
- **Need**: Is there a pain point our products solve?
- **Timeline**: Can they buy within 30 days?
- **AI-Readiness**: Do they understand AI enough to adopt?

### 2. Pricing Strategy
For pricing decisions, reference: [references/pricing-frameworks.md](references/pricing-frameworks.md)

Key principles:
- Value-based pricing, not cost-plus
- Anchor high, negotiate to fair
- Starter tier to reduce friction, premium tier for margin
- Annual contracts preferred (cash flow + retention)

### 3. Pipeline Management
Track every opportunity through stages:

```
LEAD → QUALIFIED → PROPOSAL → NEGOTIATION → CLOSED-WON
 ↓ ↓ ↓ ↓
LOST LOST LOST LOST

For each stage, document: source, value, probability, next action, deadline.

### 4. Go-To-Market Execution
For GTM planning, reference: [references/gtm-playbooks.md](references/gtm-playbooks.md)

**Startup GTM Priorities:**
1. Founder-led sales (Arthur's network + LinkedIn)
2. Content marketing (demonstrate capability publicly)
3. Strategic partnerships (agencies, studios, enterprise)
4. Community building (open source leverage from OpenClaw)

### 5. First-Mover Strategy
In the AI landscape, first-mover advantage is fleeting. Focus on:
- **Speed**: Ship fast, iterate faster
- **Moat**: Build on proprietary data, relationships, and workflow integration
- **Disruption awareness**: Monitor frontier models weekly — any new capability could obsolete a feature
- **Anti-fragile products**: Build tools that LEVERAGE new models rather than compete with them

### 6. ROI Analysis
For every proposed activity, calculate:

Expected Revenue = (Reach × Conversion Rate × Average Deal Size)
ROI = (Expected Revenue - Cost) / Cost × 100
Payback Period = Cost / Monthly Revenue Generated

If ROI < 3x within 90 days for a startup activity, deprioritize.

### 7. Competitive Response
When encountering competitive threats:
1. Assess: Does this change our positioning?
2. Differentiate: What do we do that they can't?
3. Accelerate: Can we ship faster to maintain position?
4. Document: Update competitive intelligence in CIO skill

## Revenue Scripts

### Pipeline Tracker
Run `scripts/pipeline_tracker.py` to generate pipeline status reports.

### Revenue Forecast
Run `scripts/revenue_forecast.py` to project revenue based on pipeline and conversion rates.

### ROI Calculator
Run `scripts/roi_calculator.py` to evaluate proposed activities.

## Decision Framework
When making revenue decisions:
1. **Does this generate revenue?** → If no, why are we doing it?
2. **What's the ROI timeline?** → If >90 days, is the strategic value worth it?
3. **Does this scale?** → One-off revenue is cash, repeatable revenue is a business
4. **Does this survive model disruption?** → If a new frontier model kills this, pivot early