---
name: aeo-analytics-free
description: >
  Track AI visibility — measure whether a brand is mentioned and cited by AI assistants
  (Gemini, ChatGPT, Perplexity) for target prompts. Runs scans, tracks mention/citation
  rates over time, detects trends, and identifies opportunities. Uses Gemini API free tier
  (with grounding) as primary method, web search as fallback.
  Use when a user wants to: check if AI models mention their brand, track AI citation
  changes over time, measure AEO content effectiveness, monitor competitor AI visibility,
  or audit their brand's presence in AI-generated answers.
  Pairs with aeo-prompt-research-free (identifies prompts) and aeo-content-free
  (creates/refreshes content). This skill closes the loop by measuring results.
---

# AEO Analytics (Free)

> **Source:** [github.com/psyduckler/aeo-skills](https://github.com/psyduckler/aeo-skills/tree/main/aeo-analytics-free)
> **Part of:** [AEO Skills Suite](https://github.com/psyduckler/aeo-skills) — [Prompt Research](https://github.com/psyduckler/aeo-skills/tree/main/aeo-prompt-research-free) → [Content](https://github.com/psyduckler/aeo-skills/tree/main/aeo-content-free) → Analytics

Track whether AI assistants mention and cite your brand — and how that changes over time.

## Requirements

- **Primary:** Gemini API key (free from aistudio.google.com) — enables grounding with source data
- **Fallback:** `web_search` only — weaker signal but zero API keys needed
- `web_fetch` — optional, for deeper analysis of cited pages

## Input

- **Domain** (required) — the brand's website (e.g., `tabiji.ai`)
- **Brand names** (required) — names to search for in responses (e.g., `["tabiji", "tabiji.ai"]`)
- **Prompts** (required for first scan) — list of target prompts to track. Can come from `aeo-prompt-research-free` output.
- **Data file path** (optional) — where to store scan history. Default: `aeo-analytics/<domain>.json`

## Commands

The skill supports three commands:

### `scan` — Run a new visibility scan

Execute all tracked prompts against the AI model and record results.

### `report` — Generate a visibility report

Analyze accumulated scan data and produce a formatted report.

### `add-prompts` / `remove-prompts` — Manage tracked prompts

Add or remove prompts from the tracking list.

---

## Scan Workflow

### Step 1: Load or Initialize Data

Check if a data file exists for this domain. If yes, load it. If no, create a new one.
See `references/data-schema.md` for the full JSON schema.

### Step 2: Run Prompts

For each tracked prompt:

**Method A — Gemini API with grounding (preferred):**
See `references/gemini-grounding.md` for API details.

1. Send prompt to Gemini API with `googleSearch` tool enabled
2. From the response, extract:
   - **Response text** — the AI's answer
   - **Grounding chunks** — the web sources cited (URLs + titles)
   - **Web search queries** — what the AI searched for

3. Analyze the response:
   - **Mentioned?** — Search response text for brand names (case-insensitive, word-boundary match)
   - **Mention excerpt** — Extract the sentence(s) containing the brand name
   - **Cited?** — Check if brand's domain appears in any grounding chunk URI
   - **Cited URLs** — List the specific brand URLs cited
   - **Sentiment** — Classify the mention context as positive/neutral/negative
   - **Competitors** — Extract other brand names and domains from response + citations

**Method B — Web search fallback (if no Gemini API key):**
1. `web_search` the exact prompt text
2. Check if brand's domain appears in search results
3. Record as "web-proxy" method (less direct than grounding)

### Step 3: Save Results

Append the scan results to the data file. Never overwrite previous scans — history is the whole point.

### Step 4: Quick Summary

After scanning, output a brief summary:
- Prompts scanned
- Current mention rate and citation rate
- Change vs. last scan (if applicable)
- Any notable changes (new mentions, lost citations)

---

## Report Workflow

### Per-Prompt Detail

For each tracked prompt, show:

```
1. "[prompt text]"
   Scans: [total] (since [first scan date])
   Mentioned: [count]/[total] ([%]) — [trend arrow] [trend description]
   Cited: [count]/[total] ([%])
   Latest: [✅/❌ Mentioned] + [✅/❌ Cited]
   Sentiment: [positive/neutral/negative]
   Competitors mentioned: [list]
```

If mentioned in latest scan, include the mention excerpt.
If not mentioned, note which sources were cited instead and rate the opportunity (HIGH/MEDIUM/LOW).

### Summary Section

```
VISIBILITY SCORE
  Brand mentioned: [X]/[total] prompts ([%]) in latest scan
  Brand cited: [X]/[total] prompts ([%]) in latest scan

TRENDS (last [N] days, [N] scans)
  Mention rate: [%] → [trend]
  Citation rate: [%] → [trend]
  Most improved: [prompt] ([old rate] → [new rate])
  Most volatile: [prompt] (mentioned [X]/[N] scans)
  Consistently absent: [list of prompts never mentioned]

COMPETITOR SHARE OF VOICE
  [Competitor 1] — mentioned in [X]/[total] prompts
  [Competitor 2] — mentioned in [X]/[total] prompts
  [Brand] — mentioned in [X]/[total] prompts

NEXT ACTIONS
  → [Prioritized recommendations based on gaps and trends]
```

### Recommendations Logic

- **High opportunity:** Prompt has 0% mention rate + no strong owner in citations → create content
- **Close to winning:** Prompt has mentions but no citations → refresh content for citation-worthiness
- **Volatile:** Mention rate between 20-60% → content exists but needs strengthening
- **Won:** Mention rate >80% + citation rate >50% → maintain, monitor for decay

---

## Data Management

- Data file location: `aeo-analytics/<domain>.json`
- Schema: see `references/data-schema.md`
- Each scan appends to the `scans` array — never delete history
- Prompts can be added/removed without affecting historical data
- When adding new prompts, they start with 0 scans (no backfill)

## Tips

- Run scans at consistent intervals (weekly or biweekly) for meaningful trend data
- After publishing new AEO content, wait 2-4 weeks for indexing before expecting changes
- Gemini's grounding results can vary run-to-run — that's normal. Aggregate data over multiple scans is more reliable than any single result
- Track 10-20 prompts max for a focused view. Too many dilutes the signal
- This skill completes the AEO loop: Research (aeo-prompt-research-free) → Create/Refresh (aeo-content-free) → Measure (this skill) → repeat
