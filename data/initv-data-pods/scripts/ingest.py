#!/usr/bin/env python3
"""
Data Pods Ingestion v0.2 - Document ingestion with embeddings
Usage: python ingest.py <command> [options]
"""

import sqlite3
import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess

PODS_DIR = Path.home() / ".openclaw" / "data-pods"

# Try importing optional dependencies
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

def ensure_pod(pod_name: str) -> Path:
    """Ensure pod exists."""
    pod_path = PODS_DIR / pod_name
    if not pod_path.exists():
        print(f"Error: Pod '{pod_name}' not found")
        return None
    return pod_path

def init_documents_table(pod_path: Path):
    """Ensure documents table exists."""
    db_path = pod_path / "data.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        file_type TEXT,
        content TEXT,
        file_hash TEXT,
        chunks TEXT,
        embedding BLOB,
        created_at TEXT,
        updated_at TEXT
    )''')
    
    conn.commit()
    conn.close()

def extract_text_from_file(file_path: Path) -> str:
    """Extract text from various file types."""
    content = ""
    ext = file_path.suffix.lower()
    
    try:
        if ext == '.pdf' and PDF_AVAILABLE:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                    
        elif ext in ['.txt', '.md', '.markdown', '.json']:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
        elif ext == '.docx' and DOCX_AVAILABLE:
            doc = Document(file_path)
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp'] and OCR_AVAILABLE:
            image = Image.open(file_path)
            content = pytesseract.image_to_string(image)
            
        else:
            # Try as plain text
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except:
                print(f"  Warning: Cannot extract text from {file_path}")
                return ""
                
    except Exception as e:
        print(f"  Error extracting {file_path}: {e}")
        return ""
    
    return content

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at word boundary
        if end < len(text):
            last_space = text.rfind(' ', start, end)
            if last_space > start:
                end = last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def get_file_hash(file_path: Path) -> str:
    """Get SHA256 hash of file."""
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()[:16]

def generate_embedding(text: str, model_name: str = 'all-MiniLM-L6-v2'):
    """Generate embedding for text."""
    if not EMBEDDINGS_AVAILABLE:
        return None
    
    try:
        model = SentenceTransformer(model_name)
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tobytes()
    except Exception as e:
        print(f"  Error generating embedding: {e}")
        return None

def cosine_similarity(a: bytes, b: bytes) -> float:
    """Calculate cosine similarity between two embeddings."""
    import numpy as np
    a = np.frombuffer(a, dtype=np.float32)
    b = np.frombuffer(b, dtype=np.float32)
    
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot / (norm_a * norm_b))

def ingest_folder(pod_name: str, folder_path: str, recursive: bool = True):
    """Ingest all files from a folder."""
    pod_path = ensure_pod(pod_name)
    if not pod_path:
        return False
    
    init_documents_table(pod_path)
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder}' not found")
        return False
    
    # Find all supported files
    patterns = ['*.pdf', '*.txt', '*.md', '*.markdown', '*.docx', '*.png', '*.jpg', '*.jpeg']
    files = []
    for pattern in patterns:
        if recursive:
            files.extend(folder.rglob(pattern))
        else:
            files.extend(folder.glob(pattern))
    
    print(f"Found {len(files)} files to ingest")
    
    db_path = pod_path / "data.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    ingested = 0
    skipped = 0
    
    for file_path in files:
        print(f"Processing: {file_path.name}")
        
        # Check if already ingested (by hash)
        file_hash = get_file_hash(file_path)
        c.execute("SELECT id FROM documents WHERE file_hash = ?", (file_hash,))
        if c.fetchone():
            print(f"  Skipped (already exists): {file_hash}")
            skipped += 1
            continue
        
        # Extract text
        content = extract_text_from_file(file_path)
        if not content:
            print(f"  Skipped (no content)")
            skipped += 1
            continue
        
        # Chunk text
        chunks = chunk_text(content)
        
        # Generate embedding
        embedding = None
        if EMBEDDINGS_AVAILABLE:
            # Embed first chunk (or combine)
            combined = " | ".join(chunks[:3])  # First 3 chunks
            embedding = generate_embedding(combined)
            print(f"  Embedded: {len(chunks)} chunks")
        else:
            print(f"  No embeddings (sentence-transformers not installed)")
        
        # Store in DB
        now = datetime.now().isoformat()
        c.execute("""INSERT INTO documents 
            (filename, file_type, content, file_hash, chunks, embedding, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (file_path.name, file_path.suffix, content, file_hash, 
             json.dumps(chunks), embedding, now, now))
        
        ingested += 1
        print(f"  Added: {file_path.name}")
    
    conn.commit()
    conn.close()
    
    print(f"\nDone: {ingested} ingested, {skipped} skipped")
    return True

def search_semantic(pod_name: str, query: str, top_k: int = 5):
    """Semantic search across documents."""
    pod_path = ensure_pod(pod_name)
    if not pod_path:
        return
    
    if not EMBEDDINGS_AVAILABLE:
        print("Error: sentence-transformers required for semantic search")
        print("Install with: pip install sentence-transformers")
        return
    
    db_path = pod_path / "data.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get all documents with embeddings
    c.execute("SELECT id, filename, chunks, embedding FROM documents WHERE embedding IS NOT NULL")
    rows = c.fetchall()
    
    if not rows:
        print("No embedded documents found. Run 'ingest' first.")
        return
    
    # Generate query embedding
    query_embedding = generate_embedding(query)
    if not query_embedding:
        return
    
    # Calculate similarities
    results = []
    for row in rows:
        doc_id, filename, chunks_json, embedding = row
        if embedding:
            sim = cosine_similarity(query_embedding, embedding)
            chunks = json.loads(chunks_json) if chunks_json else []
            results.append((sim, filename, chunks[:3]))  # Top 3 chunks
    
    # Sort by similarity
    results.sort(reverse=True, key=lambda x: x[0])
    
    # Display results
    print(f"\nTop {top_k} results for: '{query}'")
    print("=" * 60)
    
    for i, (score, filename, chunks) in enumerate(results[:top_k], 1):
        print(f"\n{i}. {filename} (score: {score:.3f})")
        print("-" * 40)
        for chunk in chunks[:2]:
            print(f"   {chunk[:200]}...")
    
    conn.close()

def list_documents(pod_name: str):
    """List all documents in pod."""
    pod_path = ensure_pod(pod_name)
    if not pod_path:
        return
    
    db_path = pod_path / "data.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT id, filename, file_type, file_hash, created_at FROM documents ORDER BY created_at DESC")
    rows = c.fetchall()
    
    if rows:
        print(f"Documents in '{pod_name}':")
        for row in rows:
            print(f"  [{row[0]}] {row[1]} ({row[2]}) - {row[3]}")
    else:
        print("No documents yet. Run 'ingest' to add documents.")
    
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Data Pods Ingestion v0.2")
    sub = parser.add_subparsers(dest="cmd")
    
    ingest_p = sub.add_parser("ingest", help="Ingest folder of documents")
    ingest_p.add_argument("pod", help="Pod name")
    ingest_p.add_argument("folder", help="Folder path to ingest")
    ingest_p.add_argument("--no-recursive", action="store_true", help="Don't scan subfolders")
    
    search_p = sub.add_parser("search", help="Semantic search")
    search_p.add_argument("pod", help="Pod name")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--top", type=int, default=5, help="Number of results")
    
    list_p = sub.add_parser("list", help="List documents")
    list_p.add_argument("pod", help="Pod name")
    
    sub.add_parser("status", help="Show ingestion status")
    
    args = parser.parse_args()
    
    PODS_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.cmd == "ingest":
        recursive = not args.no_recursive
        ingest_folder(args.pod, args.folder, recursive)
    elif args.cmd == "search":
        search_semantic(args.pod, args.query, args.top)
    elif args.cmd == "list":
        list_documents(args.pod)
    elif args.cmd == "status":
        print("Data Pods Ingestion v0.2")
        print(f"PDF support: {'Yes' if PDF_AVAILABLE else 'No (pip install PyPDF2)'}")
        print(f"DOCX support: {'Yes' if DOCX_AVAILABLE else 'No (pip install python-docx)'}")
        print(f"OCR support: {'Yes' if OCR_AVAILABLE else 'No (pip install pytesseract pillow)'}")
        print(f"Embeddings: {'Yes' if EMBEDDINGS_AVAILABLE else 'No (pip install sentence-transformers)'}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
