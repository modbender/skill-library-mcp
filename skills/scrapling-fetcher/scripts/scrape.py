#!/usr/bin/env python3
"""
Scrapling fetch script - fetches a URL with stealth capabilities.

Usage:
  python3 scrape.py <url> [options]

Options:
  --mode     http | stealth | dynamic (default: http)
  --selector CSS selector to extract specific elements
  --attr     Attribute to extract from elements (default: text)
  --json     Output as JSON array
  --text     Extract all visible text (default if no selector)
  -q         Quiet mode (suppress INFO logs)
"""

import argparse
import sys
import logging


def main():
    parser = argparse.ArgumentParser(description='Scrapling fetch')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--mode', choices=['http', 'stealth', 'dynamic'], default='http',
                        help='Fetcher mode: http (fast), stealth (anti-bot), dynamic (JS rendering)')
    parser.add_argument('--selector', '-s', help='CSS selector to extract elements')
    parser.add_argument('--attr', default='text', help='Attribute to extract (text, href, src, etc.)')
    parser.add_argument('--json', action='store_true', help='Output as JSON array')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress INFO logs')
    args = parser.parse_args()

    if args.quiet:
        logging.disable(logging.INFO)

    try:
        page = _fetch(args.url, args.mode)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.selector:
        # Default: return all visible text
        text = page.get_all_text(' ', ignore_tags=('script', 'style', 'noscript'))
        print(text)
        return

    elements = page.css(args.selector)
    if not elements:
        print(f"No elements matched: {args.selector}", file=sys.stderr)
        sys.exit(1)

    results = []
    for el in elements:
        if args.attr == 'text':
            val = el.text or el.get_all_text()
        elif args.attr == 'html':
            val = el.html_content
        else:
            val = el.attrib.get(args.attr, '')
        results.append(val.strip())

    if args.json:
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if r:
                print(r)


def _fetch(url, mode):
    if mode == 'http':
        from scrapling.fetchers import Fetcher
        return Fetcher.get(url)
    elif mode == 'stealth':
        from scrapling.fetchers import StealthyFetcher
        return StealthyFetcher.fetch(url, headless=True, network_idle=True)
    elif mode == 'dynamic':
        from scrapling.fetchers import DynamicFetcher
        return DynamicFetcher.fetch(url, headless=True, network_idle=True)


if __name__ == '__main__':
    main()
