#!/usr/bin/env python3
"""
Quick SEO/on-page audit for a single URL.

Designed for automated SEO prospect lead-gen:
- fast (~1 request + optional robots/sitemap checks)
- produces a short Markdown report you can paste into outreach

This is not a replacement for Search Console / CWV tooling.
"""

from __future__ import annotations

import argparse
import re
import ssl
import time
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_UA = "Mozilla/5.0 (compatible; OpenClaw-SEOQuickAudit/1.0; +https://github.com/openclaw)"


@dataclass(frozen=True)
class FetchResult:
    url: str
    final_url: str
    status: int
    headers: dict[str, str]
    body: str
    elapsed_ms: int


def fetch(url: str, *, timeout_s: int, user_agent: str) -> FetchResult:
    def fetch_via_urllib() -> FetchResult:
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})
        ctx = ssl.create_default_context()
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
                raw = resp.read()
                elapsed_ms = int((time.perf_counter() - start) * 1000)
                charset = resp.headers.get_content_charset() or "utf-8"
                body = raw.decode(charset, errors="ignore")
                headers = {k.lower(): v for k, v in dict(resp.headers).items()}
                final_url = resp.geturl()
                return FetchResult(
                    url=url,
                    final_url=final_url,
                    status=int(resp.status),
                    headers=headers,
                    body=body,
                    elapsed_ms=elapsed_ms,
                )
        except urllib.error.HTTPError as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            headers = {k.lower(): v for k, v in dict(e.headers).items()} if e.headers else {}
            body = ""
            try:
                raw = e.read()
                body = raw.decode("utf-8", errors="ignore")
            except Exception:
                pass
            return FetchResult(url=url, final_url=url, status=int(e.code), headers=headers, body=body, elapsed_ms=elapsed_ms)

    def fetch_via_curl() -> FetchResult:
        start = time.perf_counter()
        # Use -w to append status code and effective URL on separate lines.
        # Do NOT use -D - (dumps headers into stdout, blank lines in HTML
        # body cause the header/body split to fail catastrophically).
        sentinel = "\n__CURL_META__"
        cmd = [
            "curl",
            "-sS",
            "-L",
            "--max-time",
            str(timeout_s),
            "-A",
            user_agent,
            "-w",
            sentinel + "%{http_code}\n%{url_effective}\n",
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "").strip() or f"curl failed: {proc.returncode}")

        raw = proc.stdout
        # Split body from the appended metadata
        idx = raw.rfind("__CURL_META__")
        if idx >= 0:
            body = raw[:idx].rstrip("\n")
            meta_lines = raw[idx + len("__CURL_META__"):].strip().splitlines()
            status = int(meta_lines[0]) if meta_lines else 0
            final_url = meta_lines[1].strip() if len(meta_lines) > 1 else url
        else:
            body = raw
            status = 0
            final_url = url

        return FetchResult(
            url=url,
            final_url=final_url,
            status=status,
            headers={},
            body=body,
            elapsed_ms=elapsed_ms,
        )

    try:
        return fetch_via_urllib()
    except Exception:
        # Fallback: curl tends to behave differently in some environments (DNS/TLS).
        return fetch_via_curl()


def first_match(pattern: str, html: str, group: int = 1) -> str | None:
    m = re.search(pattern, html, re.I | re.S)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(group)).strip()


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


def _meta_content(html: str, attr: str, value: str, attr_type: str = "name") -> str | None:
    """Extract content from a meta tag, handling either attribute order.

    Uses backreferences to match opening/closing quotes correctly so that
    apostrophes inside double-quoted values don't truncate the match.
    """
    esc_val = re.escape(value)
    # Try attr before content: <meta name="X" content="Y">
    result = first_match(
        rf'<meta\s+{attr_type}=([\'"]){esc_val}\1[^>]*content=([\'"])(.*?)\2[^>]*/?>',
        html, group=3,
    )
    if result:
        return result
    # Try content before attr: <meta content="Y" name="X">
    m = re.search(
        rf'<meta\s+content=([\'"])(.*?)\1[^>]*{attr_type}=([\'"]){esc_val}\3[^>]*/?>',
        html, re.I | re.S,
    )
    if m:
        return re.sub(r"\s+", " ", m.group(2)).strip()
    return None


def parse_onpage(html: str) -> dict[str, Any]:
    title = first_match(r"<title[^>]*>(.*?)</title>", html)
    desc = _meta_content(html, "name", "description")
    canonical = first_match(r'<link\s+rel=([\'"])canonical\1[^>]*href=([\'"])(.*?)\2', html, group=3)
    if not canonical:
        canonical = first_match(r'<link[^>]*href=([\'"])(.*?)\1[^>]*rel=([\'"])canonical\3', html, group=2)
    robots_meta = _meta_content(html, "name", "robots")
    og_title = _meta_content(html, "property", "og:title", attr_type="property")
    og_desc = _meta_content(html, "property", "og:description", attr_type="property")
    og_image = _meta_content(html, "property", "og:image", attr_type="property")
    tw_card = _meta_content(html, "name", "twitter:card")
    viewport = bool(re.search(r"<meta\s[^>]*name=['\"]viewport['\"]", html, re.I))
    h1s = [strip_tags(x) for x in re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)]
    h2s = [strip_tags(x) for x in re.findall(r"<h2\b[^>]*>(.*?)</h2>", html, re.I | re.S)]
    ldjson_count = len(re.findall(r"<script\b[^>]*type=['\"]application/ld\+json['\"][^>]*>", html, re.I))
    return {
        "title": title,
        "description": desc,
        "canonical": canonical,
        "robots_meta": robots_meta,
        "og_title": og_title,
        "og_description": og_desc,
        "og_image": og_image,
        "twitter_card": tw_card,
        "viewport": viewport,
        "h1": [x for x in h1s if x],
        "h2_count": len([x for x in h2s if x]),
        "ldjson_count": ldjson_count,
    }


def origin(url: str) -> str:
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def audit(url: str, *, timeout_s: int, user_agent: str, check_robots: bool, check_sitemap: bool) -> dict[str, Any]:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    main = fetch(url, timeout_s=timeout_s, user_agent=user_agent)
    onpage = parse_onpage(main.body or "")

    out: dict[str, Any] = {
        "input_url": url,
        "final_url": main.final_url,
        "status": main.status,
        "elapsed_ms": main.elapsed_ms,
        "headers": main.headers,
        "onpage": onpage,
        "robots_txt": None,
        "sitemap_xml": None,
    }

    base = origin(main.final_url)

    if check_robots:
        try:
            robots = fetch(base + "/robots.txt", timeout_s=timeout_s, user_agent=user_agent)
            out["robots_txt"] = {
                "status": robots.status,
                "has_sitemap_line": bool(re.search(r"^sitemap:\s+\S+", robots.body or "", re.I | re.M)),
            }
        except Exception:
            out["robots_txt"] = {"status": None, "has_sitemap_line": False}

    if check_sitemap:
        try:
            sitemap = fetch(base + "/sitemap.xml", timeout_s=timeout_s, user_agent=user_agent)
            out["sitemap_xml"] = {
                "status": sitemap.status,
                "looks_like_xml": (sitemap.body or "").lstrip().startswith("<?xml"),
            }
        except Exception:
            out["sitemap_xml"] = {"status": None, "looks_like_xml": False}

    return out


def summarize_findings(result: dict[str, Any]) -> list[str]:
    items: list[str] = []
    on = result.get("onpage") or {}

    if result.get("status") != 200:
        items.append(f"HTTP status is {result.get('status')} (should be 200).")

    if not on.get("title"):
        items.append("Missing `<title>` tag.")
    if not on.get("description"):
        items.append("Missing meta description.")
    if not on.get("canonical"):
        items.append("Missing canonical URL.")
    if not on.get("h1"):
        items.append("Missing H1.")
    if len(on.get("h1") or []) > 1:
        items.append("Multiple H1s (usually want exactly one).")
    if not on.get("viewport"):
        items.append("Missing viewport meta (mobile friendliness).")
    if (on.get("ldjson_count") or 0) == 0:
        items.append("No JSON-LD schema detected (LocalBusiness/Service/FAQ are common wins).")
    if not on.get("og_title"):
        items.append("Missing OpenGraph tags (social previews).")

    robots = result.get("robots_txt")
    if isinstance(robots, dict) and robots.get("status") not in (None, 200):
        items.append("robots.txt missing or not accessible.")
    sitemap = result.get("sitemap_xml")
    if isinstance(sitemap, dict) and sitemap.get("status") not in (None, 200):
        items.append("sitemap.xml missing or not accessible.")

    return items


def to_markdown(result: dict[str, Any]) -> str:
    on = result.get("onpage") or {}
    findings = summarize_findings(result)
    lines: list[str] = []
    lines.append(f"# Quick SEO Audit\n")
    lines.append(f"- URL: {result.get('final_url')}")
    lines.append(f"- Status: {result.get('status')} ({result.get('elapsed_ms')}ms)")
    lines.append(f"- Audited at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    lines.append("## On-page\n")
    lines.append(f"- Title: {on.get('title') or '(missing)'}")
    lines.append(f"- Meta description: {on.get('description') or '(missing)'}")
    lines.append(f"- Canonical: {on.get('canonical') or '(missing)'}")
    h1s = on.get("h1") or []
    lines.append(f"- H1: {h1s[0] if h1s else '(missing)'}")
    lines.append(f"- H2 count: {on.get('h2_count')}")
    lines.append(f"- JSON-LD schema blocks: {on.get('ldjson_count')}")
    lines.append(f"- OpenGraph title: {on.get('og_title') or '(missing)'}")
    lines.append(f"- Twitter card: {on.get('twitter_card') or '(missing)'}\n")

    lines.append("## Robots / Sitemap\n")
    robots = result.get("robots_txt") or {}
    sitemap = result.get("sitemap_xml") or {}
    lines.append(f"- robots.txt: {robots.get('status')}")
    lines.append(f"- robots.txt has sitemap line: {robots.get('has_sitemap_line')}")
    lines.append(f"- sitemap.xml: {sitemap.get('status')}")
    lines.append(f"- sitemap.xml looks like XML: {sitemap.get('looks_like_xml')}\n")

    lines.append("## Top fixes (pasteable)\n")
    if findings:
        for f in findings[:6]:
            lines.append(f"- {f}")
    else:
        lines.append("- No obvious on-page/robots/sitemap issues detected by this quick check.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--out", help="Write Markdown report to this path")
    p.add_argument("--html-file", help="Parse HTML from a local file instead of fetching the URL")
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--user-agent", default=DEFAULT_UA)
    p.add_argument("--no-robots", action="store_true")
    p.add_argument("--no-sitemap", action="store_true")
    args = p.parse_args()

    if args.html_file:
        html = Path(args.html_file).read_text(errors="ignore")
        result = {
            "input_url": args.url,
            "final_url": args.url,
            "status": 200,
            "elapsed_ms": 0,
            "headers": {},
            "onpage": parse_onpage(html),
            "robots_txt": None,
            "sitemap_xml": None,
        }
    else:
        result = audit(
            args.url,
            timeout_s=args.timeout,
            user_agent=args.user_agent,
            check_robots=not args.no_robots,
            check_sitemap=not args.no_sitemap,
        )
    md = to_markdown(result)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md)
        print(f"Wrote {out_path}")
    else:
        print(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
