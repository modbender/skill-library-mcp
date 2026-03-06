# Scoped APIs

These 17 APIs are pre-authorised for this agent. Credentials are managed in Jentic (jentic.com) — not in this agent.

| API | Version | Notes |
|---|---|---|
| `googleapis.com/gmail` | v1 | Read, send, manage email |
| `googleapis.com/calendar` | v3 | Events, calendars, scheduling |
| `googleapis.com/sheets` | v4 | Read/write spreadsheet data |
| `googleapis.com/people` | v1 | Contacts, profiles |
| `github.com/api.github.com` | v1.1.4 | Repos, issues, PRs, code |
| `stripe.com/main` | 2025-03-31.basil | Payments, customers, subscriptions |
| `twilio.com/api` | v1.0.0 | SMS, voice, messaging |
| `xero.com/xero_accounting` | v7.0.0 | Invoicing, accounting |
| `openai.com/main` | v2.3.0 | Chat, assistants, embeddings |
| `nytimes.com/top_stories` | v2.0.0 | Live NYT top stories by section |
| `nytimes.com/article_search` | v1.0.0 | Search NYT article archive |
| `nytimes.com/archive` | v1.0.0 | Monthly article archive |
| `nytimes.com/movie_reviews` | v2.0.0 | NYT movie reviews |
| `nytimes.com/geo_api` | v1.0.0 | NYT geographic data |
| `finnhub.io/main` | v1.0.0 | Stock quotes, market news (no creds needed) |
| `yelp.com/main` | v1.0.0 | Business search, reviews |
| `marketdata.app/main` | v1.0.0 | Market data, options, earnings |

## Credential Status

- **Finnhub** — works without credentials (free public data)
- **All others** — require API credentials configured at jentic.com for this agent

To add credentials: add credentials via jentic.com.
