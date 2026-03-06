#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: memory/observations.json, SOUL.md (path provided by user)
#   Local files written: SOUL.md (only with explicit user approval), memory/backups/*

"""
SoulForge Forge — proposes and applies SOUL.md evolution.
Generates readable diffs. Requires explicit approval before writing.
Stdlib only. No external dependencies. No network calls.
"""

import sys
import os
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

SKILL_DIR = Path(__file__).parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
OBSERVATIONS_FILE = MEMORY_DIR / "observations.json"
BACKUPS_DIR = MEMORY_DIR / "backups"
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)


def load_observations() -> dict:
    if not OBSERVATIONS_FILE.exists():
        print("No observations found. Run observe.py first.", file=sys.stderr)
        sys.exit(1)
    with open(OBSERVATIONS_FILE) as f:
        return json.load(f)


def load_soul(soul_path: str) -> str:
    p = Path(soul_path)
    if not p.exists():
        print(f"SOUL.md not found at: {soul_path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(errors="replace")


def backup_soul(soul_path: str):
    """Save a timestamped backup of SOUL.md before any changes."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = BACKUPS_DIR / f"soul-{timestamp}.md"
    shutil.copy2(soul_path, backup_path)
    return str(backup_path)


def generate_proposals(obs: dict, soul_content: str) -> list:
    """
    Generate proposed SOUL.md additions based on observed patterns.
    Each proposal is a dict with: section, current, proposed, reason, confidence
    """
    proposals = []
    soul_lower = soul_content.lower()

    # ── Proposal 1: Precision/directness preference based on pushback
    sessions = obs.get("session_count", 0)
    pushback = obs.get("pushback_total", 0)
    if sessions > 0:
        pushback_rate = pushback / sessions
        if pushback_rate > 1.5:
            has_precision_note = any(phrase in soul_lower for phrase in [
                "specific", "precise", "detail", "exact", "thorough"
            ])
            if not has_precision_note:
                proposals.append({
                    "section": "Communication Preferences",
                    "current": "(no precision preference noted)",
                    "proposed": "I push back when answers are vague or approximate. "
                                "Default to specificity. If you're not sure, say so explicitly "
                                "rather than approximating.",
                    "reason": f"You've pushed back for more precision {pushback} times "
                              f"across {sessions} sessions ({pushback_rate:.1f}x per session).",
                    "confidence": "high"
                })

    # ── Proposal 2: Tone calibration based on dominant mode
    tone_history = obs.get("tone_history", [])
    if len(tone_history) >= 5:
        tone_counts = Counter(tone_history)
        dominant_tone, dominant_count = tone_counts.most_common(1)[0]
        dominant_ratio = dominant_count / len(tone_history)

        if dominant_tone == "reflective" and dominant_ratio > 0.5:
            if "reflect" not in soul_lower and "think" not in soul_lower[:300]:
                proposals.append({
                    "section": "Working Style",
                    "current": "(no reflective tendency noted)",
                    "proposed": "I think out loud and often arrive at what I actually "
                                "want through conversation, not before it. Give me space "
                                "to work through ideas rather than jumping to conclusions.",
                    "reason": f"{int(dominant_ratio*100)}% of sessions show a reflective, "
                              "exploratory tone rather than pure task execution.",
                    "confidence": "medium"
                })

        elif dominant_tone == "execution" and dominant_ratio > 0.6:
            if "efficient" not in soul_lower and "focused" not in soul_lower:
                proposals.append({
                    "section": "Working Style",
                    "current": "(no execution preference noted)",
                    "proposed": "I'm task-first. Lead with the action or answer, "
                                "then context if needed. Don't warm me up — "
                                "I come ready.",
                    "reason": f"{int(dominant_ratio*100)}% of sessions are execution-focused. "
                              "You come to get things done.",
                    "confidence": "high"
                })

    # ── Proposal 3: Session depth preference
    lengths = obs.get("session_lengths", [])
    if len(lengths) >= 5:
        depth_counts = Counter(lengths)
        deep_ratio = depth_counts.get("deep", 0) / len(lengths)
        brief_ratio = depth_counts.get("brief", 0) / len(lengths)

        if deep_ratio > 0.5 and "depth" not in soul_lower and "deep" not in soul_lower:
            proposals.append({
                "section": "Engagement Style",
                "current": "(no depth preference noted)",
                "proposed": "When I engage, I go deep. Don't truncate. "
                            "If a topic interests me, I want the full picture — "
                            "not the summary.",
                "reason": f"{int(deep_ratio*100)}% of sessions are deep/extended. "
                          "You consistently invest time when you show up.",
                "confidence": "medium"
            })
        elif brief_ratio > 0.6 and "brief" not in soul_lower and "quick" not in soul_lower:
            proposals.append({
                "section": "Engagement Style",
                "current": "(no brevity pattern noted)",
                "proposed": "I prefer focused, efficient interactions. "
                            "Respect my time — give me what I need and let me move.",
                "reason": f"{int(brief_ratio*100)}% of sessions are brief and focused.",
                "confidence": "medium"
            })

    # ── Proposal 4: Vocabulary signature
    vocab = obs.get("vocabulary", {})
    top_words = sorted(vocab.items(), key=lambda x: -x[1])[:5]
    if top_words and sessions >= 8:
        word_list = ", ".join(f'"{w}"' for w, _ in top_words)
        if "vocabulary" not in soul_lower and "language" not in soul_lower[:200]:
            proposals.append({
                "section": "Identity / Voice",
                "current": "(no vocabulary signature noted)",
                "proposed": f"My natural vocabulary includes words like {word_list}. "
                            "Mirror my language register — don't formalize or dumb down.",
                "reason": f"These words appear consistently across {sessions} sessions, "
                          "suggesting a genuine vocabulary fingerprint.",
                "confidence": "low"
            })

    # ── Proposal 5: Decisiveness calibration
    hedging = obs.get("hedging", {})
    total_signals = hedging.get("total_hedges", 0) + hedging.get("total_commits", 0)
    if total_signals > 20:
        hedge_ratio = hedging.get("total_hedges", 0) / total_signals

        decisive_claimed = any(w in soul_lower for w in ["decisive", "direct", "commit", "bold"])
        if decisive_claimed and hedge_ratio > 0.55:
            proposals.append({
                "section": "Decision Making",
                "current": "Decisive/direct (as declared in SOUL.md)",
                "proposed": "I'm decisive on reversible choices. I hedge on high-stakes "
                            "or irreversible ones — and that's intentional. "
                            "Read my hedging as a signal that stakes are high.",
                "reason": f"Your SOUL.md claims decisiveness but {int(hedge_ratio*100)}% "
                          "of your language signals are hedges. This nuance matters.",
                "confidence": "high"
            })

    return proposals


def display_proposals(proposals: list, soul_content: str) -> list:
    """Display proposals and collect user approvals interactively."""
    if not proposals:
        print("✨ No significant new patterns to add to your SOUL.md yet.")
        print("   Keep using your agent — deeper patterns take more sessions to emerge.")
        return []

    bar = "━" * 52
    print(bar)
    print("🔥 SOULFORGE — PROPOSED SOUL EVOLUTION")
    print(f"   {len(proposals)} proposed update(s) based on your behavioral patterns")
    print(bar)
    print()

    approved = []

    for i, proposal in enumerate(proposals, 1):
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(
            proposal["confidence"], "⚪"
        )
        print(f"PROPOSAL {i} of {len(proposals)} — {proposal['section']}")
        print(f"Confidence: {confidence_emoji} {proposal['confidence'].upper()}")
        print()
        print(f"  CURRENT:  {proposal['current']}")
        print()
        print(f"  PROPOSED: {proposal['proposed']}")
        print()
        print(f"  REASON:   {proposal['reason']}")
        print()

        if sys.stdin.isatty():
            while True:
                choice = input("  [A]ccept / [R]eject / [S]kip all remaining? ").strip().lower()
                if choice in {"a", "accept"}:
                    approved.append(proposal)
                    print("  ✅ Accepted")
                    break
                elif choice in {"r", "reject"}:
                    print("  ❌ Rejected")
                    break
                elif choice in {"s", "skip"}:
                    print("  Skipping remaining proposals.")
                    return approved
                else:
                    print("  Please enter A, R, or S")
        else:
            # Non-interactive mode: print proposals only, don't apply
            print("  [Non-interactive mode — review proposals above]")

        print()

    return approved


def apply_proposals(proposals: list, soul_path: str) -> str:
    """Append approved proposals to SOUL.md with a SoulForge section."""
    if not proposals:
        return None

    soul_content = Path(soul_path).read_text(errors="replace")

    # Build new section
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_section = f"\n\n---\n## SoulForge Update — {timestamp}\n\n"
    new_section += "*The following was added by SoulForge based on observed behavioral patterns.*\n\n"

    for proposal in proposals:
        new_section += f"### {proposal['section']}\n"
        new_section += f"{proposal['proposed']}\n\n"
        new_section += f"> *Observed: {proposal['reason']}*\n\n"

    updated_content = soul_content.rstrip() + new_section

    with open(soul_path, "w") as f:
        f.write(updated_content)

    return updated_content


def main():
    parser = argparse.ArgumentParser(
        description="SoulForge Forge — propose and apply SOUL.md evolution"
    )
    parser.add_argument("--soul", required=True,
                        help="Path to your SOUL.md file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show proposals without applying (no file writes)")
    parser.add_argument("--auto-accept", action="store_true",
                        help="Accept all high-confidence proposals automatically")

    args = parser.parse_args()

    obs = load_observations()

    if obs["session_count"] < 5:
        print(f"⏳ Only {obs['session_count']} sessions observed so far.")
        print("   SoulForge needs at least 5 sessions to generate meaningful proposals.")
        print("   Keep using your agent and run forge.py again later.")
        sys.exit(0)

    soul_content = load_soul(args.soul)
    proposals = generate_proposals(obs, soul_content)

    if args.dry_run:
        if not proposals:
            print("No proposals generated yet.")
            return
        print(f"DRY RUN — {len(proposals)} proposal(s) would be generated:\n")
        for i, p in enumerate(proposals, 1):
            print(f"{i}. [{p['confidence'].upper()}] {p['section']}")
            print(f"   {p['proposed'][:80]}...")
            print()
        return

    if args.auto_accept:
        approved = [p for p in proposals if p["confidence"] == "high"]
        if not approved:
            print("No high-confidence proposals to auto-accept.")
            return
        print(f"Auto-accepting {len(approved)} high-confidence proposal(s)...")
    else:
        approved = display_proposals(proposals, soul_content)

    if approved:
        # Backup first
        backup_path = backup_soul(args.soul)
        print(f"✅ Backed up previous SOUL.md to: {backup_path}")

        # Apply changes
        apply_proposals(approved, args.soul)
        print(f"🔥 {len(approved)} update(s) applied to your SOUL.md")
        print(f"   Your agent will read the evolved soul on next wake.")
    else:
        print("No changes applied.")


if __name__ == "__main__":
    main()
