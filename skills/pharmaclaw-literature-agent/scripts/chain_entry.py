#!/usr/bin/env python3
"""Chain Entry Point for Literature Agent.

Standard PharmaClaw chain interface. Accepts JSON input and searches both
PubMed and Semantic Scholar, merging results with deduplication.

Usage:
    python chain_entry.py --input-json '{"compound": "sotorasib", "context": "drug_discovery"}'
    python chain_entry.py --input-json '{"query": "KRAS G12C inhibitor resistance mechanisms", "context": "user"}'
    python chain_entry.py --input-json '{"compound": "aspirin", "target": "COX-2", "disease": "colorectal cancer"}'
    python chain_entry.py --input-json '{"doi": "10.1038/s41586-021-03819-2", "action": "citations"}'
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pubmed_search import search_and_fetch as pubmed_search
from semantic_scholar import search_papers as s2_search, get_paper, get_related, get_citations


def build_query(input_data: dict) -> str:
    """Build a search query from structured input."""
    parts = []

    if input_data.get("query"):
        return input_data["query"]

    if input_data.get("compound") or input_data.get("name"):
        parts.append(input_data.get("compound") or input_data.get("name"))
    if input_data.get("smiles"):
        # SMILES aren't great for text search, but compound name should be provided too
        pass
    if input_data.get("target"):
        parts.append(input_data["target"])
    if input_data.get("disease"):
        parts.append(input_data["disease"])
    if input_data.get("mechanism"):
        parts.append(input_data["mechanism"])
    if input_data.get("reaction"):
        parts.append(input_data["reaction"] + " catalyst")
    if input_data.get("topic"):
        parts.append(input_data["topic"])

    return " ".join(parts) if parts else ""


def deduplicate(pubmed_papers: list, s2_papers: list) -> list:
    """Merge and deduplicate papers from both sources."""
    seen_dois = set()
    seen_pmids = set()
    seen_titles = set()
    merged = []

    # PubMed papers first (more reliable metadata)
    for p in pubmed_papers:
        doi = p.get("doi", "").lower()
        pmid = p.get("pmid", "")
        title_key = p.get("title", "").lower()[:80]

        if doi and doi in seen_dois:
            continue
        if pmid and pmid in seen_pmids:
            continue
        if title_key in seen_titles:
            continue

        p["sources"] = ["pubmed"]
        if doi:
            seen_dois.add(doi)
        if pmid:
            seen_pmids.add(pmid)
        seen_titles.add(title_key)
        merged.append(p)

    # Add S2 papers that aren't already present
    for p in s2_papers:
        doi = p.get("doi", "").lower()
        pmid = p.get("pmid", "")
        title_key = p.get("title", "").lower()[:80]

        if doi and doi in seen_dois:
            # Enrich existing entry with S2 data
            for m in merged:
                if m.get("doi", "").lower() == doi:
                    m["sources"].append("semantic_scholar")
                    m["citation_count"] = p.get("citation_count", 0)
                    m["influential_citations"] = p.get("influential_citations", 0)
                    m["tldr"] = p.get("tldr", "")
                    m["pdf_url"] = p.get("pdf_url", "")
                    break
            continue

        if pmid and pmid in seen_pmids:
            continue
        if title_key in seen_titles:
            continue

        p["sources"] = ["semantic_scholar"]
        if doi:
            seen_dois.add(doi)
        if pmid:
            seen_pmids.add(pmid)
        seen_titles.add(title_key)
        merged.append(p)

    return merged


def chain_run(input_data: dict) -> dict:
    """Route input to appropriate literature search workflow."""
    context = input_data.get("context", "user")
    max_results = input_data.get("max_results", 10)
    years = input_data.get("years")

    # Handle specific paper lookups
    if input_data.get("doi"):
        paper_id = f"DOI:{input_data['doi']}"
        action = input_data.get("action", "details")
        if action == "citations":
            return get_citations(paper_id, max_results)
        elif action == "related":
            return get_related(paper_id, max_results)
        else:
            return get_paper(paper_id)

    if input_data.get("pmid"):
        paper_id = f"PMID:{input_data['pmid']}"
        return get_paper(paper_id)

    # Build search query
    query = build_query(input_data)
    if not query:
        return {
            "agent": "literature",
            "version": "1.0.0",
            "status": "error",
            "error": "No search query could be constructed. Provide 'query', 'compound', 'target', 'disease', or 'topic'.",
        }

    # Search both sources
    pubmed_results = pubmed_search(query, max_results, "relevance", years)
    s2_results = s2_search(query, max_results)

    pubmed_papers = pubmed_results.get("papers", [])
    s2_papers = s2_results.get("papers", [])

    # Merge and deduplicate
    merged = deduplicate(pubmed_papers, s2_papers)

    # Sort by citation count (if available), then year
    merged.sort(key=lambda p: (p.get("citation_count", 0), p.get("year", "0")), reverse=True)

    # Determine recommended next agents
    recommend_next = set()
    if any("drug" in (p.get("title", "") + " " + " ".join(p.get("mesh_terms", []))).lower() for p in merged[:5]):
        recommend_next.add("pharmacology")
    if any("synth" in (p.get("title", "") + " " + p.get("abstract", "")).lower() for p in merged[:5]):
        recommend_next.update(["chemistry-query", "catalyst-design"])
    if any("patent" in (p.get("title", "") + " " + p.get("abstract", "")).lower() for p in merged[:5]):
        recommend_next.add("ip-expansion")
    if any("adverse" in (p.get("title", "") + " " + p.get("abstract", "")).lower() for p in merged[:5]):
        recommend_next.add("market-intel")

    return {
        "agent": "literature",
        "version": "1.0.0",
        "context": context,
        "query": query,
        "status": "success" if merged else "no_results",
        "pubmed_total": pubmed_results.get("total_found", 0),
        "s2_total": s2_results.get("total_found", 0),
        "returned": len(merged),
        "papers": merged[:max_results],
        "recommend_next": sorted(recommend_next) if recommend_next else ["chemistry-query", "pharmacology"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Literature Agent - Chain Entry")
    parser.add_argument("--input-json", required=True, help="JSON input string")
    args = parser.parse_args()

    try:
        input_data = json.loads(args.input_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"agent": "literature", "status": "error", "error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = chain_run(input_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
