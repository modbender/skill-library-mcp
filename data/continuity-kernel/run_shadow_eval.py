from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from policy import (
    COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL,
    COMPACTION_POLICY_SIZE_ONLY,
    SELECTOR_MODE_DETERMINISTIC,
    SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL,
)
from shadow_eval import (
    DEFAULT_PERTURB_PROFILE,
    DEFAULT_SUITE,
    SUPPORTED_PERTURB_PROFILES,
    SUPPORTED_SUITES,
    append_shadow_snapshot,
    build_shadow_snapshot,
    write_shadow_summary,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run shadow-mode eval snapshot for a P0 chunk (trace-backed when provided).")
    parser.add_argument("--layer", required=True, help="Active P0 layer name, e.g. 'Soul Card'.")
    parser.add_argument("--chunk", required=True, help="Active chunk id/name, e.g. 'SC-01'.")
    parser.add_argument("--runs", type=int, default=100, help="Number of evaluated shadow runs.")
    parser.add_argument(
        "--suite",
        default=DEFAULT_SUITE,
        choices=sorted(SUPPORTED_SUITES),
        help="Task suite used for eval scoring.",
    )
    parser.add_argument(
        "--perturb-profile",
        default=DEFAULT_PERTURB_PROFILE,
        choices=sorted(SUPPORTED_PERTURB_PROFILES),
        help="Deterministic perturb profile (used by memoryarena-mini-perturb suite).",
    )
    parser.add_argument(
        "--selector-mode",
        default=SELECTOR_MODE_DETERMINISTIC,
        choices=[SELECTOR_MODE_DETERMINISTIC, SELECTOR_MODE_DUAL_ROUTE_EXPERIMENTAL],
        help="Injector selector mode to annotate in receipts.",
    )
    parser.add_argument(
        "--compaction-policy",
        default=COMPACTION_POLICY_SIZE_ONLY,
        choices=[COMPACTION_POLICY_SIZE_ONLY, COMPACTION_POLICY_ATTENTION_PRESERVING_EXPERIMENTAL],
        help="Compaction policy label for A/B shadow receipts.",
    )
    parser.add_argument(
        "--trace-jsonl",
        action="append",
        default=[],
        help="JSONL trace file with observed shadow outcomes. Repeatable.",
    )
    parser.add_argument(
        "--trace-dir",
        action="append",
        default=[],
        help="Directory containing *.jsonl observed shadow traces. Repeatable.",
    )
    parser.add_argument(
        "--append",
        required=True,
        help="Path to p0-evals JSON file where snapshot should be appended.",
    )
    parser.add_argument(
        "--allow-synthetic",
        action="store_true",
        help="Allow synthetic fallback when no observed traces are provided. Synthetic snapshots are always marked pass=false.",
    )
    parser.add_argument(
        "--artifacts-root",
        default=str(Path.home() / ".cache" / "continuity-kernel" / "p0-evals"),
        help="Directory for shadow summary receipts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")

    trace_jsonl_paths = [Path(raw).expanduser() for raw in args.trace_jsonl]
    trace_dirs = [Path(raw).expanduser() for raw in args.trace_dir]

    snapshot = build_shadow_snapshot(
        layer=args.layer,
        chunk=args.chunk,
        suite=args.suite,
        perturb_profile=args.perturb_profile,
        runs=args.runs,
        selector_mode=args.selector_mode,
        compaction_policy=args.compaction_policy,
        trace_jsonl_paths=trace_jsonl_paths,
        trace_dirs=trace_dirs,
        allow_synthetic=args.allow_synthetic,
    )

    append_path = Path(args.append).expanduser()

    appended = append_shadow_snapshot(snapshot=snapshot, append_path=append_path)
    persisted_snapshot = snapshot
    snapshots = appended.get("snapshots") if isinstance(appended, dict) else None
    if isinstance(snapshots, list) and snapshots and isinstance(snapshots[-1], dict):
        persisted_snapshot = snapshots[-1]

    artifacts_root = Path(args.artifacts_root).expanduser()

    summary_path = write_shadow_summary(
        snapshot=persisted_snapshot,
        append_path=append_path,
        artifacts_root=artifacts_root,
        generated_at=persisted_snapshot.get("generated_at"),
    )

    print(summary_path.as_posix())


if __name__ == "__main__":
    main()
