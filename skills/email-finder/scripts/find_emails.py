#!/usr/bin/env python3
"""
Email Finder — discover email addresses for a domain.

Combines website scraping, search dorking, pattern guessing, DNS hints,
and SMTP verification.

Usage:
    python3 find_emails.py domain.com
    python3 find_emails.py domain.com --name "First Last"

Output: JSON to stdout.

Dependencies: dnspython (pip3 install dnspython)
"""

import argparse
import json
import re
import smtplib
import socket
import ssl
import sys
import time
import random
import string
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin

try:
    import dns.resolver
except ImportError:
    print("Error: dnspython required. Install with: pip3 install dnspython", file=sys.stderr)
    sys.exit(1)

EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

JUNK_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js',
    '.woff', '.woff2', '.ttf', '.eot', '.ico', '.mp4', '.mp3',
}


def log(msg):
    print(f"  [{msg}]", file=sys.stderr)


def fetch_page(url, timeout=10):
    """Fetch a URL and return its text content, or None on failure."""
    try:
        req = Request(url, headers=HEADERS)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            data = resp.read(500_000)  # max 500KB
            charset = resp.headers.get_content_charset() or 'utf-8'
            return data.decode(charset, errors='replace')
    except Exception:
        return None


def extract_emails_from_text(text, domain):
    """Extract email addresses matching the target domain from text."""
    if not text:
        return set()
    found = set()
    for match in EMAIL_RE.findall(text):
        email = match.lower().strip('.')
        # Filter to target domain and skip junk
        if email.endswith(f'@{domain}'):
            local = email.split('@')[0]
            # Skip image/file-like matches
            if any(local.endswith(ext.replace('.', '')) for ext in JUNK_EXTENSIONS):
                continue
            if len(local) > 64 or len(local) < 1:
                continue
            found.add(email)
    return found


# ── Method 1: Website Scraping ──────────────────────────────────────

def scrape_website(domain, scrape_delay=0.5):
    """Scrape common pages on the domain for email addresses."""
    log("Scraping website pages")
    emails = set()
    paths = ['/', '/contact', '/contact-us', '/about', '/about-us', '/team', '/our-team', '/people', '/staff']
    base = f'https://{domain}'

    for path in paths:
        url = base + path
        log(f"  GET {url}")
        text = fetch_page(url)
        if text:
            found = extract_emails_from_text(text, domain)
            emails.update(found)
        time.sleep(scrape_delay)

    # Also try http if https found nothing
    if not emails:
        base = f'http://{domain}'
        for path in ['/', '/contact']:
            text = fetch_page(base + path)
            if text:
                emails.update(extract_emails_from_text(text, domain))
            time.sleep(scrape_delay)

    return emails


# ── Method 2: Search (offline — just extracts from page text) ───────

def search_for_emails(domain):
    """Search for emails by fetching search-engine-like pages.
    Since we can't use web_search from Python, we try common directories."""
    log("Searching public directories for emails")
    emails = set()
    urls = [
        f'https://www.google.com/search?q=%22%40{domain}%22',
        f'https://hunter.io/try/v2/domain-search?domain={domain}&type=personal',
    ]
    # These will likely get blocked, but worth trying
    for url in urls:
        text = fetch_page(url, timeout=8)
        if text:
            emails.update(extract_emails_from_text(text, domain))
        time.sleep(1)
    return emails


# ── Method 3: Common Pattern Guessing ───────────────────────────────

def generate_patterns(first, last, domain):
    """Generate common email patterns from a name."""
    first = first.lower().strip()
    last = last.lower().strip()
    fl = first[0] if first else ''
    ll = last[0] if last else ''

    patterns = [
        f'{first}@{domain}',
        f'{last}@{domain}',
        f'{first}.{last}@{domain}',
        f'{first}{last}@{domain}',
        f'{fl}{last}@{domain}',
        f'{first}{ll}@{domain}',
        f'{fl}.{last}@{domain}',
        f'{first}.{ll}@{domain}',
        f'{last}.{first}@{domain}',
        f'{last}{first}@{domain}',
        f'{last}{fl}@{domain}',
        f'{first}_{last}@{domain}',
        f'{first}-{last}@{domain}',
        f'{fl}{ll}@{domain}',
    ]
    # Deduplicate preserving order
    seen = set()
    unique = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


# ── Method 4: DNS Hints ─────────────────────────────────────────────

def get_mx_host(domain):
    """Resolve the highest-priority MX record."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
    except Exception:
        return None


def get_dns_hints(domain):
    """Check MX, SPF, DMARC records for email provider info."""
    log("Checking DNS records")
    hints = {}

    # MX
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_list = sorted(mx_records, key=lambda x: x.preference)
        hints['mx'] = [str(r.exchange).rstrip('.') for r in mx_list]
        mx_str = hints['mx'][0].lower()
        if 'google' in mx_str or 'gmail' in mx_str:
            hints['provider'] = 'Google Workspace'
        elif 'outlook' in mx_str or 'microsoft' in mx_str:
            hints['provider'] = 'Microsoft 365'
        elif 'zoho' in mx_str:
            hints['provider'] = 'Zoho'
        elif 'protonmail' in mx_str or 'proton' in mx_str:
            hints['provider'] = 'ProtonMail'
        elif 'mimecast' in mx_str:
            hints['provider'] = 'Mimecast'
        elif 'barracuda' in mx_str:
            hints['provider'] = 'Barracuda'
    except Exception:
        hints['mx'] = []

    # SPF
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for r in txt_records:
            val = str(r).strip('"')
            if val.startswith('v=spf1'):
                hints['spf'] = val
                break
    except Exception:
        pass

    # DMARC
    try:
        dmarc = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
        for r in dmarc:
            val = str(r).strip('"')
            if 'v=DMARC1' in val:
                hints['dmarc'] = val
                # Extract rua/ruf emails
                for part in val.split(';'):
                    part = part.strip()
                    if part.startswith('rua=') or part.startswith('ruf='):
                        mailto = part.split('mailto:', 1)
                        if len(mailto) > 1:
                            hints.setdefault('dmarc_emails', []).append(mailto[1].split(',')[0])
                break
    except Exception:
        pass

    return hints


# ── Method 5: SMTP Verification ─────────────────────────────────────

def verify_email_smtp(email, mx_host=None, helo_domain="verify.local", timeout=10):
    """Verify an email via SMTP RCPT TO. Returns deliverable status."""
    domain = email.split('@')[-1]
    if not mx_host:
        mx_host = get_mx_host(domain)
    if not mx_host:
        return 'unknown', 'No MX record'

    try:
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo(helo_domain)
        smtp.mail(f'verify@{helo_domain}')
        code, msg = smtp.rcpt(email)
        msg_str = msg.decode('utf-8', errors='replace')

        if code == 250:
            # Catch-all check
            fake = ''.join(random.choices(string.ascii_lowercase, k=14)) + f'@{domain}'
            fake_code, _ = smtp.rcpt(fake)
            smtp.quit()
            if fake_code == 250:
                return 'catch-all', msg_str
            return 'yes', msg_str
        elif code in (550, 551, 552, 553, 554):
            smtp.quit()
            return 'no', msg_str
        else:
            smtp.quit()
            return 'unknown', msg_str

    except smtplib.SMTPServerDisconnected:
        return 'unknown', 'Server disconnected'
    except socket.timeout:
        return 'unknown', 'Timeout'
    except ConnectionRefusedError:
        return 'unknown', 'Connection refused (port 25)'
    except Exception as e:
        return 'unknown', str(e)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Find email addresses for a domain')
    parser.add_argument('domain', help='Target domain (e.g. example.com)')
    parser.add_argument('--name', type=str, help='Person name for pattern guessing (e.g. "First Last")')
    parser.add_argument('--verify', action='store_true', default=True, help='Verify emails via SMTP (default: on)')
    parser.add_argument('--no-verify', action='store_true', help='Skip SMTP verification')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds (default: 10)')
    parser.add_argument('--smtp-delay', type=float, default=2.0,
                        help='Seconds between SMTP checks (default: 2.0)')
    parser.add_argument('--scrape-delay', type=float, default=0.5,
                        help='Seconds between page fetches (default: 0.5)')
    parser.add_argument('--max-smtp-checks', type=int, default=15,
                        help='Max SMTP checks per run before stopping (default: 15)')
    args = parser.parse_args()

    domain = args.domain.lower().strip()
    do_verify = not args.no_verify

    # Remove protocol if provided
    domain = domain.replace('https://', '').replace('http://', '').strip('/')

    all_emails = {}  # email -> {source, ...}

    # 1. Scrape website
    log("Step 1: Website scraping")
    scraped = scrape_website(domain, scrape_delay=args.scrape_delay)
    for e in scraped:
        all_emails[e] = {'source': 'scraped'}
    log(f"  Found {len(scraped)} emails from scraping")

    # 2. Search
    log("Step 2: Search/directories")
    searched = search_for_emails(domain)
    for e in searched:
        if e not in all_emails:
            all_emails[e] = {'source': 'searched'}
    log(f"  Found {len(searched)} emails from search")

    # 3. Pattern guessing
    guessed = []
    if args.name:
        log("Step 3: Pattern guessing")
        parts = args.name.strip().split()
        if len(parts) >= 2:
            first, last = parts[0], parts[-1]
        else:
            first, last = parts[0], ''
        guessed = generate_patterns(first, last, domain)
        for e in guessed:
            if e not in all_emails:
                all_emails[e] = {'source': 'guessed'}
        log(f"  Generated {len(guessed)} pattern candidates")
    else:
        log("Step 3: Skipped (no --name provided)")

    # 4. DNS hints
    log("Step 4: DNS hints")
    dns_hints = get_dns_hints(domain)
    provider = dns_hints.get('provider', 'Unknown')
    log(f"  Provider: {provider}")
    if dns_hints.get('mx'):
        log(f"  MX: {', '.join(dns_hints['mx'][:3])}")

    # Add DMARC report emails if they match domain
    for de in dns_hints.get('dmarc_emails', []):
        de = de.lower()
        if de.endswith(f'@{domain}') and de not in all_emails:
            all_emails[de] = {'source': 'dns'}

    # 5. SMTP verification (with rate limiting)
    results = []
    if do_verify and all_emails:
        log(f"Step 5: SMTP verification (max {args.max_smtp_checks} checks, {args.smtp_delay}s delay)")
        mx_host = get_mx_host(domain)
        smtp_count = 0
        for email, info in all_emails.items():
            if smtp_count >= args.max_smtp_checks:
                log(f"  Rate limit: stopping after {args.max_smtp_checks} SMTP checks")
                results.append({
                    'email': email,
                    'source': info['source'],
                    'deliverable': 'not_checked',
                    'smtp_detail': f'Skipped: rate limit ({args.max_smtp_checks} max)',
                })
                continue
            log(f"  Verifying {email} [{smtp_count+1}/{min(len(all_emails), args.max_smtp_checks)}]")
            status, detail = verify_email_smtp(email, mx_host=mx_host, timeout=args.timeout)
            results.append({
                'email': email,
                'source': info['source'],
                'deliverable': status,
                'smtp_detail': detail,
            })
            smtp_count += 1
            time.sleep(args.smtp_delay)
    elif all_emails:
        for email, info in all_emails.items():
            results.append({
                'email': email,
                'source': info['source'],
                'deliverable': 'not_checked',
            })

    # Build output
    output = {
        'domain': domain,
        'provider': provider,
        'mx': dns_hints.get('mx', []),
        'spf': dns_hints.get('spf'),
        'dmarc': dns_hints.get('dmarc'),
        'emails_found': len(results),
        'emails': results,
    }

    print(json.dumps(output, indent=2))
    log(f"Done. Found {len(results)} email(s) for {domain}")


if __name__ == '__main__':
    main()
