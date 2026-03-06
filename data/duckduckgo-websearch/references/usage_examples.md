Trigger examples and expected behavior

- "Search web for 'latest K-POP comeback 2026' and give me top 5 links with short snippets."
  - Skill should return JSON with summary (if available) and 5 links.

- "Find tutorials for Django channels and summarize top resource."
  - Skill should return top links and, if requested, an optional follow-up fetch+summary of the landing page.

- "DuckDuckGo: what's the gist of X?"
  - Skill should prefer Instant Answer summary if present; otherwise return top SERP links.

Notes for callers
- To request a page summary, call the skill for the chosen link and use a separate page-summarize helper (not bundled here) to fetch and summarize the HTML body.
- Keep queries concise. For long, complex research tasks, prefer iterative queries and follow-ups.
