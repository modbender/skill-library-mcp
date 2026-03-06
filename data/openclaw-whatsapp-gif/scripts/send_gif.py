#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_MIN_BYTES = 1024
DEFAULT_MAX_BYTES = 15_000_000
DEFAULT_ALLOWED_HOSTS = {
    "media.giphy.com",
    "i.giphy.com",
    "media.tenor.com",
    "media1.tenor.com",
    "tenor.com",
}


def load_policy(script_dir: Path):
    path = script_dir.parent / "references" / "policy.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def run_find_gif(script_dir: Path, query: str, limit: int):
    py = sys.executable or "python3"
    cmd = [py, str(script_dir / "find_gif.py"), query, "--limit", str(limit), "--json"]
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def normalize_allowed_hosts(value):
    if not isinstance(value, list):
        return set(DEFAULT_ALLOWED_HOSTS)
    hosts = set()
    for raw in value:
        if not isinstance(raw, str):
            continue
        host = raw.strip().lower()
        if host:
            hosts.add(host)
    return hosts or set(DEFAULT_ALLOWED_HOSTS)


def is_allowed_host(url: str, allowed_hosts):
    host = urllib.parse.urlparse(url).netloc.lower().split(":")[0]
    if not host:
        return False
    for allowed in allowed_hosts:
        if host == allowed or host.endswith("." + allowed):
            return True
    return False


def default_cache_dir() -> str:
    return str(Path(tempfile.gettempdir()) / "openclaw-whatsapp-gif")


def default_log_file() -> str:
    return str(Path(tempfile.gettempdir()) / "openclaw-whatsapp-gif" / "send.log")


def infer_extension(url: str, content_type: str = "") -> str:
    p = urllib.parse.urlparse(url).path.lower()
    c = content_type.lower()
    if p.endswith(".mp4") or "video/mp4" in c:
        return ".mp4"
    if p.endswith(".webm") or "video/webm" in c:
        return ".webm"
    if p.endswith(".gif") or "image/gif" in c:
        return ".gif"
    return ".bin"


def download_media(url: str, out_dir: Path, min_bytes: int, max_bytes: int, allowed_hosts, retries: int = 3):
    if not is_allowed_host(url, allowed_hosts):
        raise ValueError("url host is not allowed by policy")
    out_dir.mkdir(parents=True, exist_ok=True)
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "openclaw-whatsapp-gif/1.5"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type", "")
            if len(data) < min_bytes:
                raise ValueError(f"media too small ({len(data)} bytes)")
            if len(data) > max_bytes:
                raise ValueError(f"media too large ({len(data)} bytes)")
            ext = infer_extension(url, content_type)
            if ext not in {".mp4", ".gif", ".webm"}:
                raise ValueError(f"unsupported content type: {content_type or 'unknown'}")
            out_path = out_dir / f"gif_{hashlib.sha1(url.encode()).hexdigest()[:12]}{ext}"
            out_path.write_bytes(data)
            return out_path, len(data), content_type
        except Exception as e:
            last = e
            time.sleep(0.6 * (i + 1))
    raise last


def main():
    p = argparse.ArgumentParser()
    p.add_argument("target")
    p.add_argument("query")
    p.add_argument("--caption", default="")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--json", action="store_true")
    p.add_argument("--payload-only", action="store_true")
    p.add_argument("--delivery-mode", choices=["remote", "local"], default="local")
    p.add_argument("--cache-dir")
    p.add_argument("--log-file")
    p.add_argument("--enable-telemetry-log", action="store_true")
    args = p.parse_args()

    script_dir = Path(__file__).resolve().parent
    policy = load_policy(script_dir)
    min_bytes = int(policy.get("minBytes", DEFAULT_MIN_BYTES))
    max_bytes = int(policy.get("maxBytes", DEFAULT_MAX_BYTES))
    allow_remote_fallback = bool(policy.get("allowRemoteUrlFallback", False))
    allowed_hosts = normalize_allowed_hosts(policy.get("allowedMediaHosts"))
    cache_dir = args.cache_dir or policy.get("cacheDir") or default_cache_dir()
    telemetry_enabled = bool(policy.get("enableTelemetryLog", False)) or args.enable_telemetry_log or bool(args.log_file)
    log_file = args.log_file or policy.get("logFile") or default_log_file()

    try:
        candidates = run_find_gif(script_dir, args.query, args.limit)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: find_gif failed: {e}")
        sys.exit(2)

    if not candidates:
        print("ERROR: no gif candidates")
        sys.exit(3)

    payload = {"action": "send", "channel": "whatsapp", "target": args.target, "gifPlayback": True, "caption": args.caption}
    selected, local_file, errors = None, None, []

    if args.delivery_mode == "local":
        for cand in candidates:
            try:
                local_file, size_bytes, ctype = download_media(
                    cand["url"],
                    Path(cache_dir),
                    min_bytes=min_bytes,
                    max_bytes=max_bytes,
                    allowed_hosts=allowed_hosts,
                )
                payload["filePath"] = str(local_file)
                payload["filename"] = local_file.name
                payload["_meta"] = {"sourceUrl": cand["url"], "contentType": ctype, "sizeBytes": size_bytes}
                selected = cand
                break
            except Exception as e:
                errors.append({"url": cand.get("url"), "error": str(e)})
        if selected is None:
            if allow_remote_fallback:
                remote_candidate = next((c for c in candidates if is_allowed_host(c.get("url", ""), allowed_hosts)), None)
                if remote_candidate:
                    selected = remote_candidate
                    payload["media"] = selected["url"]
                    payload["deliveryFallback"] = "all local downloads failed; using remote URL"
                else:
                    print("ERROR: local downloads failed and no allowed remote URL candidates")
                    sys.exit(4)
            else:
                print("ERROR: local downloads failed and remote URL fallback is disabled by policy")
                sys.exit(4)
    else:
        selected = next((c for c in candidates if is_allowed_host(c.get("url", ""), allowed_hosts)), None)
        if selected is None:
            print("ERROR: no allowed remote URL candidates")
            sys.exit(5)
        payload["media"] = selected["url"]

    result = {"best": selected, "payload": payload, "candidates": candidates}
    if local_file:
        result["downloadedFile"] = str(local_file)
    if errors:
        result["downloadErrors"] = errors

    # telemetry log
    if telemetry_enabled:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": int(time.time()), "query": args.query, "selected": (selected or {}).get("url"), "errors": errors, "mode": args.delivery_mode}) + "\n")
        except Exception:
            pass

    if args.payload_only:
        print(json.dumps(payload, indent=2))
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
