---
name: aeo-content-free
description: >
  Create or refresh AEO-optimized content that gets cited by AI assistants (Gemini, ChatGPT,
  Perplexity) using only free tools. Two modes: CREATE new content targeting a specific prompt,
  or REFRESH existing content to improve AI citation-worthiness. Researches what AI models
  currently cite, builds a competitive brief, and produces citation-worthy content.
  Use when a user wants to: write content optimized for AI citations, create articles that
  show up in AI answers, refresh/update existing content for better AI visibility, build
  authority content for answer engines, or produce AEO content without paid tools.
  No API keys required — uses web_fetch, web_search (free tier), and LLM reasoning only.
  Pairs with aeo-prompt-research-free (which identifies WHAT to write about; this skill
  handles HOW to write or refresh it).
---

# AEO Content Skill (Free)

> **Source:** [github.com/psyduckler/aeo-skills](https://github.com/psyduckler/aeo-skills/tree/main/aeo-content-free)
> **Part of:** [AEO Skills Suite](https://github.com/psyduckler/aeo-skills) — [Prompt Research](https://github.com/psyduckler/aeo-skills/tree/main/aeo-prompt-research-free) → Content → [Analytics](https://github.com/psyduckler/aeo-skills/tree/main/aeo-analytics-free)

Create or refresh content that AI assistants want to cite — using zero paid APIs.

## Requirements

- `web_fetch` — analyze currently-cited sources and existing content
- `web_search` — find competing content (Brave free tier, optional)
- LLM reasoning — research, brief, draft, and evaluate

## Mode Detection

- **Create mode** — User provides a target prompt but no existing URL → write new content
- **Refresh mode** — User provides an existing page URL (+ optional target prompt) → audit and update

## Input

- **Target prompt** (required for create, optional for refresh) — the AI prompt this content should win
- **Brand/domain** (required) — who the content is for
- **Existing URL** (refresh mode) — the page to update
- **Topic context** (optional) — additional info about the brand's angle
- **Content type** (optional) — guide, comparison, how-to, explainer

---

## Create Mode Workflow

### Step 1: AI Landscape Research

Search the target prompt and close variants to understand the current answer landscape:

1. **Web search the exact prompt** — search engines show similar sources to what AI cites
2. **`web_fetch` the top 5-10 results** — these are the pages AI models draw from
3. **`web_search` for `"[topic]" site:reddit.com`** — find real user questions and discussions

For each top-ranking page, extract:
- Main points and structure
- Unique data, frameworks, or insights
- Gaps — what they miss or get wrong
- Freshness — when was it last updated?

### Step 2: Build the Content Brief

Use the template in `references/content-brief-template.md` to structure research.

Key decisions:
- **Mandatory topics** — every sub-topic the AI currently covers in its answer
- **Unique value angle** — what will this content add that no current source provides? (Most important decision.)
- **Content structure** — outline with H2/H3 headings that mirror question phrasing
- **Target specs** — word count, format, tone

### Step 3: Write Citation-Worthy Content

Draft following citation signals from `references/citation-signals.md`. Key principles:

- Lead each section with a direct, quotable 1-2 sentence answer
- Use descriptive headings that match question phrasing
- Include original data, frameworks, or expert perspective
- Name specific tools, companies, people, statistics
- Cover every sub-question the AI currently answers, then go deeper on 2-3 areas
- Cut fluff — every paragraph earns its place

### Step 4: Self-Evaluate

Before delivering, check the draft against currently-cited sources:

1. **Coverage** — addresses every topic the top sources cover?
2. **Depth** — goes deeper on at least 2-3 areas?
3. **Uniqueness** — offers something no current source has?
4. **Extractability** — AI can pull a direct answer from each section?
5. **Entity richness** — specific names, tools, numbers throughout?
6. **Freshness** — examples, data, references are current?

### Step 5: Deliver with Publishing Guidance

Output final content plus title, meta description (150-160 chars), and:
- Add publication date + author byline with credentials
- Ensure page is indexable (no noindex, no paywall)
- Add schema markup if applicable (FAQ, HowTo, Article)
- Internal link from existing related content
- Re-check target prompt in AI models 2-4 weeks after indexing

---

## Refresh Mode Workflow

### Step R0: Audit the Existing Page

Before any landscape research, analyze the current page:

1. **`web_fetch` the existing URL** — get the full content
2. Extract current structure: headings, topics covered, depth per section
3. Note: publication date, last updated date, author info
4. Check freshness: outdated stats, old tool names, expired examples, stale references
5. Identify what's already strong (keep these sections)

### Step R1: AI Landscape Research

Same as Create Step 1 — research what AI models currently cite for the target prompt. If no target prompt was provided, infer it from the page's topic and title.

### Step R2: Gap Analysis (Diff)

Compare existing content against the competitive landscape:

- **Missing topics** — sub-topics AI covers that the page doesn't → flag for addition
- **Outdated info** — old statistics, discontinued tools, expired examples → flag for replacement
- **Missing entities** — competitors, tools, people the AI mentions that the page doesn't → flag for inclusion
- **Structural issues** — buried answers, vague headings, no clear extractable statements → flag for restructure
- **Freshness gaps** — old dates, prior-year references → flag for update
- **Strengths to preserve** — sections already well-written, potentially already cited → keep as-is

Output: a prioritized list of changes with rationale for each.

### Step R3: Edit (Not Rewrite)

Apply changes surgically:

- **Add** new sections for coverage gaps (place them logically in the existing structure)
- **Update** outdated data points, examples, tool names, statistics
- **Restructure** weak sections — add extractable lead sentences, improve headings
- **Weave in** missing entities naturally (don't keyword-stuff)
- **Preserve** sections that are already strong
- **Update** publication/modified date

Output the refreshed content with clear markup showing changes:
- `[ADDED]` — new sections or paragraphs
- `[UPDATED]` — modified existing content
- `[RESTRUCTURED]` — reorganized for better extractability
- `[UNCHANGED]` — kept as-is (note why it's strong)

### Step R4: Before/After Summary

Provide a clear comparison:
- What was added (new sections, topics, entities)
- What was updated (stats, examples, references)
- What was restructured (headings, lead sentences)
- What was removed (outdated info)
- Expected impact on citation-worthiness

### Step R5: Self-Evaluate + Deliver

Same 6-point evaluation as Create Step 4, plus:
- Does the refresh maintain the page's existing voice and style?
- Are all internal/external links still valid?
- Is the updated date reflected?

Deliver with the same publishing guidance as Create Step 5.

---

## Tips

- The unique value angle is make-or-break for both modes
- For refresh: resist the urge to rewrite everything. Surgical edits that add missing pieces are more efficient and preserve existing authority
- First-party data is the strongest citation signal — if the brand has relevant data, use it prominently
- For comparison prompts ("X vs Y"), be balanced — AI models avoid citing biased sources
- Shorter, sharper content that directly answers the prompt beats long rambling pieces
- This skill pairs with `aeo-prompt-research-free` which identifies target prompts
