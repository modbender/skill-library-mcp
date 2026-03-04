---
name: Meilisearch
description: Deploy and tune Meilisearch with indexing, filtering, and production configuration.
metadata: {"clawdbot":{"emoji":"🔎","os":["linux","darwin","win32"]}}
---

## Index Configuration Traps
- filterableAttributes and sortableAttributes must be declared BEFORE adding documents — adding later triggers full reindex
- Changing any index setting triggers reindex — batch all setting changes together
- Order of searchableAttributes affects ranking — put most important fields first, not alphabetical
- displayedAttributes defaults to all — explicitly limit to reduce response size

## Indexing Pitfalls
- Document updates are async — the API returns taskUid, must poll /tasks/{uid} for actual completion
- Primary key inference fails on nested or array fields — always set primaryKey explicitly
- Batch size affects indexing speed — 10-50MB batches optimal, not one document at a time
- Updating one field requires sending the whole document — no true partial updates

## Typo Tolerance Issues
- First character is never typo-tolerant — "tset" won't match "test", by design
- Typo tolerance on IDs/codes causes false matches — disable per attribute with typoTolerance.disableOnAttributes
- Min word length defaults: 1 typo at 5 chars, 2 typos at 9 chars — adjust if matching too aggressively

## Filtering Mistakes
- Filters on undeclared filterableAttributes silently return empty — no error, just no results
- Geo filtering requires _geo field with lat/lng — field name is hardcoded, can't customize
- Filter syntax is NOT SQL — use `TO` for ranges (`year 2020 TO 2024`), not `BETWEEN`
- Empty array in IN clause causes error — check array length before building filter

## Search Behavior
- Default limit is 20, max is 1000 per request — no deep pagination, use filters to narrow
- Multi-word queries match ANY word by default — use quotes for phrase matching
- Highlighting only works on searchableAttributes — not on stored-only fields
- Facets distribution counts include all matching docs — not affected by limit parameter

## Production Configuration
- Master key MUST be set in production — without it, all endpoints are public
- Create search-only API keys for frontend — never expose master key
- Snapshots are the only backup method — schedule them, no continuous replication
- No clustering — single node only, scale vertically with RAM

## Performance Realities
- Index lives in memory-mapped files — RAM determines max index size
- Payload limit is 100MB per request — split large imports into batches
- Indexing blocks during settings update — queries still work but new docs queue
- Task queue has no priority — large reindex blocks small document adds

## API Key Restrictions
- Keys can restrict to specific indexes — use for multi-tenant isolation
- Keys can have expiresAt — but no auto-rotation, must manage manually
- Actions are granular — search, documents.add, indexes.create, settings.update, etc.
- Invalid key returns 401, missing key on protected instance returns 401 — same error, check both
