#!/usr/bin/env python3
"""RLM context helper: store, peek, search, chunk with strict bounds.
Usage:
  rlm_ctx.py store --infile <path> --ctx-dir <dir>
  rlm_ctx.py meta  --ctx <file>
  rlm_ctx.py peek  --ctx <file> --offset <int> --length <int>
  rlm_ctx.py search --ctx <file> --pattern <regex>
  rlm_ctx.py chunk --ctx <file> --size <int> --overlap <int>
"""
import argparse, hashlib, json, os, re, signal, sys, time
from rlm_path import validate_path as _validate_path

MAX_SEARCH_RESULTS = 200
MAX_CHUNKS = 5000
MAX_PEEK_LENGTH = 16000
REGEX_TIMEOUT_SECONDS = 5

def _read_text(path):
    rp = _validate_path(path)
    with open(rp, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def _write_text(path, text):
    rp = _validate_path(path)
    with open(rp, 'w', encoding='utf-8') as f:
        f.write(text)

def _meta(text):
    return {
        "bytes": len(text.encode('utf-8')),
        "chars": len(text),
        "sha256": hashlib.sha256(text.encode('utf-8')).hexdigest(),
        "created": int(time.time()),
    }

def cmd_store(args):
    text = _read_text(args.infile)
    _validate_path(args.ctx_dir)
    os.makedirs(args.ctx_dir, exist_ok=True)
    ctx_id = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    ctx_path = os.path.join(args.ctx_dir, f"{ctx_id}.txt")
    meta_path = os.path.join(args.ctx_dir, f"{ctx_id}.json")
    _write_text(ctx_path, text)
    meta = _meta(text)
    meta["ctx_id"] = ctx_id
    meta["ctx_path"] = ctx_path
    _write_text(meta_path, json.dumps(meta, indent=2))
    print(json.dumps(meta))

def cmd_meta(args):
    text = _read_text(args.ctx)
    meta = _meta(text)
    meta["ctx_path"] = args.ctx
    print(json.dumps(meta))

def cmd_peek(args):
    text = _read_text(args.ctx)
    n = len(text)
    offset = max(0, min(args.offset, n))
    length = max(0, min(args.length, MAX_PEEK_LENGTH, n - offset))
    out = text[offset:offset+length]
    print(out)

def _regex_timeout_handler(signum, frame):
    raise TimeoutError("regex search exceeded time limit")

def cmd_search(args):
    text = _read_text(args.ctx)
    try:
        pattern = re.compile(args.pattern)
    except re.error as exc:
        print(f"ERROR: invalid regex: {exc}", file=sys.stderr)
        sys.exit(1)
    old_handler = signal.signal(signal.SIGALRM, _regex_timeout_handler)
    signal.alarm(REGEX_TIMEOUT_SECONDS)
    try:
        matches = []
        for m in pattern.finditer(text):
            matches.append({"start": m.start(), "end": m.end(), "match": m.group(0)})
            if len(matches) >= MAX_SEARCH_RESULTS:
                break
    except TimeoutError:
        print("ERROR: regex search timed out (possible ReDoS pattern)", file=sys.stderr)
        sys.exit(1)
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)
    print(json.dumps(matches, indent=2))

def cmd_chunk(args):
    text = _read_text(args.ctx)
    size = max(1, args.size)
    overlap = max(0, min(args.overlap, size-1))
    chunks = []
    i = 0
    while i < len(text):
        j = min(len(text), i + size)
        chunks.append({"start": i, "end": j})
        i = j - overlap
        if len(chunks) >= MAX_CHUNKS:
            break
    print(json.dumps(chunks))

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('store')
    s.add_argument('--infile', required=True)
    s.add_argument('--ctx-dir', required=True)

    m = sub.add_parser('meta')
    m.add_argument('--ctx', required=True)

    pk = sub.add_parser('peek')
    pk.add_argument('--ctx', required=True)
    pk.add_argument('--offset', type=int, required=True)
    pk.add_argument('--length', type=int, required=True)

    se = sub.add_parser('search')
    se.add_argument('--ctx', required=True)
    se.add_argument('--pattern', required=True)

    c = sub.add_parser('chunk')
    c.add_argument('--ctx', required=True)
    c.add_argument('--size', type=int, required=True)
    c.add_argument('--overlap', type=int, default=0)

    args = p.parse_args()
    if args.cmd == 'store': cmd_store(args)
    elif args.cmd == 'meta': cmd_meta(args)
    elif args.cmd == 'peek': cmd_peek(args)
    elif args.cmd == 'search': cmd_search(args)
    elif args.cmd == 'chunk': cmd_chunk(args)

if __name__ == '__main__':
    main()
