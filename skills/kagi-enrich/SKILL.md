---
name: kagi-enrich
description: Search Kagi's unique non-commercial web (Teclis) and non-mainstream news (TinyGem) indexes for independent, ad-free content you won't find in regular search results. Use when you want to discover small-web sites, independent blogs, niche discussions, or non-mainstream news on a topic.
---

# Kagi Enrichment

Search Kagi's proprietary enrichment indexes using the [Kagi Enrichment API](https://help.kagi.com/kagi/api/enrich.html). These are Kagi's "secret sauce" — curated indexes of non-commercial and independent content that complement mainstream search results.

Two indexes are available:

| Index | Backend | Best for |
|-------|---------|----------|
| `web` | **Teclis** | Independent websites, personal blogs, open-source projects, non-commercial content |
| `news` | **TinyGem** | Non-mainstream news sources, interesting discussions, off-the-beaten-path journalism |

This skill uses a Go binary for fast startup and zero runtime dependencies. The binary can be downloaded pre-built or compiled from source.

## Setup

Requires a Kagi account with API access enabled. Uses the same `KAGI_API_KEY` as all other kagi-* skills.

1. Create an account at https://kagi.com/signup
2. Navigate to Settings → Advanced → API portal: https://kagi.com/settings/api
3. Generate an API Token
4. Add funds at: https://kagi.com/settings/billing_api
5. Add to your shell profile (`~/.profile` or `~/.zprofile`):
   ```bash
   export KAGI_API_KEY="your-api-key-here"
   ```
6. Install the binary — see [Installation](#installation) below

## Pricing

**$2 per 1,000 searches** ($0.002 per query). Billed only when non-zero results are returned.

## Usage

```bash
# Search the independent web (Teclis index) — default
{baseDir}/kagi-enrich.sh web "rust async programming"
{baseDir}/kagi-enrich.sh "rust async programming"        # web is the default

# Search non-mainstream news (TinyGem index)
{baseDir}/kagi-enrich.sh news "open source AI"

# Limit number of results
{baseDir}/kagi-enrich.sh web "sqlite internals" -n 5

# JSON output
{baseDir}/kagi-enrich.sh web "zig programming language" --json
{baseDir}/kagi-enrich.sh news "climate change solutions" --json

# Custom timeout
{baseDir}/kagi-enrich.sh web "query" --timeout 30
```

### Options

| Flag | Description |
|------|-------------|
| `-n <num>` | Max results to display (default: all returned) |
| `--json` | Emit JSON output |
| `--timeout <sec>` | HTTP timeout in seconds (default: 15) |

## Output

### Default (text)

```
--- Result 1 ---
Title: SQLite Internals: How The World's Most Used Database Works
URL:   https://www.compileralchemy.com/books/sqlite-internals/
Date:  2023-04-01T00:00:00Z
       A deep-dive into how SQLite's B-tree storage engine, WAL journal...

--- Result 2 ---
...

[API Balance: $9.9980 | results: 15]
```

### JSON (`--json`)

```json
{
  "query": "sqlite internals",
  "index": "web",
  "meta": {
    "id": "abc123",
    "node": "us-east4",
    "ms": 386,
    "api_balance": 9.998
  },
  "results": [
    {
      "rank": 1,
      "title": "SQLite Internals: How The World's Most Used Database Works",
      "url": "https://www.compileralchemy.com/books/sqlite-internals/",
      "snippet": "A deep-dive into SQLite's B-tree...",
      "published": "2023-04-01T00:00:00Z"
    }
  ]
}
```

## When to Use

- **Use `web`** when you want independent, non-commercial perspectives on a topic — personal blogs, indie projects, academic pages, niche communities — results that mainstream search drowns out with SEO-optimized commercial sites
- **Use `news`** when you want news and discussions from sources outside the mainstream media cycle — niche outlets, Hacker News threads, Reddit discussions, independent journalists
- **Combine with `kagi-search`** for the most complete picture: `kagi-search` for high-quality general results, `kagi-enrich web` for independent voices, `kagi-enrich news` for alternative news angles
- **Use `kagi-fastgpt`** instead when you need a synthesized answer rather than a list of sources

### Note on result counts

The enrichment indexes are intentionally niche — they may return fewer results than general search. No results for a query means no relevant content was found in that index (and you won't be billed).

## Installation

### Option A — Download pre-built binary (no Go required)

```bash
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
case "$ARCH" in
  x86_64)        ARCH="amd64" ;;
  aarch64|arm64) ARCH="arm64" ;;
esac

TAG=$(curl -fsSL "https://api.github.com/repos/joelazar/kagi-skills/releases/latest" | grep '"tag_name"' | cut -d'"' -f4)
BINARY="kagi-enrich_${TAG}_${OS}_${ARCH}"

mkdir -p {baseDir}/.bin
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/${BINARY}" \
  -o {baseDir}/.bin/kagi-enrich
chmod +x {baseDir}/.bin/kagi-enrich

# Verify checksum (recommended)
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/checksums.txt" | \
  grep "${BINARY}" | sha256sum --check
```

Pre-built binaries are available for Linux and macOS (amd64 + arm64) and Windows (amd64).

### Option B — Build from source (requires Go 1.26+)

```bash
cd {baseDir} && go build -o .bin/kagi-enrich .
```

Alternatively, just run `{baseDir}/kagi-enrich.sh` directly — the wrapper auto-builds on first run if Go is available.

The binary has no external dependencies — only the Go standard library.
