# Tool Selection Guide

## The Core Principle

**web_search finds URLs. web_fetch and browser-use find answers.**

If you're spending more time searching than reading, you're not researching — you're asking Perplexity to do your work. Perplexity lies. Read the actual pages.

## When to use what

### web_search (Perplexity Sonar)
**Purpose:** Finding URLs to read. That's it.
**Process:** Fire query → extract citation URLs from response → add to URL queue → IGNORE the synthesized text.
**NEVER use as:** A source of truth. An answer engine. A substitute for reading.

⛔ When web_search returns, do NOT read the synthesis paragraph. Scroll to the citations array. Copy the URLs. Add them to your queue. Move on.

Why this matters: Sonar fabricates quotes, hallucinates Reddit threads, presents unverified claims as consensus. If you read the synthesis, you'll unconsciously treat it as research. It's not. It's noise with URLs attached.

### web_fetch
**Best for:** Reading specific pages — reviews, forum threads, product specs, articles, official docs
**Strengths:** Fast, gets actual page content, good for extracting specific data
**Weaknesses:** Blocked by some sites (Amazon, Reddit, JS-heavy SPAs)
**Always:** Set maxChars (5000-10000), extract only what you need

### browser-use (via exec)
**Best for:** JS-rendered sites, login-gated forums, sites that block web_fetch, multi-step navigation
**Remember:** 3 modes — chromium (free) → real (free) → remote (paid). Try ALL 3.
**Setup:** `browser-use --session {name} open/click/type/eval/extract/close`

## Combination Strategies

All strategies follow the **Read-Driven Loop**: URL queue → read pages → extract findings + new URLs → loop.

### Topic Research (legal, technical, domain-specific)
1. web_search → find authoritative pages and forum threads (URLS ONLY)
2. web_fetch → read them. Note: what sources/cases/rules do they reference?
3. Follow those references → web_fetch the cited sources
4. web_search for edge cases and forum experiences (URLS ONLY)
5. web_fetch → read actual forum threads
6. browser-use → crack any login-gated forums

### Anecdote/Experience Research
1. web_search with FIRST-PERSON queries: `"my experience with"`, `"I tried"`, `"what happened when I"`
2. Extract forum thread URLs from citations
3. web_fetch → read threads (try old.reddit.com for Reddit)
4. browser-use → login-gated forum eval extraction, Reddit if blocked
5. Follow thread links to related threads
6. Search in other languages if relevant

### Product Research
1. web_search → find review pages and forum threads (URLS ONLY)
2. web_fetch → read top 3-5 review pages
3. For each product found → new searches + reads
4. web_fetch → read Reddit/forum threads for real user experiences
5. browser-use → hit retailer sites for verified prices
6. Cross-verify prices across multiple retailers

### Price Comparison
1. web_search → identify which retailers carry the product
2. browser-use → scrape actual retailer pages (with --profile)
3. web_fetch → price tracking sites (CamelCamelCamel, Idealo, etc.)
4. Follow deal/alternative links found on pages
