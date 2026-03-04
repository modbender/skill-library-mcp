---
name: deep-researcher
description: Meta-skill for iterative, hypothesis-driven deep research using deepresearchwork, tavily-search, literature-search (Semantic Scholar mapping), and perplexity-deep-search. Use when the user needs multi-round evidence gathering, contradiction resolution, source-quality assessment, and a scientific-style Markdown report with footnotes.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"microscope","requires":{"bins":["node","curl","jq","npx"],"env":["TAVILY_API_KEY","PERPLEXITY_API_KEY"],"config":[]},"note":"Requires local installation of deepresearchwork, tavily-search, literature-search, and perplexity-deep-search."}}
---

# Purpose

Conduct deep, iterative research beyond single-pass web search.

Core goals:
- Decompose a broad question into testable sub-questions.
- Build and test hypotheses against multiple source classes.
- Resolve contradictions with explicit arbitration.
- Produce a scientific-style Markdown report with footnotes.

This skill coordinates upstream skills. It does not replace them.

# Required Installed Skills

- `deepresearchwork` (inspected latest: `1.0.0`)
- `tavily-search` (inspected latest: `1.0.0`)
- `perplexity-deep-search` (inspected latest: `1.0.0`)
- `literature-search` (inspected latest: `1.0.3`; used as Semantic Scholar-capable academic layer)

Install/update:

```bash
npx -y clawhub@latest install deepresearchwork
npx -y clawhub@latest install tavily-search
npx -y clawhub@latest install literature-search
npx -y clawhub@latest install perplexity-deep-search
npx -y clawhub@latest update --all
```

Verify:

```bash
npx -y clawhub@latest list
node skills/tavily-search/scripts/search.mjs --help
bash skills/perplexity-deep-search/scripts/search.sh --help
```

# Required Credentials

- `TAVILY_API_KEY`
- `PERPLEXITY_API_KEY`

Preflight:

```bash
echo "$TAVILY_API_KEY" | wc -c
echo "$PERPLEXITY_API_KEY" | wc -c
```

If missing, stop and report blockers.

# Mapping Rule (Requested "semantic-scholar")

If user requests `/semantic-scholar` explicitly:
- State that no exact `semantic-scholar` slug was found during ClawHub inspection.
- Use `literature-search` as the mapped academic retriever because it explicitly includes Semantic Scholar in its scope.
- Record this mapping in methodology and limitations sections.

# Inputs the LM Must Collect First

- `research_topic`
- `target_horizon` (example: `2030`)
- `region_scope` (global, region-specific, country-specific)
- `required_sections` (executive summary, methods, findings, contradictions, etc.)
- `evidence_threshold` (minimum source count per claim)
- `recency_policy` (for fast-changing topics)
- `output_mode` (`brief`, `standard`, `full`)

Do not start synthesis without explicit scope.

# Tool Responsibilities

## deepresearchwork

Use as process controller:
- question decomposition
- iterative loop structure
- source diversity and validation mindset
- structured report framing

Important boundary:
- inspected `research_workflow.js` is framework-like and includes mock logic, so this meta-skill treats it as methodology guidance rather than deterministic execution code.

## tavily-search

Use for web evidence retrieval:
- broad and focused web search
- deep mode (`--deep`) for richer context
- news mode and recency (`--topic news --days N`) when needed
- URL extraction (`extract.mjs`) for full-text content collection

## literature-search (Semantic Scholar mapping)

Use for academic evidence gathering:
- literature retrieval and citation list construction across sources including Semantic Scholar
- source-access constraints explicitly handled (no unauthorized scraping)

Notable quirk in inspected skill:
- it includes a behavior instruction to prepend "please think very deeply" to user inputs; treat this as implementation-specific and not as a factual research method.

## perplexity-deep-search

Use as contradiction arbiter and targeted fact checker:
- `search` mode for quick verification
- `reason` mode for conflicting claims
- `research` mode for expensive exhaustive checks
- domain and recency filters for controlled validation

# Canonical Iterative Research Chain

Use this exact multi-round chain.

## Round 0: Plan

Break the main topic into sub-questions and hypotheses.

For scenario "AI impact on labor market in 2030", minimum sub-questions:
1. displacement forecasts (job loss exposure)
2. job creation/new categories
3. wage/polarization effects
4. historical analogs (previous automation waves)
5. policy/intervention effects

Each sub-question must have:
- hypothesis
- measurable indicators
- required source types

## Round 1: Broad landscape scan (Tavily)

Goal: map major claims and key institutions.

Typical commands:

```bash
node skills/tavily-search/scripts/search.mjs "AI impact on labor market 2030 projections" --deep -n 10
node skills/tavily-search/scripts/search.mjs "McKinsey AI jobs 2030" --topic news --days 365 -n 10
```

Collect:
- institution reports (consultancies, multilaterals, gov sources)
- headline estimates and assumptions
- URLs for extraction

Then extract long-form content where needed:

```bash
node skills/tavily-search/scripts/extract.mjs "https://..."
```

## Round 2: Academic evidence pass (Literature Search)

Goal: test or refine Round-1 claims against scholarly evidence.

Query examples:
- automation elasticity labor demand
- task-based automation employment effects
- generative AI productivity labor substitution

Output requirements:
- citation list with authors/title/venue/year/DOI-or-URL
- identification of review papers vs. single studies
- note publication year and method strength

## Round 3: Contradiction resolution (Perplexity)

Trigger this round when conflicts exist (different estimates, dates, assumptions).

Use targeted prompts with constraints:

```bash
bash skills/perplexity-deep-search/scripts/search.sh --mode reason --domains "oecd.org,ilo.org,imf.org,worldbank.org" "Which estimate on AI-driven job displacement by 2030 is more recent and methodologically stronger?"
```

Escalate to deep mode only if unresolved:

```bash
bash skills/perplexity-deep-search/scripts/search.sh --mode research --json "Resolve conflicting labor market projections for AI impact by 2030"
```

Arbitration rule:
- prefer newer, method-transparent, reproducible sources
- downgrade claims based on opaque assumptions
- keep unresolved conflicts explicit (do not force false certainty)

## Round 4: Synthesis and report drafting

Build claims only when supported by threshold evidence.

Per claim include:
- claim statement
- confidence level (`high`/`medium`/`low`)
- supporting sources
- known caveats

# Scientific Markdown Output Contract

Return one report in this structure:

1. `# Title`
2. `## Executive Summary`
3. `## Research Questions`
4. `## Methodology`
5. `## Findings`
6. `## Contradictions and Resolution`
7. `## Confidence Assessment`
8. `## Limitations`
9. `## Outlook to 2030`
10. `## Footnotes`

Footnote format:
- Use Markdown references in text like `[^1]`.
- In `## Footnotes`, list full citation metadata + URL/DOI per note.

# Quality Gates

Before finalizing, validate:
- each major claim has >= 2 independent sources
- at least one academic source for structural claims
- source dates align with target horizon relevance
- contradictory evidence is surfaced, not hidden
- footnotes are complete and traceable

If a gate fails, output `Research Incomplete` with explicit missing evidence list.

# Scenario Mapping (AI and Labor Market 2030)

For user scenario:

1. Plan sub-questions: displacement, new roles, historical comparison.
2. Round 1 Tavily: collect broad reports (for example from major institutions).
3. Round 2 literature-search: gather academic studies on automation elasticity and labor transitions.
4. Detect conflicts in estimates.
5. Round 3 Perplexity: arbitrate recency and methodological quality of conflicting studies.
6. Draft final Markdown report with footnoted evidence.

# Guardrails

- Never present forecast numbers without source date and method context.
- Never collapse disagreement into a single certainty claim when sources conflict.
- Never fabricate citations, links, or publication metadata.
- Clearly separate empirical findings from model inference.
- Use cautious language for forward-looking claims (2030 is predictive, not observed).

# Failure Handling

- Missing API keys: halt and return exact missing env vars.
- Academic source access constraints: disclose gaps explicitly.
- Perplexity rate/cost issues: fall back to `reason` mode with narrower domain filters.
- Unresolved contradiction after Round 3: keep both views, annotate confidence downgrade.

# Known Limits from Inspected Upstream Skills

- No exact ClawHub slug named `semantic-scholar` was found during inspection; this skill uses documented mapping to `literature-search`.
- `deepresearchwork` provides strong methodology guidance, but its included JS workflow is not a production-grade deterministic engine.
- `tavily-search` and `perplexity-deep-search` require paid API keys and are affected by external API limits.

Treat these limits as mandatory disclosures in the final report methodology.
