"""CLI entrypoint for subprocess usage: python -m free_search."""

from __future__ import annotations

import argparse
import json
import sys

from . import configure_logging, get_quota_status, reset_quota, search, task_search, get_real_quota
from .router import SearchRouterError
from .storage import persist_search_payload, run_gc


def _normalize_compat_tokens(argv: list[str]) -> list[str]:
    if len(argv) >= 3 and argv[0].lower() == "brave" and argv[1].lower() == "search":
        return argv[2:]
    if len(argv) >= 2 and argv[0].lower() == "search":
        return argv[1:]
    return argv


def main(argv: list[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    normalized_args = _normalize_compat_tokens(raw_args)

    if normalized_args and normalized_args[0].lower() in ("status", "remaining", "quota"):
        parser = argparse.ArgumentParser(description="Show or reset provider quota usage")
        parser.add_argument("--config", default=None, help="Path to providers.yaml")
        parser.add_argument("--log-level", default="INFO")
        parser.add_argument("--compact", action="store_true", help="Print compact JSON")
        parser.add_argument("--reset", action="store_true", help="Reset quota counters before showing status")
        parser.add_argument("--real", action="store_true", help="Fetch real provider quota when supported")
        parser.add_argument("--probe", action="store_true", help="Allow probe requests for providers without quota endpoints (may consume quota)")
        args = parser.parse_args(normalized_args[1:])

        configure_logging(args.log_level)
        try:
            payload = (
                reset_quota(config_path=args.config)
                if args.reset
                else get_quota_status(config_path=args.config)
            )
        except Exception as exc:  # pragma: no cover - defensive for CLI consumers
            print(json.dumps({"error": f"unexpected_error: {exc}"}, ensure_ascii=False), file=sys.stderr)
            return 1

        # Add convenience totals for quick inspection
        totals = {"total_remaining": 0, "total_daily_quota": 0}
        for p in payload.get("providers", []):
            dq = p.get("daily_quota")
            rem = p.get("remaining")
            if isinstance(dq, int):
                totals["total_daily_quota"] += dq
            if isinstance(rem, int):
                totals["total_remaining"] += rem
        payload["totals"] = totals

        if args.real:
            real = get_real_quota(config_path=args.config, probe_brave=bool(args.probe))
            payload["real_quota"] = real

        indent = None if args.compact else 2
        print(json.dumps(payload, ensure_ascii=False, indent=indent))
        return 0

    if normalized_args and normalized_args[0].lower() == "gc":
        parser = argparse.ArgumentParser(description="Clean old search cache/report files")
        parser.add_argument("--cache-days", type=int, default=14)
        parser.add_argument("--report-days", type=int, default=None)
        parser.add_argument("--compact", action="store_true", help="Print compact JSON")
        args = parser.parse_args(normalized_args[1:])

        payload = run_gc(cache_days=args.cache_days, report_days=args.report_days)
        indent = None if args.compact else 2
        print(json.dumps(payload, ensure_ascii=False, indent=indent))
        return 0

    if normalized_args and normalized_args[0].lower() == "task":
        parser = argparse.ArgumentParser(description="Run task-level multi-query search")
        parser.add_argument("task", nargs="+", help="Task or goal statement")
        parser.add_argument("--max-results", type=int, default=5)
        parser.add_argument("--max-queries", type=int, default=6)
        parser.add_argument("--max-merged-results", type=int, default=None)
        parser.add_argument("--workers", type=int, default=1)
        parser.add_argument("--config", default=None, help="Path to providers.yaml")
        parser.add_argument("--log-level", default="INFO")
        parser.add_argument("--compact", action="store_true", help="Print compact JSON")
        args = parser.parse_args(normalized_args[1:])
        task = " ".join(args.task).strip()

        # Preset prefixes for interaction convenience:
        # - @dual: workers=2
        # - @deep: workers=3 and max_queries>=8 (depth first, not brute force concurrency)
        effective_workers = args.workers
        effective_max_queries = args.max_queries
        if task.startswith("@dual"):
            task = task[len("@dual"):].strip()
            effective_workers = 2
        elif task.startswith("@deep"):
            task = task[len("@deep"):].strip()
            effective_workers = 3
            effective_max_queries = max(effective_max_queries, 8)

        # Quota-aware degradation: when quota usage is high, reduce concurrency.
        try:
            status = get_quota_status(config_path=args.config)
            max_pct = 0.0
            for p in status.get("providers", []):
                pct = p.get("percentage_used")
                if isinstance(pct, (int, float)):
                    max_pct = max(max_pct, float(pct))
            if max_pct >= 80.0 and effective_workers > 2:
                effective_workers = 2
        except Exception:
            pass

        configure_logging(args.log_level)
        try:
            payload = task_search(
                task,
                max_results_per_query=args.max_results,
                max_queries=effective_max_queries,
                max_merged_results=args.max_merged_results,
                max_workers=effective_workers,
                config_path=args.config,
            )
        except SearchRouterError as exc:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
        except Exception as exc:  # pragma: no cover - defensive for CLI consumers
            print(json.dumps({"error": f"unexpected_error: {exc}"}, ensure_ascii=False), file=sys.stderr)
            return 1

        storage_info = persist_search_payload(query=task, payload=payload, mode="task")
        payload.setdefault("meta", {})["storage"] = storage_info

        indent = None if args.compact else 2
        print(json.dumps(payload, ensure_ascii=False, indent=indent))
        return 0

    parser = argparse.ArgumentParser(description="Run failover web search")
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument("--max-results", type=int, default=8)
    parser.add_argument("--config", default=None, help="Path to providers.yaml")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON")
    args = parser.parse_args(normalized_args)
    query = " ".join(args.query).strip()

    configure_logging(args.log_level)
    try:
        payload = search(query, max_results=args.max_results, config_path=args.config)
    except SearchRouterError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive for CLI consumers
        print(json.dumps({"error": f"unexpected_error: {exc}"}, ensure_ascii=False), file=sys.stderr)
        return 1

    storage_info = persist_search_payload(query=query, payload=payload, mode="search")
    payload.setdefault("meta", {})["storage"] = storage_info

    indent = None if args.compact else 2
    print(json.dumps(payload, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
