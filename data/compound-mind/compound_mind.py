#!/usr/bin/env python3
"""
CompoundMind v0.1 - Main CLI
Makes agents permanently smarter by distilling experience into searchable wisdom.

Usage:
  python3 compound_mind.py sync             # Full pipeline: distill + rebuild index
  python3 compound_mind.py search "query"   # Search wisdom index
  python3 compound_mind.py brief "task"     # Pre-session briefing
  python3 compound_mind.py report           # Growth report
  python3 compound_mind.py mistakes         # Show repeated mistake patterns
  python3 compound_mind.py stats            # Index statistics
"""

import sys
import argparse
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))


def cmd_sync(args):
    from distill import distill_all
    from index import rebuild_index
    memory_dir = Path(args.memory_dir) if args.memory_dir else Path("/root/.openclaw/workspace/memory")
    print("CompoundMind SYNC")
    print("=" * 50)
    print("Step 1: Distilling memory files...")
    distill_all(memory_dir, since=args.since, force=args.force)
    print("\nStep 2: Rebuilding wisdom index...")
    rebuild_index()
    print("\nSync complete.")


def cmd_distill(args):
    from distill import distill_all
    memory_dir = Path(args.memory_dir) if args.memory_dir else Path("/root/.openclaw/workspace/memory")
    distill_all(memory_dir, since=args.since, force=args.force, limit=args.limit)


def cmd_search(args):
    from index import search, format_results
    q = " ".join(args.query)
    results = search(q, domain=args.domain, category=args.category, limit=args.limit)
    print(f"Results for: '{q}'\n")
    print(format_results(results, verbose=args.verbose))


def cmd_rebuild(args):
    from index import rebuild_index
    rebuild_index()


def cmd_brief(args):
    from brief import brief
    task = " ".join(args.task)
    print(f"Pre-session brief for: '{task}'\n")
    print("=" * 60)
    result = brief(task, save=not args.no_save, raw=args.raw, use_llm=getattr(args, "llm", False))
    print(result)
    print("=" * 60)


def cmd_report(args):
    from growth import (analyze_experience_quality, detect_repeated_mistakes,
                        calculate_growth_score, build_report_rule_based,
                        build_report_llm, load_growth, save_growth)

    exp_dir = BASE_DIR / "data" / "experiences"
    print("Analyzing experience database...")
    stats = analyze_experience_quality(exp_dir)

    if not stats.get("total_lessons"):
        print("No experience data found. Run: python3 compound_mind.py sync")
        return

    repeated = detect_repeated_mistakes(stats)
    growth_score = calculate_growth_score(stats)

    use_llm = getattr(args, "llm", False)

    if use_llm:
        try:
            report = build_report_llm(stats, repeated, growth_score)
        except RuntimeError as e:
            print(f"[warn] {e}, using rule-based report")
            report = build_report_rule_based(stats, repeated, growth_score)
    else:
        report = build_report_rule_based(stats, repeated, growth_score)

    print()
    print(report)

    # Save snapshot
    growth = load_growth()
    if not growth["baseline_date"]:
        growth["baseline_date"] = date.today().isoformat()
    growth["growth_snapshots"].append({
        "date": date.today().isoformat(),
        "score": growth_score["score"],
        "total_lessons": stats.get("total_lessons", 0),
        "trend": growth_score.get("trend", "stable")
    })
    save_growth(growth)


def cmd_mistakes(args):
    from growth import analyze_experience_quality, detect_repeated_mistakes
    exp_dir = BASE_DIR / "data" / "experiences"
    print("Scanning for repeated mistakes...")
    stats = analyze_experience_quality(exp_dir)
    if not stats:
        print("No data. Run: python3 compound_mind.py sync")
        return
    repeated = detect_repeated_mistakes(stats)
    if not repeated:
        print("No repeated mistakes detected. Clean learning record.")
    else:
        print(f"Found {len(repeated)} repeated mistake patterns:\n")
        for i, m in enumerate(repeated, 1):
            print(f"{i}. [{m['domain']}] x{m['count']}: {m['representative'][:120]}")


def cmd_stats(args):
    from index import stats as show_stats
    show_stats()


def main():
    parser = argparse.ArgumentParser(
        description="CompoundMind v0.1 - Permanent agent intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 compound_mind.py sync
  python3 compound_mind.py search "Polymarket order types"
  python3 compound_mind.py search "git mistakes" --category lesson
  python3 compound_mind.py brief "trade on Polymarket"
  python3 compound_mind.py brief "post on X"
  python3 compound_mind.py report
  python3 compound_mind.py mistakes
"""
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # sync
    sp = sub.add_parser("sync", help="Full pipeline: distill + rebuild index")
    sp.add_argument("--since", help="Only process files from date (YYYY-MM-DD)")
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--memory-dir", default=None)

    # distill
    dp = sub.add_parser("distill", help="Distill memory files into experience data")
    dp.add_argument("--since", help="Only process files from date (YYYY-MM-DD)")
    dp.add_argument("--force", action="store_true", help="Re-distill unchanged files")
    dp.add_argument("--limit", type=int, help="Only last N files")
    dp.add_argument("--memory-dir", default=None)

    # rebuild
    sub.add_parser("rebuild", help="Rebuild wisdom index from experience files")

    # search
    sp2 = sub.add_parser("search", help="Search the wisdom index")
    sp2.add_argument("query", nargs="+")
    sp2.add_argument("--domain", help="Filter by domain (trading|coding|social|communication|system|general)")
    sp2.add_argument("--category", help="Filter by category (lesson|decision|skill|relationship|fact)")
    sp2.add_argument("--limit", type=int, default=10)
    sp2.add_argument("--verbose", "-v", action="store_true")

    # brief
    bp = sub.add_parser("brief", help="Generate pre-session briefing")
    bp.add_argument("task", nargs="+")
    bp.add_argument("--raw", action="store_true", help="Raw wisdom JSON without synthesis")
    bp.add_argument("--no-save", action="store_true")
    bp.add_argument("--llm", action="store_true", help="Use LLM synthesis (requires COMPOUND_MIND_LLM_KEY)")

    # report
    rp = sub.add_parser("report", help="Generate growth report")
    rp.add_argument("--llm", action="store_true", help="Use LLM synthesis (requires COMPOUND_MIND_LLM_KEY)")

    # mistakes
    sub.add_parser("mistakes", help="Show repeated mistake patterns")

    # stats
    sub.add_parser("stats", help="Show index statistics")

    args = parser.parse_args()

    dispatch = {
        "sync": cmd_sync,
        "distill": cmd_distill,
        "rebuild": cmd_rebuild,
        "search": cmd_search,
        "brief": cmd_brief,
        "report": cmd_report,
        "mistakes": cmd_mistakes,
        "stats": cmd_stats,
    }

    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
