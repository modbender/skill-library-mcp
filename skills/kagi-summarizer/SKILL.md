---
name: kagi-summarizer
description: Summarize any URL or text using Kagi's Universal Summarizer API. Supports multiple engines (including the enterprise-grade Muriel model), bullet-point takeaways, and output translation to 28 languages. Use when you need a high-quality summary of an article, paper, video transcript, or any document.
---

# Kagi Universal Summarizer

Summarize any URL or block of text using [Kagi's Universal Summarizer API](https://help.kagi.com/kagi/api/summarizer.html). Handles articles, papers, PDFs, video transcripts, forum threads, and more. Supports multiple summarization engines and can translate output to 28 languages.

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

Token-based, billed per 1,000 tokens processed. Cached requests are free.

| Plan | Price per 1k tokens |
|------|---------------------|
| Standard (Cecil / Agnes) | **$0.030** |
| Kagi Ultimate subscribers | **$0.025** (automatically applied) |
| Muriel (enterprise-grade) | higher — check [API pricing page](https://kagi.com/settings?p=api) |

## Usage

```bash
# Summarize a URL
{baseDir}/kagi-summarizer.sh https://example.com/article

# Summarize raw text
{baseDir}/kagi-summarizer.sh --text "Paste your article text here..."

# Pipe text from stdin
cat paper.txt | {baseDir}/kagi-summarizer
echo "Long text..." | {baseDir}/kagi-summarizer.sh --type takeaway

# Choose engine
{baseDir}/kagi-summarizer.sh https://arxiv.org/abs/1706.03762 --engine muriel

# Get bullet-point takeaways instead of prose
{baseDir}/kagi-summarizer.sh https://example.com/article --type takeaway

# Translate summary to another language
{baseDir}/kagi-summarizer.sh https://example.com/article --lang DE
{baseDir}/kagi-summarizer.sh https://example.com/article --lang JA

# JSON output
{baseDir}/kagi-summarizer.sh https://example.com/article --json

# Combined options
{baseDir}/kagi-summarizer.sh https://arxiv.org/abs/1706.03762 --engine muriel --type takeaway --lang EN --json
```

### Options

| Flag | Description |
|------|-------------|
| `--text <text>` | Summarize raw text instead of a URL |
| `--engine <name>` | Summarization engine (see below, default: `cecil`) |
| `--type <type>` | Output type: `summary` (prose) or `takeaway` (bullets) |
| `--lang <code>` | Translate output to a language code (e.g. `EN`, `DE`, `FR`, `JA`) |
| `--json` | Emit JSON output |
| `--no-cache` | Bypass cached responses |
| `--timeout <sec>` | HTTP timeout in seconds (default: 120) |

### Engines

| Engine | Description |
|--------|-------------|
| `cecil` | Friendly, descriptive, fast summary **(default)** |
| `agnes` | Formal, technical, analytical summary |
| `muriel` | Best-in-class, enterprise-grade model — highest quality, slower |

### Language Codes

Common codes: `EN` English · `DE` German · `FR` French · `ES` Spanish · `IT` Italian · `PT` Portuguese · `JA` Japanese · `KO` Korean · `ZH` Chinese (simplified) · `ZH-HANT` Chinese (traditional) · `RU` Russian · `AR` Arabic

Full list: BG CS DA DE EL EN ES ET FI FR HU ID IT JA KO LT LV NB NL PL PT RO RU SK SL SV TR UK ZH ZH-HANT

If no language is specified, the output language follows the document's own language.

## Output

### Default (text)

Prints the summary to stdout. Token usage and API balance are printed to stderr:

```
The paper "Attention Is All You Need" introduces the Transformer architecture,
a novel approach to sequence transduction tasks that relies entirely on
attention mechanisms, dispensing with recurrence and convolutions...

[API Balance: $9.9800 | tokens: 1243]
```

### JSON (`--json`)

```json
{
  "input": "https://arxiv.org/abs/1706.03762",
  "output": "The paper introduces the Transformer...",
  "tokens": 1243,
  "engine": "muriel",
  "type": "takeaway",
  "meta": {
    "id": "abc123",
    "node": "us-east",
    "ms": 4821,
    "api_balance": 9.98
  }
}
```

## When to Use

- **Use kagi-summarizer** when you have a URL or document and need a concise summary without reading it yourself
- **Use `--type takeaway`** for structured bullet points — ideal for research papers, long articles, or meeting notes
- **Use `--engine muriel`** when quality matters most (longer documents, academic papers, technical reports)
- **Use `--lang`** when you need the summary in a language different from the source
- **Use kagi-fastgpt** instead when you have a question that requires synthesizing information from multiple sources via live web search
- **Use kagi-search** instead when you need raw search results to scan or compare

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
BINARY="kagi-summarizer_${TAG}_${OS}_${ARCH}"

mkdir -p {baseDir}/.bin
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/${BINARY}" \
  -o {baseDir}/.bin/kagi-summarizer
chmod +x {baseDir}/.bin/kagi-summarizer

# Verify checksum (recommended)
curl -fsSL "https://github.com/joelazar/kagi-skills/releases/download/${TAG}/checksums.txt" | \
  grep "${BINARY}" | sha256sum --check
```

Pre-built binaries are available for Linux and macOS (amd64 + arm64) and Windows (amd64).

### Option B — Build from source (requires Go 1.26+)

```bash
cd {baseDir} && go build -o .bin/kagi-summarizer .
```

Alternatively, just run `{baseDir}/kagi-summarizer.sh` directly — the wrapper auto-builds on first run if Go is available.

The binary has no external dependencies — only the Go standard library.
