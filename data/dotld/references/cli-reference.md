# dotld CLI Reference

## Usage

```
dotld <domains...>
dotld --file domains.txt
```

All positional arguments are treated as domain search queries. The `search` subcommand is implicit — `dotld example.com` is equivalent to `dotld search example.com`.

## Flags

### `--json`

Output results as structured JSON instead of the default tree table format.

### `--file <path>`

Read domains from a text file, one domain per line. Blank lines are ignored. Can be combined with positional arguments — duplicates are deduplicated.

### `--dynadot-key <key>`

Provide the Dynadot API key directly. When used, the key is auto-saved to the config file for future runs.

### `--timeout <duration>`

Set the HTTP request timeout. Accepts:
- Seconds: `5s`
- Milliseconds: `500ms`
- Raw milliseconds: `5000`

Default: `10s` (10000ms).

### `--currency <code>`

Set the currency for prices. Only `USD` is supported in v1.

## API Key Resolution

The Dynadot production API key is resolved in order:

1. `--dynadot-key` flag
2. `DYNADOT_API_PRODUCTION_KEY` environment variable
3. Config file at `~/.config/dotld/config.json`

When a key is provided via `--dynadot-key`, it is persisted to the config file automatically.

### Key Validation Warnings

dotld warns (but does not block) when the key:
- Has leading/trailing whitespace
- Looks like a hex secret token (64 hex chars) rather than an API key
- Contains non-alphanumeric characters
- Is shorter than 16 characters

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DYNADOT_API_PRODUCTION_KEY` | Dynadot production API key |
| `AFFILIATE_URL_TEMPLATE` | Custom URL template for buy links |

## Config File

Location: `~/.config/dotld/config.json`

```json
{
  "dynadotKey": "your_api_key_here"
}
```

Created automatically when `--dynadot-key` is used. The directory is created with `0755` permissions, the file with `0644`.

## Query Planning

### Exact lookup

When the input contains a dot (e.g. `example.com`), it is looked up as-is.

### Keyword expansion

When the input has no dot and matches a bare label pattern (`[a-z0-9]` with optional hyphens, max 63 chars), it is expanded across these 9 TLDs:

1. `.com`
2. `.net`
3. `.org`
4. `.io`
5. `.ai`
6. `.co`
7. `.app`
8. `.dev`
9. `.sh`

### Deduplication

All domains are lowercased, trimmed, and deduplicated before querying. Domains from `--file` and positional arguments are merged.

## JSON Output Schema

When `--json` is used, output follows this structure:

```json
{
  "results": [
    {
      "domain": "example.com",
      "available": false,
      "price": null,
      "currency": "USD",
      "buyUrl": null,
      "cached": false,
      "quotedAt": "2026-02-21T00:00:00.000Z",
      "error": ""
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `domain` | string | The queried domain name |
| `available` | boolean | Whether the domain is available for registration |
| `price` | string \| null | Registration price (e.g. `"39.99"`) or null if taken |
| `currency` | string | Currency code, always `"USD"` in v1 |
| `buyUrl` | string \| null | Direct link to register the domain, or null if taken |
| `cached` | boolean | Whether the result came from cache |
| `quotedAt` | string | ISO 8601 timestamp of the price quote |
| `error` | string | Error message if the lookup failed for this domain (omitted when empty) |

## Error Messages

| Error | Cause |
|-------|-------|
| `Missing Dynadot key.` | No API key found in flag, env, or config |
| `Invalid Dynadot key.` | Dynadot API rejected the key |
| `--file requires a value` | `--file` flag used without a path |
| `--currency requires a value` | `--currency` flag used without a value |
| `--dynadot-key requires a value` | `--dynadot-key` flag used without a value |
| `--timeout requires a value` | `--timeout` flag used without a value |
| `Only USD is supported in v1` | Non-USD currency requested |
| `Invalid timeout value: <val>` | Unparseable timeout string |
| `No domains provided` | No domains given as arguments or via file |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (missing key, invalid args, API failure) |

## Dynadot API Limits

- Regular accounts: 1 domain per `search` API call
- Rate limit: 60 requests per minute
- dotld sends one request per domain for predictable behavior
