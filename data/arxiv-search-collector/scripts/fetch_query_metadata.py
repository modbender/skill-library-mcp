#!/usr/bin/env python3
"""Fetch one arXiv query result list and store it as indexed JSON/Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import time
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

try:
    import fcntl
except ImportError:  # pragma: no cover - non-Unix fallback
    fcntl = None

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch one query result set from arXiv API.")
    parser.add_argument("--run-dir", required=True, help="Run directory initialized by init_collection_run.py.")
    parser.add_argument("--query", required=True, help="Raw arXiv search_query string.")
    parser.add_argument("--label", default="", help="Query label for output files.")
    parser.add_argument("--categories", default="", help="Optional categories appended as cat filter.")
    parser.add_argument("--max-results", type=int, default=40, help="arXiv max_results for this query.")
    parser.add_argument("--start", type=int, default=0, help="arXiv start index.")
    parser.add_argument(
        "--sort-by",
        default="submittedDate",
        choices=["relevance", "lastUpdatedDate", "submittedDate"],
    )
    parser.add_argument(
        "--sort-order", default="descending", choices=["ascending", "descending"]
    )
    parser.add_argument("--from-date", default="", help="Override start date YYYY-MM-DD.")
    parser.add_argument("--to-date", default="", help="Override end date YYYY-MM-DD.")
    parser.add_argument("--request-timeout", type=int, default=30, help="HTTP timeout seconds.")
    parser.add_argument(
        "--user-agent",
        default="arxiv-query-fetcher/1.0 (contact: local-agent)",
        help="HTTP user agent.",
    )
    parser.add_argument(
        "--language",
        default="",
        help="Optional markdown language override. If empty, use task_meta.json params.language.",
    )
    parser.add_argument(
        "--rate-state-path",
        default="",
        help=(
            "Optional rate-state JSON path. Default: "
            "<run_dir>/.runtime/arxiv_api_state.json"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cache and force a new API request.",
    )
    parser.add_argument(
        "--min-interval-sec",
        type=float,
        default=5.0,
        help="Minimum interval between API requests in seconds. Default 5.0.",
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
    return parser.parse_args()


def split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "query"


def parse_date(raw: str, *, end_of_day: bool) -> dt.datetime:
    base = dt.datetime.strptime(raw, "%Y-%m-%d")
    if end_of_day:
        base = base.replace(hour=23, minute=59, second=59)
    return base.replace(tzinfo=dt.timezone.utc)


def normalize_arxiv_id(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    m = re.search(r"/(?:abs|pdf)/([^/?#]+)", raw)
    if m:
        return m.group(1)
    return raw.split("/")[-1]


def xml_text(node: ET.Element, path: str) -> str:
    sub = node.find(path, ATOM_NS)
    if sub is None or sub.text is None:
        return ""
    return " ".join(sub.text.split())


def parse_atom(xml_bytes: bytes) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_bytes)
    out: list[dict[str, Any]] = []

    for entry in root.findall("atom:entry", ATOM_NS):
        versioned_id = normalize_arxiv_id(xml_text(entry, "atom:id"))
        base_id = re.sub(r"v\d+$", "", versioned_id)

        categories = [
            c.attrib.get("term", "").strip()
            for c in entry.findall("atom:category", ATOM_NS)
            if c.attrib.get("term")
        ]
        primary_node = entry.find("arxiv:primary_category", ATOM_NS)
        primary_category = (
            primary_node.attrib.get("term", "").strip()
            if primary_node is not None
            else (categories[0] if categories else "")
        )

        authors = [
            " ".join(a.text.split())
            for a in entry.findall("atom:author/atom:name", ATOM_NS)
            if a.text
        ]

        abs_url = f"https://arxiv.org/abs/{versioned_id}" if versioned_id else ""
        pdf_url = f"https://arxiv.org/pdf/{versioned_id}.pdf" if versioned_id else ""
        for link in entry.findall("atom:link", ATOM_NS):
            href = link.attrib.get("href", "")
            if not href:
                continue
            title = link.attrib.get("title", "")
            media_type = link.attrib.get("type", "")
            rel = link.attrib.get("rel", "")
            if title == "pdf" or media_type == "application/pdf":
                pdf_url = href
            elif rel == "alternate" and media_type == "text/html":
                abs_url = href

        out.append(
            {
                "id": versioned_id,
                "base_id": base_id,
                "title": xml_text(entry, "atom:title"),
                "summary": xml_text(entry, "atom:summary"),
                "authors": authors,
                "published": xml_text(entry, "atom:published"),
                "updated": xml_text(entry, "atom:updated"),
                "primary_category": primary_category,
                "categories": categories,
                "comment": xml_text(entry, "arxiv:comment"),
                "journal_ref": xml_text(entry, "arxiv:journal_ref"),
                "doi": xml_text(entry, "arxiv:doi"),
                "abs_url": abs_url,
                "pdf_url": pdf_url,
            }
        )

    return out


def build_effective_query(raw_query: str, categories: list[str]) -> str:
    query = raw_query.strip()
    if not categories:
        return query
    cat_clause = "(" + " OR ".join(f"cat:{c}" for c in categories) + ")"
    return f"{cat_clause} AND ({query})"


def to_arxiv_submitted_ts(raw_date: str, *, end_of_day: bool) -> str:
    date_obj = dt.datetime.strptime(raw_date, "%Y-%m-%d")
    hhmm = "2359" if end_of_day else "0000"
    return f"{date_obj.strftime('%Y%m%d')}{hhmm}"


def attach_submitted_date_clause(query: str, from_date: str, to_date: str) -> str:
    # Avoid duplicating a custom date clause if the caller already provided one.
    if re.search(r"submittedDate\s*:\s*\[", query, flags=re.IGNORECASE):
        return query
    start_ts = to_arxiv_submitted_ts(from_date, end_of_day=False)
    end_ts = to_arxiv_submitted_ts(to_date, end_of_day=True)
    date_clause = f"submittedDate:[{start_ts} TO {end_ts}]"
    return f"({query}) AND {date_clause}"


def load_task_meta(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "task_meta.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_task_meta(run_dir: Path, task_meta: dict[str, Any]) -> None:
    path = run_dir / "task_meta.json"
    path.write_text(json.dumps(task_meta, indent=2, ensure_ascii=False) + "\n")


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


def default_rate_state_path(run_dir: Path) -> Path:
    return run_dir / ".runtime" / "arxiv_api_state.json"


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


def fetch_with_retry(
    *,
    url: str,
    user_agent: str,
    request_timeout: int,
    state_path: Path,
    min_interval_sec: float,
    retry_max: int,
    retry_base_sec: float,
    retry_max_sec: float,
    retry_jitter_sec: float,
) -> tuple[bytes, int, float]:
    attempts = 0
    total_wait_sec = 0.0
    max_retries = max(0, retry_max)
    base_backoff = max(0.0, retry_base_sec)
    cap_backoff = max(base_backoff, retry_max_sec)
    jitter_cap = max(0.0, retry_jitter_sec)

    while True:
        attempts += 1
        total_wait_sec += acquire_request_slot(state_path, min_interval_sec)

        req = Request(url, headers={"User-Agent": user_agent})
        try:
            with urlopen(req, timeout=request_timeout) as resp:
                body = resp.read()
            return body, attempts, total_wait_sec
        except HTTPError as exc:
            retryable = exc.code in {429, 503}
            retry_after_sec = parse_retry_after_seconds(exc.headers.get("Retry-After", ""))
            backoff_sec = min(cap_backoff, base_backoff * (2 ** (attempts - 1)))

            if not retryable or attempts > (max_retries + 1):
                if exc.code == 429:
                    cooldown_sec = retry_after_sec if retry_after_sec > 0 else max(
                        min_interval_sec,
                        backoff_sec,
                    )
                    register_server_cooldown(state_path, cooldown_sec)
                    print(
                        "[ERROR] arXiv API returned 429 (Too Many Requests). "
                        f"Cooldown registered for {cooldown_sec:.1f}s."
                    )
                else:
                    print(f"[ERROR] arXiv API HTTP error: {exc}")
                raise

            wait_sec = retry_after_sec if retry_after_sec > 0 else backoff_sec
            wait_sec += random.uniform(0.0, jitter_cap)
            register_server_cooldown(state_path, wait_sec)
            total_wait_sec += wait_sec
            print(
                f"[WARN] arXiv API HTTP {exc.code}, retrying in {wait_sec:.1f}s "
                f"(attempt {attempts}/{max_retries + 1})"
            )
            time.sleep(wait_sec)
        except (URLError, TimeoutError) as exc:
            if attempts > (max_retries + 1):
                print(f"[ERROR] arXiv API request failed: {exc}")
                raise
            backoff_sec = min(cap_backoff, base_backoff * (2 ** (attempts - 1)))
            wait_sec = backoff_sec + random.uniform(0.0, jitter_cap)
            total_wait_sec += wait_sec
            print(
                f"[WARN] arXiv API network error, retrying in {wait_sec:.1f}s "
                f"(attempt {attempts}/{max_retries + 1})"
            )
            time.sleep(wait_sec)


def load_cached_payload_if_compatible(
    *,
    json_path: Path,
    md_path: Path,
    label: str,
    query: str,
    effective_query: str,
    categories: list[str],
    from_date: str,
    to_date: str,
    request_params: dict[str, Any],
) -> dict[str, Any] | None:
    if not json_path.exists() or not md_path.exists():
        return None
    try:
        payload = json.loads(json_path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("label") != label:
        return None
    if payload.get("query") != query:
        return None
    if payload.get("effective_query") != effective_query:
        return None
    if payload.get("from_date") != from_date or payload.get("to_date") != to_date:
        return None
    if payload.get("categories", []) != categories:
        return None
    old_req = payload.get("request", {})
    if not isinstance(old_req, dict):
        return None
    for key in ("search_query", "start", "max_results", "sortBy", "sortOrder"):
        if old_req.get(key) != request_params.get(key):
            return None
    results = payload.get("results", [])
    if not isinstance(results, list):
        return None
    return payload


def write_result_md(path: Path, payload: dict[str, Any], lang_code: str) -> None:
    if lang_code == "zh":
        lines = [
            f"# 查询结果: {payload.get('label', '')}",
            "",
            f"- **原始 Query**: `{payload.get('query', '')}`",
            f"- **实际 Query**: `{payload.get('effective_query', '')}`",
            f"- **结果数量（API 已按日期过滤）**: {len(payload.get('results', []))}",
            f"- **时间窗口**: {payload.get('from_date', '')} to {payload.get('to_date', '')}",
            "",
            "## 索引结果列表",
        ]
    else:
        lines = [
            f"# Query Result: {payload.get('label', '')}",
            "",
            f"- **Query**: `{payload.get('query', '')}`",
            f"- **Effective Query**: `{payload.get('effective_query', '')}`",
            f"- **Total Results (API date-filtered)**: {len(payload.get('results', []))}",
            f"- **Date Window**: {payload.get('from_date', '')} to {payload.get('to_date', '')}",
            "",
            "## Indexed Results",
        ]

    for item in payload.get("results", []):
        if lang_code == "zh":
            lines += [
                f"- `[idx={item['index']}]` **{item.get('title', '')}** (`{item.get('base_id', '')}`)",
                f"  - 发布时间: {item.get('published', '')}",
                f"  - 分类: {item.get('primary_category', '')}",
                f"  - 链接: {item.get('abs_url', '')}",
            ]
        else:
            lines += [
                f"- `[idx={item['index']}]` **{item.get('title', '')}** (`{item.get('base_id', '')}`)",
                f"  - Published: {item.get('published', '')}",
                f"  - Category: {item.get('primary_category', '')}",
                f"  - URL: {item.get('abs_url', '')}",
            ]

    path.write_text("\n".join(lines).rstrip() + "\n")


def run() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        print(f"[ERROR] run directory not found: {run_dir}")
        return 1

    task_meta = load_task_meta(run_dir)
    params = task_meta.get("params", {}) if isinstance(task_meta, dict) else {}
    language = args.language.strip() or str(params.get("language", "English"))
    lang_code = normalize_language(language)

    from_date = args.from_date or params.get("from_date", "")
    to_date = args.to_date or params.get("to_date", "")
    if not from_date or not to_date:
        print("[ERROR] from/to date missing. Provide --from-date/--to-date or initialize task metadata.")
        return 1

    if args.rate_state_path.strip():
        state_path = Path(args.rate_state_path).expanduser().resolve()
    else:
        state_path = default_rate_state_path(run_dir).resolve()

    try:
        # Validate input date format early and reject reversed windows.
        from_dt = parse_date(from_date, end_of_day=False)
        to_dt = parse_date(to_date, end_of_day=True)
    except ValueError as exc:
        print(f"[ERROR] invalid date: {exc}")
        return 1
    if from_dt > to_dt:
        print("[ERROR] from-date must be <= to-date.")
        return 1

    categories = split_csv(args.categories) or split_csv(",".join(params.get("categories", [])))
    base_query = build_effective_query(args.query, categories)
    effective_query = attach_submitted_date_clause(base_query, from_date, to_date)

    label = args.label.strip() or slugify(args.query)

    request_params = {
        "search_query": effective_query,
        "start": max(0, args.start),
        "max_results": max(1, args.max_results),
        "sortBy": args.sort_by,
        "sortOrder": args.sort_order,
    }
    url = f"{ARXIV_API_URL}?{urlencode(request_params)}"
    out_dir = run_dir / "query_results"
    out_dir.mkdir(exist_ok=True)
    json_path = out_dir / f"{label}.json"
    md_path = out_dir / f"{label}.md"

    cache_hit = False
    request_attempts = 0
    request_wait_seconds = 0.0

    cached_payload = None
    if not args.force:
        cached_payload = load_cached_payload_if_compatible(
            json_path=json_path,
            md_path=md_path,
            label=label,
            query=args.query,
            effective_query=effective_query,
            categories=categories,
            from_date=from_date,
            to_date=to_date,
            request_params=request_params,
        )

    if cached_payload is not None:
        payload = cached_payload
        payload["language"] = language
        payload["language_normalized"] = lang_code
        fetch_control = payload.get("fetch_control")
        if not isinstance(fetch_control, dict):
            fetch_control = {}
            payload["fetch_control"] = fetch_control
        fetch_control["rate_state_path"] = str(state_path)
        cache_hit = True
        request_attempts = 0
        request_wait_seconds = 0.0
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        # Ensure markdown language stays consistent with current request.
        write_result_md(md_path, payload, lang_code)
    else:
        try:
            xml_bytes, request_attempts, request_wait_seconds = fetch_with_retry(
                url=url,
                user_agent=args.user_agent,
                request_timeout=args.request_timeout,
                state_path=state_path,
                min_interval_sec=args.min_interval_sec,
                retry_max=args.retry_max,
                retry_base_sec=args.retry_base_sec,
                retry_max_sec=args.retry_max_sec,
                retry_jitter_sec=args.retry_jitter_sec,
            )
        except HTTPError:
            return 1
        except (URLError, TimeoutError):
            return 1

        fetched = parse_atom(xml_bytes)
        indexed = []
        for idx, paper in enumerate(fetched):
            indexed.append({"index": idx, **paper})

        payload = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "label": label,
            "query": args.query,
            "effective_query": effective_query,
            "categories": categories,
            "from_date": from_date,
            "to_date": to_date,
            "language": language,
            "language_normalized": lang_code,
            "request": request_params,
            "results": indexed,
            "fetch_control": {
                "min_interval_sec": args.min_interval_sec,
                "retry_max": args.retry_max,
                "retry_base_sec": args.retry_base_sec,
                "retry_max_sec": args.retry_max_sec,
                "retry_jitter_sec": args.retry_jitter_sec,
                "rate_state_path": str(state_path),
            },
        }

        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        write_result_md(md_path, payload, lang_code)

    # Update task meta query logs.
    query_plan = task_meta.setdefault("query_plan", []) if isinstance(task_meta, dict) else []
    if isinstance(query_plan, list):
        query_plan.append(
            {
                "label": label,
                "query": args.query,
                "effective_query": effective_query,
                "cache_hit": cache_hit,
            }
        )

    query_logs = task_meta.setdefault("query_fetch_logs", []) if isinstance(task_meta, dict) else []
    if isinstance(query_logs, list):
        query_logs.append(
            {
                "label": label,
                "api_returned_count": len(payload.get("results", [])),
                "date_filter_mode": "api_submittedDate",
                "json_path": str(json_path),
                "md_path": str(md_path),
                "language": language,
                "language_normalized": lang_code,
                "cache_hit": cache_hit,
                "request_attempts": request_attempts,
                "request_wait_seconds": round(request_wait_seconds, 3),
                "rate_state_path": str(state_path),
            }
        )
    if isinstance(task_meta, dict):
        save_task_meta(run_dir, task_meta)

    print(
        json.dumps(
            {
                "label": label,
                "query_json": str(json_path),
                "query_md": str(md_path),
                "api_returned_count": len(payload.get("results", [])),
                "language": language,
                "language_normalized": lang_code,
                "cache_hit": cache_hit,
                "request_attempts": request_attempts,
                "request_wait_seconds": round(request_wait_seconds, 3),
                "rate_state_path": str(state_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
