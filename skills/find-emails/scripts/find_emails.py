#!/usr/bin/env python3
"""Crawl websites locally via crawl4ai and extract contact emails from relevant pages."""
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# www. prefix stripped for canonical domain grouping (www.example.com === example.com)
DOMAIN_WWW_PREFIX = re.compile(r"^www\.", re.IGNORECASE)


def normalize_domain(netloc: str) -> str:
    """Canonicalize domain for grouping: lowercase, strip www. prefix."""
    if not netloc:
        return "(unknown)"
    domain = netloc.lower()
    return DOMAIN_WWW_PREFIX.sub("", domain) or domain


def ensure_scheme(url: str) -> str:
    """Add https:// if URL has no scheme. Returns URL unchanged if scheme present."""
    parsed = urlparse(url)
    if parsed.scheme:
        return url
    if url.startswith("//"):
        return "https:" + url
    return "https://" + url


DEFAULT_URL_PATTERNS = [
    "*contact*", "*support*", "*about*", "*team*",
    "*email*", "*reach*", "*staff*", "*inquiry*", "*enquir*",
    "*get-in-touch*", "*contact-us*", "*about-us*",
]


def load_url_patterns(script_dir: Path) -> list[str]:
    """Load URL filter patterns from url_patterns.json, or return defaults."""
    config_path = script_dir / "url_patterns.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text())
            return data.get("url_patterns", DEFAULT_URL_PATTERNS)
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_URL_PATTERNS


def extract_emails_from_text(text: str, path: str) -> dict[str, list[str]]:
    """Extract emails from text and return {email_lower: [paths]}."""
    email_sources: dict[str, set[str]] = {}
    for email in EMAIL_REGEX.findall(text):
        key = email.lower()
        email_sources.setdefault(key, set()).add(path)
    return {e: sorted(paths) for e, paths in email_sources.items()}


def extract_from_file(file_path: Path) -> dict[str, dict[str, list[str]]]:
    """Extract emails from a local markdown/text file. Returns {source: {email: [paths]}}."""
    text = file_path.read_text()
    path = str(file_path.name)
    email_sources = extract_emails_from_text(text, path)
    return {path: email_sources}


async def crawl_and_extract(
    urls: list[str],
    url_patterns: list[str],
    max_depth: int,
    max_pages: int,
    verbose: bool,
) -> dict[str, dict[str, list[str]]]:
    """Crawl URLs locally via crawl4ai and extract emails. Returns {domain: {email: [paths]}}."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
    from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter
    from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

    # Prioritize pages likely to contain contact info (matches URL filter intent)
    keyword_scorer = KeywordRelevanceScorer(
        keywords=["contact", "support", "about", "team", "email", "reach", "staff", "inquiry", "enquiry"],
        weight=0.7,
    )

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=15_000,
        deep_crawl_strategy=BestFirstCrawlingStrategy(
            max_depth=max_depth,
            include_external=False,
            max_pages=max_pages,
            filter_chain=FilterChain([
                URLPatternFilter(patterns=url_patterns),
            ]),
            url_scorer=keyword_scorer,
        ),
    )

    browser_config = BrowserConfig(headless=True, verbose=verbose)
    all_pages: list = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            pages = await crawler.arun(url=url, config=crawler_config)
            items = pages if isinstance(pages, list) else [pages]
            all_pages.extend(items)

    results = all_pages

    if not results:
        return {}

    pages = results if isinstance(results, list) else [results]
    by_domain: dict[str, dict[str, set[str]]] = {}

    for result in pages:
        if result.success and result.markdown:
            parsed = urlparse(result.url)
            domain = normalize_domain(parsed.netloc or "")
            path = parsed.path or "/"
            text = (
                result.markdown.raw_markdown
                if hasattr(result.markdown, "raw_markdown")
                else str(result.markdown)
            )
            by_domain.setdefault(domain, {})
            for email in EMAIL_REGEX.findall(text):
                key = email.lower()
                by_domain[domain].setdefault(key, set()).add(path)

    return {
        domain: {e: sorted(paths) for e, paths in emails.items()}
        for domain, emails in by_domain.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl websites locally and extract contact emails via crawl4ai."
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="URL(s) to crawl",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write results to file",
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="JSON output",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max crawl depth (default: 2)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=25,
        help="Max pages to crawl (default: 25)",
    )
    parser.add_argument(
        "--from-file",
        metavar="FILE",
        help="Extract emails from local markdown file (skip crawl)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose crawl output",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent

    if args.from_file:
        file_path = Path(args.from_file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        email_sources = extract_from_file(file_path)
    elif args.urls:
        url_patterns = load_url_patterns(script_dir)
        urls = [ensure_scheme(u) for u in args.urls]
        try:
            email_sources = asyncio.run(crawl_and_extract(
                urls=urls,
                url_patterns=url_patterns,
                max_depth=args.max_depth,
                max_pages=args.max_pages,
                verbose=args.verbose,
            ))
        except Exception as e:
            print(f"Crawl failed: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.error("Either provide URLs or use --from-file")

    # Build domain-grouped output (email_sources: {domain: {email: [paths]}})
    total_emails = sum(len(emails) for emails in email_sources.values())

    output_lines: list[str] = []
    if args.json:
        # LLM-friendly JSON: domains with nested email→paths
        output_lines.append(json.dumps({
            "summary": {
                "domains_crawled": len(email_sources),
                "total_unique_emails": total_emails,
            },
            "emails_by_domain": {
                domain: {
                    "emails": {
                        email: paths
                        for email, paths in sorted(emails.items())
                    },
                    "count": len(emails),
                }
                for domain, emails in sorted(email_sources.items())
            },
        }, indent=2))
    else:
        if not args.quiet:
            output_lines.append(f"Found {total_emails} unique email(s) across {len(email_sources)} domain(s)")
            output_lines.append("")
        for domain in sorted(email_sources):
            emails = email_sources[domain]
            output_lines.append(f"## {domain}")
            output_lines.append("")
            for email in sorted(emails):
                paths = emails[email]
                paths_str = ", ".join(sorted(paths)) if paths else "(page)"
                output_lines.append(f"  • {email}")
                if paths and (len(paths) > 1 or paths[0] != "/"):
                    output_lines.append(f"    Found on: {paths_str}")
            output_lines.append("")

    out_text = "\n".join(output_lines).rstrip()
    if args.output:
        Path(args.output).write_text(out_text)
        if not args.quiet:
            print(f"→ {args.output}", file=sys.stderr)
    else:
        print(out_text)


if __name__ == "__main__":
    main()
