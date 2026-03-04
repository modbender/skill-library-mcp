#!/usr/bin/env python3
"""
🐾 OEE's Second Brain — RAG Knowledge Base
Personal knowledge base with semantic retrieval.
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

# 🐾
DB_PATH = Path(__file__).parent / "kb.db"
EMBED_MODEL = os.environ.get("KB_EMBED_MODEL", "text-embedding-3-small")
EMBED_DIM = 1536
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
MIN_CHUNK_LEN = 100
MAX_CONTENT = 200_000
BATCH_SIZE = 10
BATCH_DELAY = 0.2
EMBED_RETRIES = 3

ERROR_SIGNALS = [
    "access denied", "captcha", "cloudflare", "just a moment",
    "enable javascript", "please verify", "403 forbidden", "401 unauthorized",
    "robot", "blocked", "rate limit",
]


# ── Database ──────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            source_type TEXT,
            summary TEXT,
            raw_content TEXT,
            content_hash TEXT UNIQUE,
            tags TEXT DEFAULT '[]',
            created_at REAL DEFAULT (unixepoch('now'))
        );
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            chunk_index INTEGER,
            content TEXT,
            embedding BLOB,
            created_at REAL DEFAULT (unixepoch('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_content_hash ON sources(content_hash);
    """)
    return db


# ── URL Normalization & Dedup ─────────────────────────────────────────

def normalize_url(url: str) -> str:
    """Strip tracking params, normalize twitter domains."""  # 🐾
    url = url.strip()
    url = re.sub(r'^https?://(www\.)?twitter\.com/', 'https://x.com/', url)
    url = re.sub(r'^https?://(www\.)?x\.com/', 'https://x.com/', url)
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    clean = {k: v for k, v in params.items() if not k.startswith("utm_") and k not in ("ref", "fbclid", "gclid", "s", "t")}
    new_query = urllib.parse.urlencode(clean, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_query, fragment=""))


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def is_duplicate(db: sqlite3.Connection, chash: str) -> bool:
    return db.execute("SELECT 1 FROM sources WHERE content_hash=?", (chash,)).fetchone() is not None


# ── Content Extraction ────────────────────────────────────────────────

def classify_url(url: str) -> str:
    if re.search(r'(x\.com|twitter\.com)/\w+/status/', url):
        return "tweet"
    if re.search(r'(youtube\.com/watch|youtu\.be/)', url):
        return "youtube"
    if url.lower().endswith(".pdf"):
        return "pdf"
    return "article"


def _api_get(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OEEBot/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def _retry(fn, retries=1, delay=2):
    for i in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            if i == retries:
                raise
            time.sleep(delay)


def extract_tweet(url: str) -> tuple[str, str]:
    """Extract tweet via FxTwitter API → web fetch fallback."""  # 🐾
    norm = normalize_url(url)
    match = re.search(r'x\.com/(\w+)/status/(\d+)', norm)
    if not match:
        raise ValueError(f"Not a valid tweet URL: {url}")
    user, tweet_id = match.groups()
    api_url = f"https://api.fxtwitter.com/{user}/status/{tweet_id}"
    try:
        data = json.loads(_retry(lambda: _api_get(api_url)))
        tweet = data.get("tweet", {})
        text = tweet.get("text", "")
        author = tweet.get("author", {}).get("name", user)
        title = f"@{user}: {text[:80]}..."
        return title, f"Tweet by {author} (@{user}):\n\n{text}"
    except Exception:
        raw = _retry(lambda: _api_get(f"https://api.fxtwitter.com/{user}/status/{tweet_id}"))
        return f"Tweet by @{user}", raw


def extract_youtube(url: str) -> tuple[str, str]:
    """Extract YouTube transcript via yt-dlp."""  # 🐾
    try:
        title_out = subprocess.run(
            ["yt-dlp", "--get-title", url],
            capture_output=True, text=True, timeout=30
        )
        title = title_out.stdout.strip() or "YouTube Video"
    except Exception:
        title = "YouTube Video"

    result = subprocess.run(
        ["yt-dlp", "--write-auto-sub", "--sub-lang", "en", "--skip-download",
         "--sub-format", "vtt", "-o", "/tmp/kb_yt_%(id)s", url],
        capture_output=True, text=True, timeout=60
    )

    vid_id = re.search(r'[?&]v=([^&]+)', url) or re.search(r'youtu\.be/([^?]+)', url)
    vid_id = vid_id.group(1) if vid_id else ""

    vtt_path = None
    for ext in [".en.vtt", ".vtt"]:
        p = Path(f"/tmp/kb_yt_{vid_id}{ext}")
        if p.exists():
            vtt_path = p
            break

    if not vtt_path:
        import glob
        matches = glob.glob(f"/tmp/kb_yt_{vid_id}*.vtt")
        if matches:
            vtt_path = Path(matches[0])

    if not vtt_path:
        raise RuntimeError(f"No transcript found for {url}. yt-dlp stderr: {result.stderr[:500]}")

    raw = vtt_path.read_text()
    lines = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or "-->" in line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:") or re.match(r'^\d+$', line):
            continue
        line = re.sub(r'<[^>]+>', '', line)
        if line and (not lines or line != lines[-1]):
            lines.append(line)
    vtt_path.unlink(missing_ok=True)
    transcript = " ".join(lines)
    return title, transcript


def extract_pdf(url_or_path: str) -> tuple[str, str]:
    """Extract text from PDF."""  # 🐾
    import tempfile
    path = url_or_path
    if url_or_path.startswith("http"):
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        data = urllib.request.urlopen(url_or_path, timeout=30).read()
        tmp.write(data)
        tmp.close()
        path = tmp.name

    try:
        result = subprocess.run(
            ["python3", "-c", f"""
import sys
try:
    import fitz
    doc = fitz.open("{path}")
    for page in doc: print(page.get_text())
except ImportError:
    import subprocess
    r = subprocess.run(["pdftotext", "{path}", "-"], capture_output=True, text=True)
    print(r.stdout)
"""],
            capture_output=True, text=True, timeout=60
        )
        text = result.stdout.strip()
        if not text:
            raise RuntimeError("No text extracted from PDF")
        title = Path(path).stem.replace("_", " ").replace("-", " ").title()
        return title, text
    finally:
        if url_or_path.startswith("http"):
            Path(path).unlink(missing_ok=True)


def extract_article(url: str) -> tuple[str, str]:
    """Extract article content with readability → raw fallback."""  # 🐾
    raw = _retry(lambda: _api_get(url))
    if _is_error_page(raw):
        raise RuntimeError(f"Error page detected for {url}")
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', raw, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else url
    # Strip HTML tags for content
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Decode HTML entities
    import html
    text = html.unescape(text)
    return title, text


def _is_error_page(html_text: str) -> bool:
    lower = html_text.lower()
    return any(sig in lower for sig in ERROR_SIGNALS) and len(html_text) < 5000


def extract_content(url: str) -> tuple[str, str, str]:
    """Returns (title, content, source_type)."""  # 🐾
    source_type = classify_url(url)
    extractors = {
        "tweet": extract_tweet,
        "youtube": extract_youtube,
        "pdf": extract_pdf,
        "article": extract_article,
    }
    title, content = extractors[source_type](url)
    return title, content, source_type


def validate_content(content: str, source_type: str) -> str:
    """Validate and truncate content."""
    if len(content) < 20:
        raise ValueError(f"Content too short ({len(content)} chars)")
    if source_type == "article" and len(content) < 500:
        raise ValueError(f"Article content too short ({len(content)} chars)")
    return content[:MAX_CONTENT]


# ── Chunking ──────────────────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks at sentence boundaries."""  # 🐾
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sent in sentences:
        if len(current) + len(sent) + 1 > CHUNK_SIZE and len(current) >= MIN_CHUNK_LEN:
            chunks.append(current.strip())
            # Overlap: take end of current chunk
            overlap_text = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else current
            current = overlap_text + " " + sent
        else:
            current = (current + " " + sent).strip() if current else sent

    if current.strip() and len(current.strip()) >= MIN_CHUNK_LEN:
        chunks.append(current.strip())
    elif current.strip() and chunks:
        chunks[-1] += " " + current.strip()
    elif current.strip():
        chunks.append(current.strip())

    return chunks


# ── Embeddings ────────────────────────────────────────────────────────

def _openai_embed(texts: list[str]) -> list[list[float]]:
    """Call OpenAI embeddings API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    payload = json.dumps({"input": texts, "model": EMBED_MODEL}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )

    for attempt in range(EMBED_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            return [d["embedding"] for d in sorted(data["data"], key=lambda x: x["index"])]
        except Exception as e:
            if attempt == EMBED_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts in batches."""  # 🐾
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        embs = _openai_embed(batch)
        all_embeddings.extend(embs)
        if i + BATCH_SIZE < len(texts):
            time.sleep(BATCH_DELAY)
    return all_embeddings


def embed_query(text: str) -> list[float]:
    return _openai_embed([text])[0]


def embedding_to_blob(emb: list[float]) -> bytes:
    return struct.pack(f'{len(emb)}f', *emb)


def blob_to_embedding(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f'{n}f', blob))


# ── Similarity ────────────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ── Ingestion ─────────────────────────────────────────────────────────

def ingest(url: str, tags: Optional[list[str]] = None) -> dict:
    """Ingest a URL into the knowledge base. Returns source info."""  # 🐾
    db = get_db()
    norm_url = normalize_url(url)

    print(f"🔍 Extracting content from: {norm_url}")
    title, content, source_type = extract_content(norm_url)
    content = validate_content(content, source_type)

    chash = content_hash(content)
    if is_duplicate(db, chash):
        print("⚡ Content already exists (duplicate hash)")
        row = db.execute("SELECT id, title FROM sources WHERE content_hash=?", (chash,)).fetchone()
        return {"status": "duplicate", "source_id": row["id"], "title": row["title"]}

    print(f"📝 Title: {title}")
    print(f"📄 Type: {source_type} | Length: {len(content)} chars")

    chunks = chunk_text(content)
    print(f"🧩 Chunks: {len(chunks)}")

    print("🧠 Generating embeddings...")
    embeddings = embed_texts(chunks)

    # Generate summary (first 500 chars)
    summary = content[:500].strip() + ("..." if len(content) > 500 else "")

    cur = db.execute(
        "INSERT INTO sources (url, title, source_type, summary, raw_content, content_hash, tags) VALUES (?,?,?,?,?,?,?)",
        (norm_url, title, source_type, summary, content, chash, json.dumps(tags or []))
    )
    source_id = cur.lastrowid

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        db.execute(
            "INSERT INTO chunks (source_id, chunk_index, content, embedding) VALUES (?,?,?,?)",
            (source_id, i, chunk, embedding_to_blob(emb))
        )

    db.commit()
    db.close()
    print(f"✅ Ingested: {title} (id={source_id}, {len(chunks)} chunks)")
    return {"status": "ok", "source_id": source_id, "title": title, "chunks": len(chunks)}


# ── Retrieval ─────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = 10) -> list[dict]:
    """Find most relevant chunks for a query."""  # 🐾
    db = get_db()
    q_emb = embed_query(query)

    rows = db.execute("""
        SELECT c.id, c.source_id, c.content, c.embedding, s.title, s.url, s.source_type
        FROM chunks c JOIN sources s ON c.source_id = s.id
    """).fetchall()

    scored = []
    for row in rows:
        emb = blob_to_embedding(row["embedding"])
        sim = cosine_similarity(q_emb, emb)
        scored.append({
            "chunk_id": row["id"],
            "source_id": row["source_id"],
            "content": row["content"],
            "title": row["title"],
            "url": row["url"],
            "source_type": row["source_type"],
            "similarity": sim,
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)

    # Dedupe by source
    seen_sources = set()
    deduped = []
    for item in scored:
        if item["source_id"] not in seen_sources or len(deduped) < top_k:
            deduped.append(item)
            seen_sources.add(item["source_id"])
        if len(deduped) >= top_k:
            break

    db.close()
    return deduped


def ask(query: str, top_k: int = 10) -> str:
    """Retrieve context and ask LLM to answer."""  # 🐾
    results = retrieve(query, top_k)
    if not results:
        return "No relevant content found in the knowledge base."

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[{i}] {r['title']} ({r['url']})\n{r['content']}")

    context = "\n\n---\n\n".join(context_parts)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    system = "You are a helpful research assistant. Answer using ONLY the provided context. Cite sources using [n] notation. If the context doesn't contain enough information, say so."
    user_msg = f"Context:\n\n{context}\n\n---\n\nQuestion: {query}"

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2048,
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())

    answer = data["content"][0]["text"]

    # Append sources
    sources = []
    seen = set()
    for r in results:
        if r["url"] not in seen:
            sources.append(f"  [{len(sources)+1}] {r['title']} — {r['url']}")
            seen.add(r["url"])

    return f"{answer}\n\nSources:\n" + "\n".join(sources)


# ── Ingest plain text ────────────────────────────────────────────────

def ingest_text(text: str, title: str = "Plain Text", tags: Optional[list[str]] = None) -> dict:
    """Ingest plain text directly."""  # 🐾
    db = get_db()
    content = validate_content(text, "text")
    chash = content_hash(content)

    if is_duplicate(db, chash):
        row = db.execute("SELECT id, title FROM sources WHERE content_hash=?", (chash,)).fetchone()
        return {"status": "duplicate", "source_id": row["id"], "title": row["title"]}

    chunks = chunk_text(content)
    embeddings = embed_texts(chunks)
    summary = content[:500].strip() + ("..." if len(content) > 500 else "")

    cur = db.execute(
        "INSERT INTO sources (url, title, source_type, summary, raw_content, content_hash, tags) VALUES (?,?,?,?,?,?,?)",
        (None, title, "text", summary, content, chash, json.dumps(tags or []))
    )
    source_id = cur.lastrowid

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        db.execute(
            "INSERT INTO chunks (source_id, chunk_index, content, embedding) VALUES (?,?,?,?)",
            (source_id, i, chunk, embedding_to_blob(emb))
        )

    db.commit()
    db.close()
    return {"status": "ok", "source_id": source_id, "title": title, "chunks": len(chunks)}


if __name__ == "__main__":
    print("🐾 OEE's Second Brain — Knowledge Base Library")
    print(f"   DB: {DB_PATH}")
    db = get_db()
    src_count = db.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    chunk_count = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(f"   Sources: {src_count} | Chunks: {chunk_count}")
    db.close()
