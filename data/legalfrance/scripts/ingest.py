#!/usr/bin/env python3
"""
JurisFR — Ingest LEGI dataset from HuggingFace into ChromaDB + SQLite FTS5.
Uses pre-computed BGE-M3 embeddings from AgentPublic/legi.
Memory-efficient: streams dataset, processes in batches.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
SQLITE_PATH = DATA_DIR / "fts_index.db"

# Filter: only keep CODE category articles in force
CATEGORY_FILTER = "CODE"
STATUS_FILTER = "VIGUEUR"


def setup_sqlite(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            chunk_id TEXT PRIMARY KEY,
            doc_id TEXT,
            title TEXT,
            full_title TEXT,
            number TEXT,
            status TEXT,
            category TEXT,
            start_date TEXT,
            end_date TEXT,
            nota TEXT,
            text TEXT,
            chunk_text TEXT
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
            chunk_id,
            title,
            number,
            text,
            chunk_text,
            content='articles',
            content_rowid='rowid'
        )
    """)
    conn.commit()
    return conn


def main():
    from datasets import load_dataset
    import chromadb

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] Loading dataset in streaming mode...")
    ds = load_dataset("AgentPublic/legi", split="train", streaming=True)

    # Setup ChromaDB
    print("[2/4] Setting up indexes...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection("legi_articles")
    except Exception:
        pass
    collection = client.create_collection(
        name="legi_articles",
        metadata={"hnsw:space": "cosine"}
    )

    conn = setup_sqlite(SQLITE_PATH)

    # Stream and filter
    print(f"[3/4] Streaming + indexing (category={CATEGORY_FILTER}, status={STATUS_FILTER})...")
    
    BATCH_SIZE = 200
    batch_ids, batch_docs, batch_embeds, batch_metas, batch_sqlite = [], [], [], [], []
    total = 0
    skipped = 0

    for row in ds:
        # Filter: only CODE + VIGUEUR
        if row.get("category") != CATEGORY_FILTER or row.get("status") != STATUS_FILTER:
            skipped += 1
            if skipped % 50000 == 0:
                print(f"       Skipped {skipped} non-code rows, indexed {total}...", flush=True)
            continue

        chunk_id = row["chunk_id"]
        
        batch_ids.append(chunk_id)
        batch_docs.append(row["chunk_text"] or "")
        raw_emb = row["embeddings_bge-m3"]
        batch_embeds.append(json.loads(raw_emb) if isinstance(raw_emb, str) else raw_emb)
        batch_metas.append({
            "doc_id": row.get("doc_id") or "",
            "title": row.get("title") or "",
            "number": row.get("number") or "",
            "status": row.get("status") or "",
            "category": row.get("category") or "",
            "start_date": row.get("start_date") or "",
        })
        batch_sqlite.append({
            "chunk_id": chunk_id,
            "doc_id": row.get("doc_id") or "",
            "title": row.get("title") or "",
            "full_title": row.get("full_title") or "",
            "number": row.get("number") or "",
            "status": row.get("status") or "",
            "category": row.get("category") or "",
            "start_date": row.get("start_date") or "",
            "end_date": row.get("end_date") or "",
            "nota": row.get("nota") or "",
            "text": row.get("text") or "",
            "chunk_text": row.get("chunk_text") or "",
        })

        if len(batch_ids) >= BATCH_SIZE:
            # Deduplicate within batch
            seen = set()
            dedup = [(i, d, e, m, s) for i, d, e, m, s in zip(batch_ids, batch_docs, batch_embeds, batch_metas, batch_sqlite) if i not in seen and not seen.add(i)]
            batch_ids = [x[0] for x in dedup]
            batch_docs = [x[1] for x in dedup]
            batch_embeds = [x[2] for x in dedup]
            batch_metas = [x[3] for x in dedup]
            batch_sqlite = [x[4] for x in dedup]
            
            collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                embeddings=batch_embeds,
                metadatas=batch_metas
            )
            conn.executemany("""
                INSERT OR REPLACE INTO articles 
                (chunk_id, doc_id, title, full_title, number, status, category, start_date, end_date, nota, text, chunk_text)
                VALUES (:chunk_id, :doc_id, :title, :full_title, :number, :status, :category, :start_date, :end_date, :nota, :text, :chunk_text)
            """, batch_sqlite)
            conn.commit()
            
            total += len(batch_ids)
            batch_ids, batch_docs, batch_embeds, batch_metas, batch_sqlite = [], [], [], [], []
            print(f"       Indexed {total} code articles...", flush=True)

    # Flush remaining
    if batch_ids:
        seen = set()
        dedup = [(i, d, e, m, s) for i, d, e, m, s in zip(batch_ids, batch_docs, batch_embeds, batch_metas, batch_sqlite) if i not in seen and not seen.add(i)]
        batch_ids = [x[0] for x in dedup]
        batch_docs = [x[1] for x in dedup]
        batch_embeds = [x[2] for x in dedup]
        batch_metas = [x[3] for x in dedup]
        batch_sqlite = [x[4] for x in dedup]
        collection.upsert(ids=batch_ids, documents=batch_docs, embeddings=batch_embeds, metadatas=batch_metas)
        conn.executemany("""
            INSERT OR REPLACE INTO articles 
            (chunk_id, doc_id, title, full_title, number, status, category, start_date, end_date, nota, text, chunk_text)
            VALUES (:chunk_id, :doc_id, :title, :full_title, :number, :status, :category, :start_date, :end_date, :nota, :text, :chunk_text)
        """, batch_sqlite)
        conn.commit()
        total += len(batch_ids)

    # Build FTS index
    print("       Building FTS index...")
    conn.execute("INSERT INTO articles_fts(articles_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()

    print(f"\n[4/4] Done!")
    print(f"       ChromaDB: {CHROMA_DIR}")
    print(f"       SQLite:   {SQLITE_PATH}")
    print(f"       Code articles indexed: {total}")
    print(f"       Non-code rows skipped: {skipped}")


if __name__ == "__main__":
    main()
