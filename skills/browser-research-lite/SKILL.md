---
name: browser-research-lite
description: |
  API-key-free online research via the built-in browser tool.
  Use this skill when web_search fails due to missing keys, and you still need web evidence.
---

# Browser Research Lite

Goal: perform reliable web retrieval without Brave/Tavily/Serper API keys.

## When To Use

- `web_search` reports key/config errors (for example: `missing_brave_api_key`).
- You need factual lookup, definitions, theorem statements, or reference pages.
- Benchmark tasks need external evidence but remote search APIs are unavailable.

## Core Policy

- Use local computation tools first for computable questions.
- If online retrieval is required, use the built-in `browser` tool directly.
- Prefer trusted sources (official docs, textbooks, university pages, Wikipedia as secondary).
- Cross-check at least 2 sources for non-trivial claims.

## Browser Workflow

1. Run browser availability guard first:

```bash
python3 skills/browser-research-lite/scripts/browser_guard.py
```

2. If `browser_available=false`, stop browser retries and switch to local tools.
   - If `browser_running=false` or `browser_cdp_ready=false`, attach browser manually:
     - open any page in Chrome with OpenClaw extension installed,
     - click the OpenClaw extension icon once to attach current tab,
     - rerun `browser_guard.py`.
3. If `browser_available=true`, open a search page with concise query terms.
4. Scan top results and open 2-3 high-quality sources.
5. Extract only the minimal facts needed to answer the question.
6. If pages are noisy, refine query with exact keywords and retry once.
7. Produce final answer with concise rationale; avoid copying long passages.

## Fallbacks

- If browsing is blocked/captcha-heavy, switch to alternative domains and shorter queries.
- If browser node is unavailable, avoid repeated browser calls in the same question.
- If browser remains unavailable, switch to `skills/web-fetch-research-lite/SKILL.md` and run URL-first retrieval via `web_fetch`.
- If no reliable source is found quickly, return best-effort answer and mark uncertainty.

## Solidify Note

When this skill improves benchmark progress, record:

- trigger signal(s),
- source quality and retrieval steps,
- measurable effect on benchmark score/accuracy.

