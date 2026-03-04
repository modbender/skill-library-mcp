#!/usr/bin/env python3
"""Self-Optimize — run all diagnostic tools and produce a unified optimization report.

Usage: python3 self_optimize.py [workspace_path]

This is the main entry point for periodic self-optimization.
Runs: health_score, memory_auditor, cron_optimizer, skill_comparator
Produces a unified report with prioritized action items.
"""

import subprocess, sys, json, os
from pathlib import Path
from datetime import datetime

ws = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".openclaw" / "workspace"
scripts_dir = Path(__file__).parent

def run_tool(name, script, extra_args=None):
    """Run a diagnostic tool and capture output."""
    args = [sys.executable, str(scripts_dir / script), str(ws)]
    if extra_args:
        args.extend(extra_args)
    
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=240)
        return {
            "name": name,
            "output": result.stdout,
            "errors": result.stderr if result.returncode != 0 else "",
            "success": result.returncode == 0
        }
    except Exception as e:
        return {"name": name, "output": "", "errors": str(e), "success": False}

def load_json_report(filename):
    """Load a JSON report from memory/."""
    path = ws / "memory" / filename
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            pass
    return None

def compare_with_last(current_report):
    """Compare with last run to show trends."""
    last_path = ws / "memory" / "self-optimize-last.json"
    if not last_path.exists():
        return None
    try:
        last = json.loads(last_path.read_text())
        return last
    except:
        return None

def main():
    print("🔄 Self-Optimization Running...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📁 {ws}")
    print("=" * 60)

    # Run all tools
    results = []
    
    print("\n1/4 🏥 Health Score...")
    results.append(run_tool("Health Score", "health_score.py"))
    
    print("2/4 🔍 Memory Audit...")
    results.append(run_tool("Memory Audit", "memory_auditor.py"))
    
    print("3/4 ⏰ Cron Optimizer...")
    results.append(run_tool("Cron Optimizer", "cron_optimizer.py"))
    
    print("4/4 📦 Skill Comparator...")
    results.append(run_tool("Skill Comparator", "skill_comparator.py"))

    # Print all outputs
    for r in results:
        if r["output"]:
            print(r["output"])
        if r["errors"]:
            print(f"⚠️ {r['name']} errors: {r['errors'][:200]}")

    # Load JSON reports for unified summary
    health = load_json_report("health-score.json")
    memory = load_json_report("memory-audit.json")
    cron = load_json_report("cron-optimizer.json")
    skills = load_json_report("skill-comparator.json")

    # Unified action items
    print("\n" + "=" * 60)
    print("🎯 PRIORITIZED ACTION ITEMS")
    print("=" * 60)

    actions = []
    
    if health:
        for issue in health.get("issues", []):
            actions.append(("🚨 HIGH", issue))
        for sug in health.get("suggestions", [])[:3]:
            if "❌" in sug:
                actions.append(("🚨 HIGH", sug))
            elif "⚠️" in sug:
                actions.append(("⚠️ MED", sug))
            else:
                actions.append(("💡 LOW", sug))

    if memory:
        for issue in memory.get("issues", []):
            actions.append(("🚨 HIGH", issue))

    if cron:
        for issue in cron.get("issues", []):
            if "ERROR" in issue.upper():
                actions.append(("🚨 HIGH", issue))
            else:
                actions.append(("⚠️ MED", issue))

    # Deduplicate
    seen = set()
    unique_actions = []
    for priority, text in actions:
        clean = text.strip()
        if clean not in seen:
            seen.add(clean)
            unique_actions.append((priority, clean))

    if unique_actions:
        for priority, text in sorted(unique_actions, key=lambda x: {"🚨 HIGH": 0, "⚠️ MED": 1, "💡 LOW": 2}.get(x[0], 3)):
            print(f"  {priority}: {text}")
    else:
        print("  ✅ No action items — everything looks good!")

    # Trend comparison
    last = compare_with_last({"health": health})
    if last and last.get("health") and health:
        last_score = last["health"].get("pct", 0)
        curr_score = health.get("pct", 0)
        diff = curr_score - last_score
        if diff > 0:
            print(f"\n📈 Health trend: +{diff}% since last run")
        elif diff < 0:
            print(f"\n📉 Health trend: {diff}% since last run")
        else:
            print(f"\n📊 Health trend: unchanged since last run")

    # Save unified report
    unified = {
        "timestamp": datetime.now().isoformat(),
        "health": health,
        "memory": memory,
        "cron": cron,
        "actions": [{"priority": p, "text": t} for p, t in unique_actions]
    }

    # Save current as "last" for next comparison
    report_path = ws / "memory" / "self-optimize-report.json"
    last_path = ws / "memory" / "self-optimize-last.json"
    
    # Move current to last
    if report_path.exists():
        last_path.write_text(report_path.read_text())
    
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(unified, indent=2, ensure_ascii=False))
    
    print(f"\n📊 Unified report: {report_path}")
    print("🔄 Self-optimization complete!")

if __name__ == "__main__":
    main()
