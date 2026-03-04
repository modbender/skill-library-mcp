---
name: aeo-prompt-research-free
description: >
  Discover which AI prompts and topics matter for a brand's Answer Engine Optimization (AEO)
  using only free tools. Crawls a website, analyzes the brand's positioning, generates prioritized
  prompts people ask AI assistants, and audits existing content coverage — all without paid APIs.
  Use when a user wants to: find what questions people ask AI about their industry, discover AEO
  opportunities, research prompts for content creation, audit a site's AI visibility, or build
  an AEO content strategy. No API keys required — uses web_fetch, web_search (free tier), and
  LLM reasoning only.
---

# AEO Prompt Research (Free)

> **Source:** [github.com/psyduckler/aeo-skills](https://github.com/psyduckler/aeo-skills/tree/main/aeo-prompt-research-free)
> **Part of:** [AEO Skills Suite](https://github.com/psyduckler/aeo-skills) — Prompt Research → [Content](https://github.com/psyduckler/aeo-skills/tree/main/aeo-content-free) → [Analytics](https://github.com/psyduckler/aeo-skills/tree/main/aeo-analytics-free)

Discover which prompts and topics matter for a brand's AI visibility — using zero paid APIs.

## Requirements

- `web_fetch` — crawl the target site
- `web_search` — Brave Search free tier (optional but recommended)
- LLM reasoning — the agent's own model does the heavy lifting

No API keys, no paid tools, no accounts needed.

## Workflow

### Input

The user provides:
- **Domain URL** (required) — e.g. `clearscope.io`
- **Niche/category** (optional) — e.g. "SEO software for content teams"
- **Competitors** (optional) — e.g. "Surfer SEO, MarketMuse, Frase"

### Step 1: Crawl the Site

Use `web_fetch` on key pages to understand the brand:

```
Pages to fetch (try each, skip 404s):
- / (homepage)
- /about or /about-us
- /pricing
- /products or /features or /services
- /blog (index only)
```

Alternatively, run `scripts/crawl_site.sh <domain>` for a batch crawl.

Extract from crawled content:
- Core product/service offering
- Target audience (industry, company size, persona)
- Key differentiators / value props
- Competitor mentions
- Content themes from blog titles

### Step 2: Discover the Topic Universe

Using the brand understanding, brainstorm topic categories. For methodology and category types, read `references/aeo-methodology.md`.

Core prompt categories to generate:
1. Problem-aware — "How do I solve [problem]?"
2. Solution-aware — "What tools exist for [category]?"
3. Comparison — "[Brand] vs [competitor]"
4. Best-of — "Best [category] for [use case]"
5. How-to — "How to [task the product helps with]"
6. Evaluation — "Is [brand] good for [need]?"
7. Industry — "[Industry] trends / best practices"

### Step 3: Generate Prompts

For each category, generate 5-15 specific prompts people would actually ask an AI assistant.

Guidelines:
- Write naturally — how people talk to ChatGPT, not how they Google
- Be specific — include context (company size, industry, use case)
- Vary intent — research, comparison, how-to, buying decision
- Avoid jargon-heavy or unrealistic prompts

### Step 4: Prioritize

Score each prompt (1-5) on:
- **Relevance** — How closely tied to the brand's core offering?
- **Volume potential** — How many people likely ask this?
- **Winability** — Can this brand realistically be the best answer?
- **Intent value** — Does this indicate buying/conversion intent?

Formula: `Priority = (Relevance × 2 + Volume + Winability + Intent) / 5`

Sort into Tier 1 (≥3.5), Tier 2 (2.5-3.4), Tier 3 (<2.5).

### Step 5: Audit Existing Coverage

For Tier 1 prompts, use `web_search` with `site:domain.com [topic keywords]` to check if content already exists.

Rate coverage:
- **Strong** — Dedicated page directly answers the prompt
- **Partial** — Related content exists but doesn't fully address it
- **None** — No relevant content found

### Step 6: Deliver Results

Output a structured report with:
1. Brand summary (2-3 sentences)
2. Prioritized prompt list with scores and coverage status
3. Content gap analysis (high-priority prompts with no coverage)
4. Top 5 recommended content pieces to create first

Use the output format from `references/aeo-methodology.md`.

## Tips for Better Results

- If `web_search` is unavailable, the skill still works — just skip the coverage audit or have the user manually check
- For competitor analysis, crawl competitor sites too and compare topic coverage
- Re-run quarterly — AI prompt trends shift as models and user behavior evolve
- The agent's own knowledge of the industry is a valid research input — use it
