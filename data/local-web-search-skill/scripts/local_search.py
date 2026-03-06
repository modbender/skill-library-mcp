#!/usr/bin/env python3
import argparse
import html
import json
import random
import re
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError


DISCLAIMER = (
    "Uses public search engine HTML scraping behavior; selectors/endpoints may change over time."
)
SECURITY_NOTE = (
    "No environment/token exfiltration. No external writes. Only outbound HTTPS GET to search page."
)


def unwrap_ddg_url(href: str) -> str:
    href = html.unescape(href)
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        q = urllib.parse.parse_qs(parsed.query)
        target = q.get("uddg", [None])[0]
        if target:
            return urllib.parse.unquote(target)
    return href


def domain_of(url: str) -> str:
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


def trust_score(url: str) -> dict:
    d = domain_of(url)
    if not d:
        return {"score": 0.45, "tier": "unknown", "reason": "unparsed domain"}

    high = {"docs.polymarket.com", "github.com", "arxiv.org", "nature.com", "science.org"}
    medium = {
        "reuters.com", "apnews.com", "bloomberg.com", "wsj.com", "ft.com",
        "coindesk.com", "theblock.co"
    }
    low = {"medium.com", "substack.com", "dev.to"}

    if d in high or d.endswith(".gov") or d.endswith(".edu"):
        return {"score": 0.92, "tier": "high", "reason": f"authoritative domain: {d}"}
    if d in medium:
        return {"score": 0.78, "tier": "medium", "reason": f"reputable publication: {d}"}
    if d in low:
        return {"score": 0.58, "tier": "low", "reason": f"user-generated platform: {d}"}
    return {"score": 0.65, "tier": "medium", "reason": f"default domain trust: {d}"}


def fetch_with_backoff(url: str, retries: int = 4, base_delay: float = 1.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
            )
        },
    )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8", errors="ignore")
        except HTTPError as e:
            # Rate limit / transient server-side issues
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = base_delay * (2 ** attempt) + random.uniform(0.0, 0.35)
                time.sleep(wait)
                continue
            raise
        except URLError:
            if attempt < retries:
                wait = base_delay * (2 ** attempt) + random.uniform(0.0, 0.35)
                time.sleep(wait)
                continue
            raise


def search_ddg(query: str, max_results: int = 8):
    url = "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    html_text = fetch_with_backoff(url)

    blocks = re.findall(r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>', html_text)
    snippets = re.findall(r'<a class="result__snippet".*?>(.*?)</a>', html_text)

    out = []
    for i, (href, title_html) in enumerate(blocks[:max_results]):
        final_url = unwrap_ddg_url(href)
        title = html.unescape(re.sub("<.*?>", "", title_html))
        snippet = html.unescape(re.sub("<.*?>", "", snippets[i])) if i < len(snippets) else ""
        score = trust_score(final_url)
        out.append(
            {
                "title": title.strip(),
                "url": final_url,
                "snippet": snippet.strip(),
                "trust": score,
            }
        )
    return out


def main():
    p = argparse.ArgumentParser(description="Free local web search via DuckDuckGo HTML")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=8, dest="max_results")
    args = p.parse_args()

    try:
        results = search_ddg(args.query, args.max_results)
        print(
            json.dumps(
                {
                    "query": args.query,
                    "count": len(results),
                    "disclaimer": DISCLAIMER,
                    "security": SECURITY_NOTE,
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "query": args.query,
                    "count": 0,
                    "error": str(e),
                    "disclaimer": DISCLAIMER,
                    "security": SECURITY_NOTE,
                    "results": [],
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
