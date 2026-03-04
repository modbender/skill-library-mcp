# AEO System — Answer Engine Optimization

**Category:** Marketing  
**Price:** $9–$19  
**Author:** Carson Jarvis ([@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI))

---

## What It Does

When someone asks ChatGPT or Perplexity "what's the best [product] for [use case]?" — AEO determines which brand gets named.

The AEO System gives your OpenClaw agent a complete toolkit for getting AI assistants to recommend your brand. It's the AI equivalent of SEO, and most brands haven't started.

---

## The 7-Layer Framework

| Layer | What You Build |
|-------|---------------|
| 1 | **Answer Intent Map** — track which brands AI recommends for each query |
| 2 | **Answer Hub** — a long-form guide that AI models cite directly |
| 3 | **Brand-Facts Page** — a neutral, cite-able facts page |
| 4 | **brand-facts.json** — machine-readable brand data at `/.well-known/brand-facts.json` |
| 5 | **Schema Markup** — structured data for products, FAQs, and your organization |
| 6 | **Citation Network** — getting listed on sites that AI models actually cite |
| 7 | **GPT Shopping** — Google Merchant Center + reviews for AI shopping results |

---

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Full agent instructions |
| `scripts/answer-intent-map.js` | Node.js script to query AI platforms and log competitive data |
| `templates/brand-facts.json` | Fill-in-the-blank machine-readable brand data template |
| `templates/answer-hub-template.md` | Answer Hub page template with TL;DR section |
| `templates/weekly-maintenance-checklist.md` | 90-minute weekly protocol |

---

## Quick Start

### 1. Set up your API key

```bash
export PERPLEXITY_API_KEY="your-key-here"
# Get one free at: https://www.perplexity.ai/settings/api
```

### 2. Run your first Answer Intent Map

```bash
node scripts/answer-intent-map.js \
  --category "your product category" \
  --brand "Your Brand Name" \
  --queries 20
```

This will show you exactly where your brand stands vs. competitors across 20 purchase-intent queries.

### 3. Run a full audit

Tell your agent:
```
"Run an AEO audit for mybrand.com"
```

The agent will score all 7 layers and give you a prioritized action plan.

---

## Example Output

```
Answer Intent Map: Magnesium Supplements

Query: "best magnesium for sleep"
Platform: Perplexity
#1: MagTech ✓ (our brand)
#2: Natural Vitality
#3: Doctor's Best
Source cited: healthline.com

Query: "best magnesium glycinate brand"  
Platform: ChatGPT
#1: Pure Encapsulations (not us)
#2: Thorne (not us)
#3: MagTech ✓

Our #1 position: 8/20 queries
Our top-3 position: 14/20 queries
```

---

## Requirements

- OpenClaw agent with any model
- Node.js v18+
- `PERPLEXITY_API_KEY` (free tier sufficient)
- `OPENAI_API_KEY` (optional)

---

## Built By

Carson Jarvis — AI operator, builder of systems that ship.  
Follow the build: [@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI)  
More skills: [larrybrain.com](https://larrybrain.com)
