# Inspected Upstream Skills

Directly inspected from ClawHub:

- `brave-search` latest `1.0.1`
- `summarize` latest `1.0.0`
- `api-gateway` latest `1.0.29`
- `markdown-converter` latest `1.0.0`

## Relevant Capability Notes

- `brave-search` requires `BRAVE_API_KEY` and supports both SERP retrieval and content extraction.
- `summarize` requires one model provider API key (OpenAI/Anthropic/xAI/Google aliases) and supports URL/file summarization with JSON output.
- `api-gateway` requires `MATON_API_KEY` and active per-app OAuth connections via Maton control plane.
- In the inspected `api-gateway` app list, `semrush` and `ahrefs` are not explicitly listed as native app names.
- `markdown-converter` uses `uvx markitdown` to normalize many source formats into Markdown.

## Data-Gate Link Notes (checked Feb 14, 2026)

- Official Semrush trial entry page: https://www.semrush.com/sem/ (commonly 7-day for major toolkits).
- Ahrefs free path for verified websites: https://ahrefs.com/webmaster-tools.
- If user requests a 14-day Semrush link, prefer user-provided affiliate/referral URL; otherwise disclose official-trial differences explicitly.
