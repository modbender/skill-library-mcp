#!/usr/bin/env python3
"""
Google Search v2.0 - Web Search via Gemini Grounding + Custom Search API
Author: Leo 🦁
Updated: 2026-02-07

Modes:
- search (grounded): Gemini 2.0 Flash + Google Search tool → synthesized answer with citations
- raw: Custom Search JSON API → raw results (title, link, snippet)
- image: Custom Search image search

Environment Variables:
- GOOGLE_API_KEY: Required. Google API key with Gemini + Custom Search enabled.
- GOOGLE_CSE_CX: Custom Search Engine ID (default: 36ec250a5e68544b6)
- GOOGLE_SEARCH_LANG: Default language code (default: he)
- GOOGLE_SEARCH_COUNTRY: Default country code (default: IL)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

# ─── Configuration ───────────────────────────────────────────────────────────

API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
CSE_CX: str = os.environ.get("GOOGLE_CSE_CX", "")
DEFAULT_LANG: Optional[str] = os.environ.get("GOOGLE_SEARCH_LANG", "he")
DEFAULT_COUNTRY: Optional[str] = os.environ.get("GOOGLE_SEARCH_COUNTRY", "IL")
GEMINI_MODEL: str = "gemini-3-flash-preview"  # Alternatives: "gemini-2.5-flash", "gemini-2.0-flash"
REQUEST_TIMEOUT: int = 30
RETRY_WAIT: int = 5  # seconds to wait on 429 before retry


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _resolve_lang(lang: Optional[str]) -> Optional[str]:
    """Resolve language: explicit arg > env var > None."""
    if lang is not None:
        return lang
    return DEFAULT_LANG


def _resolve_country(country: Optional[str]) -> Optional[str]:
    """Resolve country: explicit arg > env var > None."""
    if country is not None:
        return country
    return DEFAULT_COUNTRY


def _cse_request(params: dict, retry: bool = True) -> dict:
    """
    Make a Custom Search API request with timeout and retry on 429.

    Args:
        params: Query parameters for the CSE API.
        retry: Whether to retry once on 429 rate limit.

    Returns:
        Parsed JSON response.

    Raises:
        Exception: On API errors after retry exhaustion.
    """
    if not CSE_CX:
        raise Exception("GOOGLE_CSE_CX environment variable not set. Required for raw/image search. Get one at https://programmablesearchengine.google.com/")
    params["key"] = API_KEY
    params["cx"] = CSE_CX
    url = "https://www.googleapis.com/customsearch/v1?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429 and retry:
            time.sleep(RETRY_WAIT)
            return _cse_request(params, retry=False)
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise Exception(f"Custom Search API error {e.code}: {body}")
    except urllib.error.URLError as e:
        raise Exception(f"Network error: {e.reason}")


# ─── Search Modes ────────────────────────────────────────────────────────────

def grounded_search(
    query: str,
    lang: Optional[str] = None,
    country: Optional[str] = None,
    as_json: bool = False,
) -> str:
    """
    Search using Gemini + Google Search grounding.

    Returns a synthesized answer with numbered source citations.
    Best for: questions, current events, Hebrew queries, anything needing
    a direct answer rather than a list of links.

    Args:
        query: Search query string.
        lang: Language code (e.g. 'he', 'en'). Falls back to GOOGLE_SEARCH_LANG env.
        country: Country code (e.g. 'IL', 'US'). Falls back to GOOGLE_SEARCH_COUNTRY env.
        as_json: Return structured JSON instead of formatted text.

    Returns:
        Formatted answer string or JSON string.
    """
    from google import genai
    from google.genai import types

    lang = _resolve_lang(lang)
    country = _resolve_country(country)

    client = genai.Client(api_key=API_KEY)
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    # Build prompt with language/country hints
    prompt = query
    hints = []
    if lang and lang != "en":
        hints.append(f"Language: {lang}")
    if country:
        hints.append(f"Region: {country}")
    if hints:
        prompt = f"[{', '.join(hints)}] {query}"

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config,
        )
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            time.sleep(RETRY_WAIT)
            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=config,
                )
            except Exception as e2:
                raise Exception(f"Gemini API rate limited (retried once): {e2}")
        else:
            raise

    # Extract sources, grounding supports, and search queries
    sources: list[dict] = []
    grounding: list[dict] = []
    search_queries: list[str] = []

    if response.candidates and response.candidates[0].grounding_metadata:
        gm = response.candidates[0].grounding_metadata

        # Sources from grounding chunks
        if gm.grounding_chunks:
            seen: set[str] = set()
            for chunk in gm.grounding_chunks:
                if chunk.web and chunk.web.uri and chunk.web.uri not in seen:
                    seen.add(chunk.web.uri)
                    sources.append({
                        "title": chunk.web.title or "",
                        "uri": chunk.web.uri,
                    })

        # Confidence scores from grounding supports
        if hasattr(gm, "grounding_supports") and gm.grounding_supports:
            for support in gm.grounding_supports:
                entry: dict = {}
                if hasattr(support, "segment") and support.segment:
                    entry["text"] = getattr(support.segment, "text", "")
                if hasattr(support, "confidence_scores") and support.confidence_scores:
                    entry["confidence"] = round(max(support.confidence_scores), 4)
                if hasattr(support, "grounding_chunk_indices") and support.grounding_chunk_indices:
                    entry["source_indices"] = list(support.grounding_chunk_indices)
                if entry:
                    grounding.append(entry)

        # Search queries used by Gemini
        if hasattr(gm, "web_search_queries") and gm.web_search_queries:
            search_queries = list(gm.web_search_queries)

    if as_json:
        result: dict = {
            "answer": response.text,
            "sources": sources,
        }
        if grounding:
            result["grounding"] = grounding
        if search_queries:
            result["search_queries"] = search_queries
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Clean text output: answer + numbered sources + search queries
    lines = [response.text.strip()]
    if sources:
        lines.append("")
        lines.append("Sources:")
        for i, src in enumerate(sources, 1):
            title = src["title"] or src["uri"]
            lines.append(f"  {i}. {title}")
            lines.append(f"     {src['uri']}")
    if search_queries:
        lines.append("")
        lines.append(f"Search queries: {', '.join(search_queries)}")

    return "\n".join(lines)


def raw_search(
    query: str,
    n: int = 10,
    lang: Optional[str] = None,
    country: Optional[str] = None,
    as_json: bool = False,
) -> str:
    """
    Raw search via Custom Search JSON API.

    Returns a list of links with titles and snippets. Best for: getting
    actual URLs, research, when you need links not answers.

    Args:
        query: Search query string.
        n: Number of results (1-10).
        lang: Language code. Falls back to GOOGLE_SEARCH_LANG env.
        country: Country code. Falls back to GOOGLE_SEARCH_COUNTRY env.
        as_json: Return structured JSON.

    Returns:
        Formatted results string or JSON string.
    """
    lang = _resolve_lang(lang)
    country = _resolve_country(country)

    params: dict = {"q": query, "num": min(n, 10)}
    if lang:
        params["lr"] = f"lang_{lang}"
        params["hl"] = lang
    if country:
        params["gl"] = country

    data = _cse_request(params)
    items = data.get("items", [])

    if as_json:
        results = [
            {"title": i["title"], "link": i["link"], "snippet": i.get("snippet", "")}
            for i in items
        ]
        return json.dumps(results, ensure_ascii=False, indent=2)

    if not items:
        return "No results found."

    lines: list[str] = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['title']}")
        lines.append(f"   {item['link']}")
        if item.get("snippet"):
            lines.append(f"   {item['snippet'].strip()}")
        lines.append("")
    return "\n".join(lines)


def image_search(
    query: str,
    n: int = 10,
    lang: Optional[str] = None,
    country: Optional[str] = None,
    as_json: bool = False,
) -> str:
    """
    Image search via Custom Search JSON API.

    Args:
        query: Search query string.
        n: Number of results (1-10).
        lang: Language code. Falls back to GOOGLE_SEARCH_LANG env.
        country: Country code. Falls back to GOOGLE_SEARCH_COUNTRY env.
        as_json: Return structured JSON.

    Returns:
        Formatted image results or JSON string.
    """
    lang = _resolve_lang(lang)
    country = _resolve_country(country)

    params: dict = {"q": query, "num": min(n, 10), "searchType": "image"}
    if lang:
        params["lr"] = f"lang_{lang}"
    if country:
        params["gl"] = country

    data = _cse_request(params)
    items = data.get("items", [])

    if as_json:
        results = [
            {
                "title": i["title"],
                "link": i["link"],
                "thumbnail": i.get("image", {}).get("thumbnailLink", ""),
            }
            for i in items
        ]
        return json.dumps(results, ensure_ascii=False, indent=2)

    if not items:
        return "No results found."

    lines: list[str] = []
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['title']}")
        lines.append(f"   {item['link']}")
        lines.append("")
    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Google Search v2.0 (Gemini Grounding + Custom Search API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "latest news about AI"
  %(prog)s search "מזג אוויר תל אביב"
  %(prog)s raw "python asyncio tutorial" -n 5
  %(prog)s image "aurora borealis" --json
  %(prog)s search "OpenAI news" --lang en --country US
        """,
    )
    parser.add_argument(
        "mode",
        choices=["search", "raw", "image"],
        help="search=grounded answer, raw=links+snippets, image=image search",
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--lang", default=None, help=f"Language code (default: env GOOGLE_SEARCH_LANG={DEFAULT_LANG or 'auto'})")
    parser.add_argument("--country", default=None, help=f"Country code (default: env GOOGLE_SEARCH_COUNTRY={DEFAULT_COUNTRY or 'auto'})")
    parser.add_argument("-n", type=int, default=10, help="Number of results - raw/image only (default: 10)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    args = parser.parse_args()

    if not API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it in OpenClaw config or export GOOGLE_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "search":
            result = grounded_search(args.query, lang=args.lang, country=args.country, as_json=args.as_json)
        elif args.mode == "raw":
            result = raw_search(args.query, n=args.n, lang=args.lang, country=args.country, as_json=args.as_json)
        elif args.mode == "image":
            result = image_search(args.query, n=args.n, lang=args.lang, country=args.country, as_json=args.as_json)
        else:
            parser.print_help()
            sys.exit(1)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
