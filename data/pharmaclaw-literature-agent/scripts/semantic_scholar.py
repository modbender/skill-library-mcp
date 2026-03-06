#!/usr/bin/env python3
"""Semantic Scholar API Search.

Searches Semantic Scholar for papers with citation counts, influential citations,
TLDR summaries, and related papers. Complements PubMed with CS/ML/AI coverage.

No API key required (rate limit: 100 req/5 min).

Usage:
    python semantic_scholar.py --query "machine learning drug discovery"
    python semantic_scholar.py --query "graph neural networks molecular property prediction" --max-results 5
    python semantic_scholar.py --paper-id "DOI:10.1038/s41586-021-03819-2" --related
"""

import argparse
import json
import sys

try:
    import requests
except ImportError:
    print(json.dumps({"status": "error", "error": "requests not installed"}))
    sys.exit(1)

BASE_URL = "https://api.semanticscholar.org/graph/v1"
TIMEOUT = 15
FIELDS = "title,authors,year,abstract,citationCount,influentialCitationCount,publicationTypes,journal,externalIds,tldr,url,openAccessPdf"


def search_papers(query: str, max_results: int = 10, year_range: str = None) -> dict:
    """Search Semantic Scholar for papers."""
    params = {
        "query": query,
        "limit": min(max_results, 50),
        "fields": FIELDS,
    }
    if year_range:
        params["year"] = year_range

    try:
        resp = requests.get(f"{BASE_URL}/paper/search", params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for p in data.get("data", []):
            papers.append(format_paper(p))

        return {
            "agent": "literature",
            "version": "1.0.0",
            "source": "semantic_scholar",
            "query": query,
            "total_found": data.get("total", 0),
            "returned": len(papers),
            "papers": papers,
            "status": "success" if papers else "no_results",
        }
    except Exception as e:
        return {
            "agent": "literature",
            "version": "1.0.0",
            "source": "semantic_scholar",
            "query": query,
            "status": "error",
            "error": str(e),
        }


def get_paper(paper_id: str) -> dict:
    """Get details for a specific paper by DOI, PMID, ArXiv ID, or S2 ID."""
    try:
        resp = requests.get(
            f"{BASE_URL}/paper/{paper_id}",
            params={"fields": FIELDS},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return {"status": "success", "paper": format_paper(resp.json())}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_related(paper_id: str, max_results: int = 5) -> dict:
    """Get papers related to a given paper."""
    try:
        resp = requests.get(
            f"{BASE_URL}/paper/{paper_id}/references",
            params={"fields": FIELDS, "limit": max_results},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("data", []):
            cited = item.get("citedPaper", {})
            if cited and cited.get("title"):
                papers.append(format_paper(cited))

        return {
            "agent": "literature",
            "version": "1.0.0",
            "source": "semantic_scholar",
            "action": "related",
            "paper_id": paper_id,
            "papers": papers,
            "status": "success" if papers else "no_results",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_citations(paper_id: str, max_results: int = 10) -> dict:
    """Get papers that cite a given paper."""
    try:
        resp = requests.get(
            f"{BASE_URL}/paper/{paper_id}/citations",
            params={"fields": FIELDS, "limit": max_results},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        papers = []
        for item in data.get("data", []):
            citing = item.get("citingPaper", {})
            if citing and citing.get("title"):
                papers.append(format_paper(citing))

        return {
            "agent": "literature",
            "version": "1.0.0",
            "source": "semantic_scholar",
            "action": "citations",
            "paper_id": paper_id,
            "papers": papers,
            "status": "success" if papers else "no_results",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def format_paper(p: dict) -> dict:
    """Format a Semantic Scholar paper object."""
    authors = []
    for a in (p.get("authors") or [])[:5]:
        authors.append(a.get("name", ""))

    external_ids = p.get("externalIds") or {}
    doi = external_ids.get("DOI", "")
    pmid = external_ids.get("PubMed", "")
    arxiv = external_ids.get("ArXiv", "")

    tldr = p.get("tldr")
    tldr_text = tldr.get("text", "") if isinstance(tldr, dict) else ""

    pdf = p.get("openAccessPdf")
    pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""

    journal = p.get("journal")
    journal_name = journal.get("name", "") if isinstance(journal, dict) else ""

    return {
        "title": p.get("title", ""),
        "authors": authors,
        "author_count": len(p.get("authors") or []),
        "year": p.get("year"),
        "journal": journal_name,
        "abstract": (p.get("abstract") or "")[:2000],
        "tldr": tldr_text,
        "citation_count": p.get("citationCount", 0),
        "influential_citations": p.get("influentialCitationCount", 0),
        "doi": doi,
        "doi_url": f"https://doi.org/{doi}" if doi else "",
        "pmid": pmid,
        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        "arxiv_id": arxiv,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv}" if arxiv else "",
        "s2_url": p.get("url", ""),
        "pdf_url": pdf_url,
        "pub_types": p.get("publicationTypes") or [],
    }


def main():
    parser = argparse.ArgumentParser(description="Semantic Scholar Search")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--paper-id", help="Paper ID (DOI:xxx, PMID:xxx, ArXiv:xxx, or S2 ID)")
    parser.add_argument("--related", action="store_true", help="Get related papers (requires --paper-id)")
    parser.add_argument("--citations", action="store_true", help="Get citing papers (requires --paper-id)")
    parser.add_argument("--max-results", type=int, default=10)
    parser.add_argument("--year-range", help="Year range, e.g. '2020-2026' or '2023-'")
    args = parser.parse_args()

    if args.paper_id and args.related:
        result = get_related(args.paper_id, args.max_results)
    elif args.paper_id and args.citations:
        result = get_citations(args.paper_id, args.max_results)
    elif args.paper_id:
        result = get_paper(args.paper_id)
    elif args.query:
        result = search_papers(args.query, args.max_results, args.year_range)
    else:
        result = {"status": "error", "error": "Provide --query or --paper-id"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
