"""Task-level search: expand a goal into multiple queries and aggregate results."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .router import SearchRouter, SearchRouterError


_SPLIT_PATTERN = re.compile(r"[，。；;、/|]+|\s+(?:and|or|vs|versus)\s+", re.IGNORECASE)
_CONJUNCTION_PATTERN = re.compile(r"\s+(?:和|及|以及|并|对比|比较|vs|versus)\s+", re.IGNORECASE)
_STOPWORDS = {
    "的", "了", "和", "及", "以及", "并", "对比", "比较", "是", "如何", "为什么", "怎么样",
    "what", "how", "why", "compare", "vs", "versus", "the", "a", "an", "of", "to", "for",
}
_TASK_PREFIXES = (
    "请", "帮我", "请帮我", "请你", "帮我查", "帮我搜索", "搜索", "查一下", "查",
    "对比", "比较", "请对比", "请比较",
)
_TRACKING_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "igshid", "mc_cid", "mc_eid", "spm", "ref",
}


def _normalize_query(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip())


def _strip_task_prefix(text: str) -> str:
    s = _normalize_query(text)
    changed = True
    while changed and s:
        changed = False
        for p in _TASK_PREFIXES:
            if s.startswith(p):
                ns = _normalize_query(s[len(p):])
                if ns != s:
                    s = ns
                    changed = True
    return s


def _uniq_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _extract_candidates(text: str) -> list[str]:
    raw = _SPLIT_PATTERN.split(text)
    cleaned: list[str] = []
    for part in raw:
        part = _strip_task_prefix(part)
        part = _normalize_query(part)
        if not part:
            continue
        tokens = [t for t in re.split(r"\s+", part) if t and t.lower() not in _STOPWORDS]
        if not tokens:
            continue
        cleaned.append(" ".join(tokens))
    return _uniq_preserve(cleaned)


def _build_compare_queries(text: str) -> list[str]:
    # Handle patterns like "A 对比 B" / "A vs B"
    normalized = _strip_task_prefix(text)
    parts = _CONJUNCTION_PATTERN.split(normalized)
    parts = [_normalize_query(p) for p in parts if _normalize_query(p)]
    if len(parts) >= 2:
        left = _strip_task_prefix(parts[0])
        right = _strip_task_prefix(parts[1])
        if left and right:
            return _uniq_preserve(
                [
                    f"{left} vs {right}",
                    f"{left} {right} 对比",
                    f"{left} {right} 优缺点",
                    f"{left} {right} 区别",
                    f"{left} {right} benchmark",
                ]
            )
    return []


def generate_task_queries(task: str, *, max_queries: int = 6) -> list[str]:
    task = _normalize_query(task)
    if not task:
        raise ValueError("task must be non-empty")

    core_task = _strip_task_prefix(task) or task

    queries: list[str] = [core_task]
    queries.extend(_build_compare_queries(core_task))

    # Expand with extracted candidates (entities or sub-phrases)
    candidates = _extract_candidates(core_task)
    for cand in candidates:
        if cand != core_task:
            queries.append(cand)

    # Add intent hints for common question types
    lower = core_task.lower()
    if any(k in core_task for k in ["如何", "怎么"]) or "how" in lower:
        queries.append(f"{core_task} 步骤")
        queries.append(f"{core_task} 方法")
    if any(k in core_task for k in ["为什么"]) or "why" in lower:
        queries.append(f"{core_task} 原因")
    if any(k in core_task for k in ["是什么"]) or "what is" in lower or "what's" in lower:
        queries.append(f"{core_task} 定义")

    queries = _uniq_preserve([_normalize_query(q) for q in queries if q.strip()])
    return queries[: max(1, max_queries)]


def _canonicalize_url(url: str) -> str:
    try:
        p = urlparse(url)
        scheme = (p.scheme or "https").lower()
        netloc = p.netloc.lower()
        path = p.path or "/"
        # Normalize trailing slash (except root)
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        qs = parse_qsl(p.query, keep_blank_values=True)
        qs = [(k, v) for (k, v) in qs if k.lower() not in _TRACKING_QUERY_KEYS]
        qs.sort(key=lambda x: (x[0], x[1]))
        query = urlencode(qs, doseq=True)
        return urlunparse((scheme, netloc, path, "", query, ""))
    except Exception:
        return url


def _run_one_query(
    router: SearchRouter,
    query: str,
    *,
    max_results_per_query: int,
) -> dict[str, Any]:
    try:
        payload = router.search(query, max_results=max_results_per_query)
        results = payload.get("results", [])
        return {
            "query": query,
            "provider": payload.get("provider"),
            "results": results,
            "meta": payload.get("meta"),
            "status": "ok",
            "error": None,
        }
    except SearchRouterError as exc:
        return {
            "query": query,
            "provider": None,
            "results": [],
            "meta": None,
            "status": "failed",
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover
        return {
            "query": query,
            "provider": None,
            "results": [],
            "meta": None,
            "status": "failed",
            "error": f"unexpected_error: {exc}",
        }


def task_search(
    task: str,
    *,
    max_results_per_query: int = 5,
    max_queries: int = 6,
    max_merged_results: int | None = None,
    max_workers: int = 1,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Expand a task into multiple queries and aggregate results."""
    if not task or not task.strip():
        raise ValueError("task must be non-empty")
    if max_results_per_query <= 0:
        raise ValueError("max_results_per_query must be > 0")
    if max_queries <= 0:
        raise ValueError("max_queries must be > 0")
    if max_workers <= 0:
        raise ValueError("max_workers must be > 0")

    router = SearchRouter(config_path=config_path)
    queries = generate_task_queries(task, max_queries=max_queries)

    grouped_results: list[dict[str, Any]] = []
    merged: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    # Concurrent execution to reduce latency on multi-query tasks.
    workers = min(max_workers, max(1, len(queries)))
    idx_map = {q: i for i, q in enumerate(queries)}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run_one_query, router, q, max_results_per_query=max_results_per_query)
            for q in queries
        ]
        for fut in as_completed(futs):
            grouped_results.append(fut.result())

    # Preserve original query order in output.
    grouped_results.sort(key=lambda x: idx_map.get(x.get("query", ""), 10**9))

    raw_result_count = 0
    success_queries = 0
    failed_queries = 0

    for g in grouped_results:
        results = g.get("results", []) or []
        raw_result_count += len(results)
        if g.get("status") == "ok":
            success_queries += 1
        else:
            failed_queries += 1

        for item in results:
            url = (item or {}).get("url")
            if not url:
                continue
            key = _canonicalize_url(url)
            if key in seen_urls:
                continue
            seen_urls.add(key)
            merged.append(item)
            if isinstance(max_merged_results, int) and max_merged_results > 0 and len(merged) >= max_merged_results:
                break
        if isinstance(max_merged_results, int) and max_merged_results > 0 and len(merged) >= max_merged_results:
            break

    deduped_count = len(merged)
    dedupe_ratio = 0.0
    if raw_result_count > 0:
        dedupe_ratio = round(1 - (deduped_count / raw_result_count), 4)

    return {
        "task": task,
        "queries": queries,
        "grouped_results": grouped_results,
        "merged_results": merged,
        "meta": {
            "query_count": len(queries),
            "success_queries": success_queries,
            "failed_queries": failed_queries,
            "max_results_per_query": max_results_per_query,
            "raw_result_count": raw_result_count,
            "deduped_count": deduped_count,
            "dedupe_ratio": dedupe_ratio,
            "max_workers": workers,
            "max_merged_results": max_merged_results,
        },
    }
