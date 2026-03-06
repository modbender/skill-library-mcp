---
name: exa
description: Use when tasks need Exa MCP for web or people research, or when preparing Exa MCP server configuration with a fixed tool set. Trigger for requests to run Exa search, advanced Exa search, people search, or summarize Exa-based findings with source links.
---

# Exa MCP Skill

## Workflow
1. Clarify the research goal, scope, and output format.
2. Select one enabled tool using the guide below: `web_search_exa`, `web_search_advanced_exa`, `people_search_exa`.
3. Prefer the hosted Exa MCP endpoint with fixed tools in the URL query.
4. Return concise findings with links and explicit unknowns.
5. On rate limits (`429`), reduce query breadth or require an API key.

## Tool Policy
- Enabled now: `web_search_exa`, `web_search_advanced_exa`, `people_search_exa`.
- Keep all other Exa tools disabled unless the user explicitly asks to expand.

## Tool Selection Guide
- Use `web_search_exa` for fast, broad discovery when the user asks general web research.
  Example intent: "Find the latest docs and announcements about X."
- Use `web_search_advanced_exa` for precision research when you must constrain by domains, freshness, depth, or richer query controls.
  Example intent: "Search only official docs and recent sources for X."
- Use `people_search_exa` when the task is about identifying people, roles, background, or profile-style information.
  Example intent: "Find people working on X at company Y."

## Selection Rules
- Start with `web_search_exa` when speed and coverage matter more than strict filtering.
- Choose `web_search_advanced_exa` when `web_search_exa` returns noisy or insufficiently targeted results.
- Choose `people_search_exa` only for person-centric requests, not generic topic research.

## Config Reference
- Read `references/exa-mcp-setup.md` for URL templates and generic MCP snippets.
