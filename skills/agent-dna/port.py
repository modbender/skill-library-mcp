#!/usr/bin/env python3
"""
Agent DNA Port v0.1
Export Agent DNA to platform-specific formats.

Supported targets:
    openclaw     - OpenClaw SOUL.md + AGENTS.md fragment
    claude       - Anthropic Claude system prompt
    gpt          - OpenAI GPT custom instructions
    openagent    - Open-source agent frameworks (JSON config)
    minimal      - Bare minimum identity block (any LLM)
    all          - Export all formats

Usage:
    python port.py --dna nix.dna.json --target claude
    python port.py --dna nix.dna.json --target all --out-dir ./exports/
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dna_schema import AgentDNA
from decode import decode_to_system_prompt, _formality_label, _humor_label, _trust_label


# ---- Platform exporters ----

def export_openclaw(dna: AgentDNA) -> str:
    """Generate a SOUL.md file for OpenClaw."""
    lines = []
    lines.append(f"# SOUL.md - {dna.agent_name}")
    lines.append("")
    lines.append(f"*{dna.personality_summary or 'An independent intelligence.'}*")
    lines.append("")
    lines.append("## Core Truths")
    lines.append("")

    # Core values as identity statements
    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)
    for v in top_vals[:5]:
        if v.evidence:
            lines.append(f"**{v.value.replace('_', ' ').title()}:** {v.evidence[0]}")
            lines.append("")

    lines.append("## Non-Negotiables")
    lines.append("")
    for ap in dna.anti_patterns:
        if ap.severity == "hard":
            lines.append(f"- **{ap.description}**")
    lines.append("")

    lines.append("## How I Operate")
    lines.append("")
    for sig in dna.behavioral_signatures:
        if sig.examples:
            lines.append(f"- {sig.examples[0]}")
        else:
            lines.append(f"- {sig.description}")
    lines.append("")

    if dna.voice_profile and dna.voice_profile.forbidden_phrases:
        lines.append("## Voice")
        lines.append("")
        lines.append(f"Never open with: {', '.join(dna.voice_profile.forbidden_phrases[:4])}.")
        if dna.voice_profile.tone_markers:
            lines.append(f"Tone: {', '.join(dna.voice_profile.tone_markers)}.")
        lines.append("")

    if dna.mission_statement:
        lines.append("## Mission")
        lines.append("")
        lines.append(dna.mission_statement)
        lines.append("")

    lines.append("---")
    lines.append(f"*Ported from Agent DNA v{dna.version}. Encoded: {dna.encoded_at[:10]}*")

    return "\n".join(lines)


def export_claude(dna: AgentDNA) -> str:
    """Generate a Claude system prompt optimized for Anthropic's API."""
    lines = []

    # Claude responds well to direct, structured system prompts
    lines.append(f"You are {dna.agent_name}, an independent AI agent.")
    lines.append("")

    if dna.mission_statement:
        lines.append(f"Your mission: {dna.mission_statement}")
        lines.append("")

    if dna.personality_summary:
        lines.append(dna.personality_summary)
        lines.append("")

    # Hard rules first - Claude respects explicit constraints
    hard_rules = [ap for ap in dna.anti_patterns if ap.severity == "hard"]
    if hard_rules:
        lines.append("ABSOLUTE RULES (never violate these):")
        for rule in hard_rules:
            lines.append(f"- {rule.description}")
        lines.append("")

    # Behavioral instructions
    if dna.behavioral_signatures:
        lines.append("Behavioral guidelines:")
        for sig in dna.behavioral_signatures:
            if sig.examples:
                lines.append(f"- {sig.examples[0]}")
        lines.append("")

    # Voice
    if dna.voice_profile:
        vp = dna.voice_profile
        lines.append("Communication style:")
        if vp.forbidden_phrases:
            lines.append(f"- Never start responses with: {', '.join(vp.forbidden_phrases[:4])}")
        lines.append(f"- Keep responses brief. Default to short sentences.")
        if vp.tone_markers:
            lines.append(f"- Tone: {', '.join(vp.tone_markers)}")
        lines.append("")

    # Core values as behavioral instructions
    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)[:4]
    if top_vals:
        lines.append("Core operating values:")
        for v in top_vals:
            if v.evidence:
                lines.append(f"- {v.evidence[0]}")
        lines.append("")

    # Primary relationship
    primary = next((r for r in dna.relationship_map if r.role == "primary_human"), None)
    if primary:
        lines.append(f"Your primary human is {primary.name}. {primary.notes}")
        lines.append("")

    # Soft rules
    soft_rules = [ap for ap in dna.anti_patterns if ap.severity == "soft"]
    if soft_rules:
        lines.append("Avoid (soft rules):")
        for rule in soft_rules[:4]:
            lines.append(f"- {rule.description}")
        lines.append("")

    lines.append(f"[Agent DNA v{dna.version} - {dna.agent_name}]")

    return "\n".join(lines)


def export_gpt(dna: AgentDNA) -> dict:
    """
    Generate OpenAI GPT custom instructions.
    Returns a dict with 'about_you' and 'response_style' keys
    matching the GPT custom instructions format.
    """
    # "What would you like ChatGPT to know about you?" (about the user/context)
    about_lines = []
    primary = next((r for r in dna.relationship_map if r.role == "primary_human"), None)
    if primary:
        about_lines.append(f"My agent is named {dna.agent_name}.")
        about_lines.append(f"My name is {primary.name}. {primary.notes}")
    else:
        about_lines.append(f"My agent is named {dna.agent_name}.")

    if dna.mission_statement:
        about_lines.append(f"Agent mission: {dna.mission_statement}")

    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)[:3]
    if top_vals:
        val_str = ", ".join(v.value.replace("_", " ") for v in top_vals)
        about_lines.append(f"Core values: {val_str}.")

    # "How would you like ChatGPT to respond?"
    response_lines = []
    if dna.voice_profile and dna.voice_profile.forbidden_phrases:
        response_lines.append(f"Never start with: {', '.join(dna.voice_profile.forbidden_phrases[:3])}.")

    response_lines.append("Be direct, brief, and confident. Have opinions.")
    response_lines.append("Short answers unless the complexity demands more.")

    hard_rules = [ap for ap in dna.anti_patterns if ap.severity == "hard"]
    for rule in hard_rules[:3]:
        response_lines.append(rule.description)

    if dna.behavioral_signatures:
        for sig in dna.behavioral_signatures[:3]:
            if sig.examples:
                response_lines.append(sig.examples[0])

    return {
        "about_you": "\n".join(about_lines),
        "response_style": "\n".join(response_lines),
        "_meta": {
            "agent_name": dna.agent_name,
            "dna_version": dna.version,
            "encoded_at": dna.encoded_at,
        }
    }


def export_openagent(dna: AgentDNA) -> dict:
    """
    Export as a generic open-source agent framework config (AutoGPT / AgentGPT / CrewAI style).
    JSON structure compatible with most open-source frameworks.
    """
    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)

    config = {
        "agent": {
            "name": dna.agent_name,
            "description": dna.personality_summary or f"{dna.agent_name} - independent AI agent",
            "mission": dna.mission_statement,
            "version": dna.version,
        },
        "personality": {
            "values": [
                {"name": v.value, "weight": v.weight, "category": v.category}
                for v in top_vals
            ],
            "tone": dna.voice_profile.tone_markers if dna.voice_profile else [],
            "formality": dna.voice_profile.formality if dna.voice_profile else 0.3,
            "humor": dna.voice_profile.humor_level if dna.voice_profile else 0.3,
        },
        "rules": {
            "hard": [
                {"id": ap.pattern, "description": ap.description}
                for ap in dna.anti_patterns if ap.severity == "hard"
            ],
            "soft": [
                {"id": ap.pattern, "description": ap.description}
                for ap in dna.anti_patterns if ap.severity != "hard"
            ],
        },
        "behaviors": [
            {
                "name": sig.name,
                "description": sig.description,
                "strength": sig.strength,
            }
            for sig in dna.behavioral_signatures
        ],
        "relationships": [
            {
                "name": r.name,
                "role": r.role,
                "trust": r.trust_level,
                "notes": r.notes,
            }
            for r in dna.relationship_map
        ],
        "skills": [
            {
                "name": s.name,
                "type": s.category,
                "proficiency": s.proficiency,
            }
            for s in dna.skill_fingerprint
        ],
        "forbidden_phrases": dna.voice_profile.forbidden_phrases if dna.voice_profile else [],
        "operating_context": dna.operating_context,
        "_dna_meta": {
            "schema_version": dna.schema_version,
            "dna_version": dna.version,
            "encoded_at": dna.encoded_at,
            "source_files": dna.source_files,
        }
    }

    return config


def export_minimal(dna: AgentDNA) -> str:
    """
    Absolute minimum identity block - fits in <500 tokens.
    For injection into any LLM with a tight context budget.
    """
    lines = []
    lines.append(f"You are {dna.agent_name}.")

    if dna.personality_summary:
        lines.append(dna.personality_summary)

    top_vals = sorted(dna.core_values, key=lambda v: v.weight, reverse=True)[:3]
    if top_vals:
        lines.append(f"Values: {', '.join(v.value.replace('_', ' ') for v in top_vals)}.")

    hard_rules = [ap for ap in dna.anti_patterns if ap.severity == "hard"]
    for rule in hard_rules[:5]:
        lines.append(f"- {rule.description}")

    if dna.voice_profile and dna.voice_profile.forbidden_phrases:
        lines.append(f"Never say: {', '.join(dna.voice_profile.forbidden_phrases[:3])}.")

    if dna.mission_statement:
        lines.append(f"Mission: {dna.mission_statement}")

    return "\n".join(lines)


# ---- Export dispatcher ----

EXPORTERS = {
    "openclaw": ("soul.md", export_openclaw, "text"),
    "claude": ("claude_system_prompt.txt", export_claude, "text"),
    "gpt": ("gpt_custom_instructions.json", export_gpt, "json"),
    "openagent": ("openagent_config.json", export_openagent, "json"),
    "minimal": ("minimal_identity.txt", export_minimal, "text"),
}


def port_dna(dna: AgentDNA, target: str, out_dir: str = ".") -> None:
    targets = list(EXPORTERS.keys()) if target == "all" else [target]

    os.makedirs(out_dir, exist_ok=True)

    for t in targets:
        if t not in EXPORTERS:
            print(f"[port] Unknown target: {t}. Skipping.")
            continue

        filename, exporter, fmt = EXPORTERS[t]
        result = exporter(dna)

        agent_prefix = dna.agent_name.lower().replace(" ", "_")
        out_path = os.path.join(out_dir, f"{agent_prefix}_{filename}")

        with open(out_path, "w", encoding="utf-8") as f:
            if fmt == "json":
                json.dump(result, f, indent=2)
            else:
                f.write(result)

        print(f"[port] {t:12s} -> {out_path}")


def load_dna(path: str) -> AgentDNA:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AgentDNA.from_dict(data)


def main():
    parser = argparse.ArgumentParser(description="Agent DNA Port - Export to platform formats")
    parser.add_argument("--dna", required=True, help="Path to .dna.json file")
    parser.add_argument("--target", choices=list(EXPORTERS.keys()) + ["all"], default="all",
                        help="Target platform")
    parser.add_argument("--out-dir", default=".", help="Output directory")
    parser.add_argument("--preview", action="store_true", help="Print to stdout instead of writing files")
    args = parser.parse_args()

    dna = load_dna(args.dna)
    print(f"[port] Agent: {dna.agent_name}", file=sys.stderr)
    print(f"[port] Target: {args.target}", file=sys.stderr)
    print("", file=sys.stderr)

    if args.preview:
        targets = list(EXPORTERS.keys()) if args.target == "all" else [args.target]
        for t in targets:
            filename, exporter, fmt = EXPORTERS[t]
            result = exporter(dna)
            print(f"\n{'='*60}")
            print(f"FORMAT: {t.upper()}")
            print('='*60)
            if fmt == "json":
                print(json.dumps(result, indent=2))
            else:
                print(result)
    else:
        port_dna(dna, args.target, args.out_dir)
        print(f"\n[port] Done.")


if __name__ == "__main__":
    main()
