# Proxy Rotation

## When to Use

- Rate limiting on target sites
- Geographic restrictions
- Large-scale crawls (100+ pages)
- Anti-bot evasion (with permission)

## ProxyRotator Setup

```python
from scrapling.spiders import ProxyRotator

# Cyclic rotation (round-robin)
rotator = ProxyRotator([
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://user:pass@proxy3.example.com:8080",
], strategy="cyclic")

# Get next proxy
proxy = rotator.next()
```

## With Sessions

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(proxy=rotator.next()) as session:
    page = session.get('https://example.com')
```

## With Spiders

```python
from scrapling.spiders import Spider
from scrapling.fetchers import FetcherSession

class RotatingSpider(Spider):
    name = "rotating"
    
    def __init__(self):
        self.rotator = ProxyRotator([
            "http://proxy1:8080",
            "http://proxy2:8080",
        ])
    
    def configure_sessions(self, manager):
        manager.add("rotating", FetcherSession())
    
    async def parse(self, response):
        # Access current session and rotate proxy
        self.sessions["rotating"].proxy = self.rotator.next()
        # ... continue parsing
```

## Custom Rotation Strategy

```python
import random

class RandomRotator:
    def __init__(self, proxies):
        self.proxies = proxies
    
    def next(self):
        return random.choice(self.proxies)

rotator = RandomRotator(["http://p1:8080", "http://p2:8080"])
```

## Provider Recommendations

See Sponsors in Scrapling README for proxy providers:
- Scrapeless
- ThorData
- Evomi
- Decodo
- ProxyEmpire
- SwiftProxy
- RapidProxy

## Best Practices

1. **Test proxies first** — Check latency and success rate
2. **Rotate on failure** — Switch proxy after 3 consecutive failures
3. **Respect rate limits** — Don't use proxies to bypass reasonable limits
4. **Session affinity** — Keep same proxy for session duration when possible
5. **Monitor usage** — Track success rates per proxy
