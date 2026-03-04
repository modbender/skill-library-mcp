---
name: masterswarm
description: Analyze any document with 15 parallel AI engines via the MasterSwarm cloud API. Upload receipts, contracts, lab results, or ask business/crypto/legal questions — get professional intelligence reports. Requires a paid MasterSwarm API key purchased from masterswarm.net.
metadata: {"openclaw": {"emoji": "⚡", "homepage": "https://masterswarm.net"}}
---

# MasterSwarm AI — 15 Engines. 31 Agents. One Verdict.

MasterSwarm is a cloud-based distributed AI orchestration API that analyzes documents and questions using 15 specialized AI engines running in parallel.

## What It Does

Send any text or question to the MasterSwarm API — 15 engines analyze it simultaneously and return a professional multi-page analysis.

### Available Engines

| Engine ID | Name | Use Case |
|---|---|---|
| `chef` | Chef Omega | Recipes, food cost, restaurant consulting |
| `apex` | APEX Strategy | Business strategy, financial projections, crypto |
| `consult` | NEXUS Consulting | SWOT, roadmaps, systems thinking |
| `research` | Research Lab | Scientific analysis, medical labs, papers |
| `market` | Market Intel | Competitive analysis, TAM/SAM, growth plans |
| `molecular` | APEIRON Lab | Molecular gastronomy, food science |
| `oracle` | Oracle | Forecasting, predictions, scenario planning |
| `assembly` | GAIA Brain | Multi-perspective analysis (12 cognitive neurons) |
| `analyst` | Data Analyst | Statistics, anomaly detection, modeling |

## Setup

### Required Credentials

This skill requires a **MasterSwarm API key** to authenticate requests. All API calls are sent to `https://api.neurodoc.app`.

```
MASTERSWARM_API_KEY=your_personal_key_here
```

### How to Get Your API Key

1. Visit **https://masterswarm.net** and purchase a plan:
   - Explorer (€9.99) — 5 reports
   - Professional (€29.99) — 20 reports
   - Enterprise (€79.99) — 60 reports
2. After purchase, Gumroad emails you a **license key**
3. Go to **https://masterswarm.net/app/** → click Upgrade → paste your license key → Activate
4. Your key is now active — use it as `MASTERSWARM_API_KEY`

### Data Handling & Privacy

- **API Host**: `api.neurodoc.app` (operated by NeuroDoc Pro, same entity as masterswarm.net)
- **Servers**: Hetzner, Germany (EU-only)
- **Encryption**: TLS 1.3 end-to-end
- **Data Retention**: Zero — documents are processed in real-time and immediately discarded
- **GDPR**: Compliant — privacy policy at https://masterswarm.net (footer → Privacy Policy)
- **No data is stored, logged, or used for training**

## How To Use

### Single Engine Analysis

```bash
curl -s --max-time 120 -X POST https://api.neurodoc.app/aetherlang/execute \
  -H "Content-Type: application/json" \
  -H "X-Aether-Key: MASTERSWARM_API_KEY" \
  -d '{
    "code": "flow Q {\n  using target \"neuroaether\" version \">=0.2\";\n  input text query;\n  node G: guard mode=\"STANDARD\";\n  node E: ENGINE_ID style=\"professional\";\n  G -> E;\n  output text result from E;\n}",
    "query": "USER_QUESTION_OR_DOCUMENT_TEXT"
  }'
```

**Replace:**
- `MASTERSWARM_API_KEY` — your personal API key
- `ENGINE_ID` — one from the table above (e.g. `apex`, `chef`, `research`)
- `USER_QUESTION_OR_DOCUMENT_TEXT` — the user's question or extracted document text

### Engine Selection Guide

| User Request | Engine ID |
|---|---|
| Recipe, food, restaurant, menu | `chef` |
| Business strategy, startup, ROI | `apex` |
| SWOT, consulting, roadmap, KPIs | `consult` |
| Research, science, papers, evidence | `research` |
| Market analysis, competition, pricing | `market` |
| Crypto, trading, DeFi, portfolio | `apex` |
| Medical labs, blood tests, health | `research` |
| Legal, contracts, compliance | `consult` |
| Financial analysis, P&L, ratios | `apex` |
| General or multi-domain question | `assembly` |
| Data, statistics, anomalies | `analyst` |
| Molecular gastronomy, food science | `molecular` |
| Forecasting, predictions | `oracle` |

### Multi-Engine Analysis

For comprehensive reports, call multiple engines sequentially:

```bash
# Example: Run apex + consult + research on the same query
for ENGINE_ID in apex consult research; do
  curl -s --max-time 120 -X POST https://api.neurodoc.app/aetherlang/execute \
    -H "Content-Type: application/json" \
    -H "X-Aether-Key: MASTERSWARM_API_KEY" \
    -d "{
      \"code\": \"flow M {\n  using target \\\"neuroaether\\\" version \\\">=0.2\\\";\n  input text query;\n  node G: guard mode=\\\"STANDARD\\\";\n  node E: $ENGINE_ID style=\\\"professional\\\";\n  G -> E;\n  output text result from E;\n}\",
      \"query\": \"USER_QUESTION\"
    }"
done
```

### Response Format

```json
{
  "status": "success",
  "result": {
    "final_output": "## Full analysis report in markdown...",
    "outputs": {"E": "..."},
    "execution_log": [
      {"node": "G", "status": "OK"},
      {"node": "E", "status": "OK", "duration": 5.2}
    ]
  },
  "duration_seconds": 6.1
}
```

Extract `result.final_output` to present the report to the user.

**Error responses:**
- `"status": "error"` — check `error` field for details
- `"status": "validation_error"` — malformed flow code
- HTTP 429 — rate limited, wait and retry

### Important Notes

- **Timeout**: Use 120-180 second timeout — multi-engine analysis needs time
- **Credits**: Each API call consumes 1 credit from the user's purchased plan
- **Language**: Auto-detects input language — reports match the query language
- **Rate Limit**: Max 5 concurrent requests per key

## Links

| Resource | URL |
|---|---|
| Landing Page | https://masterswarm.net |
| Buy Credits | https://masterswarm.net (Pricing section) |
| App Dashboard | https://masterswarm.net/app/ |
| Telegram Bot | https://t.me/aetherlang_bot |
| AetherLang Docs | https://aetherlang.net |
| Privacy Policy | https://masterswarm.net (footer) |
| Support Email | echelonvoids@protonmail.com |
