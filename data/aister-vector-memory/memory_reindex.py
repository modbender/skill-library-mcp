#!/usr/bin/env python3
"""Memory Reindex - Reindex memory files into vector database."""

import os
import sys
import json
import argparse
import hashlib
import psycopg2
from pathlib import Path
from typing import Optional
import requests

DB_HOST = os.environ.get("VECTOR_MEMORY_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("VECTOR_MEMORY_DB_PORT", "5432"))
DB_NAME = os.environ.get("VECTOR_MEMORY_DB_NAME", "vector_memory")
DB_USER = os.environ.get("VECTOR_MEMORY_DB_USER", "aister")
DB_PASSWORD = os.environ.get("VECTOR_MEMORY_DB_PASSWORD", "")

EMBEDDING_SERVICE_URL = os.environ.get("EMBEDDING_SERVICE_URL", "http://127.0.0.1:8765")

DEFAULT_MEMORY_DIR = os.environ.get("VECTOR_MEMORY_DIR", os.path.expanduser("~/.openclaw/workspace/memory"))
DEFAULT_CHUNK_SIZE = int(os.environ.get("VECTOR_MEMORY_CHUNK_SIZE", "500"))

MEMORY_FILES = ["MEMORY.md", "IDENTITY.md", "USER.md"]


def get_embeddings(texts: list) -> Optional[list]:
    """Get embeddings from the embedding service."""
    try:
        response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed",
            json={"texts": texts, "prefix": "passage: "},
            timeout=120
        )
        response.raise_for_status()
        return response.json()["embeddings"]
    except Exception as e:
        print(f"Error getting embeddings: {e}", file=sys.stderr)
        return None


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> list:
    """Split text into chunks."""
    chunks = []
    paragraphs = text.split("\n\n")

    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def get_file_checksum(file_path: str) -> str:
    """Calculate MD5 checksum of a file."""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def is_file_indexed(cur, file_path: str, checksum: str) -> bool:
    """Check if file is already indexed with same checksum."""
    cur.execute(
        "SELECT checksum FROM indexed_files WHERE file_path = %s",
        (file_path,)
    )
    result = cur.fetchone()
    return result is not None and result[0] == checksum


def reindex_memory(memory_dir: str = DEFAULT_MEMORY_DIR, force: bool = False):
    """Reindex all memory files."""
    memory_path = Path(memory_dir)
    if not memory_path.exists():
        print(f"Memory directory not found: {memory_dir}", file=sys.stderr)
        return False

    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False
        cur = conn.cursor()

        total_chunks = 0
        total_files = 0

        for memory_file in MEMORY_FILES:
            file_path = memory_path / memory_file
            if not file_path.exists():
                print(f"Skipping {memory_file} (not found)")
                continue

            checksum = get_file_checksum(str(file_path))

            if not force and is_file_indexed(cur, str(file_path), checksum):
                print(f"Skipping {memory_file} (already indexed)")
                continue

            print(f"Indexing {memory_file}...")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunk_text(content)
            if not chunks:
                continue

            print(f"  Generating embeddings for {len(chunks)} chunks...")

            embeddings = get_embeddings(chunks)
            if not embeddings:
                print(f"  Failed to get embeddings for {memory_file}", file=sys.stderr)
                continue

            cur.execute(
                "DELETE FROM memories WHERE source = %s",
                (memory_file,)
            )

            for chunk, embedding in zip(chunks, embeddings):
                cur.execute("""
                    INSERT INTO memories (content, embedding, metadata, source)
                    VALUES (%s, %s::vector, %s, %s)
                """, (chunk, str(embedding), json.dumps({"file": memory_file}), memory_file))

            cur.execute("""
                INSERT INTO indexed_files (file_path, checksum, last_indexed)
                VALUES (%s, %s, NOW())
                ON CONFLICT (file_path) 
                DO UPDATE SET checksum = EXCLUDED.checksum, last_indexed = NOW()
            """, (str(file_path), checksum))

            conn.commit()
            total_chunks += len(chunks)
            total_files += 1
            print(f"  Indexed {len(chunks)} chunks from {memory_file}")

        cur.execute("SELECT COUNT(*) FROM memories")
        result = cur.fetchone()
        total_memories = result[0] if result else 0

        cur.close()

        print(f"\nReindex complete:")
        print(f"  Files processed: {total_files}")
        print(f"  Chunks indexed: {total_chunks}")
        print(f"  Total memories in DB: {total_memories}")

        return True

    except psycopg2.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Reindex memory files into vector database")
    parser.add_argument("-d", "--dir", default=DEFAULT_MEMORY_DIR, help=f"Memory directory (default: {DEFAULT_MEMORY_DIR})")
    parser.add_argument("-f", "--force", action="store_true", help="Force reindex even if files unchanged")

    args = parser.parse_args()

    success = reindex_memory(args.dir, args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
