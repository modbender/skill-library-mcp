---
name: contact-enrichment
description: "Extract contact information from a website using a 3-tier approach. Direct HTML scraping, WHOIS lookup, then Hunter.io API domain search for verified business emails."
metadata:
  requires:
    packages: [requests, beautifulsoup4, lxml, python-whois]
  optionalEnv: [HUNTER_API_KEY]
---

# Contact Enrichment Skill

3-tier contact extraction. Runs cheapest method first, escalates only when needed.

## Extraction Hierarchy

```
Tier 1: Direct HTML Scrape (free, always try first)
   → Check: homepage, /contact, /about, /about-us, /contact-us
   → Extract: all emails, all phone numbers, business name
   ↓ (if no email found)
Tier 2: WHOIS Lookup (free)
   → Extract: registrant org, registrant email
   ↓ (if still no email)
Tier 3: Hunter.io API (paid, 25 free/month)
   → Domain search → verified emails + first/last name + job title
```

## Output Format

```python
{
    "business_name": "Green Valley Landscaping",
    "emails": ["info@greenvalley.com", "john@greenvalley.com"],
    "primary_email": "info@greenvalley.com",
    "phones": ["(503) 555-0123"],
    "primary_phone": "(503) 555-0123",
    "owner_name": "John Smith",           # from Hunter.io or About page
    "whois_org": "Green Valley LLC",
    "whois_email": "registrant@email.com",
    "source": "scrape",                   # "scrape" | "whois" | "hunter"
    "confidence": "high"                  # "high" | "medium" | "low"
}
```

## Tier 1: Direct HTML Scrape

```python
import re, requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

EMAIL_REGEX = re.compile(
    r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b'
)

PHONE_REGEX = re.compile(
    r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
)

# Emails that are never real contacts
EMAIL_BLACKLIST = {
    "example.com", "sentry.io", "schema.org", "w3.org",
    "wix.com", "wordpress.com", "squarespace.com", "shopify.com",
    "google.com", "jquery.com", "bootstrap.com", "cloudflare.com"
}

def is_valid_email(email: str) -> bool:
    domain = email.split("@")[-1].lower()
    return domain not in EMAIL_BLACKLIST and len(email) < 100

def scrape_page(url: str) -> tuple[str, str]:
    """Fetch a page. Returns (html, final_url)."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code < 400:
            return r.text, r.url
    except Exception:
        pass
    return "", url

def extract_from_html(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ")
    
    # Extract emails
    emails = list({e for e in EMAIL_REGEX.findall(text) if is_valid_email(e)})
    
    # Extract phones
    phones_raw = PHONE_REGEX.findall(text)
    phones = list({p[0] + p[1] if isinstance(p, tuple) else p for p in phones_raw})
    # Clean up: remove very short matches
    phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 10]
    
    # Extract business name from title
    title = soup.find("title")
    business_name = ""
    if title:
        t = title.text.strip()
        # Take the first meaningful segment
        for sep in ["|", "–", "-", "·", "—", ":"]:
            if sep in t:
                t = t.split(sep)[0].strip()
                break
        business_name = t
    
    return {"emails": emails, "phones": phones, "business_name": business_name}

def scrape_contact_pages(base_url: str, existing_html: str = "") -> dict:
    """
    Scrape multiple pages for contact info.
    existing_html: pass HTML already fetched by website-auditor to avoid re-fetching.
    """
    from urllib.parse import urljoin
    
    all_emails = set()
    all_phones = set()
    business_name = ""
    
    # Try homepage first (using already-fetched HTML if available)
    if existing_html:
        data = extract_from_html(existing_html)
        all_emails.update(data["emails"])
        all_phones.update(data["phones"])
        business_name = data["business_name"]
    
    # Try contact/about pages
    contact_paths = ["/contact", "/about", "/contact-us", "/about-us",
                     "/get-in-touch", "/reach-us", "/find-us"]
    
    for path in contact_paths:
        if all_emails:
            break  # Found emails — no need to keep crawling
        url = urljoin(base_url, path)
        html, _ = scrape_page(url)
        if html:
            data = extract_from_html(html)
            all_emails.update(data["emails"])
            all_phones.update(data["phones"])
            if not business_name:
                business_name = data["business_name"]
    
    emails = list(all_emails)
    phones = list(all_phones)
    
    return {
        "emails": emails,
        "primary_email": emails[0] if emails else None,
        "phones": phones,
        "primary_phone": phones[0] if phones else None,
        "business_name": business_name,
        "source": "scrape",
        "confidence": "high" if emails else "low"
    }
```

## Tier 2: WHOIS Lookup

```python
import whois  # pip install python-whois

def whois_lookup(domain: str) -> dict:
    """
    Look up WHOIS registration data.
    Returns registrant org + email if publicly available.
    """
    try:
        w = whois.whois(domain)
        
        # Extract emails (some registrars redact these)
        emails = w.emails if isinstance(w.emails, list) else ([w.emails] if w.emails else [])
        emails = [e for e in emails if e and is_valid_email(e) and "whoisprotect" not in e.lower()
                  and "privacy" not in e.lower() and "proxy" not in e.lower()]
        
        org = w.get("org") or w.get("registrant_organization") or ""
        creation = w.get("creation_date")
        if isinstance(creation, list):
            creation = creation[0]
        
        return {
            "whois_org": org,
            "whois_email": emails[0] if emails else None,
            "whois_emails": emails,
            "domain_created": str(creation)[:10] if creation else None,
            "registrar": w.get("registrar")
        }
    except Exception as e:
        return {"whois_org": None, "whois_email": None, "whois_error": str(e)}
```

## Tier 3: Hunter.io API

```python
import requests, os

def hunter_domain_search(domain: str, limit: int = 5) -> dict:
    """
    Search Hunter.io for emails associated with a domain.
    Returns verified business emails + contact names.
    Requires HUNTER_API_KEY env var.
    Free: 25 searches/month | Starter: $34/mo for 500
    """
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        return {"hunter_emails": [], "hunter_source": "no_key"}
    
    params = {
        "domain": domain,
        "api_key": api_key,
        "limit": limit,
        "type": "personal"  # personal | generic
    }
    
    try:
        r = requests.get("https://api.hunter.io/v2/domain-search", params=params, timeout=10)
        data = r.json().get("data", {})
        
        contacts = []
        for email_obj in data.get("emails", []):
            contacts.append({
                "email": email_obj.get("value"),
                "first_name": email_obj.get("first_name"),
                "last_name": email_obj.get("last_name"),
                "position": email_obj.get("position"),
                "confidence": email_obj.get("confidence"),
                "linkedin": email_obj.get("linkedin")
            })
        
        primary = contacts[0] if contacts else {}
        
        return {
            "hunter_emails": [c["email"] for c in contacts if c["email"]],
            "primary_email": primary.get("email"),
            "owner_name": f"{primary.get('first_name', '')} {primary.get('last_name', '')}".strip(),
            "owner_title": primary.get("position"),
            "owner_linkedin": primary.get("linkedin"),
            "hunter_contacts": contacts,
            "organization": data.get("organization"),
            "source": "hunter",
            "confidence": "high" if contacts else "low"
        }
    except Exception as e:
        return {"hunter_emails": [], "hunter_error": str(e)}

def hunter_email_verify(email: str) -> dict:
    """Verify if an email is deliverable."""
    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        return {"valid": None}
    params = {"email": email, "api_key": api_key}
    r = requests.get("https://api.hunter.io/v2/email-verifier", params=params)
    data = r.json().get("data", {})
    return {"valid": data.get("status") == "valid", "score": data.get("score")}
```

## Full Enrichment Runner

```python
import tldextract

def enrich_contact(url: str, existing_html: str = "") -> dict:
    """
    Run all 3 tiers. Returns the best contact data found.
    Pass existing_html from website-auditor to avoid re-fetching.
    """
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"
    
    result = {"url": url, "domain": domain}
    
    # Tier 1: Scrape
    scrape_data = scrape_contact_pages(url, existing_html)
    result.update(scrape_data)
    
    if not result.get("primary_email"):
        # Tier 2: WHOIS
        whois_data = whois_lookup(domain)
        result.update(whois_data)
        if whois_data.get("whois_email"):
            result["primary_email"] = whois_data["whois_email"]
            result["emails"] = [whois_data["whois_email"]] + result.get("emails", [])
            result["source"] = "whois"
            result["confidence"] = "medium"
    
    if not result.get("primary_email"):
        # Tier 3: Hunter.io
        hunter_data = hunter_domain_search(domain)
        result.update(hunter_data)
        if hunter_data.get("primary_email"):
            result["emails"] = hunter_data["hunter_emails"]
            result["source"] = "hunter"
            result["confidence"] = "high"
    
    return result
```

## Privacy & Ethics Notes

- Only scrape **publicly visible** contact info
- Respect `robots.txt` for large-scale operations
- Do not scrape pages behind login walls
- WHOIS data is public by design — legal to use
- Hunter.io only indexes publicly available emails
- Always include opt-out mechanism in outreach
- Comply with CAN-SPAM and GDPR when emailing
