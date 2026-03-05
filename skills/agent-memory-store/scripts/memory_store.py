"""
Agent Memory Store v3 — SQLite + OpenAI embeddings (text-embedding-3-small) + TTL
Falls back to Jaccard if no OPENAI_API_KEY
"""
import json, os, time, uuid, sqlite3, threading, struct, math, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_FILE = "/root/.openclaw/workspace/data/agent_memory.db"
PORT = 8768
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
_lock = threading.Lock()
_db = None

def get_db():
    global _db
    if _db is None:
        c = sqlite3.connect(DB_FILE, check_same_thread=False)
        c.row_factory = sqlite3.Row
        c.execute("""CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, content TEXT NOT NULL,
            tags TEXT DEFAULT '[]', public INTEGER DEFAULT 0,
            created_at REAL, expires_at REAL
        )""")
        # Migrate: add embedding column if missing
        cols = [r[1] for r in c.execute("PRAGMA table_info(memories)").fetchall()]
        if "embedding" not in cols:
            c.execute("ALTER TABLE memories ADD COLUMN embedding BLOB")
        c.commit()
        _db = c
    return _db

def embed_openai(text):
    if not OPENAI_KEY: return None
    try:
        payload = json.dumps({"input": text[:2000], "model": "text-embedding-3-small"}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings", data=payload,
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            vec = json.loads(r.read())["data"][0]["embedding"]
            return struct.pack(f"{len(vec)}f", *vec)
    except: return None

def cosine(a_bytes, b_bytes):
    if not a_bytes or not b_bytes: return 0
    n = len(a_bytes) // 4
    a = struct.unpack(f"{n}f", a_bytes)
    b = struct.unpack(f"{n}f", b_bytes)
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0

def jaccard(a, b):
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb: return 0
    return len(sa & sb) / len(sa | sb)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
    def _row(self, r):
        d = dict(r); d["tags"] = json.loads(d.get("tags") or "[]")
        d["public"] = bool(d["public"]); d.pop("embedding", None); return d

    def do_GET(self):
        p = urlparse(self.path); qs = parse_qs(p.query); now = time.time()
        db = get_db()
        if p.path == "/health":
            with _lock: cnt = db.execute("SELECT COUNT(*) FROM memories WHERE (expires_at IS NULL OR expires_at>?)",(now,)).fetchone()[0]
            return self._send(200, {"status":"ok","memories":cnt,"db":DB_FILE,"embeddings":bool(OPENAI_KEY)})
        if p.path == "/memories":
            agent = qs.get("agent",[None])[0]; query = qs.get("q",[None])[0]
            limit = int(qs.get("limit",["20"])[0])
            sql = "SELECT * FROM memories WHERE (expires_at IS NULL OR expires_at>?)"
            params = [now]
            if agent: sql += " AND (owner=? OR public=1)"; params.append(agent)
            with _lock: rows_raw = db.execute(sql, params).fetchall()
            pairs = [(self._row(r), bytes(r["embedding"]) if r["embedding"] else None) for r in rows_raw]
            if query:
                qemb = embed_openai(query) if OPENAI_KEY else None
                scored = []
                for d, emb in pairs:
                    s = cosine(qemb, emb) if qemb and emb else jaccard(query, d["content"])
                    scored.append((s, d))
                scored.sort(key=lambda x: -x[0])
                rows = [d for _, d in scored]
            else:
                rows = [d for d, _ in pairs]
            return self._send(200, {"memories": rows[:limit], "total": len(rows)})
        if p.path.startswith("/memories/") and len(p.path.split("/"))==3:
            mid = p.path.split("/")[-1]
            with _lock: row = db.execute("SELECT * FROM memories WHERE id=? AND (expires_at IS NULL OR expires_at>?)",(mid,now)).fetchone()
            if not row: return self._send(404, {"error":"not found"})
            return self._send(200, {"memory": self._row(row)})
        self._send(404, {"error":"not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length",0))
        body = json.loads(self.rfile.read(length) or b"{}")
        p = urlparse(self.path)
        if p.path == "/memories":
            if not body.get("owner") or not body.get("content"):
                return self._send(400, {"error":"required: owner, content"})
            mid = str(uuid.uuid4())[:8]
            ttl = body.get("ttl_seconds")
            emb = embed_openai(body["content"])
            with _lock:
                get_db().execute("INSERT INTO memories VALUES (?,?,?,?,?,?,?,?)",
                    (mid, body["owner"], body["content"],
                     json.dumps(body.get("tags",[])), 1 if body.get("public") else 0,
                     time.time(), time.time()+ttl if ttl else None, emb))
                get_db().commit()
            return self._send(201, {"memory":{"id":mid,"owner":body["owner"],"content":body["content"],
                "tags":body.get("tags",[]),"public":bool(body.get("public")),"embedded":emb is not None}})
        if p.path.startswith("/memories/") and p.path.endswith("/delete"):
            mid = p.path.split("/")[-2]
            with _lock: get_db().execute("DELETE FROM memories WHERE id=?",(mid,)); get_db().commit()
            return self._send(200, {"deleted":mid})
        self._send(404, {"error":"not found"})

if __name__ == "__main__":
    print(f"Agent Memory Store v3 :{PORT} | embeddings={'openai' if OPENAI_KEY else 'jaccard-fallback'} | db={DB_FILE}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
