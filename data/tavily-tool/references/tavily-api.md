# Tavily API notes (quick reference)

## Endpoint

- Search: `POST https://api.tavily.com/search`

## Auth

- Send the API key via HTTP header: `Authorization: Bearer <TAVILY_API_KEY>`.
- This skill’s scripts read the key from **env var only**: `TAVILY_API_KEY`.

## Common request fields

```json
{
  "query": "...",
  "max_results": 5,
  "include_domains": ["example.com"],
  "exclude_domains": ["spam.com"]
}
```

(Additional Tavily options exist; this skill’s CLI supports only a common subset for discovery use-cases.)

## Script usage

### JSON output (stdout) + URL list (stderr)

```bash
export TAVILY_API_KEY="..."
node skills/tavily/scripts/tavily_search.js --query "best open source vector database" --max_results 5
```

### URLs only

```bash
export TAVILY_API_KEY="..."
node skills/tavily/scripts/tavily_search.js --query "SvelteKit tutorial" --urls-only
```

### Include / exclude domains

```bash
export TAVILY_API_KEY="..."
node skills/tavily/scripts/tavily_search.js \
  --query "websocket load testing" \
  --include_domains k6.io,github.com \
  --exclude_domains medium.com
```

## Notes

- Exit code `2` indicates missing required args or missing `TAVILY_API_KEY`.
- Exit code `3` indicates network/HTTP failure.
- Exit code `4` indicates a non-JSON response.
