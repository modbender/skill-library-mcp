# Inspected Upstream Skills

Directly inspected from ClawHub:

- `tavily-search` latest `1.0.0`
- `goplaces` latest `1.0.0`
- `api-gateway` latest `1.0.29`
- `shopify` latest `1.0.1` (marked under maintenance)

## Relevant Capability Notes

- `tavily-search` requires `TAVILY_API_KEY` and supports web search + URL extraction workflows.
- `goplaces` requires `GOOGLE_PLACES_API_KEY` and is suitable for local demand context, not social virality metrics.
- `api-gateway` requires `MATON_API_KEY` plus active app-specific OAuth connections via `ctrl.maton.ai`.
- `api-gateway` explicitly lists WooCommerce app routing; missing app connection returns HTTP 400 in documented error handling.
- Inspected `api-gateway` service list does not explicitly list Helium 10 or Jungle Scout as native app names.
- `shopify` skill currently states under maintenance; production deployment should prefer WooCommerce or manual fallback.
