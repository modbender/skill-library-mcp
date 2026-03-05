#!/usr/bin/env python3
"""Bulk embed markdown history files into an OpenClaw-compatible memory SQLite database."""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def chunk_text(text, path, chunk_size=1600, overlap=320, hard_max=6000):
    """Character-based chunking with overlap."""
    lines = text.split('\n')
    chunks = []
    current = []
    current_len = 0
    start_line = 1

    for i, line in enumerate(lines, 1):
        if len(line) > hard_max:
            if current:
                chunks.append({
                    'text': '\n'.join(current)[:hard_max],
                    'start_line': start_line, 'end_line': i - 1, 'path': str(path),
                })
                current, current_len = [], 0
            for pos in range(0, len(line), hard_max - 200):
                chunks.append({
                    'text': line[pos:pos + hard_max - 200],
                    'start_line': i, 'end_line': i, 'path': str(path),
                })
            start_line = i + 1
            continue

        current.append(line)
        current_len += len(line) + 1

        if current_len >= chunk_size:
            chunks.append({
                'text': '\n'.join(current)[:hard_max],
                'start_line': start_line, 'end_line': i, 'path': str(path),
            })
            overlap_lines, overlap_len = [], 0
            for l in reversed(current):
                if overlap_len + len(l) > overlap:
                    break
                overlap_lines.insert(0, l)
                overlap_len += len(l) + 1
            current, current_len = overlap_lines, overlap_len
            start_line = i - len(overlap_lines) + 1

    if current:
        t = '\n'.join(current)
        if t.strip():
            chunks.append({
                'text': t[:hard_max],
                'start_line': start_line, 'end_line': len(lines), 'path': str(path),
            })
    return chunks


def embed_batch(texts, api_key, model):
    """Call OpenAI embeddings API."""
    data = json.dumps({"input": texts, "model": model}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings", data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return [d["embedding"] for d in result["data"]]
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise


def main():
    parser = argparse.ArgumentParser(description='Bulk embed markdown files into OpenClaw memory SQLite')
    parser.add_argument('--history-dir', required=True, help='Directory containing markdown files')
    parser.add_argument('--db', required=True, help='Output SQLite database path')
    parser.add_argument('--api-key', default=None, help='OpenAI API key (default: OPENAI_API_KEY env var)')
    parser.add_argument('--model', default='text-embedding-3-small', help='Embedding model (default: text-embedding-3-small)')
    parser.add_argument('--batch-size', type=int, default=200, help='Texts per API call (default: 200)')
    parser.add_argument('--max-workers', type=int, default=8, help='Parallel API calls (default: 8)')
    parser.add_argument('--chunk-size', type=int, default=1600, help='Characters per chunk (default: 1600)')
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("Error: --api-key or OPENAI_API_KEY env var required", file=sys.stderr)
        sys.exit(1)

    history_dir = Path(args.history_dir)
    md_files = sorted(history_dir.glob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    if not md_files:
        print("No .md files found, exiting.")
        return

    # Chunk
    all_chunks, file_meta = [], []
    for f in md_files:
        text = f.read_text(errors='replace')
        chunks = chunk_text(text, str(f), chunk_size=args.chunk_size)
        all_chunks.extend(chunks)
        stat = f.stat()
        file_meta.append({
            'path': str(f), 'hash': hashlib.sha256(text.encode()).hexdigest()[:16],
            'mtime': int(stat.st_mtime), 'size': stat.st_size,
        })

    print(f"Total chunks: {len(all_chunks)}")

    # Embed
    texts = [c['text'] for c in all_chunks]
    embeddings = [None] * len(texts)
    batches = [(i, texts[i:i + args.batch_size]) for i in range(0, len(texts), args.batch_size)]
    print(f"Sending {len(batches)} API batches ({args.batch_size} texts each, {args.max_workers} parallel)...")

    done, start_time = 0, time.time()
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {executor.submit(embed_batch, bt, api_key, args.model): off for off, bt in batches}
        for future in as_completed(futures):
            offset = futures[future]
            try:
                batch_embs = future.result()
                for j, emb in enumerate(batch_embs):
                    embeddings[offset + j] = emb
                done += 1
                elapsed = time.time() - start_time
                rate = done / elapsed if elapsed > 0 else 0
                eta = (len(batches) - done) / rate if rate > 0 else 0
                print(f"  [{done}/{len(batches)}] {rate:.1f} batches/sec, ETA {eta:.0f}s")
            except Exception as e:
                print(f"  FAILED batch at offset {offset}: {e}")
                sys.exit(1)

    print(f"Embedding done in {time.time() - start_time:.1f}s")

    # Write DB
    db_path = args.db
    if os.path.exists(db_path):
        print(f"Error: output DB already exists at {db_path}", file=sys.stderr)
        print(f"Back it up or remove it manually before running again.", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.execute("""CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY, source TEXT NOT NULL DEFAULT 'memory',
        hash TEXT NOT NULL, mtime INTEGER NOT NULL, size INTEGER NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY, path TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'memory',
        start_line INTEGER NOT NULL, end_line INTEGER NOT NULL,
        hash TEXT NOT NULL, model TEXT NOT NULL, text TEXT NOT NULL,
        embedding TEXT NOT NULL, updated_at INTEGER NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS embedding_cache (
        provider TEXT NOT NULL, model TEXT NOT NULL, provider_key TEXT NOT NULL,
        hash TEXT NOT NULL, embedding TEXT NOT NULL, dims INTEGER,
        created_at INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (provider, model, hash))""")
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
        text, content='chunks', content_rowid='rowid')""")

    print("Writing to SQLite...")
    now = int(time.time() * 1000)

    for fm in file_meta:
        conn.execute("INSERT OR REPLACE INTO files (path, source, hash, mtime, size) VALUES (?,?,?,?,?)",
                     (fm['path'], 'memory', fm['hash'], fm['mtime'], fm['size']))

    for chunk, emb in zip(all_chunks, embeddings):
        chunk_hash = hashlib.sha256(chunk['text'].encode()).hexdigest()[:16]
        chunk_id = f"{chunk['path']}:{chunk['start_line']}-{chunk['end_line']}"
        emb_json = json.dumps(emb)
        conn.execute("""INSERT OR REPLACE INTO chunks
            (id, path, source, start_line, end_line, hash, model, text, embedding, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (chunk_id, chunk['path'], 'memory', chunk['start_line'], chunk['end_line'],
             chunk_hash, f"openai/{args.model}", chunk['text'], emb_json, now))
        conn.execute("""INSERT OR REPLACE INTO embedding_cache
            (provider, model, provider_key, hash, embedding, dims, created_at)
            VALUES (?,?,?,?,?,?,?)""",
            ('openai', args.model, 'redacted', chunk_hash, emb_json, len(emb), now))

    conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                 ('provider', f'openai/{args.model}'))
    conn.commit()

    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    conn.close()

    print(f"\nDone! {total_chunks} chunks from {total_files} files in {db_path}")
    print(f"Database size: {os.path.getsize(db_path) / 1024 / 1024:.1f} MB")
    print(f"\nTo activate in OpenClaw:")
    print(f"  1. openclaw gateway stop")
    print(f"  2. Copy/move {db_path} to ~/.openclaw/memory/main.sqlite")
    print(f"     (or add to memorySearch.extraPaths in config)")
    print(f"  3. openclaw gateway start")


if __name__ == '__main__':
    main()
