#!/usr/bin/env -S uv run python
from __future__ import annotations
import argparse, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS analyses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  library_id TEXT,
  title TEXT,
  format TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  lang TEXT,
  summary TEXT,
  highlights_json TEXT,
  reread_json TEXT,
  tags_json TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(book_id, format, file_hash)
);
CREATE INDEX IF NOT EXISTS idx_analyses_book_fmt ON analyses(book_id, format);
CREATE VIRTUAL TABLE IF NOT EXISTS analyses_fts USING fts5(
  title, summary, highlights, reread, content=''
);
"""

def connect(db):
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db)

def init_db(db):
    con = connect(db)
    con.executescript(SCHEMA)
    con.commit(); con.close()

def upsert(db, obj):
    now = datetime.now(timezone.utc).isoformat()
    con = connect(db)
    con.executescript(SCHEMA)
    vals = (
      int(obj['book_id']), obj.get('library_id'), obj.get('title'), obj.get('format','EPUB'), obj.get('file_hash'),
      obj.get('lang','ja'), obj.get('summary',''), json.dumps(obj.get('highlights',[]), ensure_ascii=False),
      json.dumps(obj.get('reread',[]), ensure_ascii=False), json.dumps(obj.get('tags',[]), ensure_ascii=False), now
    )
    con.execute('''INSERT OR IGNORE INTO analyses(book_id,library_id,title,format,file_hash,lang,summary,highlights_json,reread_json,tags_json,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)''', vals)
    row = con.execute('SELECT id,title,summary,highlights_json,reread_json FROM analyses WHERE book_id=? AND format=? AND file_hash=?',
                      (int(obj['book_id']), obj.get('format','EPUB'), obj.get('file_hash'))).fetchone()
    if row:
      con.execute('INSERT INTO analyses_fts(rowid,title,summary,highlights,reread) VALUES(?,?,?,?,?)',
                  (row[0], row[1] or '', row[2] or '', row[3] or '', row[4] or ''))
    con.commit(); con.close()

def status(db, book_id, fmt):
    con=connect(db)
    con.executescript(SCHEMA)
    row=con.execute('SELECT book_id,format,file_hash,created_at FROM analyses WHERE book_id=? AND format=? ORDER BY id DESC LIMIT 1',
                    (book_id, fmt)).fetchone()
    con.close()
    return row

def search(db, q, limit):
    con=connect(db)
    con.executescript(SCHEMA)
    rows=con.execute('''SELECT a.book_id,a.title,a.format,a.file_hash,a.created_at,
                               snippet(analyses_fts,1,'[',']',' … ',12)
                        FROM analyses_fts JOIN analyses a ON a.id=analyses_fts.rowid
                        WHERE analyses_fts MATCH ? ORDER BY rank LIMIT ?''', (q, limit)).fetchall()
    con.close(); return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['init','upsert','status','search'])
    ap.add_argument('--db', required=True)
    ap.add_argument('--book-id', type=int)
    ap.add_argument('--format', default='EPUB')
    ap.add_argument('--query')
    ap.add_argument('--limit', type=int, default=10)
    ns=ap.parse_args()
    if ns.cmd=='init':
      init_db(ns.db); print(json.dumps({'ok':True,'db':ns.db}, ensure_ascii=False)); return
    if ns.cmd=='upsert':
      obj=json.loads(sys.stdin.read()); upsert(ns.db,obj); print(json.dumps({'ok':True,'book_id':obj.get('book_id')}, ensure_ascii=False)); return
    if ns.cmd=='status':
      if ns.book_id is None: raise SystemExit('--book-id required')
      r=status(ns.db, ns.book_id, ns.format)
      print(json.dumps({'ok':True,'status':None if not r else {'book_id':r[0],'format':r[1],'file_hash':r[2],'created_at':r[3]}}, ensure_ascii=False)); return
    if ns.cmd=='search':
      if not ns.query: raise SystemExit('--query required')
      rows=search(ns.db, ns.query, ns.limit)
      print(json.dumps({'ok':True,'items':[{'book_id':r[0],'title':r[1],'format':r[2],'file_hash':r[3],'created_at':r[4],'snippet':r[5]} for r in rows]}, ensure_ascii=False))

if __name__=='__main__':
    main()
