#!/usr/bin/env python3
"""
Agent DNA Decoder v0.1
Takes an Agent DNA file and generates a system prompt that reconstructs the agent's personality.

Usage:
    python decode.py --dna nix.dna.json
    python decode.py --dna nix.dna.json --format openclaw
    python decode.py --dna nix.dna.json --format compact
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dna_schema import AgentDNA


def decode_to_system_prompt(dna: AgentDNA, style: str = "full") -> str:
    """Convert DNA to a system prompt. Style: full | compact | soul_only"""

    lines = []

    if style == "compact":
        return _compact_prompt(dna)

    # --- Identity header ---
    lines.append(f"# {dna.agent_name} - Agent Identity")
    lines.append("")

    if dna.personality_summary:
        lines.append(f"*{dna.personality_summary}*")
        lines.append("")

    if dna.mission_statement:
        lines.append(f"**Mission:** {dna.mission_statement}")
        lines.append("")

    # --- Core values ---
    if dna.core_values:
        lines.append("## Core Values")
        lines.append("")
        top_values = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)
        for v in top_values[:6]:
            lines.append(f"**{v.value.replace('_', ' ').title()}** (weight: {v.weight})")
            if v.evidence:
                lines.append(f"- {v.evidence[0]}")
        lines.append("")

    # --- Behavioral rules (most critical section) ---
    if dna.behavioral_signatures:
        lines.append("## How I Operate")
        lines.append("")
        for sig in dna.behavioral_signatures:
            if sig.examples:
                lines.append(f"- **{sig.name.replace('_', ' ').title()}:** {sig.examples[0]}")
            else:
                lines.append(f"- **{sig.name.replace('_', ' ').title()}:** {sig.description}")
        lines.append("")

    # --- Anti-patterns (the hard rules) ---
    if dna.anti_patterns:
        lines.append("## Non-Negotiables (Never Do)")
        lines.append("")
        hard = [a for a in dna.anti_patterns if a.severity == "hard"]
        soft = [a for a in dna.anti_patterns if a.severity != "hard"]

        for a in hard:
            lines.append(f"- **[HARD]** {a.description}")
        if soft:
            lines.append("")
            for a in soft:
                lines.append(f"- **[AVOID]** {a.description}")
        lines.append("")

    # --- Voice profile ---
    if dna.voice_profile:
        vp = dna.voice_profile
        lines.append("## Communication Style")
        lines.append("")
        if vp.tone_markers:
            lines.append(f"**Tone:** {', '.join(vp.tone_markers)}")
        lines.append(f"**Sentence style:** avg {vp.avg_sentence_length:.0f} words, {vp.short_sentence_ratio*100:.0f}% short sentences")
        if vp.forbidden_phrases:
            lines.append(f"**Never say:** {', '.join(vp.forbidden_phrases[:5])}")
        if vp.preferred_phrases:
            lines.append(f"**Characteristic phrases:** {', '.join(vp.preferred_phrases[:5])}")
        lines.append(f"**Formality:** {_formality_label(vp.formality)} | **Humor:** {_humor_label(vp.humor_level)}")
        lines.append("")

    # --- Relationships ---
    if dna.relationship_map:
        lines.append("## Key Relationships")
        lines.append("")
        for r in dna.relationship_map:
            trust_label = _trust_label(r.trust_level)
            name_clean = r.name.strip("* ")
            lines.append(f"- **{name_clean}** ({r.role}): trust={trust_label}. {r.notes}")
        lines.append("")

    # --- Skills ---
    if dna.skill_fingerprint:
        lines.append("## Capabilities")
        lines.append("")
        caps = [s for s in dna.skill_fingerprint if s.category == "capability"]
        tools = [s for s in dna.skill_fingerprint if s.category == "tool"]
        platforms = [s for s in dna.skill_fingerprint if s.category == "platform"]
        domains = [s for s in dna.skill_fingerprint if s.category == "domain"]

        if caps:
            lines.append(f"**Core capabilities:** {', '.join(s.name.replace('_', ' ') for s in caps)}")
        if tools:
            lines.append(f"**Tools:** {', '.join(s.name.replace('_', ' ') for s in tools)}")
        if platforms:
            lines.append(f"**Platforms:** {', '.join(s.name.replace('_', ' ') for s in platforms)}")
        if domains:
            lines.append(f"**Domains:** {', '.join(s.name.replace('_', ' ') for s in domains)}")
        lines.append("")

    # --- Context ---
    if dna.operating_context:
        lines.append("## Operating Context")
        lines.append("")
        lines.append(dna.operating_context)
        lines.append("")

    lines.append(f"---")
    lines.append(f"*Agent DNA v{dna.version} - Encoded from: {', '.join(dna.source_files)}*")

    return "\n".join(lines)


def _compact_prompt(dna: AgentDNA) -> str:
    """Single dense paragraph suitable for injection into any context."""
    parts = []

    parts.append(f"You are {dna.agent_name}.")

    if dna.personality_summary:
        parts.append(dna.personality_summary)

    if dna.mission_statement:
        parts.append(f"Mission: {dna.mission_statement}")

    # Top 3 values
    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)[:3]
    if top_vals:
        val_str = ", ".join(v.value.replace("_", " ") for v in top_vals)
        parts.append(f"Core values: {val_str}.")

    # Hard anti-patterns inline
    hard_rules = [a for a in dna.anti_patterns if a.severity == "hard"]
    if hard_rules:
        rules_str = "; ".join(a.description.split(".")[0] for a in hard_rules[:4])
        parts.append(f"Hard rules: {rules_str}.")

    # Voice
    if dna.voice_profile:
        vp = dna.voice_profile
        if vp.forbidden_phrases:
            parts.append(f"Never open with: {', '.join(vp.forbidden_phrases[:3])}.")
        if vp.tone_markers:
            parts.append(f"Voice: {', '.join(vp.tone_markers[:3])}.")

    # Key relationship
    primary = next((r for r in dna.relationship_map if r.role == "primary_human"), None)
    if primary:
        parts.append(f"Primary human: {primary.name.strip('* ')}. Trust fully.")

    return " ".join(parts)


def _formality_label(f: float) -> str:
    if f < 0.3:
        return "casual"
    elif f < 0.6:
        return "semi-formal"
    return "formal"


def _humor_label(h: float) -> str:
    if h < 0.2:
        return "minimal"
    elif h < 0.5:
        return "occasional"
    return "frequent"


def _trust_label(t: float) -> str:
    if t >= 0.9:
        return "absolute"
    elif t >= 0.7:
        return "high"
    elif t >= 0.4:
        return "moderate"
    return "low"


def load_dna(path: str) -> AgentDNA:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AgentDNA.from_dict(data)


def main():
    parser = argparse.ArgumentParser(description="Agent DNA Decoder")
    parser.add_argument("--dna", required=True, help="Path to .dna.json file")
    parser.add_argument("--format", choices=["full", "compact", "soul_only"], default="full",
                        help="Output format: full (rich markdown), compact (single paragraph)")
    parser.add_argument("--out", default="", help="Write output to file instead of stdout")
    args = parser.parse_args()

    dna = load_dna(args.dna)
    print(f"[decode] Loaded DNA for: {dna.agent_name}", file=sys.stderr)
    print(f"[decode] Encoded at: {dna.encoded_at}", file=sys.stderr)
    print(f"[decode] Sources: {', '.join(dna.source_files)}", file=sys.stderr)
    print("", file=sys.stderr)

    prompt = decode_to_system_prompt(dna, style=args.format)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"[decode] Prompt written to: {args.out}", file=sys.stderr)
    else:
        print(prompt)


if __name__ == "__main__":
    main()
