#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Iterable

INDEXEDDB_DEFAULT = Path.home() / "Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/IndexedDB/flomo_._0.indexeddb.leveldb"
RENDER_LOG_DEFAULT = Path.home() / "Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/log/renderer.log"
FLOMO_CONFIG_DEFAULT = Path.home() / "Library/Containers/com.flomoapp.m/Data/Library/Application Support/flomo/config.json"

# Extracted from flomo macOS app bundle (app.asar) in v5.26.12.
FLOMO_SIGN_SECRET_DEFAULT = "dbbc3dd73364b4084c3a69346e0ce2b2"


def _html_to_text(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p\s*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def _masked_webhook(url: str) -> str:
    if len(url) < 18:
        return "***"
    return f"{url[:12]}...{url[-6:]}"


def _run_strings(path: Path) -> str:
    proc = subprocess.run(["strings", "-n", "6", str(path)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"strings failed for {path}")
    return proc.stdout


def _run_curl(args: list[str]) -> str:
    # Use curl for network calls to avoid Python SSL cert issues on some machines.
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or "").strip()
        out = (proc.stdout or "").strip()
        raise RuntimeError(err or out or f"curl failed: {args[0]}")
    return proc.stdout


def _curl_json(method: str, url: str, headers: dict[str, str] | None = None, data_json: dict | None = None) -> dict:
    cmd = ["curl", "-sS", "-X", method.upper(), url]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    if data_json is not None:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data_json, ensure_ascii=False)])
    raw = _run_curl(cmd)
    return json.loads(raw)


def _extract_memos_from_strings(raw: str):
    lines = raw.splitlines()
    memos = []
    current = {}
    for line in lines:
        if line.startswith("slug"):
            if current.get("content"):
                memos.append(current)
            current = {"slug": line}
            continue
        if line.startswith("recorded") or re.match(r"^20\d\d-\d\d-\d\d", line):
            current["recorded_at"] = line
            continue
        if "content" in line and len(line.strip()) > 7:
            text = line.strip()
            if not text.startswith("content"):
                current["content"] = text
            continue
        if current.get("content") is None and len(line.strip()) >= 10:
            if re.search(r"[\u4e00-\u9fffA-Za-z0-9]", line):
                if all(k not in line for k in ["http://", "https://", "thumbnail", "creator_id", "linked_count", "is_show_cloud"]):
                    current["content"] = line.strip()
    if current.get("content"):
        memos.append(current)

    uniq = []
    seen = set()
    for m in memos:
        c = m.get("content", "")
        if not c or c in seen:
            continue
        seen.add(c)
        uniq.append(m)
    return uniq


def read_local(limit: int, query: str | None):
    dbdir = Path(os.getenv("FLOMO_INDEXEDDB_DIR", str(INDEXEDDB_DEFAULT)))
    if not dbdir.exists():
        raise FileNotFoundError(f"IndexedDB dir not found: {dbdir}")

    ldb_files = sorted(dbdir.glob("*.ldb"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not ldb_files:
        raise FileNotFoundError(f"No .ldb files in {dbdir}")

    memos = []
    for f in ldb_files[:8]:
        raw = _run_strings(f)
        memos.extend(_extract_memos_from_strings(raw))
        if len(memos) >= limit * 2:
            break

    if query:
        q = query.lower()
        memos = [m for m in memos if q in m.get("content", "").lower()]

    memos = memos[:limit]
    return {"ok": True, "source": "local_indexeddb", "count": len(memos), "items": memos}


def _load_flomo_config() -> dict:
    p = Path(os.getenv("FLOMO_CONFIG_PATH", str(FLOMO_CONFIG_DEFAULT)))
    if not p.exists():
        raise FileNotFoundError(f"flomo config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8", errors="ignore"))


def _get_access_token() -> str:
    if os.getenv("FLOMO_ACCESS_TOKEN"):
        return os.getenv("FLOMO_ACCESS_TOKEN", "")
    cfg = _load_flomo_config()
    token = cfg.get("user", {}).get("access_token")
    if not token:
        raise RuntimeError("Missing access_token in flomo config")
    return token


def _get_app_version() -> str:
    if os.getenv("FLOMO_APP_VERSION"):
        return os.getenv("FLOMO_APP_VERSION", "")
    cfg = _load_flomo_config()
    v = cfg.get("appConfig", {}).get("VUE_APP_VERSION")
    return v or "unknown"


def _sign_params(params: dict) -> str:
    secret = os.getenv("FLOMO_SIGN_SECRET", FLOMO_SIGN_SECRET_DEFAULT)

    items = []
    for k in sorted(params.keys()):
        v = params[k]
        if v is None:
            continue
        if v is False or v == "" or v == 0 or v:
            pass
        else:
            continue

        if isinstance(v, (list, tuple)):
            vs = sorted([str(x) for x in v if x or x == 0])
            for x in vs:
                items.append(f"{k}[]={x}")
        else:
            items.append(f"{k}={v}")

    qs = "&".join(items)
    return hashlib.md5((qs + secret).encode("utf-8")).hexdigest()


def _api_get(path: str, extra_params: dict | None = None) -> dict:
    base = os.getenv("FLOMO_API_BASE", "https://flomoapp.com/api/v1").rstrip("/")

    params = {
        "api_key": "flomo_web",
        "app_version": _get_app_version(),
        "platform": os.getenv("FLOMO_PLATFORM", "mac"),
        "timestamp": int(time.time()),
        "webp": "1",
    }
    if extra_params:
        params.update(extra_params)
    params["sign"] = _sign_params(params.copy())

    url = f"{base}{path}?{urllib.parse.urlencode(params, doseq=True)}"
    return _curl_json(
        "GET",
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {_get_access_token()}",
            "platform": "Mac",
            "device-model": "Mac",
        },
    )


def _normalize_tag(tag: str) -> str:
    return tag.strip().lstrip("#").strip().lower()


def _extract_hashtags(text: str) -> set[str]:
    if not text:
        return set()
    return {_normalize_tag(x) for x in re.findall(r"#([^\s#]+)", text) if x.strip()}


def _coerce_tags(raw_tags: object) -> list[str]:
    tags: list[str] = []
    if not isinstance(raw_tags, list):
        return tags
    for it in raw_tags:
        if isinstance(it, str):
            t = it
        elif isinstance(it, dict):
            t = it.get("name") or it.get("tag") or it.get("title") or ""
        else:
            t = ""
        t_norm = _normalize_tag(str(t))
        if t_norm:
            tags.append(t_norm)
    return tags


def _dt_key(s: str | None) -> str:
    return s or ""


def _fetch_updated_window(limit: int, tz: str, since_seconds: int) -> list[dict]:
    now = int(time.time())
    cursor_updated_at = now - max(0, since_seconds)
    obj = _api_get(
        "/memo/updated/",
        {
            "limit": limit,
            "tz": tz,
            # This endpoint is incremental: return memos updated after the cursor.
            "latest_updated_at": cursor_updated_at,
            "latest_slug": 0,
        },
    )
    if obj.get("code") != 0:
        raise RuntimeError(f"memo/updated failed: {obj.get('message') or obj.get('code')}")
    data = obj.get("data") or []
    return [x for x in data if isinstance(x, dict)]


def _matches_memo(txt: str, raw_html: str, tags: Iterable[str], query: str | None, tag: str | None) -> bool:
    norm_tags = set(tags)
    inline_tags = _extract_hashtags(txt)
    all_tags = norm_tags | inline_tags

    if tag:
        tgt = _normalize_tag(tag)
        if tgt and tgt not in all_tags:
            return False

    if query:
        q = query.strip()
        if q.startswith("#"):
            q_tag = _normalize_tag(q)
            if q_tag and q_tag not in all_tags:
                return False
        else:
            ql = q.lower()
            if ql not in txt.lower():
                return False

    return True


def dump_remote_tags(limit: int, tz: str, since_seconds: int) -> dict:
    fetch_limit = 500
    scan_target = min(max(limit * 30, 300), 3000)
    windows = [86400, 7 * 86400, 30 * 86400, 180 * 86400, 365 * 86400, 5 * 365 * 86400]
    if since_seconds and since_seconds > 0:
        windows = [since_seconds]

    seen = set()
    scanned = []

    for win in windows:
        items = _fetch_updated_window(fetch_limit, tz, win)
        for it in items:
            slug = it.get("slug")
            if slug and slug in seen:
                continue
            if slug:
                seen.add(slug)
            scanned.append(it)
            if len(scanned) >= scan_target:
                break
        if len(scanned) >= scan_target:
            break

    counts: dict[str, int] = {}
    for it in scanned:
        raw = it.get("content") or ""
        txt = _html_to_text(raw)
        memo_tags = set(_coerce_tags(it.get("tags"))) | _extract_hashtags(txt)
        for t in memo_tags:
            counts[t] = counts.get(t, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    top = [{"tag": x[0], "count": x[1]} for x in ranked[:limit]]
    return {
        "ok": True,
        "source": "remote_api",
        "mode": "tag_summary",
        "scanned_memos": len(scanned),
        "unique_tags": len(counts),
        "count": len(top),
        "items": top,
    }


def get_incoming_webhook_url() -> str:
    obj = _api_get("/incoming_webhook")
    if obj.get("code") != 0:
        raise RuntimeError(f"incoming_webhook failed: {obj.get('message') or obj.get('code')}")
    path = obj.get("data", {}).get("incoming_webhook")
    if not path:
        raise RuntimeError("incoming_webhook missing in response")
    return "https://flomoapp.com/iwh" + path


def read_remote(limit: int, query: str | None, tz: str, since_seconds: int, tag: str | None = None):
    fetch_limit = min(max(limit * 12, 120), 500)
    # Auto-expand windows to avoid "only one hit" when a tag is sparse in recent notes.
    windows = [86400, 7 * 86400, 30 * 86400, 180 * 86400, 365 * 86400, 5 * 365 * 86400]
    if since_seconds and since_seconds > 0:
        windows = [since_seconds]

    seen = set()
    out = []

    for win in windows:
        items = _fetch_updated_window(fetch_limit, tz, win)
        for it in items:
            slug = it.get("slug")
            if slug and slug in seen:
                continue
            raw = it.get("content") or ""
            txt = _html_to_text(raw)
            parsed_tags = _coerce_tags(it.get("tags"))
            if not _matches_memo(txt, raw, parsed_tags, query, tag):
                continue
            if slug:
                seen.add(slug)
            out.append(
                {
                    "slug": slug,
                    "created_at": it.get("created_at"),
                    "updated_at": it.get("updated_at"),
                    "source": it.get("source"),
                    "tags": sorted(set(parsed_tags)),
                    "content": txt,
                    "content_html": raw,
                }
            )

        if len(out) >= limit:
            break

    out.sort(key=lambda x: (_dt_key(x.get("updated_at")), _dt_key(x.get("created_at"))), reverse=True)
    out = out[:limit]
    return {"ok": True, "source": "remote_api", "count": len(out), "items": out}


def write_webhook(content: str, webhook_url: str):
    resp = _curl_json("POST", webhook_url, data_json={"content": content})
    return {
        "ok": True,
        "mode": "webhook",
        # curl does not expose status without extra flags; treat successful JSON parse as 200.
        "status": 200,
        "response": json.dumps(resp, ensure_ascii=False)[:800],
        "webhook": _masked_webhook(webhook_url),
    }


def write_url_scheme(content: str):
    qs = urllib.parse.urlencode({"content": content})
    url = f"flomo://create?{qs}"
    proc = subprocess.run(["open", url], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "open flomo:// failed")
    return {"ok": True, "mode": "url_scheme", "opened": True}


def _extract_token_from_renderer_log() -> str | None:
    log_path = Path(os.getenv("FLOMO_RENDER_LOG", str(RENDER_LOG_DEFAULT)))
    if not log_path.exists():
        return None
    text = log_path.read_text(errors="ignore")
    m = re.search(r"Authorization\":\"Bearer ([^\"]+)\"", text)
    return m.group(1) if m else None


def cmd_read(args):
    if args.dump_tags:
        out = dump_remote_tags(args.limit, args.tz, args.since_seconds)
    elif args.remote:
        out = read_remote(args.limit, args.query, args.tz, args.since_seconds, args.tag)
    elif args.local:
        out = read_local(args.limit, args.query)
    else:
        try:
            out = read_remote(args.limit, args.query, args.tz, args.since_seconds, args.tag)
        except Exception:
            out = read_local(args.limit, args.query)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_write(args):
    content = args.content.strip()
    if not content:
        raise ValueError("content is empty")

    webhook = args.webhook or os.getenv("FLOMO_WEBHOOK_URL")
    if webhook and not args.url_scheme:
        out = write_webhook(content, webhook)
    elif args.url_scheme:
        out = write_url_scheme(content)
    else:
        webhook = get_incoming_webhook_url()
        out = write_webhook(content, webhook)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_verify(args):
    result = {"ok": True, "checks": []}

    try:
        remote = read_remote(limit=10, query=args.query, tz=args.tz, since_seconds=args.since_seconds)
        result["checks"].append({"name": "read_remote", "ok": True, "count": remote["count"]})
    except Exception as e:
        result["ok"] = False
        result["checks"].append({"name": "read_remote", "ok": False, "error": str(e)})

    if args.try_webhook:
        try:
            webhook = args.webhook or os.getenv("FLOMO_WEBHOOK_URL") or get_incoming_webhook_url()
            nonce = f"ocv{int(time.time())}"
            content = (args.content or "").strip()
            if nonce not in content:
                content = f"{content} {nonce}".strip()
            out = write_webhook(content, webhook)

            verify_q = nonce
            time.sleep(1.2)
            verify_window = min(args.since_seconds, 3600) if args.since_seconds > 0 else 3600
            check = read_remote(limit=40, query=verify_q, tz=args.tz, since_seconds=verify_window)
            result["checks"].append({"name": "write_webhook", "ok": True, "status": out.get("status"), "readback_hits": check.get("count")})
        except Exception as e:
            result["ok"] = False
            result["checks"].append({"name": "write_webhook", "ok": False, "error": str(e)})

    if args.try_url_scheme:
        try:
            write_url_scheme(args.content)
            result["checks"].append({"name": "write_url_scheme", "ok": True})
        except Exception as e:
            result["ok"] = False
            result["checks"].append({"name": "write_url_scheme", "ok": False, "error": str(e)})

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        sys.exit(1)


def build_parser():
    p = argparse.ArgumentParser(description="flomo read/write helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    default_since_seconds = int(os.getenv("FLOMO_SINCE_SECONDS", "0"))

    read = sub.add_parser("read", help="read memos")
    read.add_argument("--limit", type=int, default=20)
    read.add_argument("--query", default=None)
    read.add_argument("--tag", default=None, help="filter by tag (supports with/without leading #)")
    read.add_argument("--dump-tags", action="store_true", help="dump top tags by frequency from remote memos")
    read.add_argument("--remote", action="store_true", help="force read using remote API")
    read.add_argument("--local", action="store_true", help="force read using local cache")
    read.add_argument("--tz", default=os.getenv("FLOMO_TZ", "8:0"), help="timezone offset like '8:0' (default: 8:0)")
    read.add_argument("--since-seconds", type=int, default=default_since_seconds, help="remote read cursor window in seconds (0 = auto-expand, default: 0)")
    read.set_defaults(func=cmd_read)

    write = sub.add_parser("write", help="write memo")
    write.add_argument("--content", required=True)
    write.add_argument("--webhook", default=None)
    write.add_argument("--url-scheme", action="store_true")
    write.set_defaults(func=cmd_write)

    verify = sub.add_parser("verify", help="verify skill")
    verify.add_argument("--query", default=None)
    verify.add_argument("--content", default=f"OpenClaw flomo skill verify {time.strftime('%Y-%m-%d %H:%M:%S')} #openclaw")
    verify.add_argument("--webhook", default=None)
    verify.add_argument("--try-webhook", action="store_true")
    verify.add_argument("--try-url-scheme", action="store_true")
    verify.add_argument("--tz", default=os.getenv("FLOMO_TZ", "8:0"), help="timezone offset like '8:0' (default: 8:0)")
    verify.add_argument("--since-seconds", type=int, default=default_since_seconds, help="remote read cursor window in seconds (0 = auto-expand, default: 0)")
    verify.set_defaults(func=cmd_verify)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
