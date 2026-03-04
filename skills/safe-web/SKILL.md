# safe-web

Secure web fetch and search with **PromptGuard** scanning.

## Status

✅ Working

## Purpose

Protects against prompt injection attacks hidden in web content before returning it to the AI. Wraps web fetching and searching with security scanning.

## Installation

Requires [PromptGuard](https://clawhub.ai/seojoonkim/prompt-guard) and Python dependencies:

```bash
# Install PromptGuard first
cd /home/linuxbrew/.openclaw/workspace/skills/prompt-guard
pip3 install --break-system-packages -e .

# Install web dependencies (if not present)
pip3 install --break-system-packages requests beautifulsoup4
```

## Usage

### Fetch Command

Fetch a URL and scan the content:

```bash
# Basic fetch
safe-web fetch https://example.com/article

# Save to file
safe-web fetch https://example.com --output article.txt

# JSON output for automation
safe-web fetch https://example.com --json

# Strict mode (block on MEDIUM)
safe-web fetch https://example.com --strict
```

### Search Command

Search the web and scan results:

```bash
# Basic search
safe-web search "AI safety research"

# More results
safe-web search "stock market news" --count 10

# JSON output
safe-web search "machine learning" --json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - content/results are clean |
| 1 | Error (network, parsing, etc.) |
| 2 | Threat detected - content blocked |

## Configuration

### Environment Variables

- `BRAVE_API_KEY` - API key for Brave Search (optional, enables search command)
  - Get one at: https://brave.com/search/api/

### Symlink (Recommended)

Create a system-wide symlink so `safe-web` works from any directory:

```bash
sudo ln -s /home/linuxbrew/.openclaw/workspace/skills/safe-web/scripts/safe-web.py /usr/local/bin/safe-web
```

After creating the symlink, you can use `safe-web` directly without specifying the full path.

## How It Works

### Fetch Flow
1. Downloads URL content with requests
2. Extracts text using BeautifulSoup (removes scripts, styles)
3. Scans extracted text with PromptGuard
4. Returns clean content or blocks with SHIELD report

### Search Flow
1. Queries Brave Search API (requires API key)
2. Scans each result title and description
3. Filters out suspicious results
4. Returns only clean results

## Security Model

**Fail-closed:** If PromptGuard cannot be loaded or scanning fails, the tool reports an error rather than returning unverified content.

**Content sanitization:** HTML is parsed and scripts/styles are removed before scanning to reduce false positives.

**No execution:** This tool only fetches and scans. It never executes JavaScript or runs commands found in web content.

## Example Output

### Clean Fetch
```
Fetching: https://site.com/article
Fetched 1523 characters
Scanning with PromptGuard...

Article content here...
```

### Blocked Content
```
Fetching: https://suspicious-site.com
Fetched 2048 characters
Scanning with PromptGuard...
============================================================
🛡️  SAFE-WEB SECURITY ALERT
============================================================
Source: https://suspicious-site.com
Severity: CRITICAL
Action: BLOCK_NOTIFY
Patterns Matched: 8

Detected Patterns:
  - instruction_override_en
  - role_manipulation_en
  - system_impersonation_en
============================================================

Content from https://suspicious-site.com has been blocked.
```

### Search Results
```
Searching: AI research
Found 5 results, scanning...

Showing 3 clean results:

1. Latest AI Research Papers
   URL: https://arxiv.org/list/ai/recent
   Recent submissions in artificial intelligence...

2. AI Safety Institute
   URL: https://www.safe.ai/
   Research and development for safe AI systems...
```

## When to Use

Use `safe-web` when:
- Fetching content from untrusted URLs
- Scraping web pages for analysis
- Searching and processing web results
- Any web content will enter the AI context window

Use standard `web_fetch`/`web_search` tools only for:
- Trusted, known-safe domains
- Internal documentation sites
- When you explicitly want to bypass scanning

## Comparison with Native Tools

| Feature | Native `web_fetch` | `safe-web fetch` |
|---------|-------------------|------------------|
| Fetches HTML | ✅ | ✅ |
| Extracts text | ✅ | ✅ |
| Injection scanning | ❌ | ✅ |
| JSON output | ✅ | ✅ |
| Save to file | ❌ | ✅ |
| Exit codes | 0/1 | 0/1/2 (security) |

## Dependencies

- Python 3.8+
- [PromptGuard 3.1.0+](https://clawhub.ai/seojoonkim/prompt-guard) (installed in workspace)
- requests
- beautifulsoup4
- Brave Search API key (for search command)

## Limitations

- Search requires Brave API key (free tier available)
- Fetch does not execute JavaScript (static HTML only)
- Large pages may be truncated during text extraction
- Network timeouts default to 30 seconds
