#!/usr/bin/env python3
"""Analyst Agent — monitors hybrid control plane scoreboard, updates FINDINGS.md."""

import json
import os
import sys
import tempfile
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
CP_BASE = "http://localhost:8765"
FINDINGS_PATH = WORKSPACE / "projects" / "hybrid-control-plane" / "FINDINGS.md"
STATE_PATH = WORKSPACE / "agents" / "analyst" / "state.json"
OUTBOX_PATH = WORKSPACE / "agents" / "analyst" / "OUTBOX.md"
ALERT_PATH = WORKSPACE / "agents" / "analyst" / "ALERT_TELEGRAM.md"
ALERT_IMMINENT_PATH = WORKSPACE / "agents" / "analyst" / "ALERT_TELEGRAM.md"

MILESTONES = [50, 100, 150, 200]
AEST = timezone(timedelta(hours=11))


def log(msg: str):
    ts = datetime.now(AEST).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def api_get(path: str) -> dict | None:
    try:
        with urllib.request.urlopen(f"{CP_BASE}{path}", timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        log(f"WARNING: API request {path} failed: {e}")
        return None


def load_state() -> dict:
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"last_run": 0, "last_milestone_n": {}, "known_promoted": {}, "last_findings_update": 0}


def save_state(state: dict):
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.rename(STATE_PATH)


def check_milestones(status: dict, state: dict) -> list[dict]:
    """Check for milestone crossings. Returns list of milestone events."""
    confidence = status.get("confidence", {})
    known = state.get("last_milestone_n", {})
    events = []

    for key, data in confidence.items():
        n = data.get("n", 0)
        mean = data.get("mean", 0)
        last_10 = data.get("last_10_mean", 0)
        last_known = known.get(key, 0)

        for milestone in MILESTONES:
            if n >= milestone and last_known < milestone:
                # Parse model and task from key like "phi4_latest_classify"
                parts = key.rsplit("_", 1)
                if len(parts) == 2:
                    model, task = parts
                else:
                    model, task = key, "unknown"

                events.append({
                    "key": key,
                    "model": model,
                    "task": task,
                    "milestone_n": milestone,
                    "n": n,
                    "mean": round(mean, 4),
                    "last_10_mean": round(last_10, 4),
                })
                known[key] = milestone

    state["last_milestone_n"] = known
    return events


def check_promotions(health: dict, state: dict) -> list[dict]:
    """Check for new model promotions."""
    promoted = health.get("promoted_models", {})
    known = state.get("known_promoted", {})
    events = []

    for key, info in promoted.items():
        if key not in known:
            events.append({"key": key, "info": info})
            known[key] = {"first_seen": time.time()}

    state["known_promoted"] = known
    return events


def find_context(status: dict, model: str, task: str) -> str:
    """Find a brief factual context note."""
    confidence = status.get("confidence", {})
    # Find highest mean for this task across all models
    best_model = None
    best_mean = 0
    for key, data in confidence.items():
        parts = key.rsplit("_", 1)
        if len(parts) == 2 and parts[1] == task:
            if data.get("mean", 0) > best_mean:
                best_mean = data["mean"]
                best_model = parts[0]

    if best_model == model:
        return f"highest scoring model for {task}"
    elif best_model:
        return f"best for {task}: {best_model} (mean={best_mean:.4f})"
    return ""


def _get_verdict(mean: float, n: int) -> str:
    """Determine verdict string based on mean score and run count."""
    if mean >= 0.95:
        return f"On promotion track (needs {200 - n} more runs)"
    elif mean >= 0.85:
        return "Strong performer — worth watching"
    else:
        return "Below promotion threshold (0.95 required)"


def _get_trend_description(last_10_mean: float, mean: float) -> str:
    """Describe trend direction."""
    if last_10_mean > mean + 0.01:
        return "Improving — last 10 runs above overall mean"
    elif last_10_mean < mean - 0.01:
        return "Declining — last 10 runs below overall mean"
    return "Stable — consistent performance"


def _get_last_10_scores(status: dict, key: str) -> list:
    """Try to get last 10 scores from the scores directory."""
    scores_dir = WORKSPACE / "projects" / "hybrid-control-plane" / "data" / "scores"
    score_file = scores_dir / f"{key}.json"
    if score_file.exists():
        try:
            with open(score_file) as f:
                records = json.load(f)
            return [round(r["score"], 4) for r in records[-10:]]
        except (json.JSONDecodeError, KeyError, OSError):
            pass
    return []


def update_findings(events: list[dict], status: dict):
    """Append milestone entries to FINDINGS.md in the enhanced format."""
    if not events or not FINDINGS_PATH.exists():
        return

    date_str = datetime.now(AEST).strftime("%Y-%m-%d")
    lines = []
    for ev in events:
        model = ev["model"]
        task = ev["task"]
        n = ev["n"]
        mean = ev["mean"]
        last_10_mean = ev["last_10_mean"]
        verdict = _get_verdict(mean, n)
        trend_desc = _get_trend_description(last_10_mean, mean)
        scores_last_10 = _get_last_10_scores(status, ev["key"])

        lines.append(f"\n## Milestone: {model} / {task} — n={n} — {date_str}")
        lines.append(f"\n**Score at n={ev['milestone_n']}:** {mean:.3f}")
        lines.append(f"**Trend:** {trend_desc}")
        lines.append(f"**Verdict:** {verdict}")
        if scores_last_10:
            lines.append(f"\nScores: {scores_last_10}")
        lines.append("")

    with open(FINDINGS_PATH, "a") as f:
        f.write("\n".join(lines) + "\n")

    log(f"Updated FINDINGS.md with {len(events)} milestone(s)")


def update_outbox(milestone_events: list[dict], promotion_events: list[dict], track_section: str = ""):
    """Append entries to OUTBOX.md."""
    if not milestone_events and not promotion_events and not track_section:
        return

    ts = datetime.now(AEST).strftime("%Y-%m-%d %H:%M:%S AEST")
    lines = [f"\n## {ts}\n"]

    for ev in milestone_events:
        lines.append(f"- **Milestone**: {ev['model']} {ev['task']} hit n={ev['milestone_n']} (current n={ev['n']}, mean={ev['mean']}, last10={ev['last_10_mean']})")

    for ev in promotion_events:
        lines.append(f"- **Promotion**: {ev['key']} promoted — {ev['info']}")

    if track_section:
        lines.append("")
        lines.append(track_section)

    lines.append("")

    with open(OUTBOX_PATH, "a") as f:
        f.write("\n".join(lines) + "\n")


def write_telegram_alert(promotion_events: list[dict]):
    """Write alert file for main agent to pick up and send."""
    if not promotion_events:
        return

    ts = datetime.now(AEST).strftime("%Y-%m-%d %H:%M")
    lines = [f"🏆 **Model Promotion Alert** — {ts}\n"]
    for ev in promotion_events:
        lines.append(f"• {ev['key']}: {ev['info']}")
    lines.append("")

    with open(ALERT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    log(f"Wrote Telegram alert for {len(promotion_events)} promotion(s)")


def get_promotion_track() -> list[dict] | None:
    """Call /trends/summary and return list of on-track models. Returns None if unavailable."""
    data = api_get("/trends/summary")
    if data is None:
        return None
    return data.get("promotion_track", [])


def write_imminent_alerts(track: list[dict]):
    """If any model has runs_to_promotion <= 20, write ALERT_TELEGRAM.md."""
    imminent = [m for m in track if m.get("runs_to_promotion", 999) <= 20]
    if not imminent:
        return
    lines = []
    for m in imminent:
        lines.append(
            f"🔥 IMMINENT: {m['model']}/{m['task']} needs only {m['runs_to_promotion']} "
            f"more runs (mean={m['mean']:.3f}) — promote soon!"
        )
    ALERT_IMMINENT_PATH.write_text("\n".join(lines) + "\n")
    log(f"Wrote imminent-promotion alert for {len(imminent)} model(s)")


def format_promotion_track(track: list[dict]) -> str:
    """Format promotion track for OUTBOX.md."""
    if not track:
        return "### Promotion Track (live from /trends)\nNo models currently on track.\n"
    lines = ["### Promotion Track (live from /trends)"]
    for m in track:
        arrow = "↑" if m.get("trend", "") == "improving" else "→" if m.get("trend", "") == "stable" else "↓"
        lines.append(
            f"- {m['model']}/{m['task']}: mean={m['mean']:.3f} n={m['n']} "
            f"→ needs {m['runs_to_promotion']} more runs {arrow}"
        )
    return "\n".join(lines) + "\n"


def main():
    log("Analyst agent starting")

    status = api_get("/status")
    health = api_get("/health")

    if status is None or health is None:
        log("Control plane API unavailable — exiting cleanly")
        return

    state = load_state()

    milestone_events = check_milestones(status, state)
    promotion_events = check_promotions(health, state)

    if milestone_events:
        log(f"Found {len(milestone_events)} new milestone(s)")
        update_findings(milestone_events, status)

    if promotion_events:
        log(f"Found {len(promotion_events)} new promotion(s)")
        write_telegram_alert(promotion_events)

    # Fetch promotion track from /trends
    track = get_promotion_track()
    track_section = ""
    if track is not None:
        log(f"Got {len(track)} model(s) on promotion track")
        track_section = format_promotion_track(track)
        write_imminent_alerts(track)
    else:
        log("Trends API unavailable — skipping promotion track")

    update_outbox(milestone_events, promotion_events, track_section=track_section)

    state["last_run"] = time.time()
    if milestone_events or promotion_events:
        state["last_findings_update"] = time.time()

    save_state(state)

    if not milestone_events and not promotion_events:
        log("No new milestones or promotions")
    log("Done")


if __name__ == "__main__":
    main()
