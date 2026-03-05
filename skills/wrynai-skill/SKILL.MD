# WrynAI Web Crawling Skill

## Overview

This skill enables OpenClaw to perform advanced web crawling and content extraction using the WrynAI SDK. It provides capabilities for multi-page crawling, content extraction, search engine results parsing, and intelligent data gathering from websites.

## Core Capabilities

- **Multi-page crawling** with depth and breadth control
- **Content extraction** (text, markdown, structured data, links)
- **Search engine results** parsing (SERP data)
- **Screenshot capture** (viewport and full-page)
- **Smart listing extraction** (e-commerce, directory pages)
- **Pattern-based URL filtering** for targeted crawling

## Prerequisites

### Environment Setup

```bash
# Install the WrynAI SDK
pip install wrynai

# Set your API key as environment variable
export WRYNAI_API_KEY="your-api-key-here"
```

### API Key

Sign up at https://wryn.ai to obtain an API key. The key must be set in the `WRYNAI_API_KEY` environment variable.

## Usage Patterns

### 1. Basic Website Crawling

Use this when the user wants to crawl an entire website or section of a website.

```python
import os
from wrynai import WrynAI, WrynAIError

def crawl_website(url: str, max_pages: int = 10) -> dict:
    """
    Crawl a website starting from the given URL.
    
    Args:
        url: Starting URL for the crawl
        max_pages: Maximum number of pages to crawl (hard limit: 10)
    
    Returns:
        Dictionary containing crawl results with pages and their content
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    if not api_key:
        raise ValueError("WRYNAI_API_KEY environment variable required")
    
    try:
        with WrynAI(api_key=api_key) as client:
            result = client.crawl(
                url=url,
                max_pages=min(max_pages, 10),  # Hard limit enforced
                max_depth=3,
                return_urls=True,
            )
            
            return {
                "success": result.success,
                "total_pages": result.total_pages,
                "total_visited": result.total_visited,
                "pages": [
                    {
                        "url": page.page_url,
                        "content": page.content,
                        "urls_found": len(page.urls),
                        "discovered_urls": page.urls[:10],  # First 10 URLs
                    }
                    for page in result.pages
                ],
            }
    except WrynAIError as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": getattr(e, 'status_code', None),
        }
```

**When to use:**
- User asks to "crawl a website"
- User wants to gather content from multiple pages
- User needs to discover site structure

### 2. Documentation Crawling

Specialized crawling for documentation sites with pattern filtering.

```python
from wrynai import WrynAI, Engine

def crawl_documentation(base_url: str, doc_patterns: list = None) -> list:
    """
    Crawl documentation sites with targeted URL patterns.
    
    Args:
        base_url: Base URL of the documentation site
        doc_patterns: List of URL patterns to include (e.g., ["/docs/", "/api/"])
    
    Returns:
        List of crawled documentation pages with content
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    doc_patterns = doc_patterns or ["/docs/", "/guide/", "/api/", "/reference/"]
    
    with WrynAI(api_key=api_key) as client:
        result = client.crawl(
            url=base_url,
            max_pages=10,
            max_depth=3,
            include_patterns=doc_patterns,
            exclude_patterns=["/internal/", "/draft/", "/changelog/", "/admin/"],
            return_urls=True,
            timeout_ms=60000,  # 60 seconds for documentation crawling
        )
        
        return [
            {
                "url": page.page_url,
                "content": page.content,
                "word_count": len(page.content.split()),
            }
            for page in result.pages
        ]
```

**When to use:**
- User needs to extract documentation content
- User wants to crawl specific sections of a site
- User needs to build a knowledge base from docs

### 3. Search + Crawl Pipeline

Search for topics and crawl the top results.

```python
from wrynai import WrynAI, CountryCode, WrynAIError
import time

def search_and_crawl(query: str, num_sites: int = 3, country: str = "US") -> list:
    """
    Search for a query and crawl the top results.
    
    Args:
        query: Search query
        num_sites: Number of top results to crawl
        country: Country code for search localization
    
    Returns:
        List of search results with crawled content
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key) as client:
        # Step 1: Perform search
        try:
            search_result = client.search(
                query=query,
                num_results=num_sites,
                country_code=getattr(CountryCode, country, CountryCode.US),
                timeout_ms=120000,
            )
        except WrynAIError as e:
            return [{"error": f"Search failed: {str(e)}"}]
        
        # Step 2: Crawl each result
        results = []
        for result in search_result.organic_results[:num_sites]:
            try:
                crawl_result = client.crawl(
                    url=result.url,
                    max_pages=3,
                    max_depth=1,
                    timeout_ms=60000,
                )
                
                results.append({
                    "search_position": result.position,
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "crawled_pages": [
                        {
                            "url": page.page_url,
                            "content_preview": page.content[:500],
                            "full_content": page.content,
                        }
                        for page in crawl_result.pages
                    ],
                })
                
                # Rate limiting courtesy
                time.sleep(1)
                
            except WrynAIError as e:
                results.append({
                    "title": result.title,
                    "url": result.url,
                    "error": str(e),
                })
        
        return results
```

**When to use:**
- User wants to research a topic comprehensively
- User needs content from top search results
- User wants to compare information across multiple sources

### 4. Content Extraction Only

Extract specific content types without crawling.

```python
from wrynai import WrynAI, Engine

def extract_page_content(url: str, content_type: str = "text") -> dict:
    """
    Extract specific content from a single page.
    
    Args:
        url: Target URL
        content_type: Type of content to extract 
                     ("text", "markdown", "structured", "links", "title")
    
    Returns:
        Dictionary with extracted content
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key) as client:
        try:
            if content_type == "text":
                result = client.extract_text(url, extract_main_content=True)
                return {"url": url, "text": result.text}
            
            elif content_type == "markdown":
                result = client.extract_markdown(url, extract_main_content=True)
                return {"url": url, "markdown": result.markdown}
            
            elif content_type == "structured":
                result = client.extract_structured_text(url)
                return {
                    "url": url,
                    "main_text": result.main_text,
                    "headings": [
                        {"level": h.level, "tag": h.tag, "text": h.text}
                        for h in result.headings
                    ],
                    "links": [
                        {"text": l.text, "url": l.url, "internal": l.internal}
                        for l in result.links
                    ],
                }
            
            elif content_type == "links":
                result = client.extract_links(url)
                return {
                    "url": url,
                    "links": [
                        {"text": l.text, "url": l.url, "internal": l.internal}
                        for l in result.links
                    ],
                }
            
            elif content_type == "title":
                result = client.extract_title(url)
                return {"url": url, "title": result.title}
            
            else:
                return {"error": f"Unknown content_type: {content_type}"}
                
        except WrynAIError as e:
            return {"url": url, "error": str(e)}
```

**When to use:**
- User needs specific content from a single page
- User wants structured data extraction
- User needs to extract links or headings

### 5. Robust Crawling with Error Handling

Production-ready crawling with retry logic and rate limit handling.

```python
from wrynai import WrynAI, RateLimitError, TimeoutError, ServerError, WrynAIError
import time

def robust_crawl(url: str, max_attempts: int = 3, max_pages: int = 10) -> dict:
    """
    Crawl with automatic retry and error recovery.
    
    Args:
        url: Starting URL
        max_attempts: Maximum retry attempts
        max_pages: Maximum pages to crawl
    
    Returns:
        Crawl results with success status
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key, max_retries=3) as client:
        for attempt in range(max_attempts):
            try:
                result = client.crawl(
                    url=url,
                    max_pages=max_pages,
                    max_depth=3,
                    timeout_ms=60000,
                    retries=2,
                )
                
                return {
                    "success": True,
                    "attempt": attempt + 1,
                    "total_visited": result.total_visited,
                    "pages": [
                        {
                            "url": page.page_url,
                            "content_length": len(page.content),
                            "urls_found": len(page.urls),
                        }
                        for page in result.pages
                    ],
                }
            
            except RateLimitError as e:
                wait_time = e.retry_after or (2 ** attempt * 5)
                print(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            except TimeoutError:
                print(f"Timeout on attempt {attempt + 1}. Retrying...")
                continue
            
            except ServerError as e:
                wait_time = 2 ** attempt
                print(f"Server error: {e}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            except WrynAIError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "attempt": attempt + 1,
                }
        
        return {
            "success": False,
            "error": "Maximum retry attempts exceeded",
            "attempts": max_attempts,
        }
```

**When to use:**
- Production environments requiring reliability
- Crawling sites with rate limits
- When dealing with potentially unstable targets

### 6. JavaScript-Heavy Sites

For single-page applications and JavaScript-rendered content.

```python
from wrynai import WrynAI, Engine

def crawl_spa(url: str, max_pages: int = 5) -> dict:
    """
    Crawl single-page applications or JavaScript-heavy sites.
    
    Args:
        url: Starting URL
        max_pages: Maximum pages to crawl
    
    Returns:
        Crawl results with rendered content
    """
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key) as client:
        result = client.crawl(
            url=url,
            max_pages=max_pages,
            max_depth=2,
            engine=Engine.STEALTH_MODE,  # Use browser rendering
            timeout_ms=90000,  # Longer timeout for JS rendering
            return_urls=True,
        )
        
        return {
            "success": result.success,
            "total_visited": result.total_visited,
            "pages": [
                {
                    "url": page.page_url,
                    "content": page.content,
                    "urls_found": len(page.urls),
                }
                for page in result.pages
            ],
        }
```

**When to use:**
- User needs to crawl React/Vue/Angular applications
- Content is dynamically loaded via JavaScript
- Anti-bot protection is present

## Key Parameters & Configuration

### Crawl Limits

```python
# Hard limits enforced by the API
MAX_PAGES = 10      # Maximum pages per crawl
MAX_DEPTH = 3       # Maximum link depth
```

### Engine Selection

```python
Engine.SIMPLE         # Fast, for static HTML (default)
Engine.STEALTH_MODE   # Slower, for JavaScript-rendered content
```

### Timeout Recommendations

```python
# Simple scraping: 30,000 ms (30 seconds)
# Crawling: 60,000 ms (60 seconds) 
# Search operations: 120,000 ms (2 minutes)
# Smart extraction: 45,000 ms (45 seconds)
```

### URL Pattern Filtering

```python
# Common patterns for include_patterns
DOCS_PATTERNS = ["/docs/", "/guide/", "/api/", "/reference/"]
BLOG_PATTERNS = ["/blog/", "/posts/", "/articles/"]

# Common patterns for exclude_patterns
EXCLUDE_PATTERNS = ["/admin/", "/login/", "/draft/", "/internal/"]
MEDIA_EXCLUDE = [".pdf", ".jpg", ".png", ".mp4", ".zip"]
```

## Error Handling

### Exception Types

```python
from wrynai import (
    WrynAIError,           # Base exception
    AuthenticationError,    # Invalid API key (401)
    BadRequestError,        # Invalid parameters (400)
    RateLimitError,         # Rate limit exceeded (429)
    TimeoutError,           # Request timeout
    ServerError,            # Server error (5xx)
    ConnectionError,        # Network issue
    ValidationError,        # Local validation error
)
```

### Error Handling Pattern

```python
try:
    result = client.crawl(url)
except AuthenticationError:
    # Check WRYNAI_API_KEY environment variable
    pass
except RateLimitError as e:
    # Wait for e.retry_after seconds
    time.sleep(e.retry_after or 60)
except TimeoutError:
    # Increase timeout_ms parameter
    pass
except WrynAIError as e:
    # General API error
    print(f"Error: {e} (status: {e.status_code})")
```

## Best Practices

### 1. Always Use Environment Variables

```python
import os
api_key = os.environ.get("WRYNAI_API_KEY")
if not api_key:
    raise ValueError("WRYNAI_API_KEY environment variable required")
```

### 2. Use Context Managers

```python
# Recommended - automatic resource cleanup
with WrynAI(api_key=api_key) as client:
    result = client.crawl(url)

# Not recommended - manual cleanup required
client = WrynAI(api_key=api_key)
try:
    result = client.crawl(url)
finally:
    client.close()
```

### 3. Set Appropriate Timeouts

```python
# For simple pages
timeout_ms=30000

# For crawling multiple pages
timeout_ms=60000

# For JavaScript-heavy sites
timeout_ms=90000
```

### 4. Graceful Degradation

```python
try:
    # Try structured extraction first
    result = client.extract_structured_text(url)
    content = result.main_text
except Exception:
    try:
        # Fall back to simple text
        result = client.extract_text(url)
        content = result.text
    except Exception:
        content = None
```

### 5. Respect Rate Limits

```python
import time

for url in urls:
    result = client.crawl(url)
    time.sleep(1)  # Be nice to the API
```

## Advanced Features

### Smart Listing Extraction (PRO)

Extract structured data from listing pages (e-commerce, directories).

```python
def extract_product_listings(url: str) -> list:
    """Extract product information from listing pages."""
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key) as client:
        result = client.auto_listing(
            url=url,
            engine=Engine.STEALTH_MODE,
            timeout_ms=60000,
        )
        
        return [
            {
                "title": item.get("title"),
                "price": item.get("price"),
                "rating": item.get("rating"),
                "url": item.get("url"),
            }
            for item in result.items
        ]
```

### Screenshot Capture

```python
import base64
from wrynai import ScreenshotType

def capture_page_screenshot(url: str, fullpage: bool = False) -> str:
    """Capture page screenshot and save to file."""
    api_key = os.environ.get("WRYNAI_API_KEY")
    
    with WrynAI(api_key=api_key) as client:
        result = client.take_screenshot(
            url=url,
            screenshot_type=ScreenshotType.FULLPAGE if fullpage else ScreenshotType.VIEWPORT,
            timeout_ms=30000,
        )
        
        # Decode and save
        image_data = result.screenshot
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        filename = "screenshot.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(image_data))
        
        return filename
```

## Common Use Cases

### 1. Competitive Research
"Search for [topic] and crawl the top 5 results"

### 2. Documentation Aggregation
"Crawl the Python documentation and extract all API references"

### 3. Content Migration
"Crawl our old website and extract all blog posts in markdown"

### 4. Link Analysis
"Find all external links on [website]"

### 5. Site Monitoring
"Crawl [site] and check if [content] is present"

### 6. Knowledge Base Creation
"Crawl [documentation site] and create a searchable knowledge base"

## Limitations & Considerations

1. **Hard Limits**: Maximum 10 pages per crawl, depth of 3
2. **Rate Limits**: API has rate limits; handle `RateLimitError` appropriately
3. **Timeout Management**: Adjust timeouts based on site complexity
4. **JavaScript Rendering**: Use `Engine.STEALTH_MODE` for SPAs (slower but necessary)
5. **Robots.txt**: SDK respects robots.txt; some pages may be blocked
6. **Dynamic Content**: Some dynamically loaded content may require stealth mode

## Troubleshooting

### Common Issues

**Issue**: `AuthenticationError`
- **Solution**: Verify `WRYNAI_API_KEY` environment variable is set correctly

**Issue**: `RateLimitError`
- **Solution**: Implement retry with `e.retry_after` wait time

**Issue**: `TimeoutError`
- **Solution**: Increase `timeout_ms` parameter

**Issue**: Empty content returned
- **Solution**: Try `Engine.STEALTH_MODE` for JavaScript-rendered pages

**Issue**: Missing links/content
- **Solution**: Check `exclude_patterns` and `include_patterns` configuration

## Integration with OpenClaw

When using this skill with OpenClaw:

1. **Set environment variable** before running:
   ```bash
   export WRYNAI_API_KEY="your-api-key"
   ```

2. **Install dependencies**:
   ```bash
   pip install wrynai
   ```

3. **Use in your OpenClaw workflows**:
   - Call the crawling functions directly from your automation scripts
   - Integrate with other OpenClaw skills for comprehensive data pipelines
   - Use the returned data structures in downstream processing

## API Reference Quick Links

- Documentation: https://docs.wryn.ai
- API Signup: https://wryn.ai
- GitHub: https://github.com/wrynai/wrynai-python

## Version Information

- **Skill Version**: 1.0.0
- **SDK Version**: wrynai v1.0.0
- **Python Version**: 3.8+
- **Last Updated**: 2025-02-07