---
name: kagi-fastgpt
description: Ask questions and get AI-synthesized answers backed by live web search, via Kagi's FastGPT API. Returns a direct answer with cited references. Use when you need a quick, authoritative answer rather than raw search results.
---

# Kagi FastGPT

Get AI-generated answers with cited web sources using [Kagi's FastGPT API](https://help.kagi.com/kagi/api/fastgpt.html). FastGPT runs a full web search under the hood and synthesizes results into a concise answer — ideal for factual questions, API lookups, and current-events queries.

This skill uses a Go binary for fast startup and no runtime dependencies. The binary can be downloaded pre-built or compiled from source.

## Setup

Requires a Kagi account with API access enabled. Uses the same `KAGI_API_KEY` as the `kagi-search` skill.

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

1.5¢ per query ($15 USD per 1000 queries). Cached responses are free.

## Usage

```bash
{baseDir}/kagi-fastgpt.sh "query"                        # Ask a question (default)
{baseDir}/kagi-fastgpt.sh "query" --json                 # JSON output
{baseDir}/kagi-fastgpt.sh "query" --no-refs              # Answer only, no references
{baseDir}/kagi-fastgpt.sh "query" --no-cache             # Bypass response cache
{baseDir}/kagi-fastgpt.sh "query" --timeout 60           # Custom timeout (default: 30s)
```

### Options

| Flag | Description |
|------|-------------|
| `--json` | Emit JSON output (see below) |
| `--no-refs` | Suppress references in text output |
| `--no-cache` | Bypass cached responses (use for time-sensitive queries) |
| `--timeout <sec>` | HTTP timeout in seconds (default: 30) |

## Output

### Default (text)

Prints the synthesized answer, followed by a numbered reference list:

```
Python 3.11 was released on October 24, 2022 and introduced several improvements...

--- References ---
[1] What's New In Python 3.11 — Python 3.11.3 documentation
    https://docs.python.org/3/whatsnew/3.11.html
    The headline changes in Python 3.11 include significant performance improvements...
[2] ...
```

Token usage and API balance are printed to stderr.

### JSON (`--json`)

Returns a JSON object with:

- `query` — the original query
- `output` — the synthesized answer
- `tokens` — tokens consumed
- `references[]` — array of `{ title, url, snippet }` objects
- `meta` — API metadata (`id`, `node`, `ms`)

## When to Use

- **Use kagi-fastgpt** when you need a direct answer synthesized from web sources (e.g. "What version of X was released last month?", "How do I configure Y?")
- **Use kagi-search** when you need raw search results to scan, compare, or extract data from yourself
- **Use web-browser** when you need to interact with a page or the content is behind JavaScript

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
BINARY="kagi-fastgpt_${TAG}_${OS}_${ARCH}"

mkdir -p {baseDir}/.bin
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/${BINARY}" \
  -o {baseDir}/.bin/kagi-fastgpt
chmod +x {baseDir}/.bin/kagi-fastgpt

# Verify checksum (recommended)
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/checksums.txt" | \
  grep "${BINARY}" | sha256sum --check
```

Pre-built binaries are available for Linux and macOS (amd64 + arm64) and Windows (amd64).

### Option B — Build from source (requires Go 1.26+)

```bash
cd {baseDir} && go build -o .bin/kagi-fastgpt .
```

Alternatively, just run `{baseDir}/kagi-fastgpt.sh` directly — the wrapper auto-builds on first run if Go is available.

The binary has no external dependencies — only the Go standard library.
