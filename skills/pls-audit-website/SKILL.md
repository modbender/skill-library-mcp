---
name: audit-website
description: Perform full health check on websites, identifying technical friction points and user experience issues. Use when: (1) Auditing website performance, (2) Checking for broken links, (3) Analyzing page structure, (4) Testing accessibility, (5) Reviewing security headers.
---

# Website Audit

Comprehensive website health check for performance, accessibility, security, and user experience.

## Quick Health Check

```bash
# One-command overview
curl -I https://example.com && \
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" -o /dev/null -s https://example.com
```

---

## Performance Audit

### Page Load Time

```bash
# Using curl for timing
curl -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nSSL: %{time_appconnect}s\nTTFB: %{time_starttransfer}s\nTotal: %{time_total}s\nSize: %{size_download} bytes\n" -o /dev/null -s https://example.com

# Using lighthouse
npx lighthouse https://example.com --only-categories=performance --output=json
```

### Resource Analysis

```python
import requests
from urllib.parse import urlparse

def analyze_resources(url):
    response = requests.get(url)
    resources = []
    
    # Parse HTML for resources
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Images
    for img in soup.find_all('img'):
        resources.append({
            'type': 'image',
            'url': img.get('src'),
            'size_estimate': 'unknown'
        })
    
    # Scripts
    for script in soup.find_all('script', src=True):
        resources.append({
            'type': 'script',
            'url': script.get('src')
        })
    
    # Stylesheets
    for link in soup.find_all('link', rel='stylesheet'):
        resources.append({
            'type': 'stylesheet',
            'url': link.get('href')
        })
    
    return resources
```

### Core Web Vitals

```bash
# Using web-vitals CLI
npx web-vitals https://example.com

# LCP (Largest Contentful Paint): < 2.5s
# FID (First Input Delay): < 100ms
# CLS (Cumulative Layout Shift): < 0.1
```

---

## Broken Link Checker

### Find Broken Links

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_broken_links(base_url, max_depth=2):
    visited = set()
    broken = []
    
    def check_page(url, depth):
        if depth > max_depth or url in visited:
            return
        visited.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code >= 400:
                broken.append({'url': url, 'status': response.status_code})
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                if urlparse(href).netloc == urlparse(base_url).netloc:
                    check_page(href, depth + 1)
        except Exception as e:
            broken.append({'url': url, 'error': str(e)})
    
    check_page(base_url, 0)
    return broken
```

### Quick Link Check

```bash
# Using wget
wget --spider -r -l 2 https://example.com 2>&1 | grep -E "(broken|failed|error)"

# Using linkchecker
pip install LinkChecker
linkchecker https://example.com
```

---

## Security Audit

### Check Security Headers

```bash
# Fetch and analyze headers
curl -I https://example.com

# Expected headers:
# - Strict-Transport-Security (HSTS)
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY or SAMEORIGIN
# - Content-Security-Policy
# - X-XSS-Protection
```

### Security Header Analysis

```python
import requests

def audit_security_headers(url):
    response = requests.head(url)
    headers = response.headers
    
    recommended = {
        'Strict-Transport-Security': 'Enable HSTS',
        'X-Content-Type-Options': 'Set to nosniff',
        'X-Frame-Options': 'Set to DENY or SAMEORIGIN',
        'Content-Security-Policy': 'Define CSP',
        'X-XSS-Protection': 'Enable XSS filter',
        'Referrer-Policy': 'Set referrer policy',
        'Permissions-Policy': 'Define permissions'
    }
    
    issues = []
    for header, recommendation in recommended.items():
        if header not in headers:
            issues.append(f"Missing {header}: {recommendation}")
    
    return {
        "present": {h: headers.get(h) for h in recommended if h in headers},
        "missing": issues
    }
```

### SSL Certificate Check

```bash
# Check SSL details
openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -text | grep -E "(Issuer|Not After|Subject)"

# Quick expiry check
openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -dates
```

---

## Accessibility Audit

### Basic Accessibility Check

```python
from bs4 import BeautifulSoup

def accessibility_audit(html):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []
    
    # Check images for alt text
    for img in soup.find_all('img'):
        if not img.get('alt'):
            issues.append(f"Image missing alt: {img.get('src', 'unknown')}")
    
    # Check for lang attribute
    if not soup.find('html', lang=True):
        issues.append("Missing lang attribute on <html>")
    
    # Check headings hierarchy
    headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    prev_level = 0
    for h in soup.find_all(headings):
        level = int(h.name[1])
        if level > prev_level + 1:
            issues.append(f"Skipped heading level: h{prev_level} to h{level}")
        prev_level = level
    
    # Check for form labels
    for input_tag in soup.find_all('input'):
        if not input_tag.get('id') or not soup.find('label', attrs={'for': input_tag.get('id')}):
            if not input_tag.get('aria-label'):
                issues.append(f"Input missing label: {input_tag.get('name', 'unknown')}")
    
    return issues
```

### Using axe-core

```bash
# Using @axe-core/cli
npx axe-cli https://example.com

# Using pa11y
npx pa11y https://example.com
```

---

## SEO Quick Check

```python
def seo_quick_check(html, url):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    issues = []
    
    # Title
    title = soup.find('title')
    if not title:
        issues.append("Missing <title> tag")
    elif len(title.text) < 30 or len(title.text) > 60:
        issues.append(f"Title length suboptimal: {len(title.text)} chars (30-60 ideal)")
    
    # Meta description
    desc = soup.find('meta', attrs={'name': 'description'})
    if not desc:
        issues.append("Missing meta description")
    
    # H1
    h1_tags = soup.find_all('h1')
    if len(h1_tags) == 0:
        issues.append("Missing H1 tag")
    elif len(h1_tags) > 1:
        issues.append("Multiple H1 tags found")
    
    # Canonical
    if not soup.find('link', rel='canonical'):
        issues.append("Missing canonical tag")
    
    # Robots meta
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots and 'noindex' in robots.get('content', ''):
        issues.append("Page is set to noindex")
    
    return issues
```

---

## Website Audit Report Template

```markdown
# Website Audit Report

**URL:** https://example.com  
**Date:** YYYY-MM-DD  
**Overall Score:** X/100

---

## Performance
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Load Time | 3.2s | <3s | ⚠️ |
| TTFB | 0.8s | <0.5s | ⚠️ |
| Page Size | 1.2MB | <1MB | ⚠️ |
| Requests | 45 | <30 | ⚠️ |

## Security
| Header | Status |
|--------|--------|
| HSTS | ✅ Present |
| X-Frame-Options | ❌ Missing |
| CSP | ❌ Missing |
| X-Content-Type-Options | ✅ Present |

## Accessibility
- Images missing alt: 3
- Form inputs missing labels: 2
- Heading hierarchy issues: 1

## SEO
- Title: ✅ 52 chars
- Meta description: ❌ Missing
- H1: ✅ Single tag
- Canonical: ✅ Present

## Broken Links
- /old-page (404)
- /missing-resource (404)

## Recommendations
1. Add missing security headers (CSP, X-Frame-Options)
2. Optimize images to reduce page size
3. Add meta descriptions to all pages
4. Fix broken links
5. Add alt text to images

## Priority Actions
1. **Critical:** Add CSP header
2. **High:** Fix broken links
3. **Medium:** Optimize images
4. **Low:** Add meta descriptions
```

---

## Quick Commands Reference

| Check | Command |
|-------|---------|
| Response headers | `curl -I URL` |
| Load timing | `curl -w "%{time_total}s" -o /dev/null -s URL` |
| SSL check | `openssl s_client -connect HOST:443` |
| Broken links | `linkchecker URL` |
| Accessibility | `npx pa11y URL` |
| Performance | `npx lighthouse URL` |
| Security headers | `curl -I URL \| grep -i "x-\|strict"` |
