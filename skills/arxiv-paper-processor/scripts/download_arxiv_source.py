#!/usr/bin/env python3
"""Download and extract arXiv source bundle for one paper directory."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import json
import random
import re
import tarfile
import time
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import fcntl
except ImportError:  # pragma: no cover - non-Unix fallback
    fcntl = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and extract arXiv source into paper_dir/source/.")
    parser.add_argument("--paper-dir", required=True, help="Paper directory containing metadata.")
    parser.add_argument("--arxiv-id", default="", help="Optional explicit arXiv ID override.")
    parser.add_argument(
        "--request-timeout", type=int, default=45, help="HTTP timeout seconds."
    )
    parser.add_argument(
        "--user-agent",
        default="arxiv-paper-source-downloader/1.0 (contact: local-agent)",
        help="HTTP user agent.",
    )
    parser.add_argument(
        "--language",
        default="English",
        help="Requested workflow language (logged for traceability).",
    )
    parser.add_argument(
        "--rate-state-path",
        default="",
        help=(
            "Optional throttle-state JSON path. Default: "
            "<run_dir>/.runtime/arxiv_download_state.json"
        ),
    )
    parser.add_argument(
        "--min-interval-sec",
        type=float,
        default=5.0,
        help="Minimum interval between download requests in seconds. Default 5.0.",
    )
    parser.add_argument(
        "--retry-max",
        type=int,
        default=4,
        help="Max retries on 429/503/network errors. Total attempts = retry-max + 1.",
    )
    parser.add_argument(
        "--retry-base-sec",
        type=float,
        default=5.0,
        help="Base retry backoff seconds before exponential growth.",
    )
    parser.add_argument(
        "--retry-max-sec",
        type=float,
        default=120.0,
        help="Cap for each retry wait duration in seconds.",
    )
    parser.add_argument(
        "--retry-jitter-sec",
        type=float,
        default=1.0,
        help="Random jitter upper bound added to each retry wait.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing source bundle.")
    return parser.parse_args()


def load_metadata(paper_dir: Path) -> dict[str, Any]:
    json_path = paper_dir / "metadata.json"
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    md_path = paper_dir / "metadata.md"
    if not md_path.exists():
        return {}

    data: dict[str, Any] = {}
    field_map = {
        "ArXiv ID": "base_id",
        "Versioned ID": "id",
        "Abs URL": "abs_url",
        "ArXiv 编号": "base_id",
        "版本编号": "id",
        "摘要页链接": "abs_url",
    }
    for line in md_path.read_text().splitlines():
        m = re.match(r"^- \*\*(.+?)\*\*: ?(.*)$", line.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        mapped = field_map.get(key)
        if mapped:
            data[mapped] = value.strip()
    return data


def normalize_arxiv_id(raw: str) -> str:
    raw = str(raw or "").strip()
    if not raw:
        return ""
    m = re.search(r"/(?:abs|pdf)/([^/?#]+)", raw)
    if m:
        raw = m.group(1)
    return raw.split("/")[-1]


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def resolve_arxiv_id(metadata: dict[str, Any], cli_id: str) -> str:
    if cli_id.strip():
        return normalize_arxiv_id(cli_id)
    for key in ("id", "base_id", "abs_url"):
        value = metadata.get(key, "")
        if value:
            return normalize_arxiv_id(value)
    return ""


def fetch_bytes(url: str, timeout: int, user_agent: str) -> bytes:
    req = Request(url, headers={"User-Agent": user_agent})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_rate_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_rate_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def default_rate_state_path(paper_dir: Path) -> Path:
    return paper_dir.parent / ".runtime" / "arxiv_download_state.json"


@contextmanager
def rate_state_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock_fp:
        if fcntl is not None:
            fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)


def acquire_request_slot(state_path: Path, min_interval_sec: float) -> float:
    interval = max(0.0, min_interval_sec)
    lock_path = state_path.with_name(f"{state_path.name}.lock")
    with rate_state_lock(lock_path):
        state = load_rate_state(state_path)
        now_ts = time.time()
        last_ts = float(state.get("last_request_ts", 0.0) or 0.0)
        cooldown_until_ts = float(state.get("cooldown_until_ts", 0.0) or 0.0)
        wait_sec = max(0.0, interval - (now_ts - last_ts), cooldown_until_ts - now_ts)
        if wait_sec > 0:
            time.sleep(wait_sec)
        reserved_ts = time.time()
        state["last_request_ts"] = reserved_ts
        state["last_request_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        if cooldown_until_ts <= reserved_ts:
            state.pop("cooldown_until_ts", None)
            state.pop("cooldown_until_utc", None)
        save_rate_state(state_path, state)
    return wait_sec


def register_server_cooldown(state_path: Path, cooldown_sec: float) -> None:
    cooldown = max(0.0, cooldown_sec)
    if cooldown <= 0:
        return
    lock_path = state_path.with_name(f"{state_path.name}.lock")
    with rate_state_lock(lock_path):
        state = load_rate_state(state_path)
        now_ts = time.time()
        old_until_ts = float(state.get("cooldown_until_ts", 0.0) or 0.0)
        new_until_ts = max(old_until_ts, now_ts + cooldown)
        state["cooldown_until_ts"] = new_until_ts
        state["cooldown_until_utc"] = dt.datetime.fromtimestamp(
            new_until_ts,
            tz=dt.timezone.utc,
        ).isoformat()
        save_rate_state(state_path, state)


def parse_retry_after_seconds(raw_value: str) -> float:
    value = (raw_value or "").strip()
    if not value:
        return 0.0
    if re.fullmatch(r"\d+", value):
        return max(0.0, float(int(value)))
    try:
        parsed = parsedate_to_datetime(value)
    except Exception:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    delta = (parsed - dt.datetime.now(dt.timezone.utc)).total_seconds()
    return max(0.0, delta)


def is_retryable_http(code: int) -> bool:
    return code in {429, 500, 502, 503, 504}


def fetch_with_retry(
    *,
    url: str,
    timeout: int,
    user_agent: str,
    state_path: Path,
    min_interval_sec: float,
    retry_max: int,
    retry_base_sec: float,
    retry_max_sec: float,
    retry_jitter_sec: float,
) -> bytes:
    max_retry = max(0, retry_max)
    for attempt in range(max_retry + 1):
        acquire_request_slot(state_path, min_interval_sec)
        try:
            return fetch_bytes(url, timeout=timeout, user_agent=user_agent)
        except HTTPError as exc:
            code = int(getattr(exc, "code", 0) or 0)
            if not is_retryable_http(code) or attempt >= max_retry:
                raise
            headers = getattr(exc, "headers", None)
            retry_after = 0.0
            if headers is not None:
                retry_after = parse_retry_after_seconds(headers.get("Retry-After", ""))
            backoff = min(
                max(0.0, retry_max_sec),
                max(0.0, retry_base_sec) * (2**attempt),
            ) + random.uniform(0.0, max(0.0, retry_jitter_sec))
            register_server_cooldown(state_path, max(retry_after, backoff))
        except (URLError, TimeoutError):
            if attempt >= max_retry:
                raise
            backoff = min(
                max(0.0, retry_max_sec),
                max(0.0, retry_base_sec) * (2**attempt),
            ) + random.uniform(0.0, max(0.0, retry_jitter_sec))
            register_server_cooldown(state_path, backoff)
    raise RuntimeError("unreachable retry branch")


def extract_tar_safely(archive: tarfile.TarFile, dest_dir: Path) -> None:
    root = dest_dir.resolve()
    for member in archive.getmembers():
        target = (dest_dir / member.name).resolve()
        if not str(target).startswith(str(root)):
            raise ValueError(f"Unsafe path in tar: {member.name}")
    archive.extractall(dest_dir)


def extract_from_blob(blob: bytes, dest_dir: Path) -> tuple[bool, str]:
    # case 1: tar directly
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as archive:
            extract_tar_safely(archive, dest_dir)
        return True, "tar extracted"
    except tarfile.TarError:
        pass

    # case 2: gzip payload
    try:
        gz_blob = gzip.decompress(blob)
    except OSError:
        gz_blob = b""

    if gz_blob:
        try:
            with tarfile.open(fileobj=io.BytesIO(gz_blob), mode="r:*") as archive:
                extract_tar_safely(archive, dest_dir)
            return True, "gzip->tar extracted"
        except tarfile.TarError:
            if b"\\documentclass" in gz_blob[:2048] or b"\\begin{document}" in gz_blob[:2048]:
                (dest_dir / "main.tex").write_bytes(gz_blob)
                return True, "gzip plain tex extracted"

    # case 3: plain tex
    if b"\\documentclass" in blob[:2048] or b"\\begin{document}" in blob[:2048]:
        (dest_dir / "main.tex").write_bytes(blob)
        return True, "plain tex extracted"

    return False, "source payload format not recognized"


def run() -> int:
    args = parse_args()
    paper_dir = Path(args.paper_dir).expanduser().resolve()
    if not paper_dir.exists() or not paper_dir.is_dir():
        print(f"[ERROR] paper directory not found: {paper_dir}")
        return 1

    metadata = load_metadata(paper_dir)
    arxiv_id = resolve_arxiv_id(metadata, args.arxiv_id)
    if not arxiv_id:
        print("[ERROR] arXiv ID not found. Provide --arxiv-id or valid metadata.")
        return 1

    source_dir = paper_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    bundle_path = source_dir / "source_bundle.bin"
    extract_dir = source_dir / "source_extract"
    extract_dir.mkdir(parents=True, exist_ok=True)

    effective_rate_state_path = (
        Path(args.rate_state_path).expanduser().resolve()
        if args.rate_state_path.strip()
        else default_rate_state_path(paper_dir)
    )

    fetched_from_network = False
    if bundle_path.exists() and not args.force:
        blob = bundle_path.read_bytes()
    else:
        url = f"https://arxiv.org/e-print/{arxiv_id}"
        try:
            blob = fetch_with_retry(
                url=url,
                timeout=args.request_timeout,
                user_agent=args.user_agent,
                state_path=effective_rate_state_path,
                min_interval_sec=args.min_interval_sec,
                retry_max=args.retry_max,
                retry_base_sec=args.retry_base_sec,
                retry_max_sec=args.retry_max_sec,
                retry_jitter_sec=args.retry_jitter_sec,
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"[ERROR] source download failed: {exc}")
            return 1
        bundle_path.write_bytes(blob)
        fetched_from_network = True

    ok, note = extract_from_blob(blob, extract_dir)

    tex_files = sorted(str(p.relative_to(paper_dir)) for p in extract_dir.rglob("*.tex") if p.is_file())
    payload = {
        "paper_dir": str(paper_dir),
        "arxiv_id": arxiv_id,
        "language": args.language,
        "language_normalized": normalize_language(args.language),
        "source_bundle": str(bundle_path),
        "source_extract_dir": str(extract_dir),
        "fetched_from_network": fetched_from_network,
        "extract_ok": ok,
        "extract_note": note,
        "tex_file_count": len(tex_files),
        "tex_files": tex_files[:50],
        "rate_state_path": str(effective_rate_state_path),
        "min_interval_sec": args.min_interval_sec,
        "retry_max": args.retry_max,
        "retry_base_sec": args.retry_base_sec,
        "retry_max_sec": args.retry_max_sec,
        "retry_jitter_sec": args.retry_jitter_sec,
    }

    (source_dir / "download_source_log.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
