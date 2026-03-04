# Build Your Own Stack — Help Center

Use this when vendor lock-in, compliance, or custom workflow requirements outweigh SaaS speed.

## Core Components

| Layer | Typical Choices | Notes |
|------|------------------|------|
| Content store | Markdown repo, headless CMS, SQL + admin UI | Must support versioning and ownership metadata |
| Search | Meilisearch, OpenSearch, Algolia | Prioritize typo tolerance and synonym support |
| Delivery UI | Next.js, Astro, static docs frontend | Fast load and clear taxonomy navigation are critical |
| Auth (optional) | SSO/OAuth gateway | Needed for private help centers |
| Ticket bridge | Webhooks + queue worker | Route unresolved intents to support inbox |
| Analytics | Product analytics + query logs | Track search misses and deflection impact |

## Reference Architecture

1. Authoring: product/support authors update docs in CMS or repository.
2. Indexing: publish event updates search index and article metadata store.
3. Delivery: frontend renders docs by category with search and feedback widgets.
4. Escalation: unresolved search or low-confidence results open pre-tagged support tickets.
5. Insights: weekly jobs aggregate deflection, failed queries, and stale content.

## Guardrails

- Define URL schema before launch to prevent redirect sprawl.
- Keep article IDs stable even when titles change.
- Build rollback for index or deployment failures.
- Separate public and private content paths early.
- Allocate ownership for on-call maintenance of the stack.
