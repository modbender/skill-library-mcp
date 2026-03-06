"""
search.py — Semantic search for ArXivKB.

Embeds query → FAISS search on chunks → group by paper → return ranked papers.
"""

from embed import embed_query, DIM
from faiss_index import FaissIndex


def search(query: str, db_path: str, data_dir: str, top_k: int = 10) -> list[dict]:
    """Semantic search over paper chunks. Returns papers ranked by best chunk score."""
    import sqlite3

    q_vec = embed_query(query)

    index = FaissIndex(data_dir, dim=DIM)
    index.load()

    if index.size == 0:
        return []

    # Search more chunks than needed, then deduplicate by paper
    results = index.search(q_vec, top_k=top_k * 5)
    if not results:
        return []

    faiss_ids = [r[0] for r in results]
    scores = {r[0]: r[1] for r in results}

    # Look up chunks → papers
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    placeholders = ",".join("?" * len(faiss_ids))
    rows = conn.execute(
        f"""SELECT c.faiss_id, p.arxiv_id, p.title, p.published
            FROM chunks c JOIN papers p ON c.paper_id = p.id
            WHERE c.faiss_id IN ({placeholders})""",
        faiss_ids,
    ).fetchall()
    conn.close()

    # Best score per paper
    paper_scores: dict[str, dict] = {}
    for r in rows:
        aid = r["arxiv_id"]
        score = scores.get(r["faiss_id"], 0)
        if aid not in paper_scores or score > paper_scores[aid]["score"]:
            paper_scores[aid] = {
                "arxiv_id": aid,
                "title": r["title"],
                "published": r["published"],
                "score": round(score, 4),
            }

    papers = sorted(paper_scores.values(), key=lambda x: x["score"], reverse=True)
    return papers[:top_k]
