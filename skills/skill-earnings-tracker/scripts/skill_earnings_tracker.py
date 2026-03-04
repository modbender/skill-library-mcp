#!/usr/bin/env python3
"""
skill_earnings_tracker.py - Track earnings from published skills

Usage:
  python3 skill_earnings_tracker.py log --platform clawhub --skill my-skill --metric installs --value 10
  python3 skill_earnings_tracker.py report --period weekly
  python3 skill_earnings_tracker.py list
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

EARNINGS_DIR = Path.home() / ".openclaw" / "earnings"


def ensure_dir():
    """Ensure earnings directory exists"""
    EARNINGS_DIR.mkdir(parents=True, exist_ok=True)


def get_log_path():
    """Get current month's log file"""
    today = datetime.now()
    return EARNINGS_DIR / f"earnings-{today.year}-{today.month:02d}.jsonl"


def log_entry(args):
    """Log an earnings entry"""
    ensure_dir()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "platform": args.platform,
        "skill": args.skill,
        "metric": args.metric,  # installs, credits, stars, etc.
        "value": args.value,
        "period": args.period or datetime.now().strftime("%Y-%m-%d"),
        "notes": args.notes or ""
    }
    
    log_path = get_log_path()
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✅ Logged: {args.skill} on {args.platform} - {args.metric}: {args.value}")


def list_skills(args):
    """List all tracked skills"""
    ensure_dir()
    
    skills = set()
    for log_file in EARNINGS_DIR.glob("earnings-*.jsonl"):
        with open(log_file) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    skills.add((entry["platform"], entry["skill"]))
    
    if not skills:
        print("No skills tracked yet.")
        return
    
    print("\n📊 Tracked Skills:")
    print("-" * 50)
    for platform, skill in sorted(skills):
        print(f"  {platform:15} {skill}")


def generate_report(args):
    """Generate earnings report"""
    ensure_dir()
    
    # Determine period
    if args.period == "weekly":
        days = 7
    elif args.period == "monthly":
        days = 30
    else:
        days = 7  # default
    
    cutoff = datetime.now() - timedelta(days=days)
    
    # Aggregate data
    stats = {}
    for log_file in EARNINGS_DIR.glob("earnings-*.jsonl"):
        with open(log_file) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["timestamp"])
                
                if entry_time < cutoff:
                    continue
                
                key = (entry["platform"], entry["skill"], entry["metric"])
                if key not in stats:
                    stats[key] = {
                        "total": 0,
                        "count": 0,
                        "entries": []
                    }
                
                stats[key]["total"] += entry["value"]
                stats[key]["count"] += 1
                stats[key]["entries"].append(entry)
    
    if not stats:
        print(f"No data for the last {days} days.")
        return
    
    # Print report
    print(f"\n📈 Earnings Report - Last {days} Days")
    print("=" * 70)
    
    # Group by skill
    skill_totals = {}
    for (platform, skill, metric), data in stats.items():
        if skill not in skill_totals:
            skill_totals[skill] = {}
        if metric not in skill_totals[skill]:
            skill_totals[skill][metric] = {"total": 0, "platforms": set()}
        
        skill_totals[skill][metric]["total"] += data["total"]
        skill_totals[skill][metric]["platforms"].add(platform)
    
    for skill, metrics in skill_totals.items():
        print(f"\n🎯 {skill}")
        print("-" * 50)
        for metric, data in metrics.items():
            platforms = ", ".join(data["platforms"])
            print(f"  {metric:20} {data['total']:10} ({platforms})")
    
    print("\n" + "=" * 70)


def export_data(args):
    """Export all earnings data"""
    ensure_dir()
    
    all_entries = []
    for log_file in sorted(EARNINGS_DIR.glob("earnings-*.jsonl")):
        with open(log_file) as f:
            for line in f:
                if line.strip():
                    all_entries.append(json.loads(line))
    
    output = {
        "export_date": datetime.now().isoformat(),
        "total_entries": len(all_entries),
        "entries": all_entries
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✅ Exported {len(all_entries)} entries to {args.output}")
    else:
        print(json.dumps(output, indent=2))


def get_clawhub_stats(args):
    """Get current ClawHub stats for a skill"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["clawhub", "explore", "--limit", "100"],
            capture_output=True,
            text=True
        )
        
        # Parse output for skill info
        # This is a simplified version - real implementation would parse better
        print(f"\n📊 ClawHub stats for {args.skill}:")
        print("  (Run 'clawhub explore' for detailed stats)")
        
    except FileNotFoundError:
        print("❌ ClawHub CLI not found. Install with: npm i -g clawhub")


def main():
    parser = argparse.ArgumentParser(
        description="Skill Earnings Tracker - Monitor skill performance across platforms"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log an earnings entry")
    log_parser.add_argument("--platform", required=True,
                           choices=["clawhub", "evomap", "reelmind", "custom"],
                           help="Platform name")
    log_parser.add_argument("--skill", required=True, help="Skill name")
    log_parser.add_argument("--metric", required=True,
                           help="Metric type (installs, credits, stars, etc.)")
    log_parser.add_argument("--value", type=float, required=True,
                           help="Metric value")
    log_parser.add_argument("--period", help="Period (YYYY-MM-DD)")
    log_parser.add_argument("--notes", help="Additional notes")
    
    # List command
    subparsers.add_parser("list", help="List all tracked skills")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate earnings report")
    report_parser.add_argument("--period", choices=["weekly", "monthly"],
                               default="weekly",
                               help="Report period")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export all data")
    export_parser.add_argument("--output", help="Output file path")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get ClawHub stats")
    stats_parser.add_argument("skill", help="Skill name")
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_entry(args)
    elif args.command == "list":
        list_skills(args)
    elif args.command == "report":
        generate_report(args)
    elif args.command == "export":
        export_data(args)
    elif args.command == "stats":
        get_clawhub_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
