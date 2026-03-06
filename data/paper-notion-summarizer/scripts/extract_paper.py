#!/usr/bin/env python3
"""Extract paper metadata and full text by title, DOI, or arXiv URL/ID.

Outputs a structured JSON with metadata, sections, and detected equations.
This script does NOT upload to Notion — use push_to_notion.py for that.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html import unescape
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET
from difflib import SequenceMatcher

import requests

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


SECTION_PATTERNS = [
    (r"^(abstract)\b", "Abstract"),
    (r"^((1\.?\s*)?(introduction|intro)\b)", "Introduction"),
    (r"^((1\.?\s*)?(background|motivation)\b)", "Background"),
    (r"^((2\.?\s*)?(related\s*work|related\s*research|prior\s*work)\b)", "Related Work"),
    (r"^((2\.?\s*)?(preliminaries|preliminary\s*knowledge)\b)", "Preliminaries"),
    (r"^((3\.?\s*)?(method|methods|approach|methodology)\b)", "Method"),
    (r"^((4\.?\s*)?(framework|model|proposed\s*method|proposed\s*model|architecture)\b)", "Method"),
    (r"^((5\.?\s*)?(experimental\s*results|experiments|experiments\s*and\s*analysis|evaluation)\b)", "Experiments"),
    (r"^((6\.?\s*)?(ablation|analysis|case\s*study|study)\b)", "Experiments"),
    (r"^((7\.?\s*)?(discussion|discussion\s*and\s*analysis)\b)", "Discussion"),
    (r"^((8\.?\s*)?(results|conclusion|conclusions|summary)\b)", "Conclusion"),
    (r"^((9\.?\s*)?(limitation|limitations|future\s*work)\b)", "Limitations"),
    (r"^((appendix|supplementary)\b)", "Appendix"),
]

SECTION_ORDER = [
    "Abstract", "Introduction", "Background", "Related Work", "Preliminaries",
    "Method", "Experiments", "Discussion", "Conclusion", "Limitations", "Appendix",
]


@dataclass
class Section:
    title: str
    content: str


@dataclass
class Paper:
    title: str
    authors: str
    year: str
    venue: str
    abstract: str
    doi: str
    url: str
    source: str
    sections: List[Section]
    equations: List[str]
    extra: Dict[str, str]

    def to_dict(self):
        return asdict(self)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_title(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip().lower()


def _title_tokens(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in re.split(r"\s+", text) if t and len(t) > 1]


def _title_match_score(a: str, b: str) -> float:
    at = set(_title_tokens(a))
    bt = set(_title_tokens(b))
    if not at or not bt:
        return 0.0
    overlap = len(at & bt) / max(1, len(at | bt))
    seq = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return round(0.65 * seq + 0.35 * overlap, 4)


def _pick_first(x):
    return x[0] if isinstance(x, list) and x else ""


def _authors_from_arxiv(entry: ET.Element) -> str:
    names = []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for author in entry.findall("a:author", ns):
        name = _pick_first(author.findall("a:name", ns))
        if name is not None and name.text:
            names.append(name.text.strip())
    return ", ".join(names)


# ---------- arXiv ----------

def fetch_from_arxiv(query: str, arxiv_id: Optional[str] = None) -> Optional[Paper]:
    if arxiv_id:
        q = quote_plus(f"id:{arxiv_id}")
        url = f"https://export.arxiv.org/api/query?search_query={q}&start=0&max_results=20"
    else:
        q = quote_plus(query)
        url = f"https://export.arxiv.org/api/query?search_query=all:{q}&start=0&max_results=20"

    r = requests.get(url, headers={"User-Agent": "paper-notion-summarizer/2.0"}, timeout=40)
    if r.status_code != 200:
        return None

    try:
        root = ET.fromstring(r.text)
    except Exception:
        return None

    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    if not entries:
        return None

    selected = None
    if arxiv_id:
        for e in entries:
            entry_id = e.findtext("{http://www.w3.org/2005/Atom}id", "") or ""
            if arxiv_id in entry_id:
                selected = e
                break

    if selected is None:
        best_score = 0.0
        for e in entries:
            title_candidate = e.findtext("{http://www.w3.org/2005/Atom}title", "") or ""
            score = _title_match_score(query, title_candidate)
            if score > best_score:
                best_score = score
                selected = e
        if not selected or best_score < 0.18:
            return None

    entry = selected
    ns = "{http://www.w3.org/2005/Atom}"
    title = entry.findtext(f"{ns}title", "").strip().replace("\n", " ")
    summary = entry.findtext(f"{ns}summary", "").strip().replace("\n", " ")
    published = entry.findtext(f"{ns}published", "")
    year = published[:4] if published else ""

    arxiv_abs_url = entry.findtext(f"{ns}id", "")
    found_pdf = ""
    arxiv_raw_id = ""

    for d in entry.findall(f"{ns}link"):
        href = d.attrib.get("href", "") or ""
        if d.attrib.get("title") == "pdf" or href.endswith(".pdf"):
            found_pdf = href

    m = re.search(r"arxiv\.org/abs/([\w\.\-]+)", arxiv_abs_url)
    if m:
        arxiv_raw_id = m.group(1)

    if not found_pdf and arxiv_raw_id:
        found_pdf = f"https://arxiv.org/pdf/{arxiv_raw_id}.pdf"

    return Paper(
        title=title, authors=_authors_from_arxiv(entry), year=year, venue="arXiv",
        abstract=summary, doi="", url=arxiv_abs_url, source="arXiv",
        sections=[], equations=[],
        extra={"queried_at": _now_iso(), "raw_id": arxiv_raw_id or (arxiv_id or ""), "pdf_url": found_pdf},
    )


# ---------- Crossref ----------

def fetch_from_crossref(query: str, doi: Optional[str] = None) -> Optional[Paper]:
    if doi:
        url = f"https://api.crossref.org/works/{quote_plus(doi)}"
        r = requests.get(url, headers={"User-Agent": "paper-notion-summarizer/2.0"}, timeout=40)
        if r.status_code != 200:
            return None
        items = [r.json().get("message", {})]
    else:
        url = f"https://api.crossref.org/works?query.title={quote_plus(query)}&rows=20"
        r = requests.get(url, headers={"User-Agent": "paper-notion-summarizer/2.0"}, timeout=40)
        if r.status_code != 200:
            return None
        items = r.json().get("message", {}).get("items", [])
        if not items:
            return None

    item = None
    if doi:
        item = items[0]
    else:
        best_score = 0.0
        for candidate in items:
            cand_title = _pick_first(candidate.get("title", [])) or ""
            score = _title_match_score(query, cand_title)
            if score > best_score:
                best_score = score
                item = candidate
        if not item or best_score < 0.22:
            return None

    title = _pick_first(item.get("title", [])) or ""
    if not title:
        return None

    authors = []
    for a in item.get("author", []) or []:
        fam = a.get("family", "")
        given = a.get("given", "")
        if fam or given:
            authors.append((fam + (", " + given) if fam and given else fam or given).strip())

    year = ""
    issued = item.get("issued", {}).get("date-parts", [])
    if issued and isinstance(issued, list) and issued[0]:
        year = str(issued[0][0])

    venue = _pick_first(item.get("container-title", [])) or _pick_first(item.get("publisher", "")) or ""
    abstract = re.sub(r"<[^>]+>", "", item.get("abstract", "") or "")

    pdf_url = ""
    for l in item.get("link", []) or []:
        if l.get("content-type") == "application/pdf" and l.get("URL"):
            pdf_url = l.get("URL")
            break

    return Paper(
        title=title, authors=", ".join(authors), year=year, venue=venue,
        abstract=abstract, doi=item.get("DOI", "") or "", url=item.get("URL", ""),
        source="Crossref", sections=[], equations=[],
        extra={"queried_at": _now_iso(), "type": item.get("type", ""), "pdf_url": pdf_url},
    )


# ---------- Text extraction ----------

def strip_html_to_text(html: str) -> str:
    if not html:
        return ""
    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    html = re.sub(r"(?is)<noscript.*?>.*?</noscript>", " ", html)
    html = re.sub(r"(?i)<br\s*/?>", "\n", html)
    html = re.sub(r"(?i)</(p|div|section|article|li|ul|ol|table|tr|td|th|h[1-6])>", "\n", html)
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = unescape(plain)
    lines = [ln.strip() for ln in plain.splitlines()]
    lines = [ln for ln in lines if ln and len(ln) >= 2 and not re.match(r"^[$&*#_=]{2,}|^[\d\s]*$", ln)]
    return "\n".join(lines)


def filter_redundant_lines(lines: List[str]) -> List[str]:
    out = []
    seen = set()
    for ln in lines:
        compact = re.sub(r"\s+", " ", ln).strip()
        if not compact:
            continue
        if len(compact) > 180 and compact.lower().startswith("javascript"):
            continue
        if compact.lower().startswith("cookie") and "policy" in compact.lower():
            continue
        key = compact.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(compact)
    return out


def fetch_url_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = requests.get(url, headers={"User-Agent": "paper-notion-summarizer/2.0"}, timeout=40)
    except Exception:
        return ""
    if r.status_code != 200 or not r.content:
        return ""
    return r.text or ""


def fetch_pdf_text(pdf_url: str) -> str:
    if not pdf_url or PdfReader is None:
        return ""
    try:
        r = requests.get(pdf_url, headers={"User-Agent": "paper-notion-summarizer/2.0"}, timeout=60, allow_redirects=True)
    except Exception:
        return ""
    if r.status_code != 200 or not r.content:
        return ""
    try:
        reader = PdfReader(BytesIO(r.content))
    except Exception:
        return ""
    pages = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text:
            pages.append(text)
    return "\n".join(pages)


# ---------- Section splitting ----------

def _section_candidate(line: str) -> Optional[str]:
    normalized = re.sub(r"\s+", " ", line.strip()).lower()
    normalized = re.sub(r"^(?:[0-9]+(?:\.[0-9]+)*|[ivxlcdm]+|section|sec\.?)[\s\-\.:)]*", "", normalized, flags=re.I)
    for pattern, canonical in SECTION_PATTERNS:
        if re.search(pattern, normalized, flags=re.I):
            return canonical
    if re.search(r"^acknowledg|acknowledgements|references|notes|appendix|supplementary", normalized, flags=re.I):
        if re.search(r"appendix|supplement", normalized, flags=re.I):
            return "Appendix"
        return "Discussion"
    return None


def split_sections(text: str) -> List[Section]:
    if not text:
        return []
    lines = list(text.splitlines())
    sections: List[Section] = []
    current_title = "Full Text"
    current_lines: List[str] = []

    for line in lines:
        cleaned = re.sub(r"\s+", " ", line.strip()).strip()
        cleaned = re.sub(r"^[=\-*]+|[=\-*]+$", "", cleaned).strip()
        if not cleaned:
            continue
        candidate = _section_candidate(cleaned)
        if candidate:
            if current_lines:
                sections.append(Section(title=current_title, content="\n".join(current_lines).strip()))
                current_lines = []
            current_title = candidate
            continue
        if re.match(r"^fig\.|^figure\s+\d+|^table\s+\d+|^eq\.|^equation\b", cleaned, flags=re.I):
            continue
        if len(cleaned) > 180 and any(tag in cleaned.lower() for tag in ["cookie", "javascript", "analytics", "advertisement"]):
            continue
        current_lines.append(cleaned)

    if current_lines:
        sections.append(Section(title=current_title, content="\n".join(current_lines).strip()))

    # Merge tiny fragments
    merged: List[Section] = []
    for sec in sections:
        if not sec.content or len(sec.content) < 80:
            if merged:
                merged[-1].content += "\n" + sec.title + "\n" + sec.content
            else:
                merged.append(sec)
            continue
        merged.append(sec)

    # De-dup
    deduped: List[Section] = []
    seen = set()
    for sec in merged:
        key = _normalize_title(sec.title)
        if key in seen and deduped:
            deduped[-1].content += "\n" + sec.content
            continue
        seen.add(key)
        deduped.append(sec)
    return deduped


def detect_equations(text: str) -> List[str]:
    if not text:
        return []
    formulas: List[str] = []
    inline = re.findall(r"\$[^\$]{4,220}\$", text)
    block = re.findall(r"\\\[(.*?)\\\]", text, flags=re.S)
    aligned = re.findall(r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}", text, flags=re.S)
    eq_env = re.findall(r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}", text, flags=re.S)
    formulas.extend(inline)
    formulas.extend([f"\\[{x.strip()}\\]" for x in block])
    formulas.extend([x.strip() for x in aligned])
    formulas.extend([x.strip() for x in eq_env])

    candidates = []
    for line in text.splitlines():
        if re.search(r"(\\frac|\\sum|\\int|\\log|\\argmax|\\argmin|\\rightarrow|\\left|\\right|\\infty|\\nabla|\\mathbf|\\alpha|\\beta|\\gamma)", line):
            compact = line.strip()
            if 20 < len(compact) < 500:
                candidates.append(compact)
    formulas.extend(candidates)

    uniq = []
    seen = set()
    for f in formulas:
        norm = re.sub(r"\s+", " ", f).strip()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        uniq.append(norm)
    return uniq[:60]


def load_fulltext(paper: Paper, skip_fulltext: bool) -> Paper:
    if skip_fulltext:
        paper.sections = [Section("Abstract", paper.abstract)]
        paper.equations = detect_equations(paper.abstract)
        return paper

    candidate_text = ""
    source = (paper.extra.get("pdf_url") or "").strip()
    if source:
        candidate_text = fetch_pdf_text(source)

    if not candidate_text and paper.url and "arxiv.org" in paper.url:
        html = fetch_url_text(paper.url)
        plain_html = strip_html_to_text(html)
        candidate_text = "\n".join(filter_redundant_lines(plain_html.splitlines()))

    if not candidate_text and paper.url and "doi.org" in paper.url:
        html = fetch_url_text(paper.url)
        if html:
            plain_html = strip_html_to_text(html)
            candidate_text = "\n".join(filter_redundant_lines(plain_html.splitlines()))

    if candidate_text:
        sections = split_sections(candidate_text)
        if paper.abstract and (not sections or _normalize_title(sections[0].title) != "abstract"):
            sections.insert(0, Section("Abstract", paper.abstract))
        paper.sections = sections
        all_text = "\n".join([s.content for s in sections if s.content])
        paper.equations = detect_equations(all_text)
    else:
        paper.sections = [Section("Abstract", paper.abstract)]
        paper.equations = detect_equations(paper.abstract)
    return paper


# ---------- CLI ----------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract paper metadata and full text to JSON")
    p.add_argument("query", nargs="?", help="Paper title, DOI, or arXiv URL")
    p.add_argument("--title", dest="title_opt", help="Paper title (alternative to positional arg)")
    p.add_argument("--doi", help="Explicit DOI")
    p.add_argument("--arxiv-id", help="Explicit arXiv ID")
    p.add_argument("--skip-fulltext", action="store_true", help="Extract abstract only (skip PDF)")
    p.add_argument("--output", "-o", help="Output file path (default: stdout)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    query = args.title_opt or args.query
    if not query:
        print("Error: provide a paper title, DOI, or arXiv URL")
        return 1

    # Auto-detect arXiv ID from URL
    if not args.arxiv_id and query:
        m = re.search(r"(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|pdf)/([\w\.\-]+)", query)
        if m:
            args.arxiv_id = m.group(1).replace(".pdf", "")

    # Auto-detect DOI
    if not args.doi and query:
        m = re.search(r"10\.\d{4,9}/[^\s]+", query)
        if m:
            args.doi = m.group(0)

    paper = None
    if args.arxiv_id:
        paper = fetch_from_arxiv(query, arxiv_id=args.arxiv_id)
    if not paper and args.doi:
        paper = fetch_from_crossref(query, doi=args.doi)
    if not paper:
        paper = fetch_from_crossref(query)
    if not paper:
        paper = fetch_from_arxiv(query)
    if not paper:
        print("Could not fetch paper metadata.")
        paper = Paper(
            title=query, authors="", year="", venue="", abstract="",
            doi=args.doi or "", url="", source="manual",
            sections=[Section("Abstract", "")], equations=[],
            extra={"note": "failed-to-fetch", "queried_at": _now_iso()},
        )

    paper = load_fulltext(paper, skip_fulltext=args.skip_fulltext)

    output = {
        "title": paper.title, "authors": paper.authors, "year": paper.year,
        "venue": paper.venue, "abstract": paper.abstract, "doi": paper.doi,
        "url": paper.url, "source": paper.source,
        "sections": [{"title": s.title, "content": s.content} for s in paper.sections],
        "equations": paper.equations, "extra": paper.extra,
    }
    json_str = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"Extracted to: {args.output}")
    else:
        print(json_str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
