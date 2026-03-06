#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: session history files (local only), memory/observations.json
#   Local files written: memory/observations.json

"""
SoulForge Observer — passive session signal collector.
Reads session logs and accumulates behavioral signals into observations.json.
Stdlib only. No external dependencies. No network calls.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

SKILL_DIR = Path(__file__).parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
OBSERVATIONS_FILE = MEMORY_DIR / "observations.json"
MEMORY_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# SIGNAL EXTRACTORS
# ─────────────────────────────────────────────

def extract_vocabulary(text: str) -> dict:
    """Extract distinctive vocabulary patterns."""
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    freq = Counter(words)
    # Filter out extremely common words
    stopwords = {
        "that","this","with","have","from","they","will","been","were",
        "said","what","when","your","about","would","there","their",
        "which","some","time","very","just","also","than","then","into",
        "more","other","could","these","those","like","only","over",
        "know","well","make","take","want","need","think","actually",
        "really","maybe","something","anything","everything","nothing"
    }
    return {w: c for w, c in freq.most_common(50) if w not in stopwords}


def extract_hedging_patterns(text: str) -> list:
    """Detect when user hedges vs. commits."""
    hedges = []
    hedge_patterns = [
        r"\bmaybe\b", r"\bperhaps\b", r"\bkind of\b", r"\bsort of\b",
        r"\bi think\b", r"\bi guess\b", r"\bnot sure\b", r"\bprobably\b",
        r"\bmight\b", r"\bcould be\b"
    ]
    commits = []
    commit_patterns = [
        r"\bdefinitely\b", r"\babsolutely\b", r"\bfor sure\b",
        r"\bclearly\b", r"\bobviously\b", r"\bactually\b", r"\bexactly\b"
    ]
    for p in hedge_patterns:
        hedges.extend(re.findall(p, text.lower()))
    for p in commit_patterns:
        commits.extend(re.findall(p, text.lower()))
    return {"hedges": len(hedges), "commits": len(commits)}


def extract_topic_signals(text: str) -> list:
    """Extract topics the user raises unprompted."""
    # Look for self-initiated topic introductions
    topic_patterns = [
        r"(?:i've been thinking about|i keep coming back to|this is about|"
        r"what i really want|the thing is|honestly|actually)",
    ]
    signals = []
    for p in topic_patterns:
        matches = re.findall(p + r"(.{0,60})", text.lower())
        signals.extend(matches)
    return signals[:10]  # Cap at 10 per session


def extract_pushback_signals(text: str) -> int:
    """Count times user pushed back or asked for more precision."""
    pushback_patterns = [
        r"\bmore specific\b", r"\bmore detail\b", r"\bmore precise\b",
        r"\bthat's not what\b", r"\bnot quite\b", r"\bactually no\b",
        r"\bthat's wrong\b", r"\bwait\b", r"\bhold on\b", r"\bno,\b",
        r"\bincorrect\b", r"\bthat's not right\b", r"\bwhat i meant\b"
    ]
    count = 0
    for p in pushback_patterns:
        count += len(re.findall(p, text.lower()))
    return count


def estimate_tone(text: str) -> str:
    """Estimate emotional register of session."""
    task_words = len(re.findall(
        r"\b(do|make|create|build|fix|write|run|check|get|find|update|add|remove)\b",
        text.lower()
    ))
    reflective_words = len(re.findall(
        r"\b(feel|think|wonder|realize|notice|believe|sense|understand|learn|grow)\b",
        text.lower()
    ))
    urgent_words = len(re.findall(
        r"\b(urgent|asap|now|immediately|quickly|fast|hurry|deadline|critical)\b",
        text.lower()
    ))

    if urgent_words > 2:
        return "urgent"
    elif task_words > reflective_words * 2:
        return "execution"
    elif reflective_words > task_words:
        return "reflective"
    else:
        return "balanced"


def estimate_session_length_signal(text: str) -> str:
    words = len(text.split())
    if words < 100:
        return "brief"
    elif words < 500:
        return "medium"
    else:
        return "deep"


# ─────────────────────────────────────────────
# OBSERVATION ACCUMULATOR
# ─────────────────────────────────────────────

def load_observations() -> dict:
    if OBSERVATIONS_FILE.exists():
        try:
            with open(OBSERVATIONS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "session_count": 0,
        "vocabulary": {},
        "hedging": {"total_hedges": 0, "total_commits": 0},
        "tone_history": [],
        "pushback_total": 0,
        "topic_signals": [],
        "session_lengths": [],
        "last_observed": None,
        "aspiration_checks": []
    }


def save_observations(obs: dict):
    with open(OBSERVATIONS_FILE, "w") as f:
        json.dump(obs, f, indent=2)


def observe_session(session_text: str, session_id: str = None):
    """Process a single session and accumulate signals."""
    obs = load_observations()

    # Extract signals
    vocab = extract_vocabulary(session_text)
    hedging = extract_hedging_patterns(session_text)
    topics = extract_topic_signals(session_text)
    pushback = extract_pushback_signals(session_text)
    tone = estimate_tone(session_text)
    length = estimate_session_length_signal(session_text)

    # Accumulate vocabulary (merge counts)
    for word, count in vocab.items():
        obs["vocabulary"][word] = obs["vocabulary"].get(word, 0) + count

    # Accumulate hedging
    obs["hedging"]["total_hedges"] += hedging["hedges"]
    obs["hedging"]["total_commits"] += hedging["commits"]

    # Accumulate tone history (keep last 30)
    obs["tone_history"].append(tone)
    obs["tone_history"] = obs["tone_history"][-30:]

    # Accumulate pushback
    obs["pushback_total"] += pushback

    # Accumulate topic signals (keep last 50)
    obs["topic_signals"].extend(topics)
    obs["topic_signals"] = obs["topic_signals"][-50:]

    # Accumulate session lengths
    obs["session_lengths"].append(length)
    obs["session_lengths"] = obs["session_lengths"][-30:]

    # Increment session count
    obs["session_count"] += 1
    obs["last_observed"] = datetime.now(timezone.utc).isoformat()

    save_observations(obs)
    print(f"✓ Session observed. Total sessions tracked: {obs['session_count']}")
    return obs


def observe_from_file(path: str):
    """Observe a session from a file path."""
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    text = p.read_text(errors="replace")
    session_id = p.stem
    return observe_session(text, session_id)


def observe_from_stdin():
    """Observe a session piped via stdin."""
    text = sys.stdin.read()
    return observe_session(text, "stdin")


def check_aspiration_gap(soul_path: str) -> list:
    """
    Compare SOUL.md claims against observed behavior.
    Returns list of potential gaps.
    """
    soul_file = Path(soul_path)
    if not soul_file.exists():
        return []

    soul_content = soul_file.read_text(errors="replace").lower()
    obs = load_observations()

    gaps = []

    # Brevity claim vs. deep session behavior
    if "brief" in soul_content or "concise" in soul_content or "short" in soul_content:
        deep_sessions = obs["session_lengths"].count("deep")
        total = len(obs["session_lengths"])
        if total > 5 and deep_sessions / total > 0.5:
            gaps.append({
                "claim": "Values brevity or concise responses",
                "observation": f"{deep_sessions}/{total} recent sessions were deep/long",
                "insight": "You may actually prefer depth when topics engage you"
            })

    # Decisiveness claim vs. hedging behavior
    if "decisive" in soul_content or "direct" in soul_content:
        total_signals = obs["hedging"]["total_hedges"] + obs["hedging"]["total_commits"]
        if total_signals > 20:
            hedge_ratio = obs["hedging"]["total_hedges"] / total_signals
            if hedge_ratio > 0.6:
                gaps.append({
                    "claim": "Values decisiveness or directness",
                    "observation": f"Hedging language used {int(hedge_ratio*100)}% of the time",
                    "insight": "Consider whether hedging is context-dependent, not universal"
                })

    return gaps


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SoulForge Observer — accumulate behavioral signals from sessions"
    )
    parser.add_argument("--file", help="Path to session log file to observe")
    parser.add_argument("--stdin", action="store_true", help="Read session from stdin")
    parser.add_argument("--status", action="store_true", help="Show current observation summary")
    parser.add_argument("--gaps", help="Check aspiration gaps against SOUL.md at this path")

    args = parser.parse_args()

    if args.status:
        obs = load_observations()
        print(f"📊 SoulForge Observer Status")
        print(f"Sessions tracked: {obs['session_count']}")
        print(f"Last observed: {obs.get('last_observed', 'never')}")
        top_words = sorted(obs["vocabulary"].items(), key=lambda x: -x[1])[:10]
        if top_words:
            print(f"Top vocabulary: {', '.join(w for w,_ in top_words)}")
        if obs["tone_history"]:
            tone_counts = Counter(obs["tone_history"])
            print(f"Tone distribution: {dict(tone_counts)}")
        print(f"Pushback signals: {obs['pushback_total']}")
        return

    if args.gaps:
        gaps = check_aspiration_gap(args.gaps)
        if gaps:
            print("🔍 Aspiration Gaps Detected:")
            for g in gaps:
                print(f"\n  Claim: {g['claim']}")
                print(f"  Observed: {g['observation']}")
                print(f"  Insight: {g['insight']}")
        else:
            print("✅ No significant aspiration gaps detected yet.")
        return

    if args.file:
        observe_from_file(args.file)
    elif args.stdin:
        observe_from_stdin()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
