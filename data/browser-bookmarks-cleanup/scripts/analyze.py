"""Analyze bookmarks for cleanup opportunities."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import parse

from _common import (
    WEAK_NAMES,
    bookmark_projection,
    clean_host,
    close_sqlite,
    folder_projection,
    has_tracking_params,
    load_bookmarks_auto,
    maybe_registrable_domain,
    normalize_name,
    normalize_url,
    normalize_url_without_tracking,
    now_iso,
    open_sqlite_ro,
    ts_to_dt,
    walk_nodes,
)


def _grouped_bookmarks(groups: dict[str, list[dict[str, Any]]], max_groups: int, max_per: int) -> list[dict[str, Any]]:
    rows = []
    for gkey, items in groups.items():
        if len(items) <= 1:
            continue
        rows.append({"group": gkey, "count": len(items), "items": [bookmark_projection(x) for x in items[:max_per]]})
    rows.sort(key=lambda x: x["count"], reverse=True)
    return rows[:max_groups]


# --- History index ---

def _build_history_index(history_db_path: Path, browser: str) -> tuple[dict[str, dict[str, Any]], int]:
    history_index: dict[str, dict[str, Any]] = {}
    scanned = 0
    query = (
        "SELECT url, last_visit_date, visit_count, typed FROM moz_places WHERE url IS NOT NULL"
        if browser == "firefox"
        else "SELECT url, last_visit_time, visit_count, typed_count FROM urls"
    )
    conn = open_sqlite_ro(history_db_path)
    try:
        for url, lvt, vc, tc in conn.execute(query):
            scanned += 1
            if not isinstance(url, str):
                continue
            lvt, vc, tc = int(lvt or 0), int(vc or 0), int(tc or 0)
            for key in {normalize_url(url), normalize_url_without_tracking(url)}:
                if key:
                    row = history_index.setdefault(key, {"visit_count": 0, "typed_count": 0, "last_visit_time": 0})
                    row["visit_count"] = max(row["visit_count"], vc)
                    row["typed_count"] = max(row["typed_count"], tc)
                    row["last_visit_time"] = max(row["last_visit_time"], lvt)
    finally:
        close_sqlite(conn)
    return history_index, scanned


def _select_history_row(history_index: dict[str, dict[str, Any]], url: str) -> dict[str, Any] | None:
    matches = [history_index[k] for k in {normalize_url(url), normalize_url_without_tracking(url)} if k and k in history_index]
    if not matches:
        return None
    matches.sort(key=lambda x: (x["last_visit_time"], x["visit_count"]), reverse=True)
    return matches[0]


def _with_history_fields(item: dict[str, Any], hrow: dict[str, Any], now_dt: datetime, browser: str) -> dict[str, Any]:
    out = bookmark_projection(item)
    lvt = hrow.get("last_visit_time", 0)
    out["visit_count"] = hrow.get("visit_count", 0)
    dt = ts_to_dt(lvt, browser) if lvt else None
    if dt:
        out["last_visited_at"] = dt.isoformat()
        out["days_since_last_visit"] = max((now_dt - dt).days, 0)
    else:
        out["last_visited_at"] = None
        out["days_since_last_visit"] = None
    return out


def _choose_history_path(bookmarks_path: Path, history_db_arg: str | None, browser: str) -> Path | None:
    if history_db_arg:
        candidate = Path(history_db_arg).expanduser()
        return candidate if candidate.exists() else None
    if browser == "firefox":
        return bookmarks_path if bookmarks_path.exists() else None
    sibling = bookmarks_path.parent / "History"
    return sibling if sibling.exists() else None


# --- Main analysis ---

def run(args: argparse.Namespace) -> int:
    path = Path(args.bookmarks).expanduser()
    data, browser = load_bookmarks_auto(path)
    urls, folders, _ = walk_nodes(data)

    exact: dict[str, list] = defaultdict(list)
    semantic: dict[str, list] = defaultdict(list)
    tracking_variants: dict[str, list] = defaultdict(list)
    tracking_flags: dict[str, bool] = defaultdict(bool)
    by_subdomain: Counter[str] = Counter()
    by_domain: Counter[str] = Counter()
    http_only = []
    weak_names = []
    old_candidates = []
    invalid_urls = []
    stale_by_last_visit = []
    never_visited = []
    now_dt = datetime.now(timezone.utc)

    for item in urls:
        raw_url = item["url"]
        n_exact = normalize_url(raw_url)
        n_semantic = normalize_url(raw_url, drop_query=True)
        n_no_track = normalize_url_without_tracking(raw_url)

        if n_exact:
            exact[n_exact].append(item)
        if n_semantic:
            semantic[n_semantic].append(item)
        if n_no_track:
            tracking_variants[n_no_track].append(item)
            if has_tracking_params(raw_url):
                tracking_flags[n_no_track] = True

        try:
            parsed = parse.urlsplit(raw_url)
        except ValueError:
            parsed = None

        if not parsed or parsed.scheme.lower() not in {"http", "https"}:
            invalid_urls.append(bookmark_projection(item))
            continue

        host = clean_host(parsed.hostname or "")
        if host:
            by_subdomain[host] += 1
            by_domain[maybe_registrable_domain(host)] += 1
        if parsed.scheme.lower() == "http":
            http_only.append(bookmark_projection(item))
        if normalize_name(item["name"]).lower() in WEAK_NAMES:
            weak_names.append(bookmark_projection(item))

        date_added = ts_to_dt(item.get("date_added"), browser)
        if date_added:
            age_days = (now_dt - date_added).days
            if age_days >= args.stale_days:
                row = bookmark_projection(item)
                row["age_days"] = age_days
                old_candidates.append(row)

    empty_folders = [folder_projection(f) for f in folders if not f["is_root"] and f["child_count"] == 0]
    singleton_folders = [folder_projection(f) for f in folders if not f["is_root"] and f["child_count"] == 1]
    deep_folders = [folder_projection(f) for f in folders if not f["is_root"] and f["path"].count("/") > args.max_depth]
    large_folders = [folder_projection(f) for f in folders if not f["is_root"] and f["child_count"] >= args.large_folder_threshold]

    dup_exact = _grouped_bookmarks(exact, args.max_groups, args.max_items_per_group)
    dup_semantic = _grouped_bookmarks(semantic, args.max_groups, args.max_items_per_group)
    dup_tracking = [
        g for g in _grouped_bookmarks(tracking_variants, args.max_groups, args.max_items_per_group)
        if len({i["url"] for i in g["items"]}) > 1 and tracking_flags.get(g.get("group", ""), False)
    ]
    old_candidates.sort(key=lambda x: x.get("age_days", 0), reverse=True)

    # History enrichment
    history_summary: dict[str, Any] = {"history_db_used": False}
    history_path = _choose_history_path(path, args.history_db, browser)
    if history_path:
        try:
            history_index, scanned = _build_history_index(history_path, browser)
            history_summary.update({"history_db_used": True, "history_db": str(history_path), "history_rows_scanned": scanned})
            matched = unmatched = 0
            for item in urls:
                hrow = _select_history_row(history_index, item["url"])
                if hrow:
                    matched += 1
                    enriched = _with_history_fields(item, hrow, now_dt, browser)
                    days = enriched.get("days_since_last_visit")
                    if days is not None and days >= args.stale_visit_days:
                        stale_by_last_visit.append(enriched)
                else:
                    unmatched += 1
                    never_visited.append(bookmark_projection(item))
            stale_by_last_visit.sort(key=lambda x: x.get("days_since_last_visit", 0), reverse=True)
            history_summary.update({
                "history_matched_bookmarks": matched, "history_unmatched_bookmarks": unmatched,
                "history_stale_visit_candidates": len(stale_by_last_visit),
                "history_never_visited_candidates": len(never_visited),
            })
        except Exception as exc:
            history_summary["history_error"] = str(exc)

    m = args.max_list_items
    report: dict[str, Any] = {
        "generated_at": now_iso(), "browser": browser, "bookmarks_file": str(path),
        "summary": {
            "total_bookmarks": len(urls),
            "total_folders": len([f for f in folders if not f["is_root"]]),
            "duplicate_exact_groups": len(dup_exact),
            "duplicate_semantic_groups": len(dup_semantic),
            "tracking_variant_groups": len(dup_tracking),
            "http_links": len(http_only), "empty_folders": len(empty_folders),
            "singleton_folders": len(singleton_folders), "deep_folders": len(deep_folders),
            "large_folders": len(large_folders), "weak_names": len(weak_names),
            "old_candidates": len(old_candidates), "invalid_urls": len(invalid_urls),
        },
        "duplicates": {
            "exact_url": dup_exact, "semantic_same_host_path": dup_semantic,
            "tracking_param_variants": dup_tracking,
        },
        "concentration": {
            "by_subdomain": [{"key": k, "count": c} for k, c in by_subdomain.most_common(args.max_domain_rows)],
            "by_domain_approx": [{"key": k, "count": c} for k, c in by_domain.most_common(args.max_domain_rows)],
        },
        "folder_quality": {
            "empty_folders": empty_folders[:m], "singleton_folders": singleton_folders[:m],
            "deep_folders": deep_folders[:m], "large_folders": large_folders[:m],
        },
        "url_quality": {
            "http_only": http_only[:m], "weak_names": weak_names[:m],
            "invalid_urls": invalid_urls[:m], "old_candidates": old_candidates[:m],
            "stale_by_last_visit": stale_by_last_visit[:m],
            "never_visited_candidates": never_visited[:m],
        },
        "history": history_summary, "recommendations": [],
    }

    recs = report["recommendations"]
    if dup_exact:       recs.append("Remove exact duplicates.")
    if dup_semantic:    recs.append("Review semantic duplicates.")
    if dup_tracking:    recs.append("Normalize URLs by dropping tracking parameters.")
    if http_only:       recs.append("Upgrade HTTP bookmarks to HTTPS.")
    if empty_folders:   recs.append("Delete empty folders.")
    if singleton_folders: recs.append("Flatten singleton folders.")
    if deep_folders:    recs.append("Reduce deep folder nesting.")
    if large_folders:   recs.append("Split oversized folders.")
    if history_summary.get("history_db_used") and stale_by_last_visit:
        recs.append("Archive bookmarks not visited for a long time.")
    if history_summary.get("history_db_used") and never_visited:
        recs.append("Review bookmarks never seen in local history.")

    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).expanduser().write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


def add_subparser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("analyze", help="Analyze bookmarks for cleanup opportunities.")
    p.add_argument("--bookmarks", required=True, help="Path to Chrome Bookmarks JSON or Firefox places.sqlite.")
    p.add_argument("--history-db", help="Optional history DB path. Defaults to auto-detect.")
    p.add_argument("--output", help="Write JSON report to this path.")
    p.add_argument("--stale-days", type=int, default=730)
    p.add_argument("--stale-visit-days", type=int, default=365)
    p.add_argument("--max-depth", type=int, default=5)
    p.add_argument("--large-folder-threshold", type=int, default=100)
    p.add_argument("--max-groups", type=int, default=100)
    p.add_argument("--max-items-per-group", type=int, default=20)
    p.add_argument("--max-domain-rows", type=int, default=100)
    p.add_argument("--max-list-items", type=int, default=200)
    p.set_defaults(func=run)
