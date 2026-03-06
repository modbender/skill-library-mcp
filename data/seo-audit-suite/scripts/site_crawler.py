#!/usr/bin/env python3
"""Crawl a site and run SEO audits on each page."""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from collections import deque

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip3 install beautifulsoup4 requests lxml")
    sys.exit(1)

from seo_auditor import run_audit


def crawl_and_audit(start_url, max_pages=50, output_dir=None, delay=1.0):
    """Crawl a site starting from start_url and audit each page."""
    parsed_start = urlparse(start_url)
    base_domain = parsed_start.netloc

    visited = set()
    queue = deque([start_url])
    results = []

    print(f"🕷️  Crawling {start_url} (max {max_pages} pages)")
    print()

    while queue and len(visited) < max_pages:
        url = queue.popleft()

        # Normalize
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        if normalized in visited:
            continue

        visited.add(normalized)

        try:
            result = run_audit(url, output_dir)
            results.append(result)
            print()

            # Extract internal links for further crawling
            resp = requests.get(url, timeout=10, headers={"User-Agent": "ReighlanSEOBot/1.0"})
            soup = BeautifulSoup(resp.text, "lxml")
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                link_parsed = urlparse(full_url)
                link_normalized = f"{link_parsed.scheme}://{link_parsed.netloc}{link_parsed.path}".rstrip("/")
                if link_parsed.netloc == base_domain and link_normalized not in visited:
                    queue.append(full_url)

            time.sleep(delay)
        except Exception as e:
            print(f"  ❌ Error auditing {url}: {e}")
            continue

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Site Audit Summary: {start_url}")
    print(f"   Pages audited: {len(results)}")

    if results:
        scores = [r["scores"]["overall"] for r in results]
        avg = sum(scores) / len(scores)
        print(f"   Average score: {avg:.0f}/100")
        print(f"   Best: {max(scores)}/100")
        print(f"   Worst: {min(scores)}/100")

        total_critical = sum(len([i for i in r["all_issues"] if i["severity"] == "critical"]) for r in results)
        total_warnings = sum(len([i for i in r["all_issues"] if i["severity"] == "warning"]) for r in results)
        print(f"   Total critical issues: {total_critical}")
        print(f"   Total warnings: {total_warnings}")

    # Save summary
    if output_dir:
        domain = base_domain.replace(".", "_")
        summary_file = os.path.join(output_dir, domain, f"site-summary-{datetime.now().strftime('%Y-%m-%d')}.json")
        os.makedirs(os.path.dirname(summary_file), exist_ok=True)
        with open(summary_file, "w") as f:
            json.dump({
                "url": start_url,
                "pages_audited": len(results),
                "average_score": round(avg, 1) if results else 0,
                "pages": [{"url": r["url"], "score": r["scores"]["overall"]} for r in results],
            }, f, indent=2)
        print(f"\n📄 Summary saved: {summary_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Site Crawler + SEO Auditor")
    parser.add_argument("--url", required=True, help="Starting URL")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")
    parser.add_argument("--output-dir", help="Directory to save results")
    args = parser.parse_args()

    crawl_and_audit(args.url, args.max_pages, args.output_dir)
