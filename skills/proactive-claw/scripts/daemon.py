#!/usr/bin/env python3
"""
daemon.py — Proactive Agent background daemon.

Two-phase architecture:
  PLAN:    Read user calendars, propose/instantiate actions into Action Calendar,
           maintain link graph, detect deletions.
  EXECUTE: Fire only actions that are due in Action Calendar (idempotent).

Usage:
  python3 daemon.py                  # run once (called by launchd/systemd)
  python3 daemon.py --loop           # run forever with interval sleep
  python3 daemon.py --status         # print last run info
  python3 daemon.py --simulate --days 7   # dry-run over N future days
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required. You have {sys.version}."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
STATE_FILE = SKILL_DIR / "daemon_state.json"
LOG_FILE = SKILL_DIR / "daemon.log"
CLEANUP_STATE_FILE = SKILL_DIR / "last_cleanup.json"

sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
        # Keep log under 500 lines
        lines = LOG_FILE.read_text().splitlines()
        if len(lines) > 500:
            LOG_FILE.write_text("\n".join(lines[-400:]) + "\n")
    except Exception:
        pass


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_run": None, "notified_events": {}}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def send_notification(config: dict, message: str, event_id: str = "",
                      channel_override: str = None):
    """Send a notification via configured channel(s)."""
    if channel_override:
        channels = [channel_override]
    else:
        channels = config.get("notification_channels", ["system"])
    sent = False

    for channel in channels:
        try:
            if channel == "system":
                _notify_system(message)
                sent = True
            elif channel == "openclaw":
                nudges_file = SKILL_DIR / "pending_nudges.json"
                nudges = []
                if nudges_file.exists():
                    try:
                        nudges = json.loads(nudges_file.read_text())
                    except Exception:
                        nudges = []
                nudges.append({
                    "message": message,
                    "event_id": event_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "shown": False,
                })
                nudges_file.write_text(json.dumps(nudges, indent=2))
                sent = True
            elif channel == "telegram":
                _notify_telegram(config, message)
                sent = True
        except Exception as e:
            log(f"Notification channel '{channel}' failed: {e}")

    if not sent:
        log(f"WARNING: No notification delivered for: {message[:60]}")
    return sent


def _notify_system(message: str):
    """macOS/Linux system notification."""
    platform = sys.platform
    if platform == "darwin":
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write(message)
            tmp_path = tf.name
        script = (
            f'set msgBody to (read POSIX file "{tmp_path}" as \u00ABclass utf8\u00BB)\n'
            'display notification msgBody with title "\U0001f99e Proactive Claw"'
        )
        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    elif platform.startswith("linux"):
        subprocess.run(["notify-send", "\U0001f99e Proactive Claw", message], check=True, capture_output=True)
    else:
        log(f"System notify not supported on {platform}: {message}")


def _notify_telegram(config: dict, message: str):
    import urllib.request
    tg = config.get("telegram", {})
    token = tg.get("bot_token", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = tg.get("chat_id", "") or os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        raise ValueError("telegram.bot_token and telegram.chat_id required in config.json")
    payload = json.dumps({"chat_id": chat_id, "text": f"\U0001f99e {message}", "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10)


def run_scan() -> dict:
    """Run scan_calendar.py --force and return parsed output."""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts/scan_calendar.py"), "--force"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"scan_calendar.py failed: {result.stderr[:200]}")
    return json.loads(result.stdout)


def run_conflict_check(scan_output: dict) -> list:
    """Run conflict_detector.py and return list of conflicts."""
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts/conflict_detector.py")],
        input=json.dumps(scan_output),
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    try:
        return json.loads(result.stdout).get("conflicts", [])
    except Exception:
        return []


def tick(config: dict, state: dict) -> dict:
    """One daemon tick: PLAN then EXECUTE."""
    log("Daemon tick started")
    notified = state.get("notified_events", {})
    now_iso = datetime.now(timezone.utc).isoformat()

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1: PLAN — ingest user events, update link graph, create actions
    # ═══════════════════════════════════════════════════════════════════════════
    plan_result = {}
    try:
        from action_planner import plan
        plan_result = plan(config)
        log(f"PLAN: ingested={plan_result.get('ingested', 0)}, "
            f"actions={plan_result.get('actions_planned', 0)}, "
            f"missing={plan_result.get('missing_detected', 0)}")
    except Exception as e:
        log(f"PLAN failed (falling back to legacy scan): {e}")
        # Fallback: run legacy scan for backward compatibility
        try:
            scan = run_scan()
            # Legacy proactivity engine scoring
            if config.get("feature_proactivity_engine", True):
                try:
                    from proactivity_engine import score_events
                    scan = score_events(scan, config)
                except Exception as pe:
                    log(f"Proactivity engine failed: {pe}")

            # Legacy interrupt controller filtering
            actionable = scan.get("actionable", [])
            if config.get("feature_interrupt_controller", True):
                try:
                    from interrupt_controller import filter_nudges
                    actionable = filter_nudges(actionable, config, state)
                except Exception as ic:
                    log(f"Interrupt controller failed: {ic}")

            # Legacy notification loop
            for event in actionable:
                eid = event.get("id", "")
                if not eid:
                    continue
                day_key = f"{eid}_{datetime.now(timezone.utc).date()}"
                if day_key in notified:
                    continue
                title = event.get("title", "")
                hours = event.get("hours_away")
                score = event.get("score", 0)
                if hours is not None and hours <= 2:
                    time_str = f"in {int(hours * 60)} minutes"
                elif hours is not None and hours <= 24:
                    time_str = f"in {int(hours)} hours"
                elif hours is not None:
                    time_str = f"in {int(hours / 24)} days"
                else:
                    time_str = "coming up"
                msg = f"*{title}* is {time_str}. Want to prep? (score: {score}/10)"

                # Use adaptive channel if available
                channel_override = None
                if config.get("feature_adaptive_notifications", True):
                    try:
                        from adaptive_notifications import get_db as an_db, get_channel_recommendation
                        an_conn = an_db()
                        rec = get_channel_recommendation(an_conn, event.get("event_type", ""), config)
                        if rec.get("source") == "learned":
                            channel_override = rec["channel"]
                        an_conn.close()
                    except Exception:
                        pass

                send_notification(config, msg, eid, channel_override=channel_override)
                notified[day_key] = now_iso
                log(f"Notified (legacy): {title}")
        except Exception as scan_e:
            log(f"Legacy scan also failed: {scan_e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2: EXECUTE — fire due actions from Action Calendar
    # ═══════════════════════════════════════════════════════════════════════════
    exec_result = {}
    try:
        from action_executor import execute_due
        exec_result = execute_due(config)
        log(f"EXECUTE: fired={exec_result.get('executed', 0)}, "
            f"skipped_sent={exec_result.get('skipped_already_sent', 0)}, "
            f"skipped_paused={exec_result.get('skipped_paused', 0)}")
    except Exception as e:
        log(f"EXECUTE failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3: Conflict detection (creates action events for conflicts)
    # ═══════════════════════════════════════════════════════════════════════════
    if config.get("feature_conflicts", True):
        try:
            scan = run_scan()
            conflicts = run_conflict_check(scan)
            for conflict in conflicts:
                ckey = f"conflict_{conflict.get('key', '')}"
                if ckey not in notified:
                    msg = conflict.get("message", "Calendar conflict detected.")
                    send_notification(config, msg)
                    notified[ckey] = now_iso
                    log(f"Conflict notified: {msg[:80]}")
        except Exception as e:
            log(f"Conflict check failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4: Follow-up nudges (legacy, kept for backward compatibility)
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        _check_pending_followups(config, state, notified, now_iso)
    except Exception as e:
        log(f"Follow-up check failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5: Daily cleanup (once per day)
    # ═══════════════════════════════════════════════════════════════════════════
    _maybe_run_cleanup(config)

    # ═══════════════════════════════════════════════════════════════════════════
    # Bookkeeping
    # ═══════════════════════════════════════════════════════════════════════════
    state["last_run"] = now_iso
    state["notified_events"] = notified
    state["last_plan_result"] = plan_result
    state["last_exec_result"] = exec_result

    if len(notified) > 200:
        keys = list(notified.keys())
        state["notified_events"] = {k: notified[k] for k in keys[-200:]}

    return state


def _maybe_run_cleanup(config: dict):
    """Run action_cleanup once per day."""
    try:
        last_cleanup = {}
        if CLEANUP_STATE_FILE.exists():
            last_cleanup = json.loads(CLEANUP_STATE_FILE.read_text())
        last_date = last_cleanup.get("last_cleanup_date", "")
        today = datetime.now(timezone.utc).date().isoformat()

        if last_date != today:
            from action_cleanup import cleanup
            result = cleanup(config)
            log(f"Daily cleanup: deleted={result.get('deleted_old', 0)}, "
                f"renamed={result.get('renamed_paused', 0) + result.get('renamed_canceled', 0)}")
            CLEANUP_STATE_FILE.write_text(json.dumps({"last_cleanup_date": today}))
    except Exception as e:
        log(f"Cleanup failed: {e}")


def _check_pending_followups(config: dict, state: dict, notified: dict, now_iso: str):
    """Check outcomes/ for events needing follow-up that haven't been nudged."""
    outcomes_dir = SKILL_DIR / "outcomes"
    if not outcomes_dir.exists():
        return
    now = datetime.now(timezone.utc)
    for f in outcomes_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            if not data.get("follow_up_needed"):
                continue
            action_items = data.get("action_items", [])
            if not action_items:
                continue
            event_dt_str = data.get("event_datetime", "")
            if not event_dt_str:
                continue
            event_dt = datetime.fromisoformat(event_dt_str.replace("Z", "+00:00"))
            if event_dt.tzinfo is None:
                event_dt = event_dt.replace(tzinfo=timezone.utc)
            days_since = (now - event_dt).days
            nudge_key = f"followup_7d_{f.stem}"
            if days_since >= 7 and nudge_key not in notified:
                title = data.get("event_title", "an event")
                n_items = len(action_items)
                msg = (f"*Follow-up reminder:* {title} was {days_since} days ago. "
                       f"You have {n_items} open action item(s). Want to review?")
                send_notification(config, msg)
                notified[nudge_key] = now_iso
                log(f"Follow-up nudge sent for {title}")
        except Exception:
            pass


def simulate(config: dict, days: int = 7) -> dict:
    """Dry-run the daemon over N future days. Shows what would happen."""
    log(f"Simulation started: {days} days")

    results = {
        "days_simulated": days,
        "plan_result": {},
        "would_fire": [],
    }

    # Run plan in dry-run mode
    try:
        from action_planner import plan
        results["plan_result"] = plan(config, dry_run=True)
    except Exception as e:
        results["plan_result"] = {"error": str(e)}

    # Check what actions would be due over the window
    try:
        from link_store import get_db, get_due_actions
        conn = get_db()
        now_ts = int(datetime.now(timezone.utc).timestamp())
        end_ts = now_ts + (days * 86400)
        due = conn.execute("""
            SELECT ae.*, l.user_event_uid
            FROM action_events ae
            LEFT JOIN links l ON l.action_event_uid = ae.action_event_uid
            WHERE ae.due_ts >= ? AND ae.due_ts <= ?
            AND ae.status IN ('planned', 'pending')
            ORDER BY ae.due_ts ASC
        """, (now_ts, end_ts)).fetchall()

        for action in due:
            results["would_fire"].append({
                "action_type": action["action_type"],
                "due": datetime.fromtimestamp(action["due_ts"], tz=timezone.utc).isoformat(),
                "status": action["status"],
                "user_event_uid": action["user_event_uid"] if action["user_event_uid"] else "",
            })
        conn.close()
    except Exception as e:
        results["simulation_error"] = str(e)

    # Run proactivity engine in dry mode if available
    try:
        scan = run_scan()
        if config.get("feature_proactivity_engine", True):
            from proactivity_engine import score_events
            scored = score_events(scan, config)
            results["scored_events"] = len(scored.get("actionable", []))
            results["top_events"] = [
                {"title": e.get("title"), "score": e.get("score")}
                for e in scored.get("actionable", [])[:5]
            ]
    except Exception:
        pass

    results["total_would_fire"] = len(results["would_fire"])
    log(f"Simulation complete: {results['total_would_fire']} actions would fire over {days} days")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="Run in a loop (for manual testing)")
    parser.add_argument("--status", action="store_true", help="Print daemon state and exit")
    parser.add_argument("--simulate", action="store_true", help="Dry-run simulation")
    parser.add_argument("--days", type=int, default=7, help="Days to simulate (with --simulate)")
    args = parser.parse_args()

    if args.status:
        state = load_state()
        print(json.dumps(state, indent=2))
        return

    config = load_config()

    if args.simulate:
        result = simulate(config, args.days)
        print(json.dumps(result, indent=2))
        return

    state = load_state()

    if args.loop:
        interval = config.get("daemon_interval_minutes", 15) * 60
        log(f"Running in loop mode, interval={interval}s")
        while True:
            try:
                state = tick(config, state)
                save_state(state)
            except Exception as e:
                log(f"Tick error: {e}")
            time.sleep(interval)
    else:
        # Single run (called by launchd/systemd)
        try:
            state = tick(config, state)
            save_state(state)
        except Exception as e:
            log(f"Fatal tick error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
