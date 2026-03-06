# Scrape — Code Patterns

## robots.txt Check (Do First)

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def can_scrape(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True  # No robots.txt = allowed
    return rp.can_fetch(user_agent, url)
```

## Session Setup

```python
import requests

def create_session(contact_email: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (contact: {contact_email})",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    return session
```

## Rate-Limited Fetcher

```python
import time
import random
import logging

logger = logging.getLogger(__name__)

def fetch_politely(session, url, min_delay=2.0, max_retries=5):
    """Fetch with rate limiting, backoff, and audit logging."""
    
    for attempt in range(max_retries):
        # Polite delay with jitter
        delay = min_delay + random.uniform(0, 0.5)
        time.sleep(delay)
        
        response = session.get(url)
        
        # Audit trail
        logger.info(f"SCRAPE url={url} status={response.status_code}")
        
        # Check rate limit headers
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining and int(remaining) < 5:
            logger.warning(f"Rate limit low: {remaining} remaining")
            time.sleep(10)  # Proactive slowdown
        
        # Handle 429
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", 60)
            wait = int(retry_after) if str(retry_after).isdigit() else 60
            logger.warning(f"429 received, waiting {wait}s")
            time.sleep(wait)
            continue
        
        # Success or client error (don't retry 4xx except 429)
        if response.status_code < 500:
            return response
        
        # Server error: exponential backoff
        wait = min(2 ** attempt + random.uniform(0, 1), 60)
        logger.warning(f"5xx error, retry in {wait:.1f}s")
        time.sleep(wait)
    
    raise Exception(f"Failed after {max_retries} retries: {url}")
```

## Full Example

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

contact = "your-email@example.com"
target = "https://example.com/products"

# 1. Check robots.txt
if not can_scrape(target):
    raise SystemExit("Blocked by robots.txt")

# 2. Create session
session = create_session(contact)

# 3. Fetch politely
response = fetch_politely(session, target)

# 4. Process (your logic here)
print(f"Got {len(response.text)} bytes")
```
