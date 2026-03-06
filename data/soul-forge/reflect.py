#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: memory/observations.json, SOUL.md (path provided by user)
#   Local files written: none

"""
SoulForge Reflector — surfaces patterns and insights from accumulated observations.
Generates human-readable reflection report.
Stdlib only. No external dependencies. No network calls.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

SKILL_DIR = Path(__file__).parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
OBSERVATIONS_FILE = MEMORY_DIR / "observations.json"


def load_observations() -> dict:
    if not OBSERVATIONS_FILE.exists():
        print("No observations yet. Run observe.py on some sessions first.", file=sys.stderr)
        sys.exit(0)
    with open(OBSERVATIONS_FILE) as f:
        return json.load(f)


def generate_reflection(soul_path: str = None) -> str:
    obs = load_observations()
    lines = []
    bar = "━" * 52

    lines.append(bar)
    lines.append("🔥 SOULFORGE REFLECTION")
    lines.append(f"Based on {obs['session_count']} sessions observed")
    lines.append(bar)
    lines.append("")

    # ── Vocabulary fingerprint
    top_words = sorted(obs.get("vocabulary", {}).items(), key=lambda x: -x[1])[:15]
    if top_words:
        lines.append("📝 YOUR VOCABULARY FINGERPRINT")
        lines.append("Words you actually use (vs. generic assistant vocab):")
        lines.append("  " + ", ".join(f"{w} ({c}x)" for w, c in top_words[:8]))
        lines.append("")

    # ── Tone patterns
    tone_history = obs.get("tone_history", [])
    if len(tone_history) >= 3:
        tone_counts = Counter(tone_history)
        dominant = tone_counts.most_common(1)[0]
        lines.append("🎭 TONE PATTERN")
        lines.append(f"  Dominant mode: {dominant[0]} ({dominant[1]}/{len(tone_history)} sessions)")
        if "urgent" in tone_counts and tone_counts["urgent"] > 2:
            lines.append("  ⚠️  Multiple urgent sessions — you may be under consistent pressure")
        if tone_counts.get("reflective", 0) > tone_counts.get("execution", 0):
            lines.append("  You tend toward reflection over pure task execution")
        else:
            lines.append("  You tend toward execution — you like getting things done")
        lines.append("")

    # ── Session depth
    lengths = obs.get("session_lengths", [])
    if lengths:
        depth_counts = Counter(lengths)
        lines.append("⏱️  SESSION DEPTH")
        lines.append(f"  Brief: {depth_counts.get('brief', 0)} | "
                     f"Medium: {depth_counts.get('medium', 0)} | "
                     f"Deep: {depth_counts.get('deep', 0)}")
        if depth_counts.get("deep", 0) > depth_counts.get("brief", 0):
            lines.append("  You tend to go deep. You engage fully when something matters.")
        else:
            lines.append("  You tend toward focused, efficient sessions.")
        lines.append("")

    # ── Decisiveness signal
    hedging = obs.get("hedging", {})
    total_signals = hedging.get("total_hedges", 0) + hedging.get("total_commits", 0)
    if total_signals > 10:
        hedge_ratio = hedging.get("total_hedges", 0) / total_signals
        lines.append("🎯 DECISIVENESS SIGNAL")
        if hedge_ratio < 0.35:
            lines.append(f"  You communicate with strong commitment ({int((1-hedge_ratio)*100)}% direct language)")
            lines.append("  You commit to positions. You don't leave many escape hatches.")
        elif hedge_ratio > 0.6:
            lines.append(f"  You use hedging language frequently ({int(hedge_ratio*100)}% of signals)")
            lines.append("  This could be intellectual humility — or avoidance of commitment.")
        else:
            lines.append(f"  You balance hedging and commitment roughly equally")
            lines.append("  Context-dependent — you commit when confident, hedge when uncertain.")
        lines.append("")

    # ── Pushback signal
    pushback = obs.get("pushback_total", 0)
    if obs["session_count"] > 0:
        pushback_per_session = pushback / obs["session_count"]
        lines.append("↩️  PRECISION SIGNAL")
        if pushback_per_session > 2:
            lines.append(f"  High pushback frequency ({pushback} total, {pushback_per_session:.1f}/session)")
            lines.append("  You push back when answers aren't precise enough.")
            lines.append("  Your agent should default to specificity, not approximation.")
        elif pushback_per_session > 0.5:
            lines.append(f"  Moderate pushback ({pushback} total)")
            lines.append("  You course-correct when needed, but not obsessively.")
        else:
            lines.append(f"  Low pushback ({pushback} total)")
            lines.append("  You tend to work with what you get, or you're getting good answers.")
        lines.append("")

    # ── Aspiration gap check
    if soul_path:
        soul_file = Path(soul_path)
        if soul_file.exists():
            from observe import check_aspiration_gap  # nocheck
            gaps = check_aspiration_gap(soul_path)
            if gaps:
                lines.append("🪞 ASPIRATION GAPS")
                lines.append("  Things your SOUL.md says vs. what your behavior shows:")
                for g in gaps:
                    lines.append(f"")
                    lines.append(f"  Claim:    \"{g['claim']}\"")
                    lines.append(f"  Reality:  {g['observation']}")
                    lines.append(f"  Insight:  {g['insight']}")
                lines.append("")

    # ── Soul evolution prompt
    lines.append(bar)
    if obs["session_count"] >= 5:
        lines.append("✨ Ready to evolve your soul.")
        lines.append("Run: python3 scripts/forge.py --soul ~/.openclaw/workspace/SOUL.md")
        lines.append("     to generate proposed SOUL.md edits based on these patterns.")
    else:
        sessions_needed = 5 - obs["session_count"]
        lines.append(f"⏳ {sessions_needed} more session(s) needed before SoulForge can propose edits.")
        lines.append("   Keep using your agent — patterns take time to emerge.")
    lines.append(bar)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="SoulForge Reflector — surface patterns from your observed sessions"
    )
    parser.add_argument("--soul", help="Path to SOUL.md to check for aspiration gaps")
    parser.add_argument("--json", action="store_true", help="Output raw observations as JSON")

    args = parser.parse_args()

    if args.json:
        obs = load_observations()
        print(json.dumps(obs, indent=2))
        return

    report = generate_reflection(soul_path=args.soul)
    print(report)


if __name__ == "__main__":
    main()
