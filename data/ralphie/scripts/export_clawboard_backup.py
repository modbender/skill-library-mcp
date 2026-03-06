#!/usr/bin/env python3
"""
Export Clawboard state into deterministic JSON/JSONL files for git-friendly backups.

This exporter intentionally captures user/instance state (config/topics/tasks/logs)
and avoids derived vector/index stores that can be rebuilt.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _http_json(
    api_base: str,
    path: str,
    *,
    token: str | None,
    params: dict[str, Any] | None = None,
    timeout_sec: float = 30.0,
) -> Any:
    base = api_base.rstrip("/")
    query = f"?{urlencode(params)}" if params else ""
    url = f"{base}{path}{query}"
    headers = {"Accept": "application/json"}
    if token:
        headers["X-Clawboard-Token"] = token
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {path}: {payload[:400]}") from exc
    except URLError as exc:
        raise RuntimeError(f"Request failed for {path}: {exc}") from exc


def _fetch_paged(
    api_base: str,
    path: str,
    *,
    token: str | None,
    limit: int,
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    offset = 0
    while True:
        params: dict[str, Any] = {"limit": int(limit), "offset": int(offset)}
        if extra:
            params.update(extra)
        page = _http_json(api_base, path, token=token, params=params)
        if not isinstance(page, list):
            raise RuntimeError(f"Unexpected response for {path}: expected list")
        out.extend(item for item in page if isinstance(item, dict))
        if len(page) < limit:
            break
        offset += len(page)
    return out


def _sort_topics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: (str(r.get("id") or ""), str(r.get("name") or "")))


def _sort_tasks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda r: (
            str(r.get("id") or ""),
            str(r.get("topicId") or ""),
            str(r.get("title") or ""),
        ),
    )


def _sort_logs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda r: (
            str(r.get("createdAt") or ""),
            str(r.get("id") or ""),
        ),
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            f.write("\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export Clawboard state for git backup.")
    p.add_argument("--api-base", required=True, help="Clawboard API base URL (e.g., http://localhost:8010)")
    p.add_argument("--token", default="", help="Optional API token (X-Clawboard-Token)")
    p.add_argument("--out-dir", required=True, help="Output directory for backup files")
    p.add_argument("--task-page-size", type=int, default=1000, help="Pagination size for /api/tasks")
    p.add_argument("--log-page-size", type=int, default=1000, help="Pagination size for /api/log")
    p.add_argument("--include-raw", action="store_true", help="Request includeRaw=1 for logs")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out_dir).expanduser().resolve()
    token = (args.token or "").strip()

    config = _http_json(args.api_base, "/api/config", token=token)
    topics = _sort_topics(_http_json(args.api_base, "/api/topics", token=token) or [])
    tasks = _sort_tasks(
        _fetch_paged(
            args.api_base,
            "/api/tasks",
            token=token,
            limit=max(1, int(args.task_page_size)),
        )
    )
    log_extra = {"includeRaw": 1} if args.include_raw else None
    logs = _sort_logs(
        _fetch_paged(
            args.api_base,
            "/api/log",
            token=token,
            limit=max(1, int(args.log_page_size)),
            extra=log_extra,
        )
    )

    _write_json(out_dir / "config.json", config)
    _write_json(out_dir / "topics.json", topics)
    _write_json(out_dir / "tasks.json", tasks)
    _write_jsonl(out_dir / "logs.jsonl", logs)
    _write_json(
        out_dir / "manifest.json",
        {
            "version": 1,
            "apiBase": args.api_base.rstrip("/"),
            "counts": {
                "topics": len(topics),
                "tasks": len(tasks),
                "logs": len(logs),
            },
            "includeRaw": bool(args.include_raw),
            "newestLogCreatedAt": str(logs[-1].get("createdAt") if logs else ""),
        },
    )

    print(
        json.dumps(
            {
                "ok": True,
                "outDir": str(out_dir),
                "topics": len(topics),
                "tasks": len(tasks),
                "logs": len(logs),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:  # pragma: no cover - command-line error path
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
