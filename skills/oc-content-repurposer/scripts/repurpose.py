#!/usr/bin/env python3
"""
content-repurposer: Turn any article/blog post into multi-platform social content.
Generates Twitter threads, LinkedIn posts, Instagram captions, email snippets, and summaries.
"""

import argparse
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) content-repurposer/1.0"

PLATFORM_LIMITS = {
    "twitter": 280,
    "linkedin": 3000,
    "instagram": 2200,
    "email": 5000,
    "summary": 500,
}

ALL_FORMATS = list(PLATFORM_LIMITS.keys())


# ─── Content Extraction ─────────────────────────────────────

def fetch_article(url: str) -> dict:
    """Extract article content from a URL."""
    if not HAS_BS4:
        print("beautifulsoup4 required for URL mode. Install: pip install beautifulsoup4", file=sys.stderr)
        sys.exit(1)

    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:
            encoding = resp.headers.get_content_charset() or "utf-8"
            html = resp.read().decode(encoding, errors="replace")
    except (HTTPError, URLError) as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = ""
    if soup.title:
        title = soup.title.string.strip() if soup.title.string else ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"]

    # Extract description
    description = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        description = og_desc["content"]
    elif soup.find("meta", attrs={"name": "description"}):
        description = soup.find("meta", attrs={"name": "description"}).get("content", "")

    # Extract article body
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()

    # Try to find article body
    article = soup.find("article") or soup.find("main") or soup.find(class_=re.compile(r"post|article|content|entry"))
    if article:
        body = article.get_text(separator="\n", strip=True)
    else:
        body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

    # Clean up
    body = re.sub(r"\n{3,}", "\n\n", body)

    return {"title": title, "description": description, "body": body, "url": url}


def read_file(path: str) -> dict:
    """Read content from a text/markdown file."""
    p = Path(path)
    if not p.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    content = p.read_text(encoding="utf-8")

    # Try to extract title from first heading
    title = ""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    return {"title": title or p.stem, "description": "", "body": content, "url": ""}


def read_stdin() -> dict:
    """Read content from stdin."""
    content = sys.stdin.read()
    lines = content.split("\n")
    title = lines[0].strip() if lines else "Untitled"
    return {"title": title, "description": "", "body": content, "url": ""}


# ─── Content Generation ─────────────────────────────────────

def extract_key_points(body: str, max_points: int = 8) -> list[str]:
    """Extract key points from article body."""
    sentences = re.split(r"[.!?]+", body)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    # Score sentences by position and length
    scored = []
    for i, s in enumerate(sentences):
        # Prefer early sentences and moderate-length ones
        position_score = 1.0 - (i / max(len(sentences), 1)) * 0.5
        length_score = min(len(s) / 200, 1.0)
        scored.append((s, position_score * 0.6 + length_score * 0.4))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored[:max_points]]


def extract_hashtags(body: str, title: str, max_tags: int = 10) -> list[str]:
    """Extract relevant hashtags from content."""
    text = (title + " " + body).lower()
    # Find capitalized words and common tech/business terms
    words = re.findall(r"\b[a-z]{4,15}\b", text)
    counter = {}
    for w in words:
        if w not in {"this", "that", "with", "from", "have", "been", "will", "would",
                      "could", "should", "about", "their", "there", "which", "these",
                      "those", "other", "some", "more", "than", "also", "just", "into",
                      "over", "such", "after", "most", "only", "very", "when", "what",
                      "your", "they", "them", "then", "each", "make", "like", "many",
                      "first", "being", "does", "were"}:
            counter[w] = counter.get(w, 0) + 1

    sorted_words = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    return [f"#{w[0]}" for w in sorted_words[:max_tags]]


def generate_twitter(article: dict) -> str:
    """Generate a Twitter/X thread."""
    key_points = extract_key_points(article["body"])
    hashtags = extract_hashtags(article["body"], article["title"], 5)
    hashtag_str = " ".join(hashtags[:3])

    tweets = []

    # Hook tweet
    hook = f"🧵 {article['title']}\n\nA thread on what matters most 👇"
    if len(hook) > 280:
        hook = hook[:277] + "..."
    tweets.append(hook)

    # Content tweets
    for i, point in enumerate(key_points[:6], 1):
        tweet = f"{i}/ {point}"
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        tweets.append(tweet)

    # Closing tweet
    close = f"That's a wrap! {hashtag_str}"
    if article["url"]:
        close += f"\n\nRead the full article: {article['url']}"
    if len(close) > 280:
        close = close[:277] + "..."
    tweets.append(close)

    return "\n\n---\n\n".join(tweets)


def generate_linkedin(article: dict) -> str:
    """Generate a LinkedIn post."""
    key_points = extract_key_points(article["body"], 4)
    hashtags = extract_hashtags(article["body"], article["title"], 5)

    parts = []
    parts.append(f"{article['title']}")
    parts.append("")

    if article["description"]:
        parts.append(article["description"])
        parts.append("")

    parts.append("Key takeaways:")
    parts.append("")
    for point in key_points[:4]:
        bullet = f"→ {point}"
        if len(bullet) > 200:
            bullet = bullet[:197] + "..."
        parts.append(bullet)

    parts.append("")
    if article["url"]:
        parts.append(f"Read more: {article['url']}")
        parts.append("")

    parts.append(" ".join(hashtags[:5]))

    text = "\n".join(parts)
    if len(text) > PLATFORM_LIMITS["linkedin"]:
        text = text[:PLATFORM_LIMITS["linkedin"] - 3] + "..."
    return text


def generate_instagram(article: dict) -> str:
    """Generate an Instagram caption."""
    key_points = extract_key_points(article["body"], 3)
    hashtags = extract_hashtags(article["body"], article["title"], 25)

    parts = []
    parts.append(f"✨ {article['title']}")
    parts.append("")

    for point in key_points[:3]:
        parts.append(f"💡 {point}")
        parts.append("")

    if article["url"]:
        parts.append(f"🔗 Link in bio")
        parts.append("")

    parts.append(".")
    parts.append(".")
    parts.append(".")
    parts.append(" ".join(hashtags))

    text = "\n".join(parts)
    if len(text) > PLATFORM_LIMITS["instagram"]:
        text = text[:PLATFORM_LIMITS["instagram"] - 3] + "..."
    return text


def generate_email(article: dict) -> str:
    """Generate an email newsletter snippet."""
    key_points = extract_key_points(article["body"], 3)

    parts = []
    parts.append(f"Subject: {article['title']}")
    parts.append(f"Preview: {article['description'][:100] if article['description'] else key_points[0][:100] if key_points else ''}")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"Hi there,")
    parts.append("")
    parts.append(f"Here's what caught our attention this week:")
    parts.append("")
    parts.append(f"**{article['title']}**")
    parts.append("")

    for point in key_points[:3]:
        parts.append(f"• {point}")
    parts.append("")

    if article["url"]:
        parts.append(f"[Read the full article]({article['url']})")
        parts.append("")

    parts.append("Until next time,")
    parts.append("[Your Name]")

    return "\n".join(parts)


def generate_summary(article: dict) -> str:
    """Generate a 3-sentence TL;DR."""
    key_points = extract_key_points(article["body"], 3)

    if not key_points:
        return f"TL;DR: {article['title']}. {article['description']}"

    sentences = []
    for point in key_points[:3]:
        s = point.strip()
        if not s.endswith("."):
            s += "."
        sentences.append(s)

    return f"TL;DR: {' '.join(sentences)}"


GENERATORS = {
    "twitter": generate_twitter,
    "linkedin": generate_linkedin,
    "instagram": generate_instagram,
    "email": generate_email,
    "summary": generate_summary,
}


# ─── Output ──────────────────────────────────────────────────

def output_results(results: dict, fmt: str = "text", output_dir: str = None):
    """Output generated content."""
    if fmt == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        for platform, content in results.items():
            filepath = out / f"{platform}.txt"
            filepath.write_text(content, encoding="utf-8")
        print(f"Saved {len(results)} files to {output_dir}/", file=sys.stderr)
    else:
        for platform, content in results.items():
            print(f"{'='*60}")
            print(f"  {platform.upper()}")
            print(f"{'='*60}")
            print(content)
            print()


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Content Repurposer — Multi-platform content from one source.")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd_name, cmd_help in [("url", "Repurpose from URL"), ("file", "Repurpose from file"), ("stdin", "Repurpose from stdin")]:
        p = sub.add_parser(cmd_name, help=cmd_help)
        if cmd_name in ("url", "file"):
            p.add_argument("source", help="URL or file path")
        p.add_argument("--formats", default=",".join(ALL_FORMATS), help="Comma-separated platforms")
        p.add_argument("-f", "--format", default="text", choices=["text", "json"])
        p.add_argument("-o", "--output", help="Output directory (saves separate files)")

    args = parser.parse_args()

    # Extract content
    if args.command == "url":
        article = fetch_article(args.source)
    elif args.command == "file":
        article = read_file(args.source)
    else:
        article = read_stdin()

    if not article["body"].strip():
        print("No content found to repurpose.", file=sys.stderr)
        sys.exit(1)

    # Generate for selected platforms
    formats = [f.strip() for f in args.formats.split(",")]
    results = {}
    for fmt in formats:
        if fmt in GENERATORS:
            results[fmt] = GENERATORS[fmt](article)
        else:
            print(f"Unknown format: {fmt}", file=sys.stderr)

    output_results(results, args.format, args.output)


if __name__ == "__main__":
    main()
