#!/usr/bin/env python3
"""
arxiv-search: Search arXiv via their free API and output web-search-plus compatible JSON.
No API key needed.
"""
import argparse
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


ARXIV_API = "https://export.arxiv.org/api/query"


def search_arxiv(query: str, max_results: int = 10, sort_by: str = "submittedDate", sort_order: str = "descending") -> dict:
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    })
    url = f"{ARXIV_API}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenClaw/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception as e:
        return {"provider": "arxiv", "results": [], "error": str(e)}

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_data)

    results = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        updated = entry.find("atom:updated", ns)

        # Get the abstract link
        link = ""
        for l in entry.findall("atom:link", ns):
            if l.get("type") == "text/html" or l.get("title") == "abs":
                link = l.get("href", "")
                break
        if not link:
            id_elem = entry.find("atom:id", ns)
            link = id_elem.text if id_elem is not None else ""

        # Get categories
        categories = [c.get("term", "") for c in entry.findall("atom:category", ns)]

        # Get authors
        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None:
                authors.append(name.text)

        results.append({
            "title": title.text.strip().replace("\n", " ") if title is not None else "",
            "url": link,
            "snippet": summary.text.strip().replace("\n", " ")[:500] if summary is not None else "",
            "published_date": published.text if published is not None else "",
            "updated_date": updated.text if updated is not None else "",
            "authors": authors[:5],  # First 5 authors
            "categories": categories
        })

    return {"provider": "arxiv", "results": results}


def main():
    parser = argparse.ArgumentParser(description="Search arXiv (free API, no key needed)")
    parser.add_argument("--query", "-q", required=True, help="arXiv search query (supports AND, OR, field prefixes like ti:, abs:, cat:)")
    parser.add_argument("--max-results", "-m", type=int, default=10)
    parser.add_argument("--sort-by", choices=["submittedDate", "relevance", "lastUpdatedDate"], default="submittedDate")
    parser.add_argument("--sort-order", choices=["ascending", "descending"], default="descending")
    args = parser.parse_args()

    output = search_arxiv(args.query, args.max_results, args.sort_by, args.sort_order)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
