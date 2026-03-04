---
name: duckduckgo-websearch
description: High-quality web search using DuckDuckGo (Instant Answer + SERP scraping fallback). Use when the user asks to search the web, fetch top results, or summarize web pages. Triggers for: (1) general web queries (news, facts, links), (2) site-specific searches, (3) short summaries of top results. Prefer this skill for private/offline-friendly search without Brave API keys.
---

# DuckDuckGo Websearch Skill

Purpose
- Provide a stable, privacy-minded websearch skill using DuckDuckGo's Instant Answer JSON API as primary source and a lightweight HTML SERP scrape as a fallback for richer link lists.
- Return structured results: concise summary (if available), top 5 links with titles and snippets, and optional short summary of a landed page when requested.

When to use
- Use this skill when the user asks to "search the web", "find links about X", "summarize search results for Y", or any task requiring quick web lookup without paid search APIs.
- Prefer the skill when privacy-friendly sources are acceptable and rate limits / API keys for other search providers are unavailable.

Design principles
- Progressive disclosure: SKILL.md contains the trigger and workflow. Detailed parsing and helpers are in scripts/ so the agent can execute them without loading large text.
- Fail gracefully: if Instant Answer returns limited data, the skill falls back to a minimal HTML fetch-and-parse to extract top results.
- Safety: avoid returning raw HTML; always sanitize snippets and obey robots (basic checks).

Bundled resources
- scripts/ddg_search.js — Node script that performs the search and returns JSON (summary, links[]). Executable by the agent when the skill is invoked.
- references/usage_examples.md — short examples of prompts that should trigger this skill.

Outputs
- JSON shape returned from scripts/ddg_search.js:
  {
    "query": "...",
    "summary": "short abstract or empty",
    "links": [ {"title":"...","url":"...","snippet":"..."}, ... up to 5],
    "source": "instant-answer|serp-fallback",
    "notes": "any warnings"
  }

Security & limits
- The script uses DuckDuckGo's public instant-answer endpoint (no key). For many queries this is enough; for others the SERP fallback will perform a lightweight HTML request. Respect rate limits and avoid heavy scraping.
- Do not follow or fetch pages that explicitly disallow crawling via robots.txt for automation-intended user agents.

Installation / Usage (for maintainer)
1. Place this skill in ~/.openclaw/workspace/skills/duckduckgo-websearch
2. Ensure node is available (Node 18+). The script has zero external dependencies (uses built-in https/http and node-html-parser).
3. Test manually:
   node scripts/ddg_search.js "query terms"

Trigger examples (see references/usage_examples.md)
- "Search DuckDuckGo for recent news about [topic] and give me top links."
- "Find the best tutorials for Django channels and summarize top results."


---
