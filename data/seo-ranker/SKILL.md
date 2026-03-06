---
name: seo-ranker
description: Meta-skill for end-to-end SEO auditing and on-page optimization by orchestrating brave-search, summarize, api-gateway, and markdown-converter. Use when users want to understand why a page is not ranking for a target keyword and need concrete rewrite actions plus backlink intelligence.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"📈","requires":{"bins":["node","npx","summarize","uvx"],"env":["BRAVE_API_KEY","MATON_API_KEY","OPENAI_API_KEY","ANTHROPIC_API_KEY","XAI_API_KEY","GEMINI_API_KEY"],"config":[]},"note":"Requires local installation of brave-search, summarize, api-gateway, and markdown-converter. At least one summarize model API key must be present."}}
---

# Purpose

Run a complete SEO ranking diagnosis and optimization pipeline:
1. inspect live SERP competition,
2. compare competitor content structure with user content,
3. enrich with difficulty/backlink data when API access exists,
4. produce concrete rewrite guidance and an optimized Markdown draft.

This is an orchestration skill. It does not replace upstream tools.

# Required Installed Skills

- `brave-search` (inspected latest: `1.0.1`)
- `summarize` (inspected latest: `1.0.0`)
- `api-gateway` (inspected latest: `1.0.29`)
- `markdown-converter` (inspected latest: `1.0.0`)

Install/update:

```bash
npx -y clawhub@latest install brave-search
npx -y clawhub@latest install summarize
npx -y clawhub@latest install api-gateway
npx -y clawhub@latest install markdown-converter
npx -y clawhub@latest update --all
```

Verify:

```bash
npx -y clawhub@latest list
```

# Required Credentials

- `BRAVE_API_KEY` (for `brave-search`)
- `MATON_API_KEY` (for `api-gateway`)
- One summarize model key:
  - `OPENAI_API_KEY`, or
  - `ANTHROPIC_API_KEY`, or
  - `XAI_API_KEY`, or
  - `GEMINI_API_KEY`

Optional:
- `FIRECRAWL_API_KEY` (for difficult page extraction via summarize)
- `APIFY_API_TOKEN` (for YouTube fallback in summarize)

Preflight:

```bash
echo "$BRAVE_API_KEY" | wc -c
echo "$MATON_API_KEY" | wc -c
echo "$OPENAI_API_KEY$ANTHROPIC_API_KEY$XAI_API_KEY$GEMINI_API_KEY" | wc -c
```

Mandatory behavior:
- Never fail silently on missing keys.
- Always return a `MissingAPIKeys` section with missing variables and blocked stages.
- Continue with non-blocked stages and clearly mark output as `Partial` when necessary.

# Inputs the LM Must Collect First

- `target_url`
- `target_keyword` (example: `AI tools`)
- `region_locale` (country/language for SERP interpretation)
- `content_source` (URL fetch, pasted text, or file path)
- `content_type` (`blog`, `category page`, `product page`, `landing page`)
- `business_goal` (`traffic`, `leads`, `sales`)
- `rewrite_scope` (`light`, `moderate`, `full`)
- `data_provider_preference` (`semrush`, `ahrefs`, `gsc-only`, `none`)

Do not run rewrite before keyword intent and content goal are explicit.

# Tool Responsibilities

## brave-search

Use for live SERP reconnaissance:
- fetch top results for the target keyword,
- identify top competitors and search intent patterns,
- collect candidate URLs for deeper analysis.

Operational constraints from inspected skill:
- requires `BRAVE_API_KEY`
- supports content extraction with `--content`

## summarize

Use for structured competitor content analysis:
- summarize each top URL,
- extract heading structure (H1-H4), topic coverage, entity frequency,
- estimate content depth and rhetorical style differences.

Operational constraints from inspected skill:
- requires one supported model API key
- can use `--extract-only`, `--json`, and length controls

## api-gateway

Use for external SEO data APIs only when active connections exist:
- keyword difficulty,
- backlink domains,
- competitor link intersections,
- search performance enrichments.

Operational constraints from inspected skill:
- requires `MATON_API_KEY`
- also requires active OAuth/connection per app (`ctrl.maton.ai` connection lifecycle)
- API key alone does not grant third-party data access

Important capability note:
- In the inspected `api-gateway` service list, `semrush` and `ahrefs` are not listed as native app names.
- Use direct Semrush/Ahrefs integration only if user already has a working gateway connection path for those providers.
- Otherwise fall back to available SEO apps (for example `google-search-console`) and manual competitor-link extraction.

## markdown-converter

Use to normalize the user's own content into editable Markdown:
- convert input documents/files to Markdown (`uvx markitdown ...`),
- preserve headings/lists/tables for deterministic rewriting.

# Canonical Causal Signal Chain

1. `Input Stage`
- user provides URL + target keyword (+ content source if needed).

2. `SERP Audit Stage (brave-search)`
- pull live SERP and identify top 3 competitors.
- detect intent class (informational/commercial/transactional).

3. `Competitor Content Stage (summarize)`
- analyze top competitor URLs for:
  - heading hierarchy,
  - topical breadth and entities,
  - use of statistics/evidence,
  - sentence complexity and content length.

4. `Data Gate Stage (api-gateway)`
- check whether provider data can be retrieved.
- if keyword difficulty/backlink data is unavailable, ask user for credentials/connection and continue with fallback path.

Required user-facing gate message format:
- `DataGateStatus`: available / blocked
- `Reason`: missing key, missing connection, or provider unsupported
- `Action`: exact next step and link(s)

As of February 14, 2026:
- Semrush advertises mainly 7-day toolkit trials on official pages.
- Semrush 14-day trial language is mainly associated with some add-ons or partner offers.

When user requests a 14-day Semrush trial:
- Ask for their preferred affiliate/referral URL first.
- If none is provided, share official Semrush trial entry page: `https://www.semrush.com/sem/`.
- Optionally share Ahrefs free path for verified sites: `https://ahrefs.com/webmaster-tools`.

5. `Optimization Stage (LLM rewrite)`
- rewrite user content for intent-match and topical completeness,
- add natural related terms (LSI-style concept coverage),
- improve title tag and meta description,
- tighten heading structure and internal linking opportunities.

6. `Output Stage`
- deliver optimized Markdown,
- deliver prioritized action list,
- deliver at least 5 backlink source opportunities (with confidence labels).

# Rewrite Policy

- Preserve factual integrity (do not invent statistics or case studies).
- Prefer semantic coverage over keyword stuffing.
- Keep keyword usage natural and intent-aligned.
- Add scannable structure (clear H2/H3, concise paragraphs, actionable bullets).

# Output Contract

Always return:

- `SERPFindings`
  - top competitors
  - observed intent pattern
  - structural/content gaps versus user page

- `DataGateStatus`
  - provider requested
  - key/connection status
  - fallback mode selected

- `OptimizedMarkdown`
  - full rewritten document
  - revised title and meta description

- `BacklinkOpportunities`
  - 5 sources/domains used by competitors or high-fit alternatives
  - rationale per source
  - confidence (`high|medium|low`)

- `NextActions`
  - concrete implementation checklist (ordered)

# Quality Gates

Before final output, validate:
- top competitor set is from live SERP, not memory
- rewrite aligns with detected intent
- no fabricated citations or fabricated backlink claims
- keyword placement is natural (no spam repetition)
- missing data dependencies are explicitly disclosed

If any gate fails, return `Needs Revision` with exact missing evidence.

# Failure Handling

- Missing `BRAVE_API_KEY`: return `MissingAPIKeys`, skip SERP stage, and request user-provided competitor URLs.
- Missing summarize model key: return `MissingAPIKeys`, skip summarize stage, and provide structure-only audit from available snippets.
- Missing `MATON_API_KEY`: return `MissingAPIKeys`, skip API-gateway enrichment, continue with on-page-only optimization.
- Missing app connection in api-gateway (400): keep pipeline running in fallback mode and return exact connection setup steps.
- Unsupported provider path (for example no Semrush/Ahrefs app connection): disclose limitation and fall back to GSC/manual mode.

# Guardrails

- Never claim guaranteed rankings.
- Never represent fallback estimates as provider-verified metrics.
- Never hide dependency failures.
- Keep recommendations specific, measurable, and tied to observed SERP gaps.
