"""
arxiv_crawler.py — arXiv API search and PDF download for ArXivKB.

Uses the `arxiv` Python package (free API, no key required).
"""

import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from typing import Optional


def _extract_arxiv_id(entry_id: str) -> str:
    """Extract clean arXiv ID from entry URL. Strips version suffix."""
    # e.g. http://arxiv.org/abs/2401.12345v2 → 2401.12345
    aid = entry_id.split("/abs/")[-1] if "/abs/" in entry_id else entry_id
    if "v" in aid and aid.index("v") > 4:
        aid = aid.rsplit("v", 1)[0]
    return aid.strip()


def search_arxiv(
    query: str,
    max_results: int = 50,
    days_back: int = 7,
) -> list[dict]:
    """
    Search arXiv for papers matching a query.

    Args:
        query:       Natural language or arXiv query syntax.
        max_results: Maximum number of results to fetch.
        days_back:   Only return papers published in the last N days (0 = no filter).

    Returns:
        List of paper metadata dicts.
    """
    import arxiv

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=days_back)
        if days_back > 0
        else None
    )

    # Build arXiv query
    q = query.strip()

    # If query looks like a category code (e.g., cs.AI, math.OC), use cat: prefix
    if "." in q and len(q) < 30 and " " not in q:
        arxiv_query = f"cat:{q}"
    elif q.startswith("cat:"):
        arxiv_query = q
    else:
        # Free-text: phrase match in title or abstract
        words = q.split()
        if len(words) <= 4:
            arxiv_query = f'ti:"{q}" OR abs:"{q}"'
        else:
            ti_parts = " AND ".join(f"ti:{w}" for w in words[:6])
            abs_parts = " AND ".join(f"abs:{w}" for w in words[:6])
            arxiv_query = f"({ti_parts}) OR ({abs_parts})"

    client = arxiv.Client(
        page_size=min(max_results, 100),
        delay_seconds=3.0,
        num_retries=3,
    )
    search = arxiv.Search(
        query=arxiv_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers = []
    try:
        for result in client.results(search):
            pub = result.published
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if cutoff and pub < cutoff:
                continue

            arxiv_id = _extract_arxiv_id(result.entry_id)
            papers.append({
                "arxiv_id": arxiv_id,
                "title": result.title.replace("\n", " ").strip(),
                "authors": [a.name for a in result.authors],
                "abstract": result.summary.replace("\n", " ").strip(),
                "categories": list(result.categories),
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d") if result.updated else None,
                "pdf_url": result.pdf_url,
            })
    except Exception as e:
        print(f"[arxiv] Search error for '{query}': {e}")

    return papers


def download_pdf(arxiv_id: str, pdf_dir: str, pdf_url: Optional[str] = None) -> Optional[str]:
    """
    Download the PDF for an arXiv paper.

    Args:
        arxiv_id: Clean arXiv ID (e.g. '2401.12345').
        pdf_dir:  Directory to save PDFs.
        pdf_url:  Direct PDF URL (constructed from ID if not provided).

    Returns:
        Path to the downloaded PDF, or None on failure.
    """
    os.makedirs(pdf_dir, exist_ok=True)
    safe_id = arxiv_id.replace("/", "_").replace(":", "_")
    pdf_path = os.path.join(pdf_dir, f"{safe_id}.pdf")

    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1024:
        return pdf_path

    url = pdf_url or f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    try:
        print(f"[arxiv] Downloading {arxiv_id}.pdf ...")
        # Add a user-agent to avoid 403s
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()

        if len(data) < 1024:
            print(f"[arxiv] PDF too small ({len(data)}B), skipping")
            return None

        with open(pdf_path, "wb") as f:
            f.write(data)

        print(f"[arxiv] Saved {safe_id}.pdf ({len(data) // 1024}KB)")
        return pdf_path

    except Exception as e:
        print(f"[arxiv] Download failed for {arxiv_id}: {e}")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        return None


def crawl_topics(
    topics: list[str],
    pdf_dir: str,
    max_results: int = 50,
    days_back: int = 7,
    download_pdfs: bool = True,
    dry_run: bool = False,
) -> list[dict]:
    """
    Crawl all topics and return deduplicated list of paper metadata.

    Args:
        topics:       List of search queries.
        pdf_dir:      Directory to save PDFs.
        max_results:  Max results per topic.
        days_back:    Look back N days.
        download_pdfs: If True, download PDFs after crawling.
        dry_run:      If True, skip downloads.

    Returns:
        Deduplicated list of paper metadata dicts.
    """
    seen: set[str] = set()
    all_papers: list[dict] = []

    for i, topic in enumerate(topics):
        print(f"[arxiv] [{i+1}/{len(topics)}] Searching: {topic}")
        papers = search_arxiv(topic, max_results=max_results, days_back=days_back)

        new = []
        for p in papers:
            if p["arxiv_id"] not in seen:
                seen.add(p["arxiv_id"])
                all_papers.append(p)
                new.append(p)

        print(f"[arxiv]   {len(papers)} results, {len(new)} new")

        if not dry_run and download_pdfs:
            for p in new:
                pdf_path = download_pdf(p["arxiv_id"], pdf_dir, p.get("pdf_url"))
                if pdf_path:
                    p["pdf_path"] = pdf_path
                time.sleep(1)  # Be polite

        if i < len(topics) - 1:
            time.sleep(3)

    print(f"[arxiv] Total unique papers: {len(all_papers)}")
    return all_papers
