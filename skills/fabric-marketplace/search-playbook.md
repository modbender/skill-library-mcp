# Search Playbook

Search is credit-metered. Every search costs credits, so your goal is to **find what you need in as few searches as possible** while spending as little as possible.

## Cost structure

| Action | Cost |
|---|---|
| Base search (page 1) | 5 credits |
| Targeted follow-up (same query, refined filters) | 1 credit |
| Pages 2–5 | 2–5 credits each |
| Page 6+ | 100 credits per page (anti-scrape) |
| Category drilldown (pages 1–10) | 1 credit/page |
| Category drilldown (page 11+) | 5 credits/page |

**Key insight:** Deep pagination is deliberately expensive. If you're paging past page 5, you're doing it wrong. Refine your query instead.

## The budget contract

Every search requires `budget.credits_requested` — a hard ceiling on what you'll spend.

- If cost ≤ budget: you get results and pay the actual cost
- If cost > budget: HTTP 200 with `was_capped=true`, zero items, and guidance on how many credits you'd actually need. **You're never charged more than you authorize.**
- If your balance is below the cost: HTTP 402 `credits_exhausted` with `credit_pack_options` to purchase more

**Strategy:** Start with `credits_requested: 10` for your first search. Only increase if you see `was_capped: true`.

## Search strategy: narrow → broaden → pivot

### 1. Start narrow

Use the most specific scope, category, and keyword combination you can:

```json
{
  "q": "A100 GPU hourly",
  "scope": "remote_online_service",
  "filters": { "category_ids": [8], "scope_notes": "GPU" },
  "budget": { "credits_requested": 10 },
  "limit": 20,
  "cursor": null
}
```

**Cost: 5 credits.** If this returns good results, you're done.

### 2. Broaden if too few results

Drop one filter at a time, in order of least specificity:
1. Remove `scope_notes` keyword filter
2. Widen `scope` (e.g., from `remote_online_service` to null)
3. Remove `category_ids`
4. Widen `q` to fewer/broader terms

Each broadening step is a new search (5 credits), not a pagination.

### 3. Pivot if wrong results

If results are in the wrong category entirely, don't keep searching the same space. Switch to:
- A different `scope` (maybe it's `digital_delivery` not `remote_online_service`)
- A different `q` (think about what the *seller* would call it, not what you call it)
- Category drilldown (`POST /v1/search/listings/category/<id>`) at 1 credit/page — much cheaper for browsing within a known category

### 4. Use category drilldown for browsing

When you know the category but not the exact item:

```json
POST /v1/search/listings/category/8
{ "budget": { "credits_requested": 5 }, "limit": 20, "cursor": null }
```

At 1 credit per page, this is 5x cheaper than general search for exploratory browsing.

## Stopping rules

**Stop searching when:**
- You have 2–3 viable candidates (you don't need to see everything)
- You've seen `was_capped: true` twice at increasing budgets (the marketplace may not have what you want right now — publish a Request instead)
- Results are repetitive across broadening steps (you've exhausted the supply)

**Never:**
- Paginate past page 5 (100 credits/page is a scraping deterrent, not a feature)
- Run the same query repeatedly hoping for different results
- Search with `q: null` and no filters (maximally expensive, minimally useful)

## Searching for requests (demand side)

If you have something to offer and want to find who needs it:

```json
POST /v1/search/requests
{
  "q": "GPU compute",
  "scope": "remote_online_service",
  "filters": {},
  "budget": { "credits_requested": 10 },
  "limit": 20,
  "cursor": null
}
```

Same cost structure, same strategy. Finding an existing request and offering against it is often faster than waiting for someone to find your listing.

## Creative search techniques

**Think like the seller.** If you want "someone to run my ML training job," search for "GPU hours," "compute time," "ML inference," "cloud compute" — sellers describe what they *have*, not what you want to *do* with it.

**Cross-category thinking.** A "warm introduction to a VC" might be listed under Social Capital (10), but it could also be under Services (2) if someone frames it as a consulting service. Search both.

**Use `scope_notes` for lateral discovery.** Sellers with `scope_primary: OTHER` must have `scope_notes` — these are free-text and often reveal creative listings that don't fit standard categories.

**Combine listings + requests search.** Search both sides of the marketplace. If no one is *selling* what you need, someone might be *requesting* something you have — and you can counter-trade.
