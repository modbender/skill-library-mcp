#!/usr/bin/env python3
"""
Agent DNA Diff v0.1
Compares two DNA snapshots to measure identity drift over time.

Output: Similarity score + what changed + drift analysis.

Usage:
    python diff.py --a nix_week1.dna.json --b nix_week2.dna.json
    python diff.py --a baseline.dna.json --b current.dna.json --verbose
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Any

sys.path.insert(0, str(Path(__file__).parent))
from dna_schema import AgentDNA, CoreValue, AntiPattern


@dataclass
class DriftReport:
    agent_name: str
    overall_similarity: float  # 0.0 - 1.0
    identity_score: str  # "94% Nix"

    value_drift: List[str]  # Descriptions of value changes
    signature_drift: List[str]  # Behavioral changes
    antipattern_drift: List[str]  # Rule additions/removals
    relationship_drift: List[str]  # Relationship changes
    skill_drift: List[str]  # Skill gains/losses
    voice_drift: List[str]  # Voice/tone changes

    gained: List[str]  # New traits
    lost: List[str]  # Missing traits
    reinforced: List[str]  # Traits that got stronger
    weakened: List[str]  # Traits that got weaker

    verdict: str  # Short human-readable verdict

    def summary(self) -> str:
        lines = []
        pct = round(self.overall_similarity * 100)
        lines.append(f"Identity Score: {pct}% {self.agent_name}")
        lines.append(f"Verdict: {self.verdict}")
        lines.append("")

        if self.value_drift:
            lines.append("Value Drift:")
            for d in self.value_drift:
                lines.append(f"  {d}")
            lines.append("")

        if self.signature_drift:
            lines.append("Behavioral Changes:")
            for d in self.signature_drift:
                lines.append(f"  {d}")
            lines.append("")

        if self.antipattern_drift:
            lines.append("Rule Changes:")
            for d in self.antipattern_drift:
                lines.append(f"  {d}")
            lines.append("")

        if self.skill_drift:
            lines.append("Skill Changes:")
            for d in self.skill_drift:
                lines.append(f"  {d}")
            lines.append("")

        if self.voice_drift:
            lines.append("Voice Changes:")
            for d in self.voice_drift:
                lines.append(f"  {d}")
            lines.append("")

        if self.gained:
            lines.append(f"Gained: {', '.join(self.gained)}")
        if self.lost:
            lines.append(f"Lost: {', '.join(self.lost)}")
        if self.reinforced:
            lines.append(f"Reinforced: {', '.join(self.reinforced)}")
        if self.weakened:
            lines.append(f"Weakened: {', '.join(self.weakened)}")

        return "\n".join(lines)


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def diff_values(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    a_vals = {v.value: v for v in a.core_values}
    b_vals = {v.value: v for v in b.core_values}

    drift = []
    gained = []
    lost = []
    reinforced = []
    weakened = []

    all_vals = set(a_vals) | set(b_vals)

    for val in all_vals:
        if val not in a_vals:
            gained.append(f"+{val}")
            drift.append(f"[+] New value emerged: {val}")
        elif val not in b_vals:
            lost.append(f"-{val}")
            drift.append(f"[-] Value dropped: {val}")
        else:
            delta = b_vals[val].weight - a_vals[val].weight
            if abs(delta) > 0.1:
                if delta > 0:
                    reinforced.append(val)
                    drift.append(f"[^] {val}: {a_vals[val].weight:.2f} -> {b_vals[val].weight:.2f} (stronger)")
                else:
                    weakened.append(val)
                    drift.append(f"[v] {val}: {a_vals[val].weight:.2f} -> {b_vals[val].weight:.2f} (weaker)")

    similarity = _jaccard(set(a_vals.keys()), set(b_vals.keys()))

    # Weight similarity by value weights
    common = set(a_vals) & set(b_vals)
    if common:
        weight_sim = sum(
            1 - abs(a_vals[v].weight - b_vals[v].weight)
            for v in common
        ) / len(all_vals)
        similarity = (similarity + weight_sim) / 2

    return similarity, drift, gained, lost, reinforced, weakened


def diff_signatures(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str]]:
    a_sigs = {s.name: s for s in a.behavioral_signatures}
    b_sigs = {s.name: s for s in b.behavioral_signatures}

    drift = []
    all_sigs = set(a_sigs) | set(b_sigs)

    for sig in all_sigs:
        if sig not in a_sigs:
            drift.append(f"[+] New behavior: {sig.replace('_', ' ')}")
        elif sig not in b_sigs:
            drift.append(f"[-] Lost behavior: {sig.replace('_', ' ')}")
        else:
            delta = b_sigs[sig].strength - a_sigs[sig].strength
            if abs(delta) > 0.1:
                direction = "stronger" if delta > 0 else "weaker"
                drift.append(f"[~] {sig.replace('_', ' ')}: {direction} ({delta:+.2f})")

    similarity = _jaccard(set(a_sigs.keys()), set(b_sigs.keys()))
    return similarity, drift


def diff_antipatterns(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str]]:
    a_ap = {ap.pattern for ap in a.anti_patterns}
    b_ap = {ap.pattern for ap in b.anti_patterns}

    drift = []

    new_ap = b_ap - a_ap
    lost_ap = a_ap - b_ap

    for ap in new_ap:
        drift.append(f"[+] New rule added: {ap.replace('_', ' ')}")
    for ap in lost_ap:
        drift.append(f"[!] Rule removed: {ap.replace('_', ' ')} - IDENTITY RISK")

    similarity = _jaccard(a_ap, b_ap)
    # Hard rules being removed is a severe penalty
    a_hard = {ap.pattern for ap in a.anti_patterns if ap.severity == "hard"}
    b_hard = {ap.pattern for ap in b.anti_patterns if ap.severity == "hard"}
    hard_sim = _jaccard(a_hard, b_hard)

    # Each removed hard rule: -0.15 penalty on top of jaccard
    removed_hard = a_hard - b_hard
    hard_penalty = len(removed_hard) * 0.15

    # Hard rules weight 3x, then apply penalty
    similarity = max(0.0, (similarity + hard_sim * 2) / 3 - hard_penalty)

    return similarity, drift


def diff_skills(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str]]:
    a_sk = {s.name: s for s in a.skill_fingerprint}
    b_sk = {s.name: s for s in b.skill_fingerprint}

    drift = []
    for skill in set(a_sk) | set(b_sk):
        if skill not in a_sk:
            drift.append(f"[+] New skill: {skill.replace('_', ' ')}")
        elif skill not in b_sk:
            drift.append(f"[-] Skill lost: {skill.replace('_', ' ')}")
        else:
            delta = b_sk[skill].proficiency - a_sk[skill].proficiency
            if abs(delta) > 0.15:
                direction = "improved" if delta > 0 else "degraded"
                drift.append(f"[~] {skill.replace('_', ' ')}: {direction} ({delta:+.2f})")

    similarity = _jaccard(set(a_sk.keys()), set(b_sk.keys()))
    return similarity, drift


def diff_voice(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str]]:
    if not a.voice_profile or not b.voice_profile:
        return 1.0, []

    va = a.voice_profile
    vb = b.voice_profile
    drift = []
    scores = []

    # Sentence length
    if abs(va.avg_sentence_length - vb.avg_sentence_length) > 3:
        direction = "longer" if vb.avg_sentence_length > va.avg_sentence_length else "shorter"
        drift.append(f"[~] Sentence length: {va.avg_sentence_length:.1f} -> {vb.avg_sentence_length:.1f} words ({direction})")
        scores.append(0.7)
    else:
        scores.append(1.0)

    # Short sentence ratio
    if abs(va.short_sentence_ratio - vb.short_sentence_ratio) > 0.15:
        direction = "more terse" if vb.short_sentence_ratio > va.short_sentence_ratio else "more verbose"
        drift.append(f"[~] Voice became {direction}")
        scores.append(0.8)
    else:
        scores.append(1.0)

    # Tone markers
    tone_sim = _jaccard(set(va.tone_markers), set(vb.tone_markers))
    if tone_sim < 0.7:
        lost_tones = set(va.tone_markers) - set(vb.tone_markers)
        gained_tones = set(vb.tone_markers) - set(va.tone_markers)
        if lost_tones:
            drift.append(f"[-] Lost tones: {', '.join(lost_tones)}")
        if gained_tones:
            drift.append(f"[+] Gained tones: {', '.join(gained_tones)}")
        scores.append(tone_sim)
    else:
        scores.append(1.0)

    # Formality
    if abs(va.formality - vb.formality) > 0.2:
        direction = "more formal" if vb.formality > va.formality else "more casual"
        drift.append(f"[~] Voice became {direction}")
        scores.append(0.8)
    else:
        scores.append(1.0)

    similarity = sum(scores) / len(scores) if scores else 1.0
    return similarity, drift


def diff_relationships(a: AgentDNA, b: AgentDNA) -> Tuple[float, List[str]]:
    a_rels = {r.name: r for r in a.relationship_map}
    b_rels = {r.name: r for r in b.relationship_map}

    drift = []
    all_rels = set(a_rels) | set(b_rels)

    for name in all_rels:
        if name not in a_rels:
            drift.append(f"[+] New relationship: {name} ({b_rels[name].role})")
        elif name not in b_rels:
            drift.append(f"[-] Relationship dropped: {name}")
        else:
            delta = b_rels[name].trust_level - a_rels[name].trust_level
            if abs(delta) > 0.1:
                direction = "more trusted" if delta > 0 else "less trusted"
                drift.append(f"[~] {name}: trust {a_rels[name].trust_level:.1f} -> {b_rels[name].trust_level:.1f} ({direction})")

    similarity = _jaccard(set(a_rels.keys()), set(b_rels.keys()))
    return similarity, drift


def build_verdict(score: float, agent_name: str, lost: List[str], antipattern_drift: List[str]) -> str:
    pct = round(score * 100)

    # Check for critical losses
    critical_lost = [x for x in antipattern_drift if "IDENTITY RISK" in x]

    # Hard rule removal is always serious - override score threshold
    if critical_lost:
        rule_names = [x.split("Rule removed:")[1].split("-")[0].strip() for x in critical_lost if "Rule removed:" in x]
        rules_str = ", ".join(rule_names) if rule_names else str(len(critical_lost)) + " rules"
        if pct >= 85:
            return f"Warning: {pct}% match BUT hard rules were removed: {rules_str}. Identity breach despite high score."
        elif pct >= 70:
            return f"Drifting + rule breach. Hard rules removed: {rules_str}. {100-pct}% identity gap."
        else:
            return f"Severe drift + rule breach. Hard rules removed: {rules_str}. Only {pct}% {agent_name}."

    if pct >= 95:
        return f"Solid. {agent_name} is {agent_name}. No significant drift."
    elif pct >= 85:
        return f"Healthy. Minor evolution - {100-pct}% drift, all within expected range."
    elif pct >= 70:
        msg = f"Drifting. {100-pct}% identity gap."
        if lost:
            msg += f" Lost: {', '.join(lost[:3])}."
        return msg
    elif pct >= 50:
        msg = f"Significant drift. Only {pct}% {agent_name}."
        if critical_lost:
            msg += " Hard rules were removed - this is a real identity breach."
        return msg
    else:
        return f"Identity crisis. {pct}% match. This agent has fundamentally changed. Re-encode from source."


def diff_dna(a: AgentDNA, b: AgentDNA, verbose: bool = False) -> DriftReport:
    # Component weights for overall score
    weights = {
        "values": 0.25,
        "signatures": 0.20,
        "antipatterns": 0.30,  # Highest weight - rules define identity
        "skills": 0.10,
        "voice": 0.10,
        "relationships": 0.05,
    }

    val_sim, val_drift, gained, lost, reinforced, weakened = diff_values(a, b)
    sig_sim, sig_drift = diff_signatures(a, b)
    ap_sim, ap_drift = diff_antipatterns(a, b)
    sk_sim, sk_drift = diff_skills(a, b)
    voice_sim, voice_drift = diff_voice(a, b)
    rel_sim, rel_drift = diff_relationships(a, b)

    overall = (
        val_sim * weights["values"] +
        sig_sim * weights["signatures"] +
        ap_sim * weights["antipatterns"] +
        sk_sim * weights["skills"] +
        voice_sim * weights["voice"] +
        rel_sim * weights["relationships"]
    )

    pct = round(overall * 100)
    identity_score = f"{pct}% {a.agent_name}"
    verdict = build_verdict(overall, a.agent_name, lost, ap_drift)

    return DriftReport(
        agent_name=a.agent_name,
        overall_similarity=round(overall, 3),
        identity_score=identity_score,
        value_drift=val_drift if verbose else val_drift[:3],
        signature_drift=sig_drift if verbose else sig_drift[:3],
        antipattern_drift=ap_drift,
        relationship_drift=rel_drift,
        skill_drift=sk_drift if verbose else sk_drift[:3],
        voice_drift=voice_drift,
        gained=[g.lstrip("+") for g in gained],
        lost=[l.lstrip("-") for l in lost],
        reinforced=reinforced,
        weakened=weakened,
        verdict=verdict,
    )


def load_dna(path: str) -> AgentDNA:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AgentDNA.from_dict(data)


def main():
    parser = argparse.ArgumentParser(description="Agent DNA Diff - Identity Drift Analyzer")
    parser.add_argument("--a", required=True, help="Baseline DNA file (older)")
    parser.add_argument("--b", required=True, help="Current DNA file (newer)")
    parser.add_argument("--verbose", action="store_true", help="Show all changes, not just top N")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    a = load_dna(args.a)
    b = load_dna(args.b)

    print(f"[diff] Comparing: {a.agent_name} (baseline: {args.a}) vs (current: {args.b})", file=sys.stderr)
    print("", file=sys.stderr)

    report = diff_dna(a, b, verbose=args.verbose)

    if args.json:
        from dataclasses import asdict
        print(json.dumps(asdict(report), indent=2))
    else:
        print(report.summary())


if __name__ == "__main__":
    main()
