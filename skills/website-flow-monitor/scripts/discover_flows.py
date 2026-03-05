#!/usr/bin/env python3
import argparse
import json
import re
from urllib.parse import urljoin, urlparse

import requests


def extract_links(html: str):
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)
    out = []
    for h in hrefs:
        h = h.replace('&amp;', '&').strip()
        if not h or h.startswith('#') or h.startswith('mailto:') or h.startswith('tel:'):
            continue
        out.append(h)
    return out


def classify(path: str):
    p = path.lower()
    if p.startswith('/blog') or p.startswith('/changelog'):
        return 'content'
    if any(k in p for k in ['pricing', 'checkout', 'buy', 'billing', 'payment']):
        return 'revenue'
    if any(k in p for k in ['signup', 'sign-up', 'register', 'login', 'dashboard', 'download', 'get-started']):
        return 'onboarding'
    if any(k in p for k in ['api', 'docs', 'reference']):
        return 'product'
    if any(k in p for k in ['privacy', 'terms', 'contact', 'support']):
        return 'trust'
    if any(k in p for k in ['sitemap', 'robots']):
        return 'seo'
    return 'content'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', required=True)
    ap.add_argument('--timeout', type=int, default=20)
    args = ap.parse_args()

    base = args.url.strip()
    if not base.startswith('http://') and not base.startswith('https://'):
        base = 'https://' + base

    pages = ['/', '/pricing', '/api', '/docs', '/blog', '/changelog', '/downloads']
    seen = set()
    discovered = []

    for p in pages:
        try:
            r = requests.get(urljoin(base, p), timeout=args.timeout, allow_redirects=True, headers={'User-Agent': 'OpenClawFlowMonitor/1.0'})
            html = r.text or ''
            links = extract_links(html)
            for l in links:
                full = urljoin(r.url, l)
                if full in seen:
                    continue
                seen.add(full)
                pu = urlparse(full)
                discovered.append({
                    'url': full,
                    'host': pu.netloc,
                    'path': pu.path or '/',
                    'category': classify(pu.path or '/'),
                    'source': r.url,
                })
        except Exception:
            continue

    # Add SEO essentials
    for p in ['/robots.txt', '/sitemap.xml']:
        full = urljoin(base, p)
        if full not in seen:
            discovered.append({
                'url': full,
                'host': urlparse(full).netloc,
                'path': p,
                'category': 'seo',
                'source': 'synthetic',
            })

    # Keep high-signal categories first
    order = {'revenue': 0, 'onboarding': 1, 'product': 2, 'trust': 3, 'seo': 4, 'content': 5}
    discovered.sort(key=lambda x: (order.get(x['category'], 9), x['url']))

    print(json.dumps({'base': base, 'candidates': discovered}, indent=2))


if __name__ == '__main__':
    main()
