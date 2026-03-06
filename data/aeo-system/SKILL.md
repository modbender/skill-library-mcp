---
name: aeo-system
description: "Answer Engine Optimization — get AI assistants to recommend your brand. Run AEO audits, build Answer Intent Maps, track AI recommendation positions, and maintain a 7-layer AEO infrastructure for any brand or product category."
requiredEnv:
  - PERPLEXITY_API_KEY  # Required for Answer Intent Map automation
  - OPENAI_API_KEY      # Optional — enables ChatGPT query automation
  - BRAVE_API_KEY       # Recommended — enables web-based infrastructure checks
permissions:
  - network: Queries Perplexity API, OpenAI API, and target brand websites
  - filesystem: Writes audit reports and intent map data to working directory
source:
  url: https://github.com/Batsirai/carson-skills
  author: Carson Jarvis (@CarsonJarvisAI)
  github: https://github.com/Batsirai/carson-skills
  verified: true
security:
  note: API keys are loaded from environment variables. No credentials are embedded in the skill or scripts.
---

# AEO (Answer Engine Optimization) System

> Get AI assistants — ChatGPT, Perplexity, Claude, Gemini — to recommend your brand when people ask purchase-intent questions.

---

## What This Is

AEO is the discipline of optimizing for AI-powered answer engines the same way SEO optimizes for search engines. When someone asks Perplexity "what's the best magnesium supplement for sleep?" — AEO determines whether your brand gets named.

This skill gives an OpenClaw agent the ability to:

1. **Audit** a brand's current AEO infrastructure across all 7 layers
2. **Map** which brands AI platforms recommend (and in what position) for any category
3. **Track** position changes week over week
4. **Build** the missing infrastructure (Answer Hub, brand-facts.json, schema, citations)
5. **Maintain** the system with a weekly 90-minute protocol

---

## When to Load This Skill

- User asks to "run an AEO audit" for a brand or URL
- User asks "which brands are being recommended by AI for [category]?"
- User asks to "build an Answer Intent Map" for a category
- User asks to check a brand's Answer Hub, brand-facts.json, or schema markup
- User asks to track AI recommendation positions over time
- User asks to run the "weekly AEO maintenance protocol"

---

## The 7-Layer AEO Framework

| Layer | Name | What It Is | Priority |
|-------|------|-----------|---------|
| 1 | Answer Intent Map | Spreadsheet of all purchase-intent queries + which brands AI recommends | Foundation |
| 2 | Answer Hub | A long-form guide page that answers every key question in your category | High |
| 3 | Brand-Facts Page | Human-readable brand facts page (neutral, factual, cite-able) | High |
| 4 | brand-facts.json | Machine-readable brand data at `/.well-known/brand-facts.json` | Medium |
| 5 | Schema Markup | Product, FAQ, and Organization structured data | Medium |
| 6 | Citation Network | Getting listed on the sources AI models actually cite | High |
| 7 | GPT Shopping | Google Merchant Center + review feed for AI shopping results | High |

---

## Prerequisites

**Required:**
- `PERPLEXITY_API_KEY` — enables direct API queries (get free at perplexity.ai/settings/api)
- Node.js v18+ (for the `answer-intent-map.js` script)

**Optional:**
- `OPENAI_API_KEY` — enables ChatGPT query automation
- `BRAVE_API_KEY` — enables web searches for infrastructure checks

**Without API keys:** The skill runs in "manual-assist" mode — generates the queries, provides a blank log template, and analyzes results you paste in.

---

## Core Workflows

### Workflow 1: Full AEO Audit

**Trigger:** "Run an AEO audit for [brand URL]"

**Steps:**

1. Fetch and analyze the brand's website for AEO infrastructure:
   - Check for Answer Hub page (`/guides/` or similar long-form page)
   - Check for Brand-Facts page (`/brand-facts`)
   - Check for machine-readable data (`/.well-known/brand-facts.json`)
   - Audit schema markup on product pages (via Rich Results API or web_fetch)
   - Check for a Wikidata entry
   - Check Google Merchant Center eligibility signals

2. Score each of the 7 layers (0–3 scale):
   - **0** = Doesn't exist
   - **1** = Exists but incomplete or outdated
   - **2** = Exists, functional, minor gaps
   - **3** = Complete, current, optimized

3. Generate a gap analysis report with:
   - Current score per layer
   - Priority order for implementation
   - Specific action items for each missing layer

**Output:** Markdown report saved as `aeo-audit-[brand]-[date].md`

---

### Workflow 2: Answer Intent Map

**Trigger:** "Build an Answer Intent Map for [category]" or run `scripts/answer-intent-map.js`

**Steps:**

1. Generate query list from four types:
   - **Category queries:** "best [product] for [use case]" (10–15 queries)
   - **Comparison queries:** "[brand] vs [competitor]" (10 queries)
   - **Brand queries:** "is [brand] worth it" (5 queries)
   - **Educational queries:** "does [ingredient] help with [condition]" (10 queries)

2. For each query, query available platforms:
   - Perplexity API (structured JSON response with citations)
   - OpenAI API (text response — brand names extracted by parser)
   - Browser fallback for Claude and Gemini

3. Parse responses to extract:
   - Brand names mentioned (position 1, 2, 3)
   - Source URLs cited
   - Key verbatim quotes

4. Write results to JSON data file + Markdown summary report

**Output:** `answer-intent-map-[category]-[date].json` + `.md` summary

**Run the script:**
```bash
node scripts/answer-intent-map.js \
  --category "magnesium supplements" \
  --brand "MyBrand" \
  --queries 20

# Or with a config file:
node scripts/answer-intent-map.js --config ./aeo-config.json
```

---

### Workflow 3: Weekly Maintenance Protocol

**Trigger:** "Run weekly AEO maintenance" or scheduled cron

**Steps:**

1. Load the brand's Answer Intent Map (top 15 priority queries)
2. Query ChatGPT and Perplexity for each priority query in fresh sessions
3. Compare results against previous week's log (detect position changes)
4. Generate maintenance report:
   - Position changes (up/down/new competitors)
   - New sources being cited this week
   - Recommended Answer Hub updates
5. Check `brand-facts.json` for stale `lastUpdated` timestamp
6. Check Google Merchant Center for disapprovals (via browser if needed)

**Output:** `aeo-weekly-report-[date].md`

**Use the checklist:** `templates/weekly-maintenance-checklist.md`

---

### Workflow 4: Citation Network Analysis

**Trigger:** "Analyze AEO citations for [category]"

**Steps:**

1. Run 20 category queries via Perplexity API (citations returned directly)
2. Extract all unique source URLs from responses
3. Group and count by domain
4. Identify top 10 most-cited external sources in the category
5. Generate outreach priority list

**Output:** Citation analysis report with target sites ranked by citation frequency

---

### Workflow 5: Infrastructure Build

**Trigger:** "Build AEO infrastructure for [brand]" or "Set up brand-facts.json"

**Steps:**

1. Ask for brand details (or load from `aeo-config.json`)
2. Generate from templates:
   - `brand-facts.json` → `templates/brand-facts.json` (fill placeholders)
   - Answer Hub page → `templates/answer-hub-template.md`
   - Schema markup snippet (JSON-LD for product pages)
3. Provide implementation instructions per asset

---

## Configuration

Create `aeo-config.json` in your working directory:

```json
{
  "brandName": "Your Brand Name",
  "brandUrl": "https://yourbrand.com",
  "category": "Magnesium Supplements",
  "priorityQueries": [
    "best magnesium supplement for sleep",
    "best magnesium glycinate supplement",
    "magnesium supplement for anxiety"
  ],
  "competitors": [
    "Competitor Brand A",
    "Competitor Brand B",
    "Competitor Brand C"
  ],
  "answerHubUrl": "https://yourbrand.com/guides/best-magnesium-supplements-2026",
  "brandFactsJsonUrl": "https://yourbrand.com/.well-known/brand-facts.json"
}
```

---

## Output Files

| File | Description |
|------|-------------|
| `aeo-audit-[brand]-[date].md` | Infrastructure audit report |
| `answer-intent-map-[category]-[date].json` | Raw AI query results |
| `answer-intent-map-[category]-[date].md` | Human-readable competitive summary |
| `aeo-weekly-report-[date].md` | Weekly maintenance report |
| `citation-analysis-[category]-[date].md` | Citation network analysis |

---

## Usage Examples

```
# Full infrastructure audit
"Run an AEO audit for mybrand.com"

# Build competitive intelligence
"Build an Answer Intent Map for the magnesium supplement category"

# Quick position check
"Check if mybrand.com is being recommended by Perplexity for 'best magnesium for sleep'"

# Weekly maintenance
"Run the weekly AEO maintenance protocol for my brand"

# Citation analysis
"Which sources does Perplexity cite most for collagen supplement recommendations?"

# Generate brand-facts.json
"Generate the brand-facts.json template for [brand details]"

# Scoring review
"Score my AEO infrastructure for mybrand.com on all 7 layers"
```

---

## Platform Limitations

| Platform | Access | Notes |
|----------|--------|-------|
| Perplexity | API (structured, reliable) | Returns citations directly |
| ChatGPT | API via OpenAI | Text parsing required for brand extraction |
| Claude | Browser required | Generate queries + blank log; agent uses browser |
| Gemini | Browser required | Generate queries + blank log; agent uses browser |

For Claude/Gemini: the skill generates the query list and a blank log template; use the browser tool to collect results.

**Rate limits:** Perplexity free tier ≈ 20 requests/minute. For 50+ queries, add `--delay 3000` to the script.

---

## File Structure

```
aeo-system/
├── SKILL.md                              ← This file
├── README.md                             ← Human-readable overview
├── scripts/
│   └── answer-intent-map.js              ← Core query automation script
└── templates/
    ├── answer-hub-template.md            ← Answer Hub page template
    ├── brand-facts.json                  ← Machine-readable brand data template
    └── weekly-maintenance-checklist.md  ← 90-minute weekly protocol
```

---

*AEO System v1.0 — February 2026*
*A product by Carson Jarvis (@CarsonJarvisAI)*
