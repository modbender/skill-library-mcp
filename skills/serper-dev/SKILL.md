---
name: serper-search
description: Search Google programmatically using the Serper.dev API. Returns structured organic results (title, URL, snippet, domain) for any query. Use when you need to search Google for websites, businesses, leads, or any information — especially as part of a lead generation pipeline, competitor research, or content research workflow. Cheaper and faster than SerpApi. Requires SERPER_API_KEY.
metadata:
  requires:
    env: [SERPER_API_KEY]
  primaryEnv: SERPER_API_KEY
---

# Serper.dev Search Skill

Fast, cheap Google Search API. Returns clean JSON. Best choice for lead generation pipelines.

## Credentials

Requires `SERPER_API_KEY` in environment.
Get a free key (2,500 searches) at serper.dev.

```env
SERPER_API_KEY=your_key_here
```

## Quick Usage

```python
import requests, os

def serper_search(query: str, num: int = 10, gl: str = "us") -> list[dict]:
    """
    Search Google via Serper.dev.
    Returns list of: {title, link, snippet, displayedLink, domain}
    """
    headers = {
        "X-API-KEY": os.environ["SERPER_API_KEY"],
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num, "gl": gl}
    r = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
    r.raise_for_status()
    
    results = r.json().get("organic", [])
    # Add clean domain extraction
    import tldextract
    for result in results:
        ext = tldextract.extract(result["link"])
        result["domain"] = f"{ext.domain}.{ext.suffix}"
    return results
```

## Lead Generation Usage

```python
import tldextract

EXCLUDE_DOMAINS = {
    "yelp.com", "facebook.com", "tripadvisor.com", "houzz.com",
    "thumbtack.com", "homeadvisor.com", "angi.com", "angieslist.com",
    "bbb.org", "yellowpages.com", "manta.com", "bark.com",
    "google.com", "nextdoor.com", "linkedin.com", "instagram.com"
}

def search_business_leads(niche: str, city: str, num_queries: int = 3) -> list[str]:
    """
    Run multiple queries for a niche+city combo.
    Returns deduplicated list of direct business website URLs.
    """
    query_templates = [
        f'"{niche} {city}"',
        f'"{niche} company {city}"',
        f'"{niche} service {city}"',
        f'"{city} {niche} contractor"',
    ]
    
    seen_domains = set()
    urls = []
    
    for template in query_templates[:num_queries]:
        query = template + " -yelp -facebook -tripadvisor -houzz -thumbtack -homeadvisor"
        results = serper_search(query, num=10)
        
        for r in results:
            domain = r["domain"]
            if domain not in EXCLUDE_DOMAINS and domain not in seen_domains:
                seen_domains.add(domain)
                urls.append(r["link"])
    
    return urls
```

## Available Endpoints

| Endpoint | URL | Use |
|---|---|---|
| Web search | `https://google.serper.dev/search` | Organic results |
| News | `https://google.serper.dev/news` | News articles |
| Images | `https://google.serper.dev/images` | Image results |
| Places | `https://google.serper.dev/places` | Google Maps results |
| Shopping | `https://google.serper.dev/shopping` | Product results |

## Places Endpoint (Local Business Discovery Alternative)

```python
def serper_places(query: str, gl: str = "us") -> list[dict]:
    """
    Search Google Maps / Local Places.
    Returns: {title, address, phone, website, rating, reviews}
    """
    headers = {"X-API-KEY": os.environ["SERPER_API_KEY"], "Content-Type": "application/json"}
    payload = {"q": query, "gl": gl}
    r = requests.post("https://google.serper.dev/places", headers=headers, json=payload)
    return r.json().get("places", [])

# Places returns website URLs + phone numbers directly — great for lead gen!
# usage: results = serper_places("landscaping company Portland OR")
# each result: {title, address, phone, website, rating, ratingCount}
```

## Response Structure

```json
{
  "organic": [
    {
      "title": "Green Valley Landscaping | Portland OR",
      "link": "https://www.greenvalleylandscaping.com",
      "snippet": "Professional landscaping services in Portland...",
      "displayedLink": "www.greenvalleylandscaping.com",
      "position": 1
    }
  ],
  "searchParameters": {"q": "landscaping portland OR", "gl": "us", "num": 10}
}
```

## Pricing Reference

| Plan | Cost | Searches |
|---|---|---|
| Free | $0 | 2,500 searches |
| Starter | $50 | 50,000 searches |
| Standard | $100 | 150,000 searches |

## Rate Limits & Best Practices

- No hard rate limit stated — but be reasonable
- Add 0.5s delay between rapid consecutive calls
- Cache results to avoid re-querying same niche+city
- Use `num=10` (default) — max is 100 per request
- `gl` param controls country: "us", "gb", "au", "ca", etc.

## Error Handling

```python
def serper_search_safe(query: str, num: int = 10) -> list[dict]:
    try:
        return serper_search(query, num)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Rate limited — waiting 5s")
            import time; time.sleep(5)
            return serper_search(query, num)
        print(f"Serper error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
```
