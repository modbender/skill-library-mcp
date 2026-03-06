# Usage

## Script contract

`node scripts/fetch-markdown.mjs <url> [--max-chars N] [--timeout-ms N] [--json]`

- STDOUT: markdown (or JSON with `--json`)
- STDERR: diagnostics only
- Exit codes:
  - `0` success
  - `1` bad args
  - `2` invalid/blocked URL
  - `3` fetch/network/content-type failure
  - `4` extraction failure or thin output

## Recommended in-skill workflow

1. Run script once for URL.
2. If exit `0`, return markdown as final result.
3. If exit `3/4` on JS-heavy pages, use OpenClaw `browser` tool fallback:
   - open URL
   - snapshot text from rendered page
   - return markdown summary with source URL.

## Safety

- Script blocks localhost and private IPv4 ranges by hostname literal.
- Accepts only http/https URLs.
- Never execute fetched content.
