---
name: anakin
description: Convert websites into clean data at scale - scrape URLs, batch scrape, AI search, and autonomous research
user-invocable: true
metadata: {"openclaw":{"emoji":"🕷️","requires":{"bins":["anakin"],"env":["ANAKIN_API_KEY"]},"primaryEnv":"ANAKIN_API_KEY","install":[{"id":"pip","kind":"pip","package":"anakin-cli","bins":["anakin"],"label":"Install Anakin CLI (pip)"}],"homepage":"https://anakin.io"}}
---

# Anakin - Web Data Extraction

Convert websites into clean data at scale using the anakin-cli. Supports single URL scraping, batch scraping, AI-powered search, and autonomous deep research.

## Installation & Authentication

Check status and authentication:

```bash
anakin status
```

Output when ready:
```
✓ Authenticated
Endpoint: https://api.anakin.io
Account: user@example.com
```

If not installed: `pip install anakin-cli`

Always refer to the installation rules in [rules/install.md](rules/install.md) for more information if the user is not logged in.

If not authenticated, run:

```bash
anakin login --api-key "ak-your-key-here"
```

Get your API key from [anakin.io/dashboard](https://anakin.io/dashboard).

## Organization

Create a `.anakin/` folder in the working directory unless it already exists to store results. Add `.anakin/` to the `.gitignore` file if not already there. Always use `-o` to write directly to file (avoids flooding context):

```bash
mkdir -p .anakin
echo ".anakin/" >> .gitignore
anakin scrape "https://example.com" -o .anakin/output.md
```

## Capabilities

### 1. Scrape a Single URL

Extract content from a single web page in multiple formats.

**When to use:**
- Extracting content from a single web page
- Converting a webpage to clean markdown
- Extracting structured data from one URL
- Getting full raw API response with metadata

**Basic usage:**

```bash
# Clean readable text (default markdown format)
anakin scrape "https://example.com" -o output.md

# Structured data (JSON)
anakin scrape "https://example.com" --format json -o output.json

# Full API response with HTML and metadata
anakin scrape "https://example.com" --format raw -o output.json
```

**Advanced options:**

```bash
# JavaScript-heavy or single-page app sites
anakin scrape "https://example.com" --browser -o output.md

# Geo-targeted scraping (country code)
anakin scrape "https://example.com" --country gb -o output.md

# Custom timeout for slow pages (in seconds)
anakin scrape "https://example.com" --timeout 300 -o output.md
```

### 2. Batch Scrape Multiple URLs

Scrape up to 10 URLs at once for efficient parallel processing.

**When to use:**
- Scraping multiple web pages simultaneously
- Comparing products across different sites
- Collecting multiple articles or pages
- Gathering data from several sources at once

**Basic usage:**

```bash
# Batch scrape multiple URLs (up to 10)
anakin scrape-batch "https://example.com/page1" "https://example.com/page2" "https://example.com/page3" -o batch-results.json
```

**For large lists (>10 URLs):**

```bash
# First batch (URLs 1-10)
anakin scrape-batch "https://url1.com" ... "https://url10.com" -o batch-1.json

# Second batch (URLs 11-20)
anakin scrape-batch "https://url11.com" ... "https://url20.com" -o batch-2.json
```

**Output format:** JSON file with combined results, each URL's status (success/failure), content, metadata, and any errors.

### 3. AI-Powered Web Search

Run intelligent web searches to find pages, answer questions, and discover sources.

**When to use:**
- Finding pages on a specific topic
- Answering questions with web sources
- Discovering relevant sources for research
- Gathering links before scraping specific pages
- Quick factual lookups

**Basic usage:**

```bash
# AI-powered web search
anakin search "your search query here" -o search-results.json
```

**Follow-up workflow:**

```bash
# 1. Search for relevant pages
anakin search "machine learning tutorials" -o search-results.json

# 2. Scrape specific results for full content
anakin scrape "https://result-url-from-search.com" -o page.md
```

**Output format:** JSON file with search results including titles, URLs, snippets, relevance scores, and metadata.

### 4. Deep Agentic Research

Run comprehensive autonomous research that explores the web and returns detailed reports.

**When to use:**
- Comprehensive research on complex topics
- Market analysis requiring multiple sources
- Technical deep-dives across documentation and articles
- Comparison research (products, technologies, approaches)
- Questions requiring synthesis from many sources

**Basic usage:**

```bash
# Deep agentic research (takes 1-5 minutes)
anakin research "your research topic or question" -o research-report.json

# With extended timeout for complex topics
anakin research "comprehensive analysis of quantum computing" --timeout 600 -o research-report.json
```

**⏱️ Important:** Deep research takes **1-5 minutes** and runs autonomously. Always inform the user about this duration before starting.

**What it does:**
- Autonomously searches for relevant sources
- Scrapes and analyzes multiple pages
- Synthesizes information across sources
- Generates comprehensive reports with citations
- Provides key insights and conclusions

**Output format:** JSON file with executive summary, detailed report by subtopics, key insights, citations with URLs, confidence scores, and related topics.

## Decision Guide

**Use `anakin scrape` when:**
- You have a single specific URL to extract
- You need content in markdown, JSON, or raw format
- The page is static or JavaScript-heavy (use `--browser`)

**Use `anakin scrape-batch` when:**
- You have 2-10 URLs to scrape simultaneously
- You need efficient parallel processing
- You want combined results in one file

**Use `anakin search` when:**
- You need to find relevant URLs first
- You want quick factual lookups
- You need results in under 30 seconds
- You know what you're looking for

**Use `anakin research` when:**
- You need comprehensive analysis across 5+ sources
- The topic is complex and requires deep exploration
- You want a synthesized report with insights
- You can wait 1-5 minutes for autonomous research
- The question requires comparing multiple perspectives

## Guardrails

### URL Handling
- **Always quote URLs** to prevent shell interpretation of `?`, `&`, `#` characters
- Example: `anakin scrape "https://example.com?param=value"` not `anakin scrape https://example.com?param=value`

### Output Management
- **Always use `-o <file>`** to save output to a file rather than flooding the terminal
- Choose appropriate output filenames based on content type

### Format Selection
- **Default to markdown** for readability unless user explicitly asks for JSON or raw
- Use `--format json` for structured data processing
- Use `--format raw` for full API response with HTML

### Special Cases
- **Use `--browser` only when** standard scrape returns empty or incomplete content
- **For batch scraping:** Maximum 10 URLs per command — split larger lists
- **For research:** Always warn about 1-5 minute duration before starting

### Rate Limiting
- **On HTTP 429 errors** (rate limit), wait before retrying
- Do not loop immediately on rate limit errors

### Authentication
- **On HTTP 401 errors**, re-run `anakin login` rather than retrying the same command

## Error Handling

| Error | Solution |
|:------|:---------|
| HTTP 401 (Unauthorized) | Re-run `anakin login --api-key "your-key"` |
| HTTP 429 (Rate Limited) | Wait before retrying, do not loop immediately |
| Empty content | Try adding `--browser` flag for JavaScript-heavy sites |
| Timeout | Increase with `--timeout <seconds>` for slow pages |
| Batch partial failure | Check output JSON for individual statuses, retry failed URLs with `--browser` |
| Research fails | Fall back to `search` + multiple `scrape` calls manually |

## Output Formats

### Markdown (default for scrape)
- Clean, readable text stripped of navigation and ads
- Best for human reading and summarization
- File extension: `.md`

### JSON (structured)
- Structured data with title, content, metadata
- Best for processing and parsing
- File extension: `.json`

### Raw (full response)
- Full API response including HTML, links, images, metadata
- Best for debugging or accessing all available data
- File extension: `.json`

## Examples

### Example 1: Article extraction
```bash
anakin scrape "https://blog.example.com/article" -o article.md
```

### Example 2: Product comparison
```bash
anakin scrape-batch "https://store1.com/product" "https://store2.com/product" "https://store3.com/product" -o products.json
```

### Example 3: Find and scrape
```bash
# Step 1: Find relevant URLs
anakin search "best coffee shops in Seattle" -o coffee-search.json

# Step 2: Scrape the top results
anakin scrape-batch "url1" "url2" "url3" -o coffee-details.json
```

### Example 4: Market research
```bash
anakin research "market trends in electric vehicle adoption 2024-2026" -o ev-research.json
```

### Example 5: JavaScript-heavy site
```bash
anakin scrape "https://spa-application.com" --browser -o spa-content.md
```

### Example 6: Geo-targeted content
```bash
anakin scrape "https://news-site.com" --country us -o us-news.md
anakin scrape "https://news-site.com" --country gb -o gb-news.md
```

## Best Practices

1. **Start simple:** Try basic scrape first, add flags only if needed
2. **Be specific:** Use clear, specific search queries and research topics
3. **Quote URLs:** Always wrap URLs in quotes
4. **Save output:** Always use `-o` flag to save results to files
5. **Check status:** Run `anakin status` before starting work
6. **Batch wisely:** Group similar URLs together, max 10 per batch
7. **Wait on rate limits:** Don't retry immediately on 429 errors
8. **Choose the right tool:**
   - Single page → `scrape`
   - Multiple pages → `scrape-batch`
   - Don't have URLs → `search` first
   - Need deep analysis → `research`

## Troubleshooting

### Authentication issues
```bash
# Check status
anakin status

# Re-authenticate
anakin login --api-key "ak-your-key-here"
```

### Empty or incomplete content
- Add `--browser` flag for JavaScript-heavy sites
- Increase timeout with `--timeout 300`
- Check if the site requires specific geo-location with `--country <code>`

### Rate limiting
- Wait before retrying (don't loop immediately)
- Consider spacing out requests for large batch operations
- Check your API plan limits at anakin.io/dashboard

## Resources

- [Anakin Website](https://anakin.io)
- [Anakin Dashboard](https://anakin.io/dashboard) - Get API keys and check usage
- [anakin-cli on PyPI](https://pypi.org/project/anakin-cli/)
- [Support](mailto:support@anakin.io)
