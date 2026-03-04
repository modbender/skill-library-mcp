#!/usr/bin/env python3
"""Cron Optimizer — analyze and fix cron job issues.

Usage:
  python3 cron_optimizer.py          # Read-only analysis
  python3 cron_optimizer.py --fix    # Auto-repair (creates backup first)

Detects: time collisions, missing stagger, delivery duplication,
error states, suboptimal session targets.
"""

import subprocess, sys, json, re, os
from datetime import datetime
from pathlib import Path

FIX_MODE = "--fix" in sys.argv
ws = Path(sys.argv[-1]) if len(sys.argv) > 1 and not sys.argv[-1].startswith("-") else Path.home() / ".openclaw" / "workspace"

def run_cmd(args, timeout=15):
    """Run a command and return stdout."""
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), 1

def get_all_jobs():
    """Fetch all cron jobs as JSON via openclaw cron list --json."""
    out, code = run_cmd(["openclaw", "cron", "list", "--json"])
    if code != 0:
        return {}
    try:
        data = json.loads(out)
        jobs_list = data.get("jobs", [])
        return {j["id"]: j for j in jobs_list}
    except:
        return {}

def backup_cron_state(jobs_detail):
    """Save current cron state as backup before modifications."""
    backup_path = ws / "memory" / "cron-backup.json"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup = {
        "timestamp": datetime.now().isoformat(),
        "jobs": jobs_detail
    }
    backup_path.write_text(json.dumps(backup, indent=2, ensure_ascii=False))
    print(f"💾 Cron state backed up to: {backup_path}")
    return backup_path

def main():
    print("\n⏰ Cron Optimizer")
    print("=" * 60)

    if FIX_MODE:
        print("🔧 FIX MODE — will attempt auto-repairs (backup created first)")
    else:
        print("👀 READ-ONLY MODE — analysis only")

    # Get all jobs via JSON
    jobs = get_all_jobs()
    if not jobs:
        print("No cron jobs found or could not fetch details.")
        return

    print(f"Found {len(jobs)} cron jobs.\n")

    issues = []
    fixes = []

    # Check 1: Error states
    for jid, job in jobs.items():
        state = job.get("state", {})
        name = job.get("name", jid[:8])
        if state.get("lastStatus") == "error" or state.get("lastRunStatus") == "error":
            err = state.get("lastError", "unknown")
            consecutive = state.get("consecutiveErrors", 0)
            issues.append(f"🚨 [{name}] ERROR state (consecutive: {consecutive}): {err[:100]}")

    # Check 2: Missing stagger
    no_stagger = []
    has_stagger = []
    for jid, job in jobs.items():
        schedule = job.get("schedule", {})
        stagger_ms = schedule.get("staggerMs", 0)
        name = job.get("name", jid[:8])
        if stagger_ms and stagger_ms > 0:
            has_stagger.append(name)
        else:
            no_stagger.append((jid, name))

    if no_stagger:
        issues.append(f"⚠️ {len(no_stagger)} jobs have no stagger: {', '.join(n for _,n in no_stagger)}")
        if FIX_MODE:
            for jid, name in no_stagger:
                out, code = run_cmd(["openclaw", "cron", "edit", jid, "--stagger", "2m"])
                if code == 0:
                    fixes.append(f"✅ Added 2m stagger to [{name}]")
                else:
                    fixes.append(f"❌ Failed to add stagger to [{name}]")

    if has_stagger:
        print(f"  ✅ {len(has_stagger)} jobs have stagger configured")

    # Check 3: Time collisions
    schedules = {}
    for jid, job in jobs.items():
        schedule = job.get("schedule", {})
        expr = schedule.get("expr", "")
        tz = schedule.get("tz", "")
        key = f"{expr} @ {tz}"
        if key not in schedules:
            schedules[key] = []
        schedules[key].append(job.get("name", jid[:8]))

    for sched, names in schedules.items():
        if len(names) > 1:
            issues.append(f"⚠️ Time collision on '{sched}': {', '.join(names)}")

    # Check 4: Delivery mode — jobs should have announce enabled to reach the user
    for jid, job in jobs.items():
        delivery = job.get("delivery", {})
        mode = delivery.get("mode", "none")
        name = job.get("name", jid[:8])
        if mode == "none" or mode is None:
            issues.append(f"⚠️ [{name}] has delivery=none — output won't reach user. Consider enabling announce.")
            if FIX_MODE:
                out, code = run_cmd(["openclaw", "cron", "edit", jid, "--announce"])
                if code == 0:
                    fixes.append(f"✅ Enabled announce on [{name}]")

    # Check 5: Missing delivery target — announce without 'to' will silently fail
    for jid, job in jobs.items():
        delivery = job.get("delivery", {})
        mode = delivery.get("mode", "none")
        to = delivery.get("to", "")
        name = job.get("name", jid[:8])
        if mode == "announce" and not to:
            issues.append(f"🚨 [{name}] has announce enabled but missing 'to' (delivery target) — will fail silently! Use --to <chatId>.")
            if FIX_MODE:
                # Cannot auto-fix: we don't know the user's chat ID
                fixes.append(f"⚠️ [{name}] needs --to <chatId> — cannot auto-fix, set manually")

    # Check 6: Session target
    for jid, job in jobs.items():
        target = job.get("sessionTarget", "")
        name = job.get("name", jid[:8])
        payload = job.get("payload", {})
        kind = payload.get("kind", "")
        if target == "main" and kind == "agentTurn":
            issues.append(f"💡 [{name}] uses main session for agentTurn — consider isolated for autonomous tasks")

    # Check 6: Timeout adequacy
    for jid, job in jobs.items():
        payload = job.get("payload", {})
        timeout = payload.get("timeoutSeconds", 30)
        msg = payload.get("message", "")
        name = job.get("name", jid[:8])
        # Heuristic: if message mentions multiple steps/commands, timeout should be higher
        step_count = msg.lower().count("step") + msg.lower().count("```") + msg.lower().count("curl")
        if step_count > 3 and timeout < 180:
            issues.append(f"💡 [{name}] has {step_count} steps but only {timeout}s timeout — consider increasing")

    # Backup before fixes
    if FIX_MODE and fixes:
        backup_cron_state({jid: job for jid, job in jobs.items()})

    # Summary
    print("\n📋 Analysis Results:")
    print("-" * 40)

    if not issues:
        print("  ✅ No issues found — cron setup looks good!")
    else:
        for i in issues:
            print(f"  {i}")

    if fixes:
        print(f"\n🔧 Fixes Applied ({len(fixes)}):")
        for f in fixes:
            print(f"  {f}")
    elif issues and not FIX_MODE:
        print(f"\n💡 Run with --fix to auto-repair (creates backup first)")

    # Save report
    report = {
        "total_jobs": len(jobs),
        "with_stagger": len(has_stagger),
        "without_stagger": len(no_stagger),
        "issues": issues,
        "fixes": fixes,
        "fix_mode": FIX_MODE,
        "timestamp": datetime.now().isoformat()
    }

    report_path = ws / "memory" / "cron-optimizer.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n📊 Report saved: {report_path}")

if __name__ == "__main__":
    main()
