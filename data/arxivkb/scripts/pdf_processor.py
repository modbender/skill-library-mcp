"""
pdf_processor.py — PDF text extraction and chunking for ArXivKB.

Uses pdfplumber for text extraction. Chunks text with configurable
token size and overlap using tiktoken for accurate token counting.
"""

import re
from typing import Optional

import pdfplumber
import tiktoken


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

_enc = None


def _get_encoder() -> tiktoken.Encoding:
    global _enc
    if _enc is None:
        _enc = tiktoken.get_encoding("cl100k_base")
    return _enc


def count_tokens(text: str) -> int:
    return len(_get_encoder().encode(text))


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

_SECTION_PATTERNS = [
    (r"^\s*abstract\s*$", "Abstract"),
    (r"^\s*\d*\.?\s*introduction\s*$", "Introduction"),
    (r"^\s*\d*\.?\s*related\s+work\s*$", "Related Work"),
    (r"^\s*\d*\.?\s*background\s*$", "Background"),
    (r"^\s*\d*\.?\s*method(?:s|ology)?\s*$", "Method"),
    (r"^\s*\d*\.?\s*(?:our\s+)?approach\s*$", "Method"),
    (r"^\s*\d*\.?\s*(?:proposed\s+)?(?:model|system|architecture|framework)\s*$", "Method"),
    (r"^\s*\d*\.?\s*experiment(?:s|al)?\s*(?:setup|results?)?\s*$", "Experiments"),
    (r"^\s*\d*\.?\s*(?:results?|evaluation)\s*(?:and\s+discussion)?\s*$", "Results"),
    (r"^\s*\d*\.?\s*discussion\s*$", "Discussion"),
    (r"^\s*\d*\.?\s*conclusion(?:s)?\s*$", "Conclusion"),
    (r"^\s*\d*\.?\s*(?:future\s+work|limitations)\s*$", "Conclusion"),
    (r"^\s*references\s*$", "References"),
    (r"^\s*\d*\.?\s*appendix\s*", "Appendix"),
]

_SKIP_SECTIONS = frozenset({"References", "Appendix", "Acknowledgements"})


def _detect_section(line: str) -> Optional[str]:
    stripped = line.strip()
    if len(stripped) < 3 or len(stripped) > 80:
        return None
    low = stripped.lower()
    for pattern, name in _SECTION_PATTERNS:
        if re.match(pattern, low):
            return name
    return None


# ---------------------------------------------------------------------------
# PDF text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF using pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        print(f"[pdf] Error extracting text from {pdf_path}: {e}")
        return ""


def extract_sections(pdf_path: str) -> list[dict]:
    """
    Extract text and split into labelled sections.

    Returns:
        List of {'section': str, 'text': str}
    """
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text.strip():
        return []

    sections: list[dict] = []
    current_section = "Header"
    current_lines: list[str] = []

    for line in full_text.split("\n"):
        detected = _detect_section(line)
        if detected:
            text = "\n".join(current_lines).strip()
            if text:
                sections.append({"section": current_section, "text": text})
            current_section = detected
            current_lines = []
        else:
            current_lines.append(line)

    text = "\n".join(current_lines).strip()
    if text:
        sections.append({"section": current_section, "text": text})

    return sections


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
) -> list[dict]:
    """
    Split text into overlapping token-based chunks.

    Returns:
        List of {'text': str, 'token_count': int, 'chunk_index': int}
    """
    enc = _get_encoder()
    tokens = enc.encode(text)
    if not tokens:
        return []

    step = max(max_tokens - overlap_tokens, 1)
    chunks = []
    idx = 0
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append({
            "text": chunk_text,
            "token_count": len(chunk_tokens),
            "chunk_index": idx,
        })
        idx += 1
        start += step
        if end >= len(tokens):
            break

    return chunks


def process_pdf(
    pdf_path: str,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
) -> list[dict]:
    """
    Full pipeline: extract sections → skip boilerplate → chunk each section.

    Returns:
        List of {'section': str, 'text': str, 'token_count': int, 'chunk_index': int}
    """
    sections = extract_sections(pdf_path)
    if not sections:
        # Fallback: chunk the whole text
        text = extract_text_from_pdf(pdf_path)
        if not text.strip():
            print(f"[pdf] No text extracted from {pdf_path}")
            return []
        sections = [{"section": "Full Text", "text": text}]

    all_chunks: list[dict] = []
    global_idx = 0

    for sec in sections:
        if sec["section"] in _SKIP_SECTIONS:
            continue
        for chunk in chunk_text(sec["text"], max_tokens, overlap_tokens):
            all_chunks.append({
                "section": sec["section"],
                "text": chunk["text"],
                "token_count": chunk["token_count"],
                "chunk_index": global_idx,
            })
            global_idx += 1

    print(f"[pdf] {pdf_path}: {len(sections)} sections → {len(all_chunks)} chunks")
    return all_chunks
