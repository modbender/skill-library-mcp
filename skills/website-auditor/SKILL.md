---
name: website-auditor
description: "Audit any website across 8 quality signals to determine if it is outdated, broken, or neglected. Returns a structured audit dict used by the lead-scorer skill."
metadata:
  requires:
    env: [PAGESPEED_API_KEY]
    packages: [requests, beautifulsoup4, lxml, python-Wappalyzer, python-whois]
---

# Website Auditor Skill

Runs 8 automated checks on any URL. Returns a structured dict consumed by `lead-scorer`.

## Output Format

```python
{
    "url": "https://example.com",
    "domain": "example.com",
    "status_code": 200,           # or "DEAD", "TIMEOUT", "SSL_ERROR"
    "is_live": True,
    "copyright_year": 2018,
    "years_outdated": 7,
    "last_modified": "2019-03-15", # or None
    "tech_stack": ["WordPress 4.9", "jQuery 1.11", "PHP"],
    "has_outdated_cms": True,
    "pagespeed_mobile": 32,        # 0–100 or None if API failed
    "pagespeed_seo": 61,
    "is_mobile_friendly": False,
    "has_ssl": True,
    "design_signals": ["table_layout", "no_open_graph", "no_favicon"],
    "raw_html": "...",             # used by contact-enrichment
    "audit_timestamp": "2025-03-02T17:00:00"
}
```

## Signal 1: HTTP Status Check

```python
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_status(url: str) -> dict:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        return {
            "status_code": r.status_code,
            "is_live": r.status_code < 400,
            "final_url": r.url,
            "raw_html": r.text if r.status_code < 400 else "",
            "response_headers": dict(r.headers)
        }
    except requests.exceptions.SSLError:
        return {"status_code": "SSL_ERROR", "is_live": False, "raw_html": "", "has_ssl": False}
    except requests.exceptions.ConnectionError:
        return {"status_code": "DEAD", "is_live": False, "raw_html": ""}
    except requests.exceptions.Timeout:
        return {"status_code": "TIMEOUT", "is_live": False, "raw_html": ""}
```

## Signal 2: Copyright Year

```python
import re
from datetime import datetime

def get_copyright_year(html: str) -> dict:
    # Match © 2019, Copyright 2019, (c) 2019, &copy; 2019
    pattern = r'(?:©|&copy;|copyright|\(c\))\s*(?:\d{4}\s*[-–]\s*)?(\d{4})'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    if not matches:
        return {"copyright_year": None, "years_outdated": None}
    
    latest_year = max(int(y) for y in matches)
    current_year = datetime.now().year
    years_outdated = current_year - latest_year
    
    return {
        "copyright_year": latest_year,
        "years_outdated": max(0, years_outdated)
    }
```

## Signal 3: Last-Modified Header

```python
from datetime import datetime
from email.utils import parsedate_to_datetime

def get_last_modified(headers: dict) -> str | None:
    lm = headers.get("Last-Modified") or headers.get("last-modified")
    if not lm:
        return None
    try:
        dt = parsedate_to_datetime(lm)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return lm  # return raw string if parsing fails
```

## Signal 4: Technology Stack (Wappalyzer)

```python
from Wappalyzer import Wappalyzer, WebPage

OUTDATED_TECH = {
    "Joomla", "Drupal 6", "Drupal 7", "osCommerce",
    "Magento 1", "vBulletin", "phpBB", "Flash",
    "Silverlight", "ASP.NET WebForms"
}

OUTDATED_JS = {"jQuery 1.", "jQuery 2.", "MooTools", "Prototype"}

def detect_tech_stack(url: str, html: str, headers: dict) -> dict:
    try:
        wappalyzer = Wappalyzer.latest()
        webpage = WebPage(url, html=html, headers=headers)
        techs = wappalyzer.analyze_with_categories(webpage)
        
        tech_list = list(techs.keys())
        has_outdated = any(
            any(bad in t for bad in OUTDATED_TECH) or
            any(t.startswith(js) for js in OUTDATED_JS)
            for t in tech_list
        )
        
        # Check for very old WordPress versions
        for t in tech_list:
            if t.startswith("WordPress"):
                try:
                    ver = float(t.split(" ")[1][:3])
                    if ver < 5.0:
                        has_outdated = True
                except:
                    pass
        
        return {"tech_stack": tech_list, "has_outdated_cms": has_outdated}
    except Exception as e:
        return {"tech_stack": [], "has_outdated_cms": False, "tech_error": str(e)}
```

## Signal 5: PageSpeed Score (Google PSI API — Free)

```python
import requests, os

def get_pagespeed(url: str) -> dict:
    api_key = os.environ.get("PAGESPEED_API_KEY")
    if not api_key:
        return {"pagespeed_mobile": None, "pagespeed_seo": None}
    
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {"url": url, "key": api_key, "strategy": "mobile"}
    
    try:
        r = requests.get(endpoint, params=params, timeout=30)
        data = r.json()
        cats = data.get("lighthouseResult", {}).get("categories", {})
        return {
            "pagespeed_mobile": round(cats.get("performance", {}).get("score", 0) * 100),
            "pagespeed_seo": round(cats.get("seo", {}).get("score", 0) * 100),
            "pagespeed_accessibility": round(cats.get("accessibility", {}).get("score", 0) * 100),
        }
    except Exception as e:
        return {"pagespeed_mobile": None, "pagespeed_seo": None, "pagespeed_error": str(e)}
```

## Signal 6: Mobile Responsiveness

```python
from bs4 import BeautifulSoup

def check_mobile_friendly(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    viewport = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "viewport"})
    return viewport is not None
```

## Signal 7: SSL Certificate

```python
import ssl, socket, tldextract

def check_ssl(url: str) -> bool:
    """Returns True if valid SSL, False if no SSL or invalid cert."""
    if url.startswith("http://"):
        return False
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"
    try:
        ctx = ssl.create_default_context()
        conn = ctx.wrap_socket(socket.socket(), server_hostname=domain)
        conn.settimeout(5)
        conn.connect((domain, 443))
        conn.close()
        return True
    except Exception:
        return False
```

## Signal 8: Design Age Signals

```python
from bs4 import BeautifulSoup

def detect_design_signals(html: str, url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    signals = []
    
    # 1. Table-based layout (old school)
    tables = soup.find_all("table")
    non_data_tables = [t for t in tables if not t.find_parent(["table", "th", "td"])]
    if len(non_data_tables) > 3:
        signals.append("table_layout")
    
    # 2. Flash or Silverlight
    if soup.find("object") or soup.find("embed"):
        if any(x in html.lower() for x in ["swf", "flash", "silverlight"]):
            signals.append("flash_detected")
    
    # 3. Heavy inline styles (pre-CSS era)
    inline_count = len(soup.find_all(style=True))
    if inline_count > 15:
        signals.append("heavy_inline_styles")
    
    # 4. No Open Graph tags (no social/modern marketing)
    if not soup.find("meta", property="og:title"):
        signals.append("no_open_graph")
    
    # 5. No favicon
    favicon = soup.find("link", rel=lambda x: x and "icon" in (x if isinstance(x, str) else " ".join(x)).lower())
    if not favicon:
        signals.append("no_favicon")
    
    # 6. No meta description
    if not soup.find("meta", attrs={"name": "description"}):
        signals.append("no_meta_description")
    
    # 7. Frames / framesets (ancient)
    if soup.find("frameset") or soup.find("frame"):
        signals.append("uses_frames")
    
    # 8. Font tags (pre-CSS styling)
    if len(soup.find_all("font")) > 3:
        signals.append("font_tags")
    
    # 9. No HTTPS in URL
    if url.startswith("http://"):
        signals.append("no_https_url")
    
    return signals
```

## Full Audit Runner

```python
import tldextract
from datetime import datetime
import time

def audit_website(url: str) -> dict:
    """Run all 8 signals. Returns complete audit dict."""
    result = {"url": url, "audit_timestamp": datetime.now().isoformat()}
    
    ext = tldextract.extract(url)
    result["domain"] = f"{ext.domain}.{ext.suffix}"
    
    # Signal 1: Status + HTML
    status = check_status(url)
    result.update(status)
    
    if not result.get("is_live"):
        result["has_ssl"] = False
        return result  # Dead site — score it and move on
    
    html = result.get("raw_html", "")
    headers = result.get("response_headers", {})
    
    # Signal 2: Copyright year
    result.update(get_copyright_year(html))
    
    # Signal 3: Last-Modified header
    result["last_modified"] = get_last_modified(headers)
    
    # Signal 4: Tech stack
    result.update(detect_tech_stack(url, html, headers))
    
    # Signal 5: PageSpeed (slowest — do last or async)
    result.update(get_pagespeed(url))
    
    # Signal 6: Mobile responsive
    result["is_mobile_friendly"] = check_mobile_friendly(html)
    
    # Signal 7: SSL
    result["has_ssl"] = check_ssl(url)
    
    # Signal 8: Design signals
    result["design_signals"] = detect_design_signals(html, url)
    
    return result


def audit_batch(urls: list[str], delay: float = 1.5) -> list[dict]:
    """Audit multiple URLs with delay between requests."""
    results = []
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Auditing: {url}")
        try:
            audit = audit_website(url)
            results.append(audit)
        except Exception as e:
            results.append({"url": url, "error": str(e), "is_live": False})
        time.sleep(delay)
    return results
```

## Async Version (For Speed at Scale)

```python
import asyncio, aiohttp

async def audit_website_async(session: aiohttp.ClientSession, url: str) -> dict:
    """Async version — fetch HTML only. Run other checks synchronously after."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            html = await resp.text()
            headers = dict(resp.headers)
            status = resp.status
    except Exception as e:
        return {"url": url, "status_code": "DEAD", "is_live": False, "raw_html": ""}
    
    # Run synchronous checks on fetched data
    result = {"url": url, "status_code": status, "is_live": status < 400, "raw_html": html}
    result.update(get_copyright_year(html))
    result["is_mobile_friendly"] = check_mobile_friendly(html)
    result["design_signals"] = detect_design_signals(html, url)
    result["last_modified"] = get_last_modified(headers)
    return result

async def audit_batch_async(urls: list[str], concurrency: int = 5) -> list[dict]:
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LeadScanner/1.0)"}
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [audit_website_async(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)
```
