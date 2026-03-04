#!/usr/bin/env python3
"""
Brain CMS — Memory Indexer
Embeds all schema files into LanceDB vector store using Ollama nomic-embed-text.
Run after any schema changes to keep vector store current.

Usage: python3 index_memory.py
"""

import os, sys, json, hashlib, requests, datetime
from pathlib import Path
import lancedb, numpy as np, pyarrow as pa

WORKSPACE   = Path(__file__).parent.parent
MEMORY_DIR  = WORKSPACE / "memory"
STORE_DIR   = Path(__file__).parent / "vectorstore"
OLLAMA_URL  = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE  = 400
CHUNK_OVERLAP = 80

# Auto-detect schema files (all .md files in memory/ except daily logs, INDEX, ANCHORS)
def get_schema_files() -> list[str]:
    files = []
    for p in MEMORY_DIR.rglob("*.md"):
        name = p.name
        rel  = str(p.relative_to(MEMORY_DIR))
        # Skip daily logs (YYYY-MM-DD.md) and system files
        if name[0].isdigit() or name in ("INDEX.md",):
            continue
        files.append(rel)
    return sorted(files)

def embed(text: str) -> list[float] | None:
    try:
        r = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
        r.raise_for_status()
        return r.json()["embedding"]
    except Exception as e:
        print(f"[EMBED ERROR] {e}")
        return None

def chunk_text(text: str, source: str) -> list[dict]:
    chunks, current, current_len, section = [], [], 0, "general"
    for line in text.split("\n"):
        if line.startswith("## ") or line.startswith("### "):
            section = line.lstrip("#").strip()
        current.append(line)
        current_len += len(line) + 1
        if current_len >= CHUNK_SIZE:
            ct = "\n".join(current).strip()
            if ct:
                chunks.append({"text": ct, "source": source, "section": section,
                                "chunk_id": hashlib.md5(ct.encode()).hexdigest()[:8]})
            overlap, olen = [], 0
            for l in reversed(current):
                olen += len(l) + 1
                overlap.insert(0, l)
                if olen >= CHUNK_OVERLAP: break
            current, current_len = overlap, olen
    if current:
        ct = "\n".join(current).strip()
        if ct:
            chunks.append({"text": ct, "source": source, "section": section,
                           "chunk_id": hashlib.md5(ct.encode()).hexdigest()[:8]})
    return chunks

def main():
    print("[INDEX] Starting memory indexer...")
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(STORE_DIR))

    schema_files = get_schema_files()
    all_chunks = []
    for rel_path in schema_files:
        fpath = MEMORY_DIR / rel_path
        if not fpath.exists(): continue
        chunks = chunk_text(fpath.read_text(encoding="utf-8"), rel_path)
        print(f"[READ] {rel_path} → {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("[ERROR] No chunks to index.")
        return

    print(f"[EMBED] Embedding {len(all_chunks)} chunks...")
    rows = []
    for i, chunk in enumerate(all_chunks):
        vec = embed(chunk["text"])
        if vec is None: continue
        rows.append({"vector": [float(x) for x in vec], "text": chunk["text"],
                     "source": chunk["source"], "section": chunk["section"],
                     "chunk_id": chunk["chunk_id"],
                     "indexed_at": datetime.datetime.now(datetime.UTC).isoformat()})
        if (i+1) % 10 == 0: print(f"  ... {i+1}/{len(all_chunks)}")

    if not rows: return
    dim = len(rows[0]["vector"])
    schema = pa.schema([pa.field("vector", pa.list_(pa.float32(), dim)),
                        pa.field("text", pa.string()), pa.field("source", pa.string()),
                        pa.field("section", pa.string()), pa.field("chunk_id", pa.string()),
                        pa.field("indexed_at", pa.string())])

    tables = db.list_tables()
    if hasattr(tables, 'tables'): tables = tables.tables
    if "memory_chunks" in tables: db.drop_table("memory_chunks")

    db.create_table("memory_chunks", data=rows, schema=schema)
    print(f"\n[DONE] Indexed {len(rows)} chunks.")

    meta = {"indexed_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "chunk_count": len(rows), "files": schema_files, "model": EMBED_MODEL}
    (Path(__file__).parent / "index_meta.json").write_text(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
