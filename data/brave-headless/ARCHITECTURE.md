# Architecture Reference

Headless brave-search v0.2.0 — kelexine <https://github.com/kelexine>

## Module map

```
scripts/
├── search.js            CLI entry — search
├── content.js           CLI entry — content extraction
├── content-fetcher.js   Fetch + parse pipeline
├── config.js            Env validation + typed config
├── circuit-breaker.js   Three-state fault isolation
├── retry.js             Backoff + retry orchestration
├── concurrency.js       Bounded concurrency pool
├── utils.js             htmlToMarkdown, smartTruncate, parseURL
├── logger.js            Structured leveled logger
└── errors.js            Typed error hierarchy
```

## Error hierarchy (`errors.js`)

```
BraveSearchError          Base. Adds: code, context, timestamp, toJSON()
├── ValidationError       Bad env vars or CLI args            VALIDATION_ERROR
├── NetworkError          DNS / timeout / connection refused  NETWORK_ERROR
├── APIError              Non-2xx HTTP response               API_ERROR
│   └── RateLimitError    HTTP 429. Adds: retryAfter (s)      RATE_LIMIT_ERROR
├── ParseError            HTML/Markdown parse failure         PARSE_ERROR
└── CircuitBreakerError   Breaker is OPEN, request rejected   CIRCUIT_BREAKER_OPEN
```

Every error carries a machine-readable `code` string so callers can make typed decisions
without matching on message strings.

## Config validation (`config.js`)

Environment variables are validated against a typed schema at startup. Each field has:

- `required` — fail at startup if missing
- `default` — fallback value
- `enum` — allowlist of valid values
- `parse` — type coercion (e.g. `Number`)
- `validate` — range/constraint check returning `string | null`
- `description` — human-readable label shown in error output

Validation failures accumulate all errors and throw a single `ValidationError` listing
every issue at once rather than failing on the first mismatch.

`config.js` exports two surfaces:

- `config` — lazily evaluated, no API key required (safe to import anywhere)
- `requireConfig()` — validates API key presence; call once at CLI startup

## Retry (`retry.js`)

`withRetry(fn, opts)` wraps any async function with:

- Configurable attempt count (`MAX_RETRY_ATTEMPTS`)
- **Full jitter** exponential backoff: delay = random(0, min(maxDelay, base × 2^(attempt-1)))
  This prevents thundering-herd when many concurrent requests fail simultaneously.
- `Retry-After` header awareness for `RateLimitError` — respects the server's own hint
- Pluggable `shouldRetry(err, attempt) => boolean` predicate
- Default predicate: retry on `NetworkError`, HTTP 429, HTTP 5xx. Never retry 4xx client errors.

## Circuit Breaker (`circuit-breaker.js`)

Three-state finite state machine:

```
CLOSED ──(threshold failures)──► OPEN ──(resetTimeout ms)──► HALF_OPEN
  ▲                                                               │
  └──────────────(successThreshold successes)────────────────────┘
```

- **CLOSED**: Normal operation. Failure count is tracked.
- **OPEN**: All requests are immediately rejected with `CircuitBreakerError`.
  After `resetTimeout` ms, transitions to HALF_OPEN.
- **HALF_OPEN**: One probe request is let through. On success, the success counter
  increments; once `successThreshold` consecutive successes are seen, the breaker
  closes. On any failure, it immediately reopens.

4xx client errors (except 429) never count as failures — they signal a problem with
the request, not with the service.

## Concurrency Pool (`concurrency.js`)

`ConcurrencyPool` is a promise-queue that limits simultaneous in-flight async tasks.

Key methods:

- `pool.run(fn)` — schedule `fn` when a slot is available
- `ConcurrencyPool.map(items, fn, limit)` — like `Promise.all` but bounded; preserves order
- `ConcurrencyPool.mapSettled(items, fn, limit)` — like `Promise.allSettled` but bounded

`search.js` uses `mapSettled` for `--content` fetches so one failing page never blocks
or cancels the remaining results.

## Content Extraction (`content-fetcher.js`)

Two-strategy extraction pipeline per URL:

1. **Mozilla Readability** — high-quality article extraction; produces clean prose,
   drops navigation/ads/boilerplate automatically. If the parsed content is ≥ 100 chars,
   use it.

2. **DOM fallback** — if Readability yields nothing, prune noise selectors
   (`script`, `style`, `nav`, `header`, `footer`, `aside`, cookie banners, ads),
   then try a prioritized list of content container selectors
   (`main`, `article`, `[role='main']`, `.post-content`, …).

Both paths emit Markdown via `htmlToMarkdown()` then pass through `smartTruncate()`.

## Smart Truncation (`utils.js`)

Hard character limits split mid-sentence and confuse agents. `smartTruncate(text, maxChars)`
snaps to the nearest boundary (in order of preference):

1. Last `\n\n` (paragraph break) within the window and above 50% of budget
2. Last sentence-ending punctuation (`.` `!` `?`) followed by whitespace
3. Last word boundary (space)
4. Hard cut at `maxChars` as absolute last resort

All truncated outputs are suffixed with `…`.

## Logger (`logger.js`)

Writes to **stderr** exclusively, keeping stdout clean for piped output.

- Leveled: `debug < info < warn < error < silent`
- Controlled by `LOG_LEVEL` env var
- TTY-aware ANSI colors in interactive terminals; no escape codes in pipes
- JSON mode (`LOG_JSON=true`) emits newline-delimited JSON for log aggregators
- `logger.child("label")` creates a prefixed sub-logger for per-module context
