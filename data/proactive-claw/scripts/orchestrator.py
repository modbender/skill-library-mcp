#!/usr/bin/env python3
"""
orchestrator.py — Multi-agent orchestration for high-stakes events.

Coordinates proactive-claw with other installed OpenClaw skills to run
a complete pre-event preparation flow autonomously.

Triggered by daemon.py when a high-stakes event is detected.
Reports a unified summary back to the user via pending_nudges.

Usage:
  python3 orchestrator.py --event-id <id> --event-title "Demo" --event-start "2025-03-15T14:00:00+01:00"
  python3 orchestrator.py --dry-run --event-title "Board Review" --event-start "2025-03-20T10:00:00+01:00"
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
SKILLS_ROOT = Path.home() / ".openclaw/workspace/skills"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def skill_exists(name: str) -> bool:
    return (SKILLS_ROOT / name / "SKILL.md").exists()


def run_script(script: str, args: list, input_data: str = None) -> dict:
    """Run a skill script and return parsed JSON output."""
    cmd = [sys.executable, str(SKILL_DIR / "scripts" / script)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                input=input_data, timeout=30)
    except subprocess.TimeoutExpired:
        return {"error": f"Script timed out after 30s: {script}"}
    if result.returncode != 0:
        return {"error": result.stderr[:300]}
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"raw": result.stdout[:500]}


def orchestrate(event_id: str, event_title: str, event_start: str,
                event_type: str, dry_run: bool = False) -> dict:
    """
    Run the full pre-event orchestration flow.
    Returns a summary dict with all steps attempted and results.
    """
    config = load_config()
    steps = []
    summary_lines = []

    def step(name: str, fn):
        try:
            result = fn()
            steps.append({"step": name, "status": "ok", "result": result})
            return result
        except Exception as e:
            steps.append({"step": name, "status": "error", "error": str(e)})
            return None

    # ── Step 1: Check open action items from last occurrence ──────────────────
    def get_open_items():
        result = run_script("memory.py", ["--open-actions"])
        items = result.get("open_action_items", [])
        related = [i for i in items if
                   event_title.lower()[:10] in i.get("event", "").lower() or
                   i.get("event", "").lower()[:10] in event_title.lower()]
        return related

    open_items = step("open_action_items", get_open_items)
    if open_items:
        summary_lines.append(f"⚠️ {len(open_items)} open action item(s) from last time")

    # ── Step 2: Pull cross-skill context ─────────────────────────────────────
    def get_context():
        return run_script("cross_skill.py",
                          ["--event-title", event_title, "--event-type", event_type])

    context = step("cross_skill_context", get_context)
    if context and context.get("context_block"):
        summary_lines.append(f"📎 Context pulled from: {', '.join(context.get('skills_used', []))}")

    # ── Step 3: Get pattern history ───────────────────────────────────────────
    def get_patterns():
        return run_script("memory.py", ["--search", event_title])

    patterns = step("pattern_history", get_patterns)

    # ── Step 4: Schedule prep block (if policy exists, otherwise check) ───────
    def schedule_prep():
        if dry_run:
            return {"dry_run": True, "would_create": f"Prep block for {event_title}"}
        result = run_script("create_checkin.py", [
            "--title", event_title,
            "--event-datetime", event_start,
            "--event-duration", "60",
        ])
        return result

    prep = step("schedule_prep", schedule_prep)
    if prep and prep.get("status") == "created":
        pre = prep.get("pre_checkin", {})
        summary_lines.append(f"📅 Prep scheduled: {pre.get('start_friendly', '')}")

    # ── Step 5: Draft pre-meeting email (if email/gmail skill active) ─────────
    email_draft = None
    if skill_exists("gmail") or skill_exists("email"):
        def draft_email():
            agenda_items = []
            if open_items:
                agenda_items.append(f"Follow-up: {open_items[0]['text']}")
            if context and context.get("context_block"):
                agenda_items.append("See attached context")
            agenda_str = "\n".join(f"- {a}" for a in agenda_items) if agenda_items else "- TBD"
            draft = {
                "subject": f"Prep notes: {event_title}",
                "body": f"Hi,\n\nLooking forward to our {event_title}.\n\nProposed agenda:\n{agenda_str}\n\nLet me know if you'd like to adjust.\n\nBest",
                "status": "draft_ready",
                "note": "Review and send manually or confirm to send via email skill"
            }
            return draft

        email_draft = step("email_draft", draft_email)
        if email_draft and email_draft.get("status") == "draft_ready":
            summary_lines.append("✉️ Pre-meeting email draft ready")

    # ── Step 6: Fetch Notion meeting notes ────────────────────────────────────
    if skill_exists("notion") and context:
        notion_pages = []
        for enrichment in (context.get("enrichments") or []):
            if enrichment.get("skill") == "notion":
                notion_pages = enrichment.get("pages", [])
        if notion_pages:
            summary_lines.append(f"📝 Notion: {notion_pages[0]['title']}")

    # ── Step 7: Write orchestration summary to pending_nudges ─────────────────
    nudge_message = f"🦞 *{event_title}* prep complete:\n" + "\n".join(summary_lines)
    if not dry_run:
        nudges_file = SKILL_DIR / "pending_nudges.json"
        nudges = []
        if nudges_file.exists():
            try:
                nudges = json.loads(nudges_file.read_text())
            except Exception:
                nudges = []
        nudges.append({
            "message": nudge_message,
            "event_id": event_id,
            "type": "orchestration_complete",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "shown": False,
            "email_draft": email_draft,
            "open_items": open_items or [],
            "cross_skill_context": context,
        })
        nudges_file.write_text(json.dumps(nudges, indent=2))

    return {
        "event_title": event_title,
        "event_start": event_start,
        "dry_run": dry_run,
        "steps_attempted": len(steps),
        "steps_ok": sum(1 for s in steps if s["status"] == "ok"),
        "summary": summary_lines,
        "nudge_message": nudge_message,
        "steps": steps,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-id", default="")
    parser.add_argument("--event-title", required=True)
    parser.add_argument("--event-start", required=True)
    parser.add_argument("--event-type", default="one_off_high_stakes")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = orchestrate(
        args.event_id, args.event_title, args.event_start,
        args.event_type, args.dry_run
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
