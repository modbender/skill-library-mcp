#!/usr/bin/env python3
"""
contact-finder — Find professional emails and contacts from name + company/domain.
Combines SerpAPI (Google Search) + OpenAI GPT-4o-mini for extraction and validation.

Usage:
    python3 find_contacts.py --company "Acme" --domain "acme.com" --name "John Doe"
    python3 find_contacts.py --company "Stripe" --domain "stripe.com" --output json

Importable:
    from find_contacts import find_contacts
    results = find_contacts(company="Acme", domain="acme.com", name="John Doe")
"""

import os
import sys
import json
import re
import argparse
import requests

# ── Credentials (from environment variables) ─────────────────────────────────
# Set these in your environment before running:
#   export SERPAPI_KEY=your_serpapi_key
#   export OPENAI_API_KEY=your_openai_key
#   export BRAVE_API_KEYS=key1,key2  (optional fallback)
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BRAVE_API_KEYS = [k for k in os.environ.get("BRAVE_API_KEYS", "").split(",") if k]


# ── Email pattern generation ─────────────────────────────────────────────────

def generate_email_patterns(name: str, domain: str) -> list[dict]:
    """Generate common email format guesses from a full name and domain."""
    parts = name.strip().lower().split()
    if len(parts) < 2:
        first = parts[0] if parts else ""
        last = ""
    else:
        first = parts[0]
        last = parts[-1]

    patterns = []
    if first and last:
        candidates = [
            (f"{first}.{last}@{domain}", "firstname.lastname"),
            (f"{first[0]}.{last}@{domain}", "f.lastname"),
            (f"{first}{last}@{domain}", "firstnamelastname"),
            (f"{first}@{domain}", "firstname"),
            (f"{last}@{domain}", "lastname"),
            (f"{first}_{last}@{domain}", "firstname_lastname"),
            (f"{first[0]}{last}@{domain}", "flastname"),
            (f"{last}.{first}@{domain}", "lastname.firstname"),
            (f"{first}.{last[0]}@{domain}", "firstname.l"),
        ]
    elif first:
        candidates = [(f"{first}@{domain}", "firstname")]
    else:
        return patterns

    for email, pattern in candidates:
        patterns.append({
            "email": email,
            "pattern": pattern,
            "confidence": "low",
            "source": "pattern_guess"
        })
    return patterns


# ── SerpAPI search ───────────────────────────────────────────────────────────

def serpapi_search(query: str) -> list[dict]:
    """Search Google via SerpAPI and return organic results."""
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 10,
        "engine": "google"
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic_results", [])
    except Exception as e:
        print(f"[WARN] SerpAPI error: {e}", file=sys.stderr)
        return []


def brave_search(query: str) -> list[dict]:
    """Fallback: Search via Brave Search API."""
    for key in BRAVE_API_KEYS:
        try:
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 10},
                headers={"Accept": "application/json", "X-Subscription-Token": key.strip()},
                timeout=15
            )
            if resp.status_code == 200:
                results = resp.json().get("web", {}).get("results", [])
                # Normalize to SerpAPI format
                return [{"title": r.get("title", ""), "link": r.get("url", ""), "snippet": r.get("description", "")} for r in results]
        except Exception as e:
            print(f"[WARN] Brave search error ({key[:10]}...): {e}", file=sys.stderr)
    return []


def search_with_fallback(query: str) -> list[dict]:
    results = serpapi_search(query)
    if not results:
        results = brave_search(query)
    return results


# ── OpenAI extraction ────────────────────────────────────────────────────────

def extract_contacts_with_openai(snippets: list[str], domain: str, name: str = "") -> list[dict]:
    """Use GPT-4o-mini to extract contacts from search snippets."""
    if not snippets:
        return []

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    combined = "\n\n".join(snippets[:15])  # limit tokens
    name_hint = f" for person named '{name}'" if name else ""
    
    prompt = f"""Extract professional contact information{name_hint} from the following search snippets.
Focus on domain: {domain}

For each contact found, return a JSON array with objects containing:
- "email": email address (string or null)
- "linkedin": LinkedIn URL (string or null)  
- "title": job title (string or null)
- "name": person name (string or null)
- "confidence": "high" if email found directly in text, "medium" if inferred from context, "low" if uncertain

Only return valid JSON array. If nothing found, return [].

SNIPPETS:
{combined}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        raw = response.choices[0].message.content.strip()
        # Extract JSON from response
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception as e:
        print(f"[WARN] OpenAI error: {e}", file=sys.stderr)
        return []


# ── Main logic ───────────────────────────────────────────────────────────────

def find_contacts(company: str, domain: str, name: str = "") -> list[dict]:
    """
    Find professional contacts for a company/domain.
    
    Args:
        company: Company name (e.g. "Acme Corp")
        domain: Email domain (e.g. "acme.com")
        name: Optional full name to focus search
    
    Returns:
        List of contact dicts with keys: email, linkedin, title, name, confidence, source
    """
    all_snippets = []
    all_results = []

    # Build search queries
    queries = []
    if name:
        queries.append(f'"{name}" {company} email')
        queries.append(f'"{name}" site:linkedin.com {company}')
        queries.append(f'"{name}" "@{domain}"')
    else:
        queries.append(f'{company} team email "@{domain}"')
        queries.append(f'site:linkedin.com/in "{company}" contact')

    print(f"[*] Searching for contacts at {company} ({domain}){'  — ' + name if name else ''}...")

    for query in queries:
        print(f"[*] Query: {query}")
        results = search_with_fallback(query)
        for r in results:
            snippet = f"{r.get('title', '')} | {r.get('snippet', '')} | {r.get('link', '')}"
            all_snippets.append(snippet)
            all_results.append(r)

    # Extract contacts via OpenAI
    contacts = []
    if all_snippets:
        print(f"[*] Analyzing {len(all_snippets)} snippets with GPT-4o-mini...")
        ai_contacts = extract_contacts_with_openai(all_snippets, domain, name)
        for c in ai_contacts:
            # Validate email domain
            email = c.get("email", "")
            if email and domain.lower() in email.lower():
                c["confidence"] = "high"
            elif email:
                c["confidence"] = "medium"
            c["source"] = "serpapi+openai"
            contacts.append(c)

    # Extract LinkedIn URLs from raw results
    linkedin_urls = set()
    for r in all_results:
        link = r.get("link", "")
        if "linkedin.com/in/" in link:
            linkedin_urls.add(link.split("?")[0])

    # Add LinkedIn profiles not already in contacts
    existing_linkedins = {c.get("linkedin", "") for c in contacts}
    for url in linkedin_urls:
        if url not in existing_linkedins:
            contacts.append({
                "email": None,
                "linkedin": url,
                "title": None,
                "name": name or None,
                "confidence": "low",
                "source": "serpapi_linkedin"
            })

    # Add pattern guesses if name provided
    if name:
        pattern_emails = generate_email_patterns(name, domain)
        existing_emails = {c.get("email", "").lower() for c in contacts if c.get("email")}
        for pe in pattern_emails:
            if pe["email"].lower() not in existing_emails:
                contacts.append({
                    "email": pe["email"],
                    "linkedin": None,
                    "title": None,
                    "name": name,
                    "confidence": pe["confidence"],
                    "source": pe["source"]
                })

    # Sort by confidence
    order = {"high": 0, "medium": 1, "low": 2}
    contacts.sort(key=lambda x: order.get(x.get("confidence", "low"), 2))

    return contacts


# ── CLI ──────────────────────────────────────────────────────────────────────

def print_table(contacts: list[dict]):
    if not contacts:
        print("No contacts found.")
        return

    cols = ["email", "linkedin", "title", "name", "confidence", "source"]
    widths = {c: max(len(c), max((len(str(r.get(c) or "")) for r in contacts), default=0)) for c in cols}
    
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in contacts:
        row = " | ".join(str(r.get(c) or "").ljust(widths[c]) for c in cols)
        print(row)
    print(f"\n{len(contacts)} contact(s) found.")


def main():
    parser = argparse.ArgumentParser(
        description="Find professional contacts from company + domain"
    )
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--domain", required=True, help="Email domain (e.g. acme.com)")
    parser.add_argument("--name", default="", help="Full name (optional)")
    parser.add_argument("--output", choices=["table", "json"], default="table")
    args = parser.parse_args()

    contacts = find_contacts(
        company=args.company,
        domain=args.domain,
        name=args.name
    )

    if args.output == "json":
        print(json.dumps(contacts, indent=2))
    else:
        print_table(contacts)


if __name__ == "__main__":
    main()
