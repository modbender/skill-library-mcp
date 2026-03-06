#!/usr/bin/env python3
"""
Continuous LangFuse -> routing-policy optimization loop for OpenClaw/OpenRouter.

This runner:
1) Fetches recent observations and scores from LangFuse Public API.
2) Builds a staged routing policy via closed_loop_prompt_ops.py.
3) Applies a conservative promotion gate against the live policy.
4) Persists cycle memory to reduce oscillation.
"""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_CONFIG_PATH = Path.home() / ".openclaw" / "optimizer" / "config.json"

CONFIG_DEFAULTS: Dict[str, Any] = {
    "langfuse_host": "https://us.cloud.langfuse.com",
    "environment": "",
    "window_hours": 24.0,
    "limit": 200,
    "max_pages": 50,
    "http_timeout_sec": 60,
    "out_dir": str(Path.home() / ".openclaw" / "optimizer"),
    "live_policy_path": str(Path.home() / ".openclaw" / "llm_routing_policy.json"),
    "memory_file": str(Path.home() / ".openclaw" / "optimizer" / "optimizer_memory.json"),
    "max_memory_cycles": 500,
    "promote_live_policy": False,
    "write_memory": False,
    "min_switch_gain": 0.01,
    "max_quality_drop": 0.02,
    "min_samples": 5,
    "quality_floor": 0.75,
    "quality_weight": 0.65,
    "cost_weight": 0.2,
    "latency_weight": 0.15,
    "max_cost_p95": None,
    "max_latency_p95_ms": None,
    "prompt_token_p95_warn": 20000,
    "prompt_ratio_warn": 8.0,
    "interval_min": 30.0,
}

CONFIG_KEYS = set(CONFIG_DEFAULTS.keys())
SENSITIVE_KEYS = {"langfuse_public_key", "langfuse_secret_key"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Optional[dict]:
    try:
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def config_file_path(args: argparse.Namespace) -> Path:
    raw = getattr(args, "config_file", "") or str(DEFAULT_CONFIG_PATH)
    return Path(raw).expanduser()


def load_config(path: Path) -> dict:
    payload = read_json(path)
    if not isinstance(payload, dict):
        return {}
    cfg = payload.get("config")
    if isinstance(cfg, dict):
        return cfg
    return payload


def apply_effective_config(args: argparse.Namespace, config: dict) -> argparse.Namespace:
    for key, default in CONFIG_DEFAULTS.items():
        cli_value = getattr(args, key, None)
        if cli_value is not None:
            setattr(args, key, cli_value)
            continue
        if key in config:
            setattr(args, key, config.get(key))
            continue
        setattr(args, key, default)

    for key in SENSITIVE_KEYS:
        cli_value = getattr(args, key, None)
        if cli_value is not None:
            setattr(args, key, cli_value)
            continue
        if key in config:
            setattr(args, key, config.get(key))
    return args


def cli_overrides(args: argparse.Namespace) -> dict:
    overrides = {}
    for key in CONFIG_KEYS.union(SENSITIVE_KEYS):
        if hasattr(args, key):
            value = getattr(args, key)
            if value is not None:
                overrides[key] = value
    return overrides


def save_config(path: Path, config: dict) -> None:
    payload = {
        "version": "1",
        "updated_at": to_iso_z(now_utc()),
        "config": config,
    }
    write_json(path, payload)


def basic_auth_header(public_key: str, secret_key: str) -> str:
    raw = f"{public_key}:{secret_key}".encode("utf-8")
    token = base64.b64encode(raw).decode("ascii")
    return f"Basic {token}"


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        return value
    return None


def to_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def fetch_langfuse_items(
    host: str,
    endpoint: str,
    auth_header: str,
    from_ts: str,
    to_ts: str,
    limit: int,
    max_pages: int,
    extra_params: Optional[dict] = None,
    timeout_sec: int = 60,
) -> List[dict]:
    """
    Fetch LangFuse v2 resources with tolerant pagination.
    Supports nextCursor and page-style pagination depending on endpoint behavior.
    """
    host = host.rstrip("/")
    extra_params = dict(extra_params or {})

    all_items: List[dict] = []
    seen_ids: set = set()

    cursor: Optional[str] = None
    page = 1
    for _ in range(max_pages):
        params = {
            "fromTimestamp": from_ts,
            "toTimestamp": to_ts,
            "limit": limit,
        }
        params.update(extra_params)
        params["page"] = cursor if cursor else page
        query = urlencode(params, doseq=True)
        url = f"{host}{endpoint}?{query}"

        req = Request(
            url=url,
            method="GET",
            headers={
                "Authorization": auth_header,
                "Accept": "application/json",
            },
        )
        with urlopen(req, timeout=timeout_sec) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        data = payload.get("data")
        if not isinstance(data, list):
            break

        new_count = 0
        for row in data:
            if not isinstance(row, dict):
                continue
            row_id = first_non_empty(row.get("id"), row.get("observationId"), row.get("traceId"))
            if row_id is not None:
                key = str(row_id)
                if key in seen_ids:
                    continue
                seen_ids.add(key)
            all_items.append(row)
            new_count += 1

        meta = payload.get("meta")
        meta = meta if isinstance(meta, dict) else {}
        next_cursor = first_non_empty(meta.get("nextCursor"), payload.get("nextCursor"))
        if next_cursor:
            cursor = str(next_cursor)
            continue

        total_pages = meta.get("totalPages")
        if isinstance(total_pages, int) and page < total_pages:
            page += 1
            continue

        if new_count >= limit:
            page += 1
            continue
        break

    return all_items


def normalize_scores(raw_scores: List[dict]) -> List[dict]:
    out: List[dict] = []
    for row in raw_scores:
        if not isinstance(row, dict):
            continue
        score = first_non_empty(row.get("value"), row.get("score"), row.get("numeric_score"))
        event_id = first_non_empty(
            row.get("observationId"),
            row.get("observation_id"),
            row.get("generation_id"),
            row.get("event_id"),
            row.get("id"),
            row.get("traceId"),
        )
        if event_id is None or score is None:
            continue
        out.append(
            {
                "event_id": str(event_id),
                "score": score,
                "metric": first_non_empty(row.get("name"), row.get("metric"), "score"),
                "created_at": first_non_empty(row.get("createdAt"), row.get("created_at")),
                "source_id": first_non_empty(row.get("id"), row.get("scoreId")),
            }
        )
    return out


def write_scores_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["event_id", "score", "metric", "created_at", "source_id"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in headers})


def policy_route_map(policy: dict) -> Dict[str, dict]:
    routes = {}
    for r in policy.get("routes", []):
        if not isinstance(r, dict):
            continue
        task_key = str(r.get("task_key") or "").strip().lower()
        if task_key:
            routes[task_key] = r
    return routes


def route_quality_cost(route: dict) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    observed = route.get("observed")
    observed = observed if isinstance(observed, dict) else {}
    return (
        to_float(observed.get("quality_mean")),
        to_float(observed.get("cost_mean")),
        to_float(observed.get("latency_p95_ms")),
    )


def should_promote_policy(
    staged: dict,
    live: Optional[dict],
    min_switch_gain: float,
    max_quality_drop: float,
) -> Tuple[bool, List[str]]:
    if not isinstance(live, dict):
        return True, ["No live policy exists yet."]

    staged_routes = policy_route_map(staged)
    live_routes = policy_route_map(live)
    reasons: List[str] = []
    blocked = 0

    for task_key, staged_route in staged_routes.items():
        live_route = live_routes.get(task_key)
        if not isinstance(live_route, dict):
            continue
        old_model = str(live_route.get("selected_model") or "")
        new_model = str(staged_route.get("selected_model") or "")
        if not old_model or not new_model or old_model == new_model:
            continue

        old_q, old_c, old_l = route_quality_cost(live_route)
        new_q, new_c, new_l = route_quality_cost(staged_route)

        q_delta = (new_q - old_q) if (new_q is not None and old_q is not None) else 0.0
        c_gain = ((old_c - new_c) / old_c) if (old_c and new_c is not None and old_c > 0) else 0.0
        l_gain = ((old_l - new_l) / old_l) if (old_l and new_l is not None and old_l > 0) else 0.0
        switch_gain = q_delta + (0.10 * c_gain) + (0.05 * l_gain)

        if q_delta < -abs(max_quality_drop) or switch_gain < min_switch_gain:
            blocked += 1
            reasons.append(
                f"Blocked switch for task '{task_key}' ({old_model} -> {new_model}); "
                f"q_delta={q_delta:.4f}, switch_gain={switch_gain:.4f}"
            )

    if blocked > 0:
        return False, reasons
    return True, ["Promotion gate passed."]


def update_memory(memory_file: Path, cycle_entry: dict, max_cycles: int) -> None:
    payload = read_json(memory_file) or {"version": "1", "cycles": []}
    cycles = payload.get("cycles")
    if not isinstance(cycles, list):
        cycles = []
    cycles.append(cycle_entry)
    if len(cycles) > max_cycles:
        cycles = cycles[-max_cycles:]
    payload["cycles"] = cycles
    payload["updated_at"] = to_iso_z(now_utc())
    write_json(memory_file, payload)


def run_full_cycle(script_path: Path, args: argparse.Namespace, obs_file: Path, scores_file: Optional[Path], out_dir: Path) -> None:
    cmd = [
        sys.executable,
        str(script_path),
        "full-cycle",
        "--langfuse-json",
        str(obs_file),
        "--out-dir",
        str(out_dir),
        "--dedupe",
        "--min-samples",
        str(args.min_samples),
        "--quality-floor",
        str(args.quality_floor),
        "--quality-weight",
        str(args.quality_weight),
        "--cost-weight",
        str(args.cost_weight),
        "--latency-weight",
        str(args.latency_weight),
        "--prompt-token-p95-warn",
        str(args.prompt_token_p95_warn),
        "--prompt-ratio-warn",
        str(args.prompt_ratio_warn),
    ]
    if args.max_cost_p95 is not None:
        cmd.extend(["--max-cost-p95", str(args.max_cost_p95)])
    if args.max_latency_p95_ms is not None:
        cmd.extend(["--max-latency-p95-ms", str(args.max_latency_p95_ms)])
    if scores_file and scores_file.exists():
        cmd.extend(["--scores", str(scores_file)])
    subprocess.run(cmd, check=True)


def run_once(args: argparse.Namespace) -> int:
    public_key = args.langfuse_public_key or os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = args.langfuse_secret_key or os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not public_key or not secret_key:
        print("Missing LangFuse credentials. Set --langfuse-public-key/--langfuse-secret-key or env vars.", file=sys.stderr)
        return 2

    end_dt = now_utc()
    start_dt = end_dt - timedelta(hours=args.window_hours)
    from_ts = to_iso_z(start_dt)
    to_ts = to_iso_z(end_dt)
    stamp = end_dt.strftime("%Y%m%dT%H%M%SZ")

    out_dir = Path(args.out_dir).expanduser()
    raw_dir = out_dir / "raw" / stamp
    cycle_dir = out_dir / "cycles" / stamp
    raw_dir.mkdir(parents=True, exist_ok=True)
    cycle_dir.mkdir(parents=True, exist_ok=True)

    auth = basic_auth_header(public_key, secret_key)
    obs_params = {}
    if args.environment:
        obs_params["environment"] = args.environment

    observations = fetch_langfuse_items(
        host=args.langfuse_host,
        endpoint="/api/public/v2/observations",
        auth_header=auth,
        from_ts=from_ts,
        to_ts=to_ts,
        limit=args.limit,
        max_pages=args.max_pages,
        extra_params=obs_params,
        timeout_sec=args.http_timeout_sec,
    )
    raw_obs_file = raw_dir / "langfuse_observations.json"
    raw_obs_file.write_text(json.dumps(observations, ensure_ascii=True, indent=2), encoding="utf-8")

    scores = fetch_langfuse_items(
        host=args.langfuse_host,
        endpoint="/api/public/v2/scores",
        auth_header=auth,
        from_ts=from_ts,
        to_ts=to_ts,
        limit=args.limit,
        max_pages=args.max_pages,
        extra_params={},
        timeout_sec=args.http_timeout_sec,
    )
    normalized_scores = normalize_scores(scores)
    scores_file = raw_dir / "langfuse_scores.csv"
    write_scores_csv(scores_file, normalized_scores)

    core_script = Path(__file__).with_name("closed_loop_prompt_ops.py")
    run_full_cycle(
        script_path=core_script,
        args=args,
        obs_file=raw_obs_file,
        scores_file=scores_file if normalized_scores else None,
        out_dir=cycle_dir,
    )

    staged_policy_path = cycle_dir / "routing_policy.json"
    staged_policy = read_json(staged_policy_path)
    if not isinstance(staged_policy, dict):
        print("Staged policy was not generated correctly.", file=sys.stderr)
        return 2

    live_policy_path = Path(args.live_policy_path).expanduser()
    live_policy = read_json(live_policy_path)
    gate_passed, reasons = should_promote_policy(
        staged=staged_policy,
        live=live_policy,
        min_switch_gain=args.min_switch_gain,
        max_quality_drop=args.max_quality_drop,
    )
    policy_applied = bool(gate_passed and args.promote_live_policy)
    if policy_applied:
        live_policy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(staged_policy_path, live_policy_path)

    cycle_entry = {
        "timestamp": to_iso_z(end_dt),
        "window_from": from_ts,
        "window_to": to_ts,
        "observation_count": len(observations),
        "score_count": len(normalized_scores),
        "cycle_dir": str(cycle_dir),
        "live_policy_path": str(live_policy_path),
        "promotion_gate_passed": bool(gate_passed),
        "promotion_enabled": bool(args.promote_live_policy),
        "promotion_decision": (
            "promoted"
            if policy_applied
            else ("blocked" if not gate_passed else "gated_pass_no_apply")
        ),
        "promotion_reasons": reasons,
        "global_prompt_stats": staged_policy.get("global_prompt_stats", {}),
    }
    if args.write_memory:
        memory_file = Path(args.memory_file).expanduser()
        update_memory(memory_file, cycle_entry, max_cycles=args.max_memory_cycles)

    print(f"Cycle completed at {to_iso_z(end_dt)}")
    print(f"  observations: {len(observations)}")
    print(f"  scores:       {len(normalized_scores)}")
    print(f"  cycle_dir:    {cycle_dir}")
    print(f"  gate_passed:  {gate_passed}")
    print(f"  applied:      {policy_applied}")
    print(f"  decision:     {cycle_entry['promotion_decision']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LangFuse-driven continuous optimization loop for OpenClaw.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--config-file", default=str(DEFAULT_CONFIG_PATH), help="Persistent config file path.")
        p.add_argument("--save-config", action="store_true", help="Persist effective settings to --config-file.")
        p.add_argument("--persist-secrets", action="store_true", help="Allow --save-config to store LangFuse keys in config.")
        p.add_argument("--langfuse-host", default=None, help="LangFuse host URL.")
        p.add_argument("--langfuse-public-key", default=None, help="LangFuse public key (or LANGFUSE_PUBLIC_KEY env).")
        p.add_argument("--langfuse-secret-key", default=None, help="LangFuse secret key (or LANGFUSE_SECRET_KEY env).")
        p.add_argument("--environment", default=None, help="Optional LangFuse environment filter.")
        p.add_argument("--window-hours", type=float, default=None, help="Telemetry window in hours.")
        p.add_argument("--limit", type=int, default=None, help="API page size.")
        p.add_argument("--max-pages", type=int, default=None, help="Max pages per endpoint per cycle.")
        p.add_argument("--http-timeout-sec", type=int, default=None, help="HTTP timeout for LangFuse API calls.")
        p.add_argument("--out-dir", default=None, help="Cycle output root directory.")
        p.add_argument("--live-policy-path", default=None, help="Live routing policy path used by runtime.")
        p.add_argument("--memory-file", default=None, help="Persistent optimizer memory file.")
        p.add_argument("--max-memory-cycles", type=int, default=None, help="Max cycles retained in memory.")

        promote_group = p.add_mutually_exclusive_group()
        promote_group.add_argument(
            "--promote-live-policy",
            dest="promote_live_policy",
            action="store_const",
            const=True,
            default=None,
            help="Apply staged policy to --live-policy-path when gate passes.",
        )
        promote_group.add_argument(
            "--disable-promote-live-policy",
            dest="promote_live_policy",
            action="store_const",
            const=False,
            default=None,
            help="Disable live policy promotion.",
        )

        memory_group = p.add_mutually_exclusive_group()
        memory_group.add_argument(
            "--write-memory",
            dest="write_memory",
            action="store_const",
            const=True,
            default=None,
            help="Persist cycle history to --memory-file.",
        )
        memory_group.add_argument(
            "--disable-write-memory",
            dest="write_memory",
            action="store_const",
            const=False,
            default=None,
            help="Disable memory persistence.",
        )

        p.add_argument("--min-switch-gain", type=float, default=None, help="Minimum gain required to accept model-route switch.")
        p.add_argument("--max-quality-drop", type=float, default=None, help="Maximum tolerated quality drop on route switch.")
        p.add_argument("--min-samples", type=int, default=None, help="Forwarded to policy builder.")
        p.add_argument("--quality-floor", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--quality-weight", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--cost-weight", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--latency-weight", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--max-cost-p95", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--max-latency-p95-ms", type=float, default=None, help="Forwarded to policy builder.")
        p.add_argument("--prompt-token-p95-warn", type=int, default=None, help="Forwarded to policy builder.")
        p.add_argument("--prompt-ratio-warn", type=float, default=None, help="Forwarded to policy builder.")

    once = sub.add_parser("run-once", help="Run one fetch-build-promote cycle.")
    add_common(once)

    daemon = sub.add_parser("daemon", help="Run cycles continuously.")
    add_common(daemon)
    daemon.add_argument("--interval-min", type=float, default=None, help="Minutes between cycles.")

    configure = sub.add_parser("configure", help="Persist optimizer config without running a cycle.")
    add_common(configure)
    configure.add_argument("--interval-min", type=float, default=None, help="Minutes between cycles.")
    configure.add_argument("--reset", action="store_true", help="Reset config to defaults before applying overrides.")
    configure.add_argument("--show", action="store_true", help="Print effective config after update.")

    return parser


def build_effective_settings(args: argparse.Namespace) -> Tuple[argparse.Namespace, Path, dict]:
    cfg_path = config_file_path(args)
    persisted = load_config(cfg_path)
    args = apply_effective_config(args, persisted)
    return args, cfg_path, persisted


def persist_current_settings(
    args: argparse.Namespace,
    cfg_path: Path,
    base_config: Optional[dict] = None,
) -> None:
    payload = dict(base_config or {})
    payload.update({k: getattr(args, k) for k in CONFIG_KEYS if hasattr(args, k)})
    if args.persist_secrets:
        if getattr(args, "langfuse_public_key", None):
            payload["langfuse_public_key"] = args.langfuse_public_key
        if getattr(args, "langfuse_secret_key", None):
            payload["langfuse_secret_key"] = args.langfuse_secret_key
    save_config(cfg_path, payload)
    print(f"Saved config: {cfg_path}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "configure":
        cfg_path = config_file_path(args)
        base_cfg = {} if args.reset else load_config(cfg_path)
        args = apply_effective_config(args, base_cfg)
        persist_current_settings(args, cfg_path, base_config=base_cfg)
        if args.show:
            shown = {k: getattr(args, k) for k in sorted(CONFIG_KEYS)}
            print(json.dumps(shown, indent=2, ensure_ascii=True))
        return 0

    args, cfg_path, _ = build_effective_settings(args)

    if args.save_config:
        persist_current_settings(args, cfg_path)

    if args.command == "run-once":
        return run_once(args)

    if args.command == "daemon":
        while True:
            try:
                rc = run_once(args)
                if rc != 0:
                    print(f"Cycle failed with code {rc}", file=sys.stderr)
            except Exception as e:
                print(f"Cycle exception: {e}", file=sys.stderr)
            time.sleep(max(1.0, float(args.interval_min)) * 60.0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
