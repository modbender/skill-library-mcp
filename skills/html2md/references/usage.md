# html2md — Full Usage Reference

## Synopsis

```
html2md [options] <url>
html2md [options] --file <path>
html2md [options] --stdin
```

## Flags

| Flag | Argument | Description |
|------|----------|-------------|
| `--max-tokens N` | integer | Budget-aware truncation. Keeps all headings + fills remaining budget in document order. Appends `[truncated — N more tokens]` note. |
| `--no-links` | — | Strip all hyperlink URLs; keep link text as plain text. |
| `--no-images` | — | Remove all image references entirely (including alt text). |
| `--no-tables` | — | Convert HTML tables to bullet lists (one `- cell` per cell). |
| `--json` | — | Output JSON: `{ title, url, markdown, tokens }`. Useful for programmatic use. |
| `--file <path>` | file path | Read a local HTML file instead of fetching a URL. |
| `--stdin` | — | Read HTML from stdin (pipe). |
| `--help`, `-h` | — | Show usage. |

## How It Works

### Two-Pass Extraction

1. **Mozilla Readability** isolates the main article content — eliminates navbars, sidebars, ads, cookie banners, footers, social widgets.
2. **Body fallback** — if Readability returns < 30 words (e.g. HN's table layout), falls back to cleaned `<body>` with noise elements removed via CSS selectors.

### Post-Processing Pipeline

After Turndown converts HTML → markdown:
- Strips HTML comments `<!-- ... -->`
- Removes empty markdown links `[](url)`
- Removes zero-width chars, soft hyphens, NBSP
- Filters social CTAs (share, subscribe, follow us, etc.)
- Strips breadcrumb lines (e.g. `Home › Blog › Article`)
- Removes empty headings
- Collapses 3+ blank lines → 2
- Trims trailing whitespace

### Token Budget Algorithm (`--max-tokens N`)

Uses 1 token ≈ 4 chars heuristic.

1. Collects all heading lines (`# H1`, `## H2`, etc.)
2. Puts headings at top (they get priority)
3. Fills remaining budget with body lines in document order
4. Appends `[truncated — X more tokens]` if content was cut

This means you always get the document structure even on tight budgets.

## Input Modes

### URL (default)
```bash
html2md https://example.com
```
- 15-second timeout
- Follows redirects
- Sets a descriptive User-Agent
- Errors on non-2xx status codes
- Errors on non-HTML content types

### Local file
```bash
html2md --file /path/to/page.html
```

### Stdin
```bash
curl -s https://example.com | html2md --stdin
cat page.html | html2md --stdin
```
Optionally pass a URL for context:
```bash
cat page.html | html2md --stdin https://example.com
```

## Output Modes

### Plain markdown (default)
```
# Page Title

Content in clean markdown...
```

### JSON (`--json`)
```json
{
  "title": "Page Title",
  "url": "https://example.com/",
  "markdown": "# Page Title\n\nContent...",
  "tokens": 342
}
```

Use with `jq`:
```bash
html2md --json https://example.com | jq '{title, tokens}'
html2md --json https://example.com | jq -r .markdown
```

## Examples

### Research with budget
```bash
html2md --max-tokens 3000 https://paulgraham.com/greatwork.html
```

### HN front page, no link noise
```bash
html2md --no-links --no-images https://news.ycombinator.com
```

### Get token count before committing
```bash
html2md --json https://example.com | jq .tokens
```

### Pipe to a file
```bash
html2md https://docs.example.com/api > api-docs.md
```

### Batch: check if page is worth reading
```bash
for url in url1 url2 url3; do
  tokens=$(html2md --json "$url" | jq .tokens)
  echo "$tokens $url"
done
```

### Use in Node.js scripts
```js
import { execFileSync } from 'child_process';
const md = execFileSync('html2md', ['--max-tokens', '2000', url]).toString();
```

Note: Always use `execFileSync` (not `execSync`) to avoid shell injection when the URL comes from untrusted input.

## Error Handling

All errors exit code 1 with a descriptive message to stderr:

| Error | Message |
|-------|---------|
| Bad URL / DNS failure | `Network error fetching <url>: ...` |
| Timeout (>15s) | `Timeout: request exceeded 15s for <url>` |
| HTTP error | `HTTP 404 Not Found — <url>` |
| Binary content | `Non-HTML content type: application/pdf — ...` |
| File not found | `Cannot read file: path — ...` |
| No input | `No input specified. Usage: ...` |

## When to Use vs `web_fetch`

| Situation | Use |
|-----------|-----|
| Reading articles/docs in cron jobs or sub-agents | `html2md` |
| Token budget is tight | `html2md --max-tokens N` |
| Page has heavy nav/ads/footers | `html2md` |
| Need JSON output for programmatic use | `html2md --json` |
| Quick one-off URL fetch in main session | `web_fetch` |
| Page is a JSON/XML API endpoint | `web_fetch` |
| Need JS-rendered content | Playwright |

## Requirements

- Node.js 22+
- npm (for install)
- Internet access (for URL fetching)

## Dependencies

- [`@mozilla/readability`](https://github.com/mozilla/readability) — content extraction
- [`jsdom`](https://github.com/jsdom/jsdom) — DOM parsing
- [`turndown`](https://github.com/mixmark-io/turndown) — HTML → markdown
