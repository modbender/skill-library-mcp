#!/usr/bin/env python3
"""PubMed Literature Search via NCBI E-utilities.

Searches PubMed for papers related to compounds, targets, diseases, or general queries.
Returns structured JSON with titles, authors, abstracts, DOIs, and MeSH terms.

Usage:
    python pubmed_search.py --query "sotorasib KRAS lung cancer"
    python pubmed_search.py --query "aspirin colorectal cancer prevention" --max-results 10
    python pubmed_search.py --query "EGFR inhibitor resistance" --sort relevance --years 5
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote_plus

try:
    import requests
except ImportError:
    print(json.dumps({"status": "error", "error": "requests not installed"}))
    sys.exit(1)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TIMEOUT = 15


def search_pubmed(query: str, max_results: int = 10, sort: str = "relevance", years: int = None) -> dict:
    """Search PubMed and return PMIDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": min(max_results, 50),
        "sort": sort,
        "retmode": "json",
    }
    if years:
        params["datetype"] = "pdat"
        params["reldate"] = years * 365

    try:
        resp = requests.get(f"{BASE_URL}/esearch.fcgi", params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        result = data.get("esearchresult", {})
        return {
            "pmids": result.get("idlist", []),
            "total_found": int(result.get("count", 0)),
            "query_translation": result.get("querytranslation", query),
        }
    except Exception as e:
        return {"pmids": [], "total_found": 0, "error": str(e)}


def fetch_details(pmids: list[str]) -> list[dict]:
    """Fetch paper details for a list of PMIDs."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    }

    try:
        resp = requests.get(f"{BASE_URL}/efetch.fcgi", params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
    except Exception as e:
        return [{"error": str(e)}]

    papers = []
    for article in root.findall(".//PubmedArticle"):
        paper = parse_article(article)
        if paper:
            papers.append(paper)

    return papers


def parse_article(article) -> dict:
    """Parse a PubmedArticle XML element into structured dict."""
    try:
        medline = article.find(".//MedlineCitation")
        art = medline.find(".//Article")

        # PMID
        pmid = medline.findtext(".//PMID", "")

        # Title
        title = art.findtext(".//ArticleTitle", "")

        # Abstract
        abstract_parts = []
        for abs_text in art.findall(".//Abstract/AbstractText"):
            label = abs_text.get("Label", "")
            text = abs_text.text or ""
            # Handle mixed content
            if abs_text.tail:
                text += abs_text.tail
            # Get all inner text
            full_text = ET.tostring(abs_text, encoding="unicode", method="text").strip()
            if label:
                abstract_parts.append(f"{label}: {full_text}")
            else:
                abstract_parts.append(full_text)
        abstract = " ".join(abstract_parts)

        # Authors
        authors = []
        for author in art.findall(".//AuthorList/Author"):
            last = author.findtext("LastName", "")
            fore = author.findtext("ForeName", "")
            if last:
                authors.append(f"{last} {fore}".strip())

        # Journal
        journal = art.findtext(".//Journal/Title", "")
        journal_abbr = art.findtext(".//Journal/ISOAbbreviation", "")

        # Date
        year = art.findtext(".//Journal/JournalIssue/PubDate/Year", "")
        month = art.findtext(".//Journal/JournalIssue/PubDate/Month", "")

        # DOI
        doi = ""
        for aid in art.findall(".//ELocationID"):
            if aid.get("EIdType") == "doi":
                doi = aid.text or ""
                break
        if not doi:
            for aid in medline.findall(".//PubmedData/ArticleIdList/ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text or ""
                    break

        # MeSH terms
        mesh_terms = []
        for mesh in medline.findall(".//MeshHeadingList/MeshHeading/DescriptorName"):
            mesh_terms.append(mesh.text or "")

        # Keywords
        keywords = []
        for kw in medline.findall(".//KeywordList/Keyword"):
            keywords.append(kw.text or "")

        # Publication type
        pub_types = []
        for pt in art.findall(".//PublicationTypeList/PublicationType"):
            pub_types.append(pt.text or "")

        return {
            "pmid": pmid,
            "title": title,
            "authors": authors[:5],  # First 5 authors
            "author_count": len(authors),
            "journal": journal,
            "journal_abbr": journal_abbr,
            "year": year,
            "month": month,
            "doi": doi,
            "doi_url": f"https://doi.org/{doi}" if doi else "",
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "abstract": abstract[:2000],  # Truncate long abstracts
            "mesh_terms": mesh_terms[:10],
            "keywords": keywords[:10],
            "pub_types": pub_types,
        }
    except Exception as e:
        return {"error": str(e)}


def search_and_fetch(query: str, max_results: int = 10, sort: str = "relevance", years: int = None) -> dict:
    """Full search: find PMIDs then fetch details."""
    search_result = search_pubmed(query, max_results, sort, years)

    if not search_result["pmids"]:
        return {
            "agent": "literature",
            "version": "1.0.0",
            "source": "pubmed",
            "query": query,
            "total_found": search_result["total_found"],
            "papers": [],
            "status": "no_results" if not search_result.get("error") else "error",
            "error": search_result.get("error"),
        }

    papers = fetch_details(search_result["pmids"])

    return {
        "agent": "literature",
        "version": "1.0.0",
        "source": "pubmed",
        "query": query,
        "query_translation": search_result.get("query_translation"),
        "total_found": search_result["total_found"],
        "returned": len(papers),
        "papers": papers,
        "status": "success",
    }


def main():
    parser = argparse.ArgumentParser(description="PubMed Literature Search")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-results", type=int, default=10, help="Max papers to return (1-50)")
    parser.add_argument("--sort", choices=["relevance", "date"], default="relevance")
    parser.add_argument("--years", type=int, help="Limit to last N years")
    args = parser.parse_args()

    result = search_and_fetch(args.query, args.max_results, args.sort, args.years)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
