#!/usr/bin/env python3
"""
Sefaria API wrapper for Torah Scholar skill.
Provides access to Jewish texts, search, and cross-references.
"""

import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional

BASE_URL = "https://www.sefaria.org/api"

def api_request(endpoint: str, params: dict = None, method: str = "GET", json_body: dict = None) -> dict:
    """Make a request to the Sefaria API."""
    url = f"{BASE_URL}/{endpoint}"
    if params and method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    
    try:
        headers = {"User-Agent": "TorahScholar/1.0"}
        data = None
        
        if json_body:
            headers["Content-Type"] = "application/json"
            data = json.dumps(json_body).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}

def get_text(ref: str, lang: str = "all", with_context: bool = False) -> dict:
    """
    Get text by reference (e.g., "Genesis 1:1", "Berakhot 2a").
    
    Args:
        ref: Sefaria reference string
        lang: "he" (Hebrew), "en" (English), or "all"
        with_context: Include surrounding context
    
    Returns:
        dict with text, translations, and metadata
    """
    # Normalize reference format: "Genesis 1:1" -> "Genesis.1.1"
    # But keep Talmud refs like "Berakhot 2a" as-is
    normalized_ref = ref.replace(":", ".").replace(" ", "_")
    encoded_ref = urllib.parse.quote(normalized_ref)
    
    # Use v2 API (more reliable for text content)
    endpoint = f"texts/{encoded_ref}"
    
    params = {}
    if with_context:
        params["context"] = "1"
    
    return api_request(endpoint, params if params else None)

def search(query: str, filters: dict = None, limit: int = 10) -> dict:
    """
    Search across all texts.
    
    Args:
        query: Search query
        filters: Optional filters (e.g., {"book": "Genesis"})
        limit: Max results to return
    
    Returns:
        dict with search results
    """
    body = {
        "query": query,
        "size": limit,
        "type": "text",
        "field": "naive_lemmatizer",  # Better for English searches
        "sort_type": "relevance"
    }
    
    if filters:
        if "book" in filters:
            body["filters"] = [filters["book"]]
    
    return api_request("search-wrapper/es6", method="POST", json_body=body)

def get_links(ref: str) -> dict:
    """
    Get all texts linked to a reference.
    
    Args:
        ref: Sefaria reference string
    
    Returns:
        dict with linked texts (commentaries, cross-references)
    """
    encoded_ref = urllib.parse.quote(ref.replace(" ", "_"))
    return api_request(f"links/{encoded_ref}")

def get_related(ref: str) -> dict:
    """
    Get related texts and topics for a reference.
    
    Args:
        ref: Sefaria reference string
    
    Returns:
        dict with related content
    """
    encoded_ref = urllib.parse.quote(ref.replace(" ", "_"))
    return api_request(f"related/{encoded_ref}")

def get_index(title: str) -> dict:
    """
    Get metadata about a book/text.
    
    Args:
        title: Book title (e.g., "Genesis", "Berakhot")
    
    Returns:
        dict with book metadata
    """
    encoded_title = urllib.parse.quote(title.replace(" ", "_"))
    return api_request(f"v2/index/{encoded_title}")

def get_calendars() -> dict:
    """
    Get today's learning schedule (Daf Yomi, Parsha, etc.).
    
    Returns:
        dict with calendar items
    """
    return api_request("calendars")

def get_parsha() -> dict:
    """
    Get this week's Torah portion.
    
    Returns:
        dict with parsha information
    """
    calendars = get_calendars()
    if "error" in calendars:
        return calendars
    
    for item in calendars.get("calendar_items", []):
        if item.get("title", {}).get("en") == "Parashat Hashavua":
            return {
                "parsha": item.get("displayValue", {}).get("en"),
                "ref": item.get("ref"),
                "hebrew": item.get("displayValue", {}).get("he")
            }
    
    return {"error": "Parsha not found"}

def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re
    # Remove HTML tags but keep content
    clean = re.sub(r'<[^>]+>', '', text)
    # Clean up extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def format_text(data: dict, format_type: str = "markdown") -> str:
    """
    Format API response as readable text.
    
    Args:
        data: API response dict
        format_type: "markdown", "plain", or "json"
    
    Returns:
        Formatted string
    """
    if "error" in data:
        return f"Error: {data['error']}"
    
    if format_type == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    output = []
    
    # Title/Reference
    ref = data.get("ref") or data.get("sectionRef", "")
    if ref:
        output.append(f"## {ref}\n")
    
    # Hebrew text
    he_text = data.get("he")
    if he_text:
        if isinstance(he_text, list):
            # Join verses with numbers
            formatted_he = []
            for i, verse in enumerate(he_text, 1):
                if isinstance(verse, str):
                    clean_verse = strip_html(verse)
                    formatted_he.append(f"{i}. {clean_verse}")
            he_text = "\n".join(formatted_he)
        else:
            he_text = strip_html(str(he_text))
        output.append(f"**Hebrew:**\n{he_text}\n")
    
    # English text
    en_text = data.get("text")
    if en_text:
        if isinstance(en_text, list):
            # Join verses with numbers
            formatted_en = []
            for i, verse in enumerate(en_text, 1):
                if isinstance(verse, str):
                    clean_verse = strip_html(verse)
                    formatted_en.append(f"{i}. {clean_verse}")
            en_text = "\n".join(formatted_en)
        else:
            en_text = strip_html(str(en_text))
        output.append(f"**English:**\n{en_text}\n")
    
    return "\n".join(output) if output else json.dumps(data, indent=2, ensure_ascii=False)

def format_search_results(data: dict) -> str:
    """Format search results as markdown."""
    if "error" in data:
        return f"Error: {data['error']}"
    
    hits = data.get("hits", {}).get("hits", [])
    total = data.get("hits", {}).get("total", 0)
    if not hits:
        return "No results found."
    
    output = [f"## Search Results ({total} total, showing {len(hits)})\n"]
    
    for i, hit in enumerate(hits[:10], 1):
        # Extract ref from _id (format: "Book, Section (version [lang])")
        ref_id = hit.get("_id", "Unknown")
        # Try to extract just the reference part before the version info
        ref = ref_id.split(" (")[0] if " (" in ref_id else ref_id
        
        # Get highlighted text
        highlight = hit.get("highlight", {})
        text_snippets = highlight.get("naive_lemmatizer", []) or highlight.get("exact", [])
        
        output.append(f"### {i}. {ref}")
        if text_snippets:
            # Clean up HTML bold tags and join snippets
            for snippet in text_snippets[:2]:  # Show first 2 snippets
                clean_snippet = snippet.replace("<b>", "**").replace("</b>", "**")
                output.append(f"> {clean_snippet}")
        output.append("")
    
    return "\n".join(output)

def format_links(data: list) -> str:
    """Format links as markdown."""
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    
    if not data:
        return "No linked texts found."
    
    # Group by category
    categories = {}
    for link in data:
        cat = link.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(link)
    
    output = ["## Linked Texts\n"]
    
    for cat, links in categories.items():
        output.append(f"### {cat}")
        for link in links[:5]:  # Limit per category
            ref = link.get("ref", "Unknown")
            text = link.get("he", "") or link.get("text", "")
            if isinstance(text, str) and text:
                text = text[:150] + "..." if len(text) > 150 else text
            output.append(f"- **{ref}**: {text}")
        output.append("")
    
    return "\n".join(output)


if __name__ == "__main__":
    # CLI interface
    if len(sys.argv) < 2:
        print("Usage: sefaria.py <command> [args]")
        print("Commands: text, search, links, related, parsha, calendars")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "text" and len(sys.argv) >= 3:
        ref = " ".join(sys.argv[2:])
        result = get_text(ref)
        print(format_text(result))
    
    elif command == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        result = search(query)
        print(format_search_results(result))
    
    elif command == "links" and len(sys.argv) >= 3:
        ref = " ".join(sys.argv[2:])
        result = get_links(ref)
        print(format_links(result))
    
    elif command == "related" and len(sys.argv) >= 3:
        ref = " ".join(sys.argv[2:])
        result = get_related(ref)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "parsha":
        result = get_parsha()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "calendars":
        result = get_calendars()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
