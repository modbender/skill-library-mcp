# Massive REST Usage Notes

Base URL defaults to `https://api.massive.com`.

Use the CLI as a thin wrapper over Massive's public REST docs. Prefer documented relative paths and query parameters over wrapper-specific abstractions.

## Generic Request Pattern

```bash
scripts/massive get /v3/reference/tickers/AAPL
scripts/massive get /v2/aggs/ticker/AAPL/prev --query adjusted=true
```

The CLI accepts:

- a relative Massive path such as `/v3/reference/tickers/AAPL`
- a full `https://api.massive.com/...` URL
- a `next_url` returned by Massive pagination

By default, absolute URLs must stay on `https://api.massive.com`. If you explicitly set `MASSIVE_BASE_URL` to another HTTPS origin, that override becomes the only allowed absolute origin for direct requests and pagination.

## Included Shortcuts

The bundled shortcuts cover a small set of high-signal, documented lookups:

- `stocks ticker-details <ticker>` -> `/v3/reference/tickers/<ticker>`
- `stocks previous-close <ticker>` -> `/v2/aggs/ticker/<ticker>/prev`
- `options contract-details <options-ticker>` -> `/v3/reference/options/contracts/<options-ticker>`
- `forex currencies` -> `/v3/reference/currencies?market=fx`
- `crypto currencies` -> `/v3/reference/currencies?market=crypto`
- `indices ticker-details <ticker>` -> `/v3/reference/tickers/I:<ticker>`

## Pagination

Massive commonly returns `next_url` in paginated JSON responses.

Use either pattern:

```bash
scripts/massive get "/v3/reference/tickers?limit=10"
```

Then:

```bash
scripts/massive next < first-page.json
```

Or pass the `next_url` directly:

```bash
scripts/massive get "https://api.massive.com/..."
```

## Query Discipline

- Request only the fields and date ranges needed for the task.
- Keep page sizes small enough for downstream agents to consume.
- Treat plan and entitlement errors as terminal unless the user explicitly asks to retry.
