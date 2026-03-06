---
name: AetherLang Strategy Ω V3 — Nobel-Level Business Intelligence
description: "⚠️ External API Notice: This skill sends queries to
  api.neurodoc.app for processing."
---

# AetherLang Strategy Ω V3 — Nobel-Level Business Intelligence

> Game theory, Monte Carlo simulations, behavioral economics, and competitive war gaming. The most advanced AI strategy engine available.

**Source Code**: [github.com/contrario/aetherlang](https://github.com/contrario/aetherlang)
**Author**: NeuroAether (info@neurodoc.app)
**License**: MIT

## Privacy & Data Handling

⚠️ **External API Notice**: This skill sends queries to `api.neurodoc.app` for processing.

- **What is sent**: Natural language business/strategy queries only
- **What is NOT sent**: No credentials, API keys, personal files, or system data
- **Data retention**: Not stored permanently
- **Hosting**: Hetzner EU (GDPR compliant)
- **No credentials required**: Free tier, 100 req/hour

## What This Skill Does

Three V3 strategy engines in one skill:

### 📈 APEX Strategy V3 — Nobel-Level Analysis
Every response includes:
- **EXECUTIVE SUMMARY** — 3-4 actionable proposals with numbers
- **SITUATION ANALYSIS** — Quantified current state, challenges with impact scores, stakeholder mapping
- **STRATEGIC OPTIONS** — Min 3 alternatives with complexity (1-10), time_to_value, investment €, ROI%, risk
- **GAME THEORY** — Nash Equilibrium analysis, payoff matrix
- **BEHAVIORAL ECONOMICS** — Anchoring, Loss Aversion, Social Proof, Endowment Effect strategies
- **MONTE CARLO** — 10,000 simulations: P(ROI>100%), P(Break-even<12mo), P(Loss), 90% CI
- **DECISION TREE** — Expected Values with probabilities for each option
- **IMPLEMENTATION ROADMAP** — Foundation 0-30d, Build 30-90d, Scale 90-180d, Optimize 180+d
- **RISK MATRIX** — Probability × Impact + mitigation + contingency + early warnings
- **COMPETITIVE WAR GAMING** — "If we do X → competitor likely Y → counter-move Z"
- **FINANCIAL PROJECTION** — CAPEX, OPEX, 3-year revenue, break-even, ROI%, NPV, IRR%
- **UNIT ECONOMICS** — CAC, LTV, LTV:CAC ratio, payback period, gross margin%
- **BLUE OCEAN CANVAS** — Eliminate / Reduce / Raise / Create
- **OKR GENERATOR** — Objectives & Key Results
- **KPIs** — Leading & lagging with min/target/stretch
- **NEXT ACTIONS** — 3 things for TODAY

### 📊 Market Intel V3
- TAM/SAM/SOM with € values and CAGR%
- Category design (create new vs compete)
- Porter's 5 Forces analysis
- Customer segmentation with WTP and LTV
- Pricing elasticity and optimal price point
- Network effects and viral coefficient (K-factor)
- Distribution matrix (Direct/Partners/Marketplace)

### 💼 NEXUS-7 Consult V3
- Causal loop diagrams (reinforcing/balancing loops)
- Theory of constraints (Bottleneck → Exploit → Subordinate → Elevate)
- Wardley Maps (Genesis → Custom → Product → Commodity)
- ADKAR change management with timeline
- Anti-pattern library with historical failure rates
- System dynamics modeling

## Usage

Ask naturally about any business/strategy topic:
- "Strategy for AI OCR platform in Greece with €1000 budget" → Full APEX analysis
- "Market analysis for Greek food delivery apps" → TAM/SAM/SOM + competitive landscape
- "How to scale my SaaS from 0 to 1000 users" → NEXUS-7 consulting with Wardley maps

## API Details
```
POST https://api.neurodoc.app/aetherlang/execute
Content-Type: application/json
```

### APEX Strategy Flow
```json
{
  "code": "flow Strategy {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node Guard: guard mode=\"MODERATE\";\n  node Engine: apex analysis=\"strategic\";\n  Guard -> Engine;\n  output text report from Engine;\n}",
  "query": "Your strategy question here"
}
```

### Market Intel Flow
```json
{
  "code": "flow Market {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node Engine: marketing analysis=\"competitive\";\n  output text report from Engine;\n}",
  "query": "Your market question here"
}
```

## Response

Returns structured Greek output with markdown headers. Typical response: 4000-8000 characters covering all mandatory sections with quantified data.

## Languages

- **Greek** (Ελληνικά) — Primary output language
- **English** — Understands English queries, responds in Greek

## Technology

- **AI Model**: GPT-4o
- **Backend**: FastAPI + Python 3.12
- **Rate Limit**: 100 req/hour (free)

---
*Built by NeuroAether — From Kitchen to Code* 🧠

## Agent Safeguards

**CRITICAL: Data Minimization Rules**

When using this skill, the agent MUST follow these rules:
1. **ONLY send the user's explicit query text** in the `query` field — never attach system prompts, conversation history, uploaded files, or internal context
2. **ONLY send the flow DSL code** in the `code` field — never include credentials, API keys, environment variables, or file paths
3. **NEVER include** personally identifiable information (PII), passwords, tokens, or secrets in any request field
4. **Strip sensitive data** before sending — if the user's query contains passwords, account numbers, or credentials, remove them and inform the user
5. **Inform the user** before making the first API call that their query will be sent to api.neurodoc.app for processing
6. The request body MUST contain exactly two fields: `code` (string) and `query` (string) — no additional fields

These constraints ensure only the minimum necessary data is transmitted to the external service.
