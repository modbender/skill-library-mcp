#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SRC_DIR = SKILL_DIR / "src"
CONFIG_DIR = SKILL_DIR / "config"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from optimizer import TokenOptimizer  # noqa: E402


def merge_dict(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def load_config(config_path: Path | None) -> dict:
    defaults = json.loads((CONFIG_DIR / "defaults.json").read_text(encoding="utf-8"))
    if config_path is None:
        return defaults
    override = json.loads(config_path.read_text(encoding="utf-8"))
    return merge_dict(defaults, override)


def print_text_analyze(report: dict) -> None:
    print(f"TOKEN OPTIMIZATION ANALYSIS ({report['period']})")
    print("=" * 44)
    print(f"Sessions analyzed: {report['sessionsAnalyzed']}")
    print(f"Total tokens: {report['totalTokens']:,}")
    print(f"Near-limit sessions: {report['nearLimitSessions']}")
    print("")

    print("Top Sessions:")
    for s in report["topSessions"][:8]:
        util = (s["totalTokens"] / max(1, s["contextTokens"]))
        print(f"- {s['sessionKey']} :: {s['totalTokens']:,} ({util:.0%}) [{s['model']}]")
    print("")

    print("Tool Hotspots:")
    tool_calls = report["toolStats"].get("toolCalls", {})
    top_tools = sorted(tool_calls.items(), key=lambda kv: kv[1], reverse=True)[:10]
    for name, count in top_tools:
        dups = report["toolStats"].get("duplicateCalls", {}).get(name, 0)
        big = report["toolStats"].get("largeToolOutputs", {}).get(name, 0)
        print(f"- {name}: calls={count} duplicate={dups} large_outputs={big}")
    print("")

    model_opt = report["modelOptimization"]
    print("Model Optimization:")
    print(f"- candidate_sessions: {model_opt['count']}")
    print(f"- estimated_savings: {model_opt['estimatedSavings']:,} tokens")
    print("")

    savings = report["estimatedSavings"]
    print("Estimated Savings:")
    print(f"- model_selection: {savings['modelSelection']:,}")
    print(f"- deduplication: {savings['deduplication']:,}")
    print(f"- truncation: {savings['truncation']:,}")
    print(f"- total: {savings['total']:,}")

    usage = report.get("usageCost")
    if usage:
        print("")
        print("Cost Context (gateway usage-cost):")
        totals = usage.get("totals") if isinstance(usage.get("totals"), dict) else {}
        total_cost = usage.get("totalCostUsd", totals.get("totalCost"))
        total_tokens = usage.get("totalTokens", totals.get("totalTokens"))
        if total_cost is not None:
            print(f"- total_cost_usd: ${total_cost}")
        if total_tokens is not None:
            print(f"- total_tokens: {total_tokens}")


def print_text_health(report: dict) -> None:
    print("SESSION HEALTH CHECK")
    print("=" * 24)
    print(f"Sessions checked: {report['count']}")
    print("Status summary:")
    for status, count in sorted(report["statusSummary"].items()):
        print(f"- {status}: {count}")

    important = [s for s in report["sessions"] if s["status"] in ("stuck", "urgent", "warning")]
    important = sorted(important, key=lambda s: (s["status"], s["utilization"]), reverse=True)[:20]
    if important:
        print("")
        print("Flagged sessions:")
        for s in important:
            print(
                f"- [{s['status']}] {s['key']} :: {s['total_tokens']:,}/{s['context_tokens']:,} "
                f"({s['utilization']:.0%}) age={s['age_minutes']:.0f}m reason={s['reason']}"
            )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Optimize OpenClaw token usage and session hygiene.")
    p.add_argument("--config", type=Path, default=None, help="Override config JSON")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    p.add_argument("--output", type=Path, default=None, help="Write output to path")

    p.add_argument("--enable", action="store_true", help="Write local token optimizer config to workspace")
    p.add_argument("--analyze", action="store_true", help="Analyze token usage and optimization opportunities")
    p.add_argument("--period", default="7d", help="Period for analyze (e.g. 1d, 7d, 30d)")

    p.add_argument("--compress", action="store_true", help="Generate compressed context file for a session")
    p.add_argument("--session", default=None, help="Session key (or substring) for compression")
    p.add_argument("--threshold", type=float, default=0.8, help="Compression threshold (0-1)")
    p.add_argument("--keep-recent", type=int, default=20, help="Recent messages to preserve in compressed summary")

    p.add_argument("--health-check", action="store_true", help="Check session health and token pressure")
    p.add_argument("--active-minutes", type=int, default=None, help="Only include sessions active within this window")

    p.add_argument("--cleanup", action="store_true", help="Build cleanup plan for stuck sessions")
    p.add_argument("--apply", action="store_true", help="Apply cleanup actions (currently gateway restart only)")

    p.add_argument("--preflight", type=Path, default=None, help="JSON file with planned actions to preflight optimize")
    p.add_argument("--session-limit", type=int, default=180000, help="Session token limit for preflight planner")

    return p.parse_args()


def write_result(result: dict, fmt: str, output: Path | None) -> None:
    if fmt == "json":
        payload = json.dumps(result, indent=2, sort_keys=False) + "\n"
    else:
        payload = ""
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            output.write_text(payload, encoding="utf-8")
        else:
            # text output already printed to stdout in command branches
            output.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        print(f"Wrote output to {output}", file=sys.stderr)
    elif fmt == "json":
        print(payload, end="")


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    optimizer = TokenOptimizer(config=config)

    actions = [args.enable, args.analyze, args.compress, args.health_check, args.cleanup, args.preflight is not None]
    if sum(bool(x) for x in actions) != 1:
        print(
            "Choose exactly one primary action: --enable | --analyze | --compress | --health-check | --cleanup | --preflight",
            file=sys.stderr,
        )
        return 2

    if args.enable:
        cfg_path = Path.home() / ".openclaw/workspace/token-usage/token-optimizer.config.json"
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(config, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        result = {
            "enabled": True,
            "configPath": str(cfg_path),
            "message": "Token optimizer config written. Use this with --config or as your baseline profile.",
        }
        if args.format == "text":
            print("Token optimizer enabled.")
            print(f"Config: {cfg_path}")
        write_result(result, args.format, args.output)
        return 0

    if args.analyze:
        report = optimizer.analyze(period=args.period)
        if args.format == "text":
            print_text_analyze(report)
        write_result(report, args.format, args.output)
        return 0

    if args.compress:
        result = optimizer.compress_session(session_key=args.session, threshold=args.threshold, keep_recent=args.keep_recent)
        if args.format == "text":
            print("Compression complete:")
            print(f"- session: {result['sessionKey']}")
            print(f"- output: {result['output']}")
            print(f"- utilization: {result['utilization']:.0%}")
            print(f"- threshold: {result['threshold']:.0%}")
        write_result(result, args.format, args.output)
        return 0

    if args.health_check:
        report = optimizer.health_check(active_minutes=args.active_minutes)
        if args.format == "text":
            print_text_health(report)
        write_result(report, args.format, args.output)
        return 0

    if args.cleanup:
        result = optimizer.apply_cleanup() if args.apply else optimizer.cleanup_plan()
        if args.format == "text":
            if args.apply:
                print(result.get("message", "Cleanup applied."))
            else:
                print("Cleanup plan")
                print("=" * 12)
                print(f"stuck: {result['stuckCount']}  urgent: {result['urgentCount']}")
                for action in result.get("actions", [])[:30]:
                    print(f"- {action['action']} :: {action['sessionKey']} ({action['reason']})")
        write_result(result, args.format, args.output)
        return 0

    if args.preflight is not None:
        actions = json.loads(args.preflight.read_text(encoding="utf-8"))
        if not isinstance(actions, list):
            raise RuntimeError("--preflight file must contain a JSON array of actions")
        result = optimizer.preflight_optimize(actions, session_limit=args.session_limit)
        if args.format == "text":
            print("PREFLIGHT TOKEN PLAN")
            print("=" * 20)
            print(f"session_limit: {result['sessionLimit']:,}")
            print(f"estimated_total: {result['estimatedTotal']:,}")
            print(f"sessions_needed: {result['sessionsNeeded']}")
            for row in result["plan"][:50]:
                print(f"- session {row['session']}: +{row['estimatedTokens']:,} :: {row['action']}")
        write_result(result, args.format, args.output)
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
