#!/usr/bin/env python3
"""
hxxra - A Research Assistant workflow skill
Commands: search, download, analyze, save
"""

import json
import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import re
import tempfile
import shutil
import time
from typing import List, Dict, Any, Optional, Tuple
import ssl
import certifi


# Import scholarly for Google Scholar search
try:
    from scholarly import scholarly, ProxyGenerator

    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False


# ============ Configuration ============

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.json")
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())  # 创建 SSL 上下文


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config.json: {e}")
    return {}


def get_zotero_config() -> tuple:
    """
    Get Zotero API configuration from config.json or environment variables.
    Priority: config.json > environment variables
    """
    config = load_config()
    zotero_config = config.get("zotero", {})

    # Try config.json first
    api_key = zotero_config.get("api_key")
    user_id = zotero_config.get("user_id")
    group_id = zotero_config.get("group_id")

    # Fall back to environment variables
    if not api_key:
        api_key = os.environ.get("ZOTERO_API_KEY")
    if not user_id:
        user_id = os.environ.get("ZOTERO_USER_ID")
    if not group_id:
        group_id = os.environ.get("ZOTERO_GROUP_ID")

    if not api_key:
        raise ValueError(
            "Zotero API key not found in config.json or environment variables"
        )
    if not user_id and not group_id:
        raise ValueError(
            "Zotero user_id or group_id not found in config.json or environment variables"
        )

    prefix = f"/users/{user_id}" if user_id else f"/groups/{group_id}"
    return api_key, prefix


# ============ arXiv API ============

ARXIV_API_URL = "https://export.arxiv.org/api/query"


def search_arxiv(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers.

    Args:
        query: Search keywords
        limit: Number of results to return

    Returns:
        List of paper dictionaries
    """
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/atom+xml"})
        with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
            xml_content = resp.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"arXiv API request failed: {e}")

    # Parse Atom XML
    papers = []
    try:
        root = ET.fromstring(xml_content)

        # Define namespace
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        for entry in root.findall("atom:entry", ns):
            paper = {}

            # Basic fields
            title_elem = entry.find("atom:title", ns)
            paper["title"] = (
                title_elem.text.strip() if title_elem is not None else "Unknown"
            )

            summary_elem = entry.find("atom:summary", ns)
            paper["abstract"] = (
                summary_elem.text.strip() if summary_elem is not None else ""
            )

            # Authors
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            paper["authors"] = authors

            # Published date (year)
            published_elem = entry.find("atom:published", ns)
            if published_elem is not None:
                date_str = published_elem.text
                paper["year"] = date_str[:4] if len(date_str) >= 4 else "Unknown"
            else:
                paper["year"] = "Unknown"

            # Links
            paper["url"] = ""
            paper["pdf_url"] = ""
            for link in entry.findall("atom:link", ns):
                rel = link.get("rel", "")
                href = link.get("href", "")
                if rel == "alternate":
                    paper["url"] = href
                elif rel == "related" and link.get("title") == "pdf":
                    paper["pdf_url"] = href

            # arXiv ID
            id_elem = entry.find("atom:id", ns)
            if id_elem is not None:
                # Extract arXiv ID from URL like http://arxiv.org/abs/xxxx.xxxxx
                id_match = re.search(r"arxiv\.org/abs/(\S+)", id_elem.text)
                paper["id"] = id_match.group(1) if id_match else id_elem.text
            else:
                paper["id"] = (
                    f"arxiv_{paper['authors'][0]}_{paper['title'].replace(' ', '_')}"
                )

            # arXiv category
            category_elem = entry.find("arxiv:primary_category", ns)
            paper["category"] = (
                category_elem.get("term", "") if category_elem is not None else ""
            )

            paper["source"] = "arxiv"
            paper["citations"] = 0  # arXiv doesn't provide citation count

            papers.append(paper)

    except ET.ParseError as e:
        raise RuntimeError(f"Failed to parse arXiv XML: {e}")

    return papers


# ============ Google Scholar (using scholarly) ============


def setup_scholarly_proxy() -> None:
    """Setup proxy for scholarly to avoid blocking (optional)."""
    config = load_config()
    proxy_config = config.get("scholarly_proxy", {})

    if proxy_config.get("enabled", False):
        pg = ProxyGenerator()
        if proxy_config.get("type") == "tor":
            pg.Tor_Internal(tor_cmd=proxy_config.get("tor_cmd", "tor"))
        elif proxy_config.get("type") == "free":
            pg.FreeProxies()
        scholarly.use_proxy(pg)


def search_scholar(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search Google Scholar using the scholarly library.

    Args:
        query: Search keywords
        limit: Number of results to return

    Returns:
        List of paper dictionaries
    """
    if not SCHOLARLY_AVAILABLE:
        raise RuntimeError(
            "scholarly library not installed. " "Install with: pip install scholarly"
        )

    # Setup proxy if configured
    try:
        setup_scholarly_proxy()
    except Exception:
        pass  # Continue without proxy if setup fails

    papers = []

    try:
        # Search for papers
        search_query = scholarly.search_pubs(query)

        for i, pub in enumerate(search_query):
            if i >= limit:
                break

            # Extract bibliographic info
            bib = pub.get("bib", {})

            paper = {
                "id": f"scholar_{i}",
                "title": bib.get("title", "Unknown"),
                "authors": bib.get("author", []),
                "year": str(bib.get("pub_year", "Unknown")),
                "abstract": bib.get("abstract", ""),
                "source": "scholar",
                "citations": pub.get("num_citations", 0),
            }
            paper["id"] = (
                f"scholar_{paper['authors'][0]}_{paper['title'].replace(' ', '_')}"
            )

            # Handle single author vs list
            if isinstance(paper["authors"], str):
                paper["authors"] = [a.strip() for a in paper["authors"].split(" and ")]

            # Get URL and PDF link
            paper["url"] = pub.get("pub_url", "")
            paper["pdf_url"] = pub.get("eprint_url", "")

            # Fallback: construct scholar URL
            if not paper["url"]:
                paper["url"] = (
                    f"https://scholar.google.com/scholar?q={urllib.parse.quote(query)}"
                )

            # Add venue info if available
            if bib.get("venue"):
                paper["venue"] = bib["venue"]

            papers.append(paper)

            # Be nice to Google Scholar - add small delay
            time.sleep(0.5)

    except Exception as e:
        raise RuntimeError(f"Google Scholar search failed: {e}")

    return papers


# ============ Download PDF ============


def download_pdf(url: str, dest_path: str, timeout: int = 60) -> Tuple[bool, str]:
    """
    Download a PDF file.

    Args:
        url: PDF URL
        dest_path: Destination file path
        timeout: Request timeout in seconds

    Returns:
        Tuple[bool, str]: (True if successful, error message if failed)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(resp, f)

        # Verify it's a PDF
        with open(dest_path, "rb") as f:
            header = f.read(5)
        if header != b"%PDF-":
            os.unlink(dest_path)
            return False

        return True, "Success"

    except Exception as e:
        if os.path.exists(dest_path):
            os.unlink(dest_path)
        return False, f"Download failed: {e}"


# ============ PDF Text Extraction ============

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_text_from_pdf(pdf_path: str, max_pages: int = 20) -> Dict[str, Any]:
    """
    Extract text from PDF using available libraries.

    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum pages to extract (to avoid huge files)

    Returns:
        Dictionary with extracted text and metadata
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    result = {"text": "", "metadata": {}, "pages_extracted": 0, "total_pages": 0}

    # Try PyMuPDF first (best quality)
    if PYMUPDF_AVAILABLE:
        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            result["metadata"] = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
            }

            text_parts = []
            pages_to_extract = min(len(doc), max_pages)

            for page_num in range(pages_to_extract):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

            result["text"] = "\n\n".join(text_parts)
            result["pages_extracted"] = pages_to_extract
            doc.close()
            return result

        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}", file=sys.stderr)

    # Fallback to pdfplumber
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result["total_pages"] = len(pdf.pages)
                pages_to_extract = min(len(pdf.pages), max_pages)

                text_parts = []
                for i in range(pages_to_extract):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(f"--- Page {i + 1} ---\n{text}")

                result["text"] = "\n\n".join(text_parts)
                result["pages_extracted"] = pages_to_extract
                return result

        except Exception as e:
            print(f"pdfplumber extraction failed: {e}", file=sys.stderr)

    raise RuntimeError(
        "No PDF extraction library available. "
        "Install with: pip install pymupdf pdfplumber"
    )


# ============ LLM Analysis ============

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration from config.json."""
    config = load_config()
    llm_config = config.get("llm", {})

    # Check for API key
    api_key = llm_config.get("api_key")
    if not api_key:
        # Try environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "LLM API key not found in config.json or OPENAI_API_KEY environment variable"
            )
        llm_config["api_key"] = api_key

    # Set defaults
    llm_config.setdefault("provider", "openai")
    llm_config.setdefault("base_url", "https://api.openai.com/v1")
    llm_config.setdefault("model", "gpt-4o-mini")
    llm_config.setdefault("max_tokens", 4000)
    llm_config.setdefault("temperature", 0.3)

    return llm_config


def analyze_with_llm(text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze paper text using LLM via OpenAI library.

    Args:
        text: Extracted paper text
        metadata: PDF metadata

    Returns:
        Structured analysis result
    """
    if not OPENAI_AVAILABLE:
        raise RuntimeError("openai library not installed. Run: pip install openai")

    config = get_llm_config()

    # Truncate text if too long (approximate token limit)
    max_chars = 15000  # Roughly 4000 tokens
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Text truncated due to length...]"

    # Build prompt
    system_prompt = """You are a research paper analysis assistant. Analyze the provided academic paper and extract key information in a structured format.

Provide your analysis in this exact JSON structure:
{
    "title": "The paper title",
    "authors": ["Author 1", "Author 2"],
    "year": "Publication year",
    "abstract": "Brief abstract summarizing the paper",
    "background": "The research problem, motivation, and context",
    "methodology": "The methods, approach, and techniques used",
    "results": "Key findings and experimental results",
    "conclusions": "Main conclusions and future work",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "limitations": "Any limitations mentioned",
    "impact": "Potential impact and significance of this work"
}

Be concise but comprehensive. If information is not available, use empty strings or empty arrays. Return ONLY valid JSON, no markdown formatting."""

    user_prompt = f"""Please analyze the following research paper:

--- Paper Metadata ---
Title: {metadata.get('title', 'Unknown')}
Author: {metadata.get('author', 'Unknown')}

--- Paper Content ---
{text}

Provide a structured analysis in JSON format."""

    # Initialize OpenAI client
    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

    try:
        # Make API call
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            response_format={"type": "json_object"},
        )

        # Extract and parse analysis
        content = response.choices[0].message.content
        analysis = json.loads(content)

        return analysis

    except Exception as e:
        raise RuntimeError(f"LLM analysis failed: {e}")


def analyze_single_pdf(pdf_path: str, output_dir: str) -> Dict[str, Any]:
    """
    Analyze a single PDF using text extraction and LLM.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save analysis results

    Returns:
        Analysis result dictionary
    """
    import hashlib

    pdf_name = os.path.basename(pdf_path)
    pdf_id = hashlib.md5(pdf_path.encode()).hexdigest()[:8]

    analysis_file = os.path.join(output_dir, f"{pdf_id}_analysis.json")

    try:
        # Step 1: Extract text from PDF
        extraction_result = extract_text_from_pdf(pdf_path, max_pages=20)
        extracted_text = extraction_result["text"]
        pdf_metadata = extraction_result["metadata"]

        if not extracted_text.strip():
            return {
                "id": pdf_id,
                "original_file": pdf_path,
                "analysis_file": None,
                "status": "failed",
                "error": "No text could be extracted from PDF",
            }

        # Step 2: Analyze with LLM
        analysis = analyze_with_llm(extracted_text, pdf_metadata)

        # Step 3: Build result
        result = {
            "id": pdf_id,
            "original_file": pdf_path,
            "analysis_file": os.path.abspath(analysis_file),
            "metadata": {
                "title": analysis.get("title", pdf_metadata.get("title", "Unknown")),
                "authors": analysis.get("authors", []),
                "year": analysis.get("year", "Unknown"),
                "abstract": analysis.get("abstract", ""),
                "keywords": analysis.get("keywords", []),
            },
            "analysis": {
                "background": analysis.get("background", ""),
                "methodology": analysis.get("methodology", ""),
                "results": analysis.get("results", ""),
                "conclusions": analysis.get("conclusions", ""),
                "limitations": analysis.get("limitations", ""),
                "impact": analysis.get("impact", ""),
            },
            "extraction_info": {
                "pages_extracted": extraction_result["pages_extracted"],
                "total_pages": extraction_result["total_pages"],
            },
            "status": "success",
        }

        # Save analysis
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    except Exception as e:
        error_result = {
            "id": pdf_id,
            "original_file": pdf_path,
            "analysis_file": None,
            "status": "failed",
            "error": str(e),
        }

        # Save error result too
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)

        return error_result


# ============ Zotero API ============

ZOTERO_API_BASE = "https://api.zotero.org"


def zotero_api_request(
    path: str,
    api_key: str,
    method: str = "GET",
    data: Any = None,
    content_type: str = None,
) -> tuple:
    """Make a Zotero API request."""
    url = ZOTERO_API_BASE + path

    headers = {
        "Zotero-API-Key": api_key,
        "Zotero-API-Version": "3",
    }
    if content_type:
        headers["Content-Type"] = content_type

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        if not content_type:
            headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            resp_headers = dict(resp.headers)
            return resp_body, resp_headers
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"Zotero API Error {e.code}: {e.reason} - {err_body[:500]}")


def get_or_create_collection(api_key: str, prefix: str, collection_name: str) -> str:
    """
    Get collection key by name, or create if not exists.

    Returns:
        Collection key
    """
    # List all collections
    body, _ = zotero_api_request(f"{prefix}/collections", api_key)
    collections = json.loads(body) if body.strip() else []

    for col in collections:
        if col.get("data", {}).get("name") == collection_name:
            return col["data"]["key"]

    # Create new collection
    collection_data = {"name": collection_name, "parentCollection": False}

    body, _ = zotero_api_request(
        f"{prefix}/collections",
        api_key,
        method="POST",
        data=collection_data,
        content_type="application/json",
    )

    result = json.loads(body) if body.strip() else {}
    success = result.get("successful", {})
    if success:
        return list(success.values())[0]["key"]

    raise RuntimeError("Failed to create collection")


def add_item_to_zotero(
    api_key: str, prefix: str, paper: Dict[str, Any], collection_key: str
) -> str:
    """
    Add a paper to Zotero.

    Args:
        api_key: Zotero API key
        prefix: API path prefix
        paper: Paper metadata
        collection_key: Target collection key

    Returns:
        New item key
    """
    # Prepare item data
    item_type = "preprint" if paper.get("source") == "arxiv" else "journalArticle"

    creators = []
    for author in paper.get("authors", []):
        # Try to split name into first/last
        parts = author.split()
        if len(parts) >= 2:
            creators.append(
                {
                    "creatorType": "author",
                    "firstName": " ".join(parts[:-1]),
                    "lastName": parts[-1],
                }
            )
        else:
            creators.append({"creatorType": "author", "name": author})

    item_data = {
        "itemType": item_type,
        "title": paper.get("title", "Untitled"),
        "creators": creators,
        "abstractNote": paper.get("abstract", ""),
        "url": paper.get("url", ""),
        "date": paper.get("year", ""),
        "collections": [collection_key],
        "tags": [{"tag": "hxxra"}],
        "extra": (
            f"arXiv ID: {paper.get('id', '')}" if paper.get("source") == "arxiv" else ""
        ),
    }

    # Add DOI if available
    if paper.get("doi"):
        item_data["DOI"] = paper["doi"]

    body, _ = zotero_api_request(
        f"{prefix}/items",
        api_key,
        method="POST",
        data=[item_data],
        content_type="application/json",
    )

    result = json.loads(body) if body.strip() else {}
    success = result.get("successful", {})

    if success:
        return list(success.values())[0]["key"]

    failed = result.get("failed", {})
    if failed:
        raise RuntimeError(f"Failed to add item: {failed}")

    raise RuntimeError("Unknown error adding item to Zotero")


# ============ Command Handlers ============


def handle_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle search command."""
    query = input_data.get("query") or input_data.get("q", "")
    if not query:
        return {"ok": False, "error": "Missing required parameter: query"}

    source = input_data.get("source", "arxiv")
    limit = int(input_data.get("limit", 10))
    output_file = input_data.get("output", "search_results.json")

    results = []

    if source == "arxiv":
        try:
            arxiv_results = search_arxiv(query, limit)
            results.extend(arxiv_results)
        except Exception as e:
            return {"ok": False, "error": f"arXiv search failed: {str(e)}"}

    if source == "scholar":
        try:
            scholar_results = search_scholar(query, limit)
            results.extend(scholar_results)
        except Exception as e:
            return {"ok": False, "error": f"Google Scholar search failed: {str(e)}"}

    # Limit total results
    results = results[:limit]

    # Save to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return {"ok": False, "error": f"Failed to save results: {str(e)}"}

    return {
        "ok": True,
        "command": "search",
        "query": query,
        "source": source,
        "results": results,
        "total": len(results),
        "output_file": os.path.abspath(output_file),
    }


def handle_download(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle download command."""
    ids = input_data.get("ids", [])
    from_file = input_data.get("from-file") or input_data.get("from_file")
    download_dir = input_data.get("dir") or input_data.get("download_dir", "./papers")

    # Load papers data
    papers = []
    if from_file:
        try:
            with open(from_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    papers = data
                elif isinstance(data, dict) and "results" in data:
                    papers = data["results"]
        except Exception as e:
            return {"ok": False, "error": f"Failed to load from file: {str(e)}"}
    elif ids:
        # This would need the original search results to be stored somewhere
        return {"ok": False, "error": "Download by ID requires from-file parameter"}
    else:
        return {"ok": False, "error": "Either ids or from-file must be provided"}

    # Filter by IDs if specified
    if ids:
        papers = [
            p
            for p in papers
            if p.get("id") in ids or any(str(i) == str(p.get("id")) for i in ids)
        ]

    # Create download directory
    os.makedirs(download_dir, exist_ok=True)

    downloaded = []
    failed = []

    for i, paper in enumerate(papers, 1):
        try:
            paper_id = paper.get("id", str(i))
            title = paper.get("title", "unknown")
            pdf_url = paper.get("pdf_url", "")
            authors = paper.get("authors", [])

            if not pdf_url:
                failed.append(
                    {"id": paper_id, "title": title, "error": "No PDF URL available"}
                )
                continue

            # Generate filename
            safe_title = re.sub(r"[^\w\s-]", "", title)[:50].strip()
            filename = f"{authors[0]}_{safe_title.replace(' ', '_')}.pdf"
            filepath = os.path.join(download_dir, filename)

            # Download
            success, msg = download_pdf(pdf_url, filepath)
            if success:
                downloaded.append(
                    {
                        "id": paper_id,
                        "title": title,
                        "status": "success",
                        "pdf_path": os.path.abspath(filepath),
                        "size_bytes": os.path.getsize(filepath),
                        "url": pdf_url,
                    }
                )
            else:
                failed.append({"id": paper_id, "title": title, "error": f"{msg}"})
        except Exception as e:
            failed.append({"id": paper_id, "title": title, "error": f"{str(e)}"})

    return {
        "ok": True,
        "command": "download",
        "downloaded": downloaded,
        "failed": failed,
        "total": len(papers),
        "successful": len(downloaded),
        "download_dir": os.path.abspath(download_dir),
    }


def handle_analyze(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle analyze command."""
    pdf_path = input_data.get("pdf") or input_data.get("pdf_path")
    directory = input_data.get("directory") or input_data.get("dir")
    output_dir = input_data.get("output", "./analysis")
    max_pages = int(input_data.get("max_pages", 20))

    if not pdf_path and not directory:
        return {"ok": False, "error": "Either pdf or directory must be provided"}
    if pdf_path and directory:
        return {"ok": False, "error": "Cannot specify both pdf and directory"}

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    analyzed = []

    if pdf_path:
        # Analyze single PDF
        result = analyze_single_pdf(pdf_path, output_dir)
        analyzed.append(result)
    else:
        # Analyze directory
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]

        for i, filename in enumerate(pdf_files, 1):
            print(f"Analyzing {i}/{len(pdf_files)}: {filename}", file=sys.stderr)
            pdf_file = os.path.join(directory, filename)
            result = analyze_single_pdf(pdf_file, output_dir)
            analyzed.append(result)

            # Small delay between files to avoid rate limiting
            if i < len(pdf_files):
                time.sleep(1)

    successful = sum(1 for a in analyzed if a.get("status") == "success")

    return {
        "ok": True,
        "command": "analyze",
        "analyzed": analyzed,
        "summary": {
            "total": len(analyzed),
            "successful": successful,
            "failed": len(analyzed) - successful,
        },
    }


def handle_save(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle save command."""
    ids = input_data.get("ids", [])
    from_file = input_data.get("from-file") or input_data.get("from_file")
    collection = input_data.get("collection")

    if not collection:
        return {"ok": False, "error": "Missing required parameter: collection"}

    # Load papers data
    papers = []
    if from_file:
        try:
            with open(from_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Handle different file structures
                if isinstance(data, list):
                    papers = data
                elif isinstance(data, dict):
                    if "results" in data:
                        papers = data["results"]
                    elif "analyzed" in data:
                        papers = [a.get("metadata", {}) for a in data["analyzed"]]
        except Exception as e:
            return {"ok": False, "error": f"Failed to load from file: {str(e)}"}
    else:
        return {"ok": False, "error": "from-file parameter required"}

    # Filter by IDs if specified
    if ids:
        papers = [
            p
            for p in papers
            if p.get("id") in ids or any(str(i) == str(p.get("id")) for i in ids)
        ]

    # Get Zotero config
    try:
        api_key, prefix = get_zotero_config()
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    # Get or create collection
    try:
        collection_key = get_or_create_collection(api_key, prefix, collection)
    except Exception as e:
        return {"ok": False, "error": f"Failed to access collection: {str(e)}"}

    # Save papers to Zotero
    saved_items = []
    failed_items = []

    for paper in papers:
        try:
            zotero_key = add_item_to_zotero(api_key, prefix, paper, collection_key)
            saved_items.append(
                {
                    "id": paper.get("id", "unknown"),
                    "title": paper.get("title", "Untitled"),
                    "zotero_key": zotero_key,
                    "url": f"https://www.zotero.org/items/{zotero_key}",
                    "status": "success",
                }
            )
        except Exception as e:
            failed_items.append(
                {
                    "id": paper.get("id", "unknown"),
                    "title": paper.get("title", "Untitled"),
                    "error": str(e),
                }
            )

    return {
        "ok": True,
        "command": "save",
        "collection": collection,
        "saved_items": saved_items,
        "failed_items": failed_items,
        "total": len(papers),
        "successful": len(saved_items),
        "zotero_collection": collection_key,
    }


# ============ Main Handler ============


def handle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main command handler."""
    if not input_data or "command" not in input_data:
        return {"ok": False, "error": "Missing command"}

    cmd = input_data["command"]

    handlers = {
        "search": handle_search,
        "download": handle_download,
        "analyze": handle_analyze,
        "save": handle_save,
    }

    if cmd not in handlers:
        return {"ok": False, "error": f"Unknown command: {cmd}"}

    try:
        return handlers[cmd](input_data)
    except Exception as e:
        return {
            "ok": False,
            "command": cmd,
            "error": str(e),
            "error_code": "INTERNAL_ERROR",
        }


def main():
    """Entry point - reads JSON from stdin and outputs JSON to stdout."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"Invalid JSON input: {str(e)}"}))
        sys.exit(1)
    except Exception:
        data = {}

    result = handle(data)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
