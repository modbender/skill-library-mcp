#!/usr/bin/env python3
"""
JurisFR — Hybrid search (vector + BM25) with RRF fusion.
Callable as module or CLI.
"""

import sqlite3
import json
import sys
import re
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
SQLITE_PATH = DATA_DIR / "fts_index.db"


ANCHOR_MAP = [
    # Code civil
    ("responsabilité civile délictuelle", "Code civil", ["1240", "1241"]),
    ("responsabilité délictuelle", "Code civil", ["1240", "1241"]),
    ("responsabilité civile", "Code civil", ["1240", "1241"]),
    ("parent responsable", "Code civil", ["1242"]),
    ("mineur", "Code civil", ["1242"]),
    ("validité d'un contrat", "Code civil", ["1128"]),
    ("conditions de validité", "Code civil", ["1128"]),
    ("force majeure", "Code civil", ["1218"]),
    ("vice du consentement", "Code civil", ["1130", "1131", "1132", "1137", "1140"]),
    ("droit de propriété", "Code civil", ["544"]),
    ("propriétaire", "Code civil", ["544"]),
    ("voisin", "Code civil", ["544"]),
    ("bruit", "Code civil", ["544"]),
    ("prescription", "Code civil", ["2224"]),
    ("enrichissement injustifié", "Code civil", ["1303"]),
    ("vices cachés", "Code civil", ["1641", "1644"]),
    ("produit défectueux", "Code civil", ["1641", "1644"]),
    ("recours", "Code civil", ["1641", "1644"]),
    ("se marier", "Code civil", ["144", "146"]),
    ("conditions pour se marier", "Code civil", ["144", "146"]),
    ("régimes matrimoniaux", "Code civil", ["1393", "1400"]),
    ("héritiers", "Code civil", ["734", "735"]),
    # Code de commerce
    ("fonds de commerce", "Code de commerce", ["L141-5"]),
    ("elements le composent", "Code de commerce", ["L141-5"]),
    ("capital social minimum", "Code de commerce", ["L223-2"]),
    ("capital social", "Code de commerce", ["L223-2"]),
    ("bailleur", "Code civil", ["1719", "1720"]),
    ("obligations du bailleur", "Code civil", ["1719", "1720"]),
    ("entreprise seul", "Code de commerce", ["L223-1"]),
    ("créer une entreprise seul", "Code de commerce", ["L223-1"]),
    ("sarl", "Code de commerce", ["L223-1", "L223-2", "L223-18", "L223-22"]),
    ("redressement judiciaire", "Code de commerce", ["L631-1"]),
]


def _extract_article_numbers(q: str) -> list[str]:
    # Matches L223-2, R631-1, D223-2, etc.
    out = re.findall(r"\b([LRD]\d{1,4}-\d{1,3})\b", q, flags=re.IGNORECASE)
    # Matches simple article numbers like 1240, 1128, 544
    out += re.findall(r"\b(\d{3,4})\b", q)
    # Normalize
    norm = []
    for x in out:
        x = x.upper()
        norm.append(x)
    # unique, keep order
    seen = set()
    res = []
    for x in norm:
        if x not in seen:
            seen.add(x)
            res.append(x)
    return res


def _plan_fts_query(user_query: str) -> tuple[str, str | None, list[str]]:
    """Return (fts_match_string, preferred_title, anchor_numbers)."""
    q = (user_query or "").lower()
    preferred_title = None
    anchors: list[str] = []

    for key, title, nums in ANCHOR_MAP:
        if key in q:
            preferred_title = preferred_title or title
            anchors.extend(nums)

    anchors.extend(_extract_article_numbers(user_query or ""))

    # Dedup anchors
    seen = set()
    anchors2 = []
    for a in anchors:
        if a and a not in seen:
            seen.add(a)
            anchors2.append(a)
    anchors = anchors2

    must = []
    should = []

    def norm_token(s: str) -> str:
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
        return s.lower()

    if preferred_title:
        # FTS5 column filter doesn't like quoted phrases with spaces; use token conjunction.
        raw_title_tokens = [norm_token(t) for t in re.findall(r"[\wÀ-ÿ]+", preferred_title) if t]
        title_stop = {"de", "du", "des", "la", "le", "les", "d"}
        title_tokens = [t for t in raw_title_tokens if len(t) >= 3 and t not in title_stop]
        if title_tokens:
            must.append(" AND ".join([f'title:{t}' for t in title_tokens]))

    def fts_number_expr(a: str) -> str:
        a = (a or "").upper()
        if "-" in a:
            parts = [norm_token(p) for p in a.split("-") if p]
            # number column is tokenized, so use token conjunction
            return "(" + " AND ".join([f"number:{p}" for p in parts]) + ")"
        return f'number:"{a}"'

    if anchors:
        num_clause = " OR ".join([fts_number_expr(a) for a in anchors[:8]])
        should.append(f'({num_clause})')

    tokens = re.findall(r"[\wÀ-ÿ]+", user_query or "")
    tokens = [norm_token(t) for t in tokens if len(t) >= 3]
    stop = {"quels", "quelles", "comment", "dans", "pour", "avec", "sans", "sont", "est", "une", "des", "les", "que", "quoi", "droit", "france"}
    tokens = [t for t in tokens if t not in stop]
    if tokens:
        tok_clause = " OR ".join([f'chunk_text:{t}' for t in tokens[:10]])
        should.append(f'({tok_clause})')

    if should:
        should_expr = " OR ".join(should)
        if must:
            match = " AND ".join(must) + " AND (" + should_expr + ")"
        else:
            match = should_expr
    else:
        match = '"' + (user_query or "").replace('"', ' ') + '"'

    return match, preferred_title, anchors


def bm25_search(query: str, top_k: int = 10) -> list[dict]:
    """Search using SQLite FTS5 (keyword/exact match)."""
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row

    match, _preferred, anchors = _plan_fts_query(query)

    rows = conn.execute("""
        SELECT a.chunk_id, a.title, a.number, a.text, a.chunk_text, a.full_title,
               a.category, a.start_date, a.status,
               rank AS score
        FROM articles_fts f
        JOIN articles a ON a.rowid = f.rowid
        WHERE articles_fts MATCH ?
        ORDER BY rank
        LIMIT ?
    """, (match, top_k * 5)).fetchall()

    conn.close()
    results = [dict(r) for r in rows]

    # Re-rank: exact anchor numbers first (huge precision boost)
    if anchors:
        anchor_set = set(a.lower() for a in anchors)
        results.sort(key=lambda r: (str(r.get('number','')).lower() not in anchor_set, r.get('score', 0)))

    return results[:top_k]


def vector_search(query: str, top_k: int = 10, where: dict = None) -> list[dict]:
    """Search using ChromaDB (semantic similarity)."""
    import chromadb
    
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection("legi_articles")
    
    # Embed query with the SAME model used by the dataset (BGE-M3, dim=1024).
    # No text-fallback here: Chroma's default embedder is not compatible with the stored vectors.
    from sentence_transformers import SentenceTransformer

    # Cache model at module level
    global _BGE_M3
    try:
        _BGE_M3
    except NameError:
        _BGE_M3 = SentenceTransformer("BAAI/bge-m3")

    query_embedding = _BGE_M3.encode(query).tolist()

    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"]
    }
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    
    out = []
    if results and results["ids"]:
        for i, chunk_id in enumerate(results["ids"][0]):
            out.append({
                "chunk_id": chunk_id,
                "chunk_text": results["documents"][0][i] if results["documents"] else "",
                "score": 1.0 - (results["distances"][0][i] if results["distances"] else 0),
                **(results["metadatas"][0][i] if results["metadatas"] else {})
            })
    return out


def rrf_fusion(results_lists: list[list[dict]], k: int = 60) -> list[dict]:
    """Reciprocal Rank Fusion to merge multiple result lists."""
    scores = {}
    docs = {}
    
    for results in results_lists:
        for rank, doc in enumerate(results):
            doc_id = doc["chunk_id"]
            if doc_id not in scores:
                scores[doc_id] = 0
                docs[doc_id] = doc
            scores[doc_id] += 1.0 / (k + rank + 1)
    
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [{"rrf_score": scores[did], **docs[did]} for did in sorted_ids]


def hybrid_search(query: str, top_k: int = 5, where: dict = None) -> list[dict]:
    """Combined BM25 + vector search with RRF fusion + code preference boosting."""
    _match, preferred, anchors = _plan_fts_query(query)

    bm25_results = bm25_search(query, top_k=top_k * 8)
    vec_results = vector_search(query, top_k=top_k * 8, where=where)

    fused = rrf_fusion([bm25_results, vec_results])

    anchor_set = set(a.lower() for a in anchors or [])

    # Strong re-ranking: anchors first, then preferred code, then score
    fused.sort(
        key=lambda r: (
            str(r.get("number", "")).lower() not in anchor_set,
            (preferred is not None and r.get("title") != preferred),
            -r.get("rrf_score", 0),
        )
    )

    return fused[:top_k]


def format_results(results: list[dict], verbose: bool = False) -> str:
    """Format search results for LLM consumption."""
    if not results:
        return "Aucun résultat trouvé."
    
    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        number = r.get("number", "")
        ref = f"{title}"
        if number:
            ref += f", art. {number}"
        
        text = r.get("chunk_text", r.get("text", ""))
        if not verbose and len(text) > 800:
            text = text[:800] + "…"
        
        parts.append(f"### Source {i}: [{ref}]\n{text}")
    
    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: search.py <query> [top_k]")
        sys.exit(1)
    
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"Query: {query}\n")
    
    # Try BM25 first (no model needed)
    print("=== BM25 Results ===")
    bm25 = bm25_search(query, top_k)
    print(format_results(bm25))
    
    print("\n\n=== Hybrid Results (BM25 + Vector) ===")
    try:
        hybrid = hybrid_search(query, top_k)
        print(format_results(hybrid))
    except Exception as e:
        print(f"Vector search unavailable: {e}")
        print("Using BM25 only.")
