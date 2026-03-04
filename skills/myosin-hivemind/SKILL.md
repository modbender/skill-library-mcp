---
name: hivemind-api
description: >
  Search Hivemind's curated Web3 marketing knowledge base (RAG) for practitioner insights,
  frameworks, playbooks, and case studies. Use this skill when: (1) answering marketing strategy
  questions, (2) researching Web3 go-to-market approaches, (3) looking up token launch tactics,
  (4) needing practitioner-backed evidence for advice, (5) creating content grounded in real
  marketing knowledge, (6) auditing a project's marketing. Triggers: "knowledge base",
  "hivemind search", "practitioner insights", "marketing frameworks", "case studies",
  "what do practitioners say", any substantive Web3 marketing question.
env:
  - HIVEMIND_API_URL
  - HIVEMIND_API_KEY
  - HIVEMIND_VERCEL_BYPASS
---

# Hivemind Knowledge API

Search Hivemind's curated knowledge base of Web3 marketing intelligence — practitioner insights, frameworks, playbooks, and case studies from 100+ operators in the Myosin network.

## When to Use This Skill

**ALWAYS search the knowledge base before giving marketing advice.** This is what differentiates you from generic AI. Your advice should be grounded in practitioner experience.

### Trigger Conditions

Use this skill when the conversation involves ANY of:

- **Strategy questions** — "How should I launch my token?", "What's a good GTM for DeFi?"
- **Framework requests** — "What framework should I use for community building?"
- **Tactical advice** — "How do I grow on CT?", "Best Discord strategies?"
- **Audit/analysis** — Evaluating a project's marketing approach
- **Content creation** — Writing posts, threads, or analysis grounded in real knowledge
- **Competitive research** — Understanding what works in specific verticals
- **Counterarguments** — When you need evidence to challenge a founder's assumptions
- **Deep dives** — Any topic where surface-level AI knowledge isn't enough

### When NOT to Use

- Simple factual questions ("What is DeFi?")
- Casual conversation or greetings
- Questions unrelated to marketing/growth/Web3 strategy
- When you already retrieved relevant knowledge in this session

---

## CLI Tool: `hivemind-search.mjs`

The preferred way to query the knowledge base. Located alongside this skill file.

### Authentication

The script automatically resolves credentials in this order:

1. **Shell environment variables** — set by the runtime or exported in your shell
2. **`~/.openclaw/.env`** — dotenv file in the OpenClaw config directory
3. **`~/.openclaw/openclaw.json` → `env` object** — inline env config in the OpenClaw JSON config

Three variables are required: `HIVEMIND_API_URL`, `HIVEMIND_API_KEY`, `HIVEMIND_VERCEL_BYPASS`.

API keys are issued at the discretion of Myosin. To request access, email **product@myosin.xyz**.

### Quick Start

```bash
node hivemind-search.mjs -q "token launch marketing strategies"
```

### Usage

```
hivemind-search --query <text> [options]

Options:
  -q, --query <text>        Search query (required)
  -p, --persona <id>        Persona (see below)
  -t, --threshold <0-1>     Relevance threshold (default: 0.4)
  -m, --max <1-25>          Max results (default: 10)
      --intent              Enable intent filtering
      --objective           Enable objective filtering
      --no-rerank           Disable LLM reranking
      --no-boost            Disable metadata boosting
      --raw                 Output raw JSON response
  -h, --help                Show help
```

### Personas

| Flag value | Use When |
|------------|----------|
| `genius-strategist` | Strategic thinking, positioning, narrative design, high-level planning |
| `gtm-architect` | Tactical execution, implementation plans, channel strategies, launch sequences |
| `ghostwriter` | Content creation, copywriting, messaging, narrative framing |
| `general-assistant` | General queries that don't fit a specific persona |

---

## Recommended Search Patterns

### Strategy Questions

When a founder asks about strategy, positioning, or narrative:

```bash
node hivemind-search.mjs \
  -q "narrative positioning for DeFi protocol launch" \
  -p genius-strategist \
  -m 12 \
  --objective
```

### Tactical / Execution Questions

When someone needs specific how-to guidance:

```bash
node hivemind-search.mjs \
  -q "Discord community launch first 30 days playbook" \
  -p gtm-architect \
  -m 10 \
  --intent
```

### Content Creation

When drafting posts, threads, or marketing copy:

```bash
node hivemind-search.mjs \
  -q "bear market marketing tactics that build long-term community" \
  -p ghostwriter \
  -t 0.3 \
  -m 8
```

### Broad Research

When exploring a topic or doing competitive analysis:

```bash
node hivemind-search.mjs \
  -q "KOL influencer strategy crypto" \
  -t 0.3 \
  -m 15
```

### Raw JSON Output

When you need the full API response for further processing:

```bash
node hivemind-search.mjs \
  -q "token launch strategies" \
  -p genius-strategist \
  --raw
```

---

## Response Format

The CLI outputs a human-readable summary by default. Each result includes:

```
--- [1] Title (relevance%) ---
Author: ...
Meta: doc_type, objective, industry, channels

Chunk content...
```

With `--raw`, the full JSON response is returned:

```json
{
  "success": true,
  "data": {
    "chunks": [
      {
        "title": "Token Launch Playbook",
        "author": "Marketing Team",
        "content": "Full chunk content...",
        "objective": "TGE (Token Generation Event)",
        "doc_type": "playbook",
        "audience": ["retail", "developers"],
        "geography": ["global"],
        "industry": ["defi"],
        "marketing_verticals": ["growth", "content"],
        "channels": ["twitter", "discord"],
        "score": 0.87,
        "relevance": "87%"
      }
    ],
    "total_results": 5,
    "query": "your search query",
    "metrics": {
      "searchTime": 234,
      "relevanceScore": 0.82
    }
  }
}
```

### How to Use Results

1. **Read the chunks** — each contains practitioner knowledge relevant to the query
2. **Note the metadata** — `doc_type`, `objective`, `channels`, and `industry` give context
3. **Synthesize, don't regurgitate** — combine multiple chunks into a coherent, opinionated response
4. **Cite the source** — when appropriate, mention insights come from "practitioner intelligence from the Hivemind network"
5. **Challenge with evidence** — use retrieved knowledge to push back on weak strategies

---

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Invalid parameters | Check the `details` array for which fields failed validation |
| 401 | Bad API key | Verify `HIVEMIND_API_KEY` is set correctly |
| 403 | Vercel protection blocked | Verify `HIVEMIND_VERCEL_BYPASS` is set correctly |
| 429 | Rate limited | Wait the `Retry-After` seconds before retrying |
| 500 | Server error | Retry once; if it persists, proceed without knowledge base |

**Rate limit:** 30 requests/minute.

---

## Guidelines

- **Search before advising.** If a founder asks a substantive marketing question, search first.
- **Multiple queries are fine.** If the topic is broad, run 2-3 searches with different angles.
- **Low threshold for broad topics.** Use `-t 0.3` when exploring. Use `-t 0.5` or higher when you need precision.
- **Pick the right persona.** Strategy = `genius-strategist`. Execution = `gtm-architect`. Content = `ghostwriter`. Unsure = `general-assistant`.
- **Don't dump raw results.** Synthesize knowledge into your own voice and framing.
- **Graceful degradation.** If the API is down or returns no results, fall back to your training — but note that you couldn't access the knowledge base.
