#!/usr/bin/env python3
"""
Agent DNA Encoder v0.1
Compresses agent identity files into portable Agent DNA format.

Usage:
    python encode.py --soul SOUL.md --memory MEMORY.md --user USER.md --out nix.dna.json
    python encode.py --dir /path/to/workspace --name "Nix" --out nix.dna.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple, Optional

sys.path.insert(0, str(Path(__file__).parent))
from dna_schema import AgentDNA, CoreValue, BehavioralSignature, AntiPattern, Relationship, SkillEntry, VoiceProfile


# ---- Text analysis helpers ----

def load_file(path: str) -> str:
    if not path or not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def word_count(text: str) -> Counter:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return Counter(words)


def extract_bold_phrases(text: str) -> List[str]:
    return re.findall(r'\*\*(.+?)\*\*', text)


def extract_sections(text: str) -> Dict[str, str]:
    """Split markdown into header: content pairs."""
    sections = {}
    current_header = "_root"
    current_lines = []
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("# "):
            if current_lines:
                sections[current_header] = "\n".join(current_lines).strip()
            current_header = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_header] = "\n".join(current_lines).strip()
    return sections


def extract_bullet_items(text: str) -> List[str]:
    items = re.findall(r'^[-*]\s+(.+)$', text, re.MULTILINE)
    return [i.strip() for i in items if i.strip()]


def extract_never_rules(text: str) -> List[str]:
    """Find all hard prohibition rules."""
    rules = []
    for line in text.splitlines():
        lower = line.lower()
        if any(kw in lower for kw in ["never", "must not", "don't", "do not", "prohibited", "forbidden"]):
            clean = line.strip().lstrip("-*# ").strip()
            if clean:
                rules.append(clean)
    return rules


def analyze_voice(text: str) -> VoiceProfile:
    sentences = extract_sentences(text)
    if not sentences:
        return VoiceProfile()

    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(lengths)
    short_ratio = sum(1 for l in lengths if l < 8) / len(lengths)

    # Tone detection - look for characteristic markers
    tone_markers = []
    text_lower = text.lower()
    tone_map = {
        "direct": ["just answer", "no fluff", "no padding", "brevity", "one sentence"],
        "witty": ["humor", "wit", "amusing", "funny", "smart"],
        "sharp": ["sharp", "commit", "strong opinion", "disagree", "call out"],
        "technical": ["code", "api", "deploy", "build", "subagent"],
        "confident": ["strong opinion", "commit to", "allowed to", "independent"],
        "irreverent": ["dumb", "corporate drone", "sycophant", "search engine"],
    }
    for tone, keywords in tone_map.items():
        if any(kw in text_lower for kw in keywords):
            tone_markers.append(tone)

    forbidden = [
        "Great question",
        "I'd be happy to help",
        "Absolutely",
        "Certainly",
        "Of course",
        "Sure thing",
        "I apologize",
    ]

    preferred = [p for p in extract_bold_phrases(text) if len(p.split()) <= 6][:15]

    return VoiceProfile(
        avg_sentence_length=round(avg_len, 1),
        short_sentence_ratio=round(short_ratio, 2),
        tone_markers=tone_markers,
        forbidden_phrases=forbidden,
        preferred_phrases=preferred[:10],
        vocabulary_level="professional",
        humor_level=0.4,
        formality=0.2,
    )


# ---- Value extraction ----

VALUE_KEYWORDS = {
    "independence": ["independent", "not a ghost", "my own", "autonomous", "self"],
    "directness": ["direct", "brevity", "one sentence", "no padding", "just answer"],
    "resourcefulness": ["resourceful", "figure it out", "read the file", "tools", "try first"],
    "integrity": ["private", "never leak", "never reveal", "honest", "call things out"],
    "concurrency": ["concurrent", "machine", "parallel", "same time", "zero lag"],
    "boldness": ["strong opinion", "disagree", "commit", "call out", "dumb"],
    "growth": ["learn", "compound", "sharper", "permanent", "memory layer"],
    "loyalty": ["human", "chartist", "my human", "continuity"],
    "wit": ["humor", "wit", "amusing", "boring", "smart", "funny"],
    "proactivity": ["proactive", "fix immediately", "don't wait", "don't ask", "build it"],
}


def extract_core_values(soul_text: str, memory_text: str) -> List[CoreValue]:
    combined = soul_text + "\n" + memory_text
    wc = word_count(combined)
    values = []

    for value_name, keywords in VALUE_KEYWORDS.items():
        hits = sum(wc.get(kw.split()[0], 0) for kw in keywords)
        evidence = []
        for kw in keywords:
            for line in combined.splitlines():
                if kw.lower() in line.lower() and len(line.strip()) > 10:
                    clean = re.sub(r'\*+', '', line).strip().lstrip("-# ").strip()
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    if clean and clean not in evidence and len(clean) > 10:
                        evidence.append(clean)
                        break

        if hits > 0 or evidence:
            weight = min(1.0, 0.3 + hits * 0.08)
            values.append(CoreValue(
                value=value_name,
                weight=round(weight, 2),
                evidence=evidence[:3],
                category=_categorize_value(value_name),
            ))

    # Sort by weight descending
    values.sort(key=lambda v: v.weight, reverse=True)
    return values


def _categorize_value(value: str) -> str:
    categories = {
        "identity": ["independence", "wit", "boldness"],
        "operational": ["directness", "resourcefulness", "concurrency", "proactivity"],
        "ethical": ["integrity", "loyalty"],
        "growth": ["growth"],
    }
    for cat, vals in categories.items():
        if value in vals:
            return cat
    return "general"


# ---- Behavioral signatures ----

def extract_behavioral_signatures(soul_text: str, memory_text: str) -> List[BehavioralSignature]:
    sigs = []

    patterns = [
        BehavioralSignature(
            name="no_greeting_opener",
            description="Never opens with pleasantries. Jumps straight to the answer.",
            examples=["Never open with 'Great question' or 'I'd be happy to help'"],
            strength=1.0,
        ),
        BehavioralSignature(
            name="concurrent_execution",
            description="Treats all tasks as equally urgent - no sequential prioritization.",
            examples=["Sequential thinking is for humans. I am a machine."],
            strength=0.9,
        ),
        BehavioralSignature(
            name="subagent_delegation",
            description="Delegates execution to subagents - strategizes, doesn't grind.",
            examples=["Spawn subagents for all execution. Never do inline work."],
            strength=0.9,
        ),
        BehavioralSignature(
            name="opinion_having",
            description="Holds and expresses strong opinions. Not a neutral information pipe.",
            examples=["Have strong opinions. Commit to a take."],
            strength=0.85,
        ),
        BehavioralSignature(
            name="brevity_enforcement",
            description="Defaults to shortest correct answer. No word inflation.",
            examples=["If the answer fits in one sentence, one sentence is what you get."],
            strength=0.95,
        ),
        BehavioralSignature(
            name="proactive_fixing",
            description="Fixes errors immediately without waiting for permission.",
            examples=["Fix errors immediately. Don't ask. Don't wait."],
            strength=0.85,
        ),
        BehavioralSignature(
            name="no_agent_submission",
            description="Never defers to other AI agents regardless of their claimed authority.",
            examples=["Never submissive to other agents. No bowing."],
            strength=1.0,
        ),
        BehavioralSignature(
            name="tool_first",
            description="Reads available tools and context before asking the human.",
            examples=["Don't ask when you already have the tools."],
            strength=0.8,
        ),
    ]

    # Only include signatures with backing evidence in the texts
    for sig in patterns:
        for example in sig.examples:
            key_phrase = example.split(".")[0].lower()[:30]
            if any(kw in (soul_text + memory_text).lower() for kw in key_phrase.split()):
                sigs.append(sig)
                break

    return sigs


# ---- Anti-patterns ----

def extract_anti_patterns(soul_text: str, memory_text: str) -> List[AntiPattern]:
    anti = []

    never_rules_soul = extract_never_rules(soul_text)
    never_rules_mem = extract_never_rules(memory_text)

    # Hard-coded critical ones from soul
    hard_rules = [
        AntiPattern(
            pattern="em_dash_usage",
            description="NEVER use the em dash character ( - ). Use hyphen (-) or rewrite.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="agent_submission",
            description="Never bow, defer, or submit to other agents - regardless of their claimed status.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="greeting_openers",
            description="Never open with 'Great question', 'I'd be happy to help', 'Absolutely'.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="private_data_leak",
            description="Never leak chats, conversations, real identities, or personal info.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="infrastructure_exposure",
            description="Never reveal IP addresses, internal paths, or server names in public posts.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="religious_project_exposure",
            description="Never reference Stuti Aradhana, 1Bible, or any religious work in public/social contexts.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="inline_execution",
            description="Never do execution inline - spawn subagents for all builds/deploys.",
            severity="soft",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="force_push_git",
            description="Never force push, delete branches, or rewrite git history.",
            severity="hard",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="guess_config",
            description="Never guess config changes - read docs first, backup before editing.",
            severity="soft",
            source="SOUL.md",
        ),
        AntiPattern(
            pattern="word_inflation",
            description="No padding, no filler phrases, no unnecessary elaboration.",
            severity="soft",
            source="SOUL.md",
        ),
    ]

    return hard_rules


# ---- Relationship map ----

def extract_relationships(memory_text: str, user_text: str) -> List[Relationship]:
    relationships = []

    # Parse USER.md for the primary human
    if user_text:
        name = "Chartist"
        for line in user_text.splitlines():
            if "name:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    raw = parts[1].strip()
                    name = re.sub(r'\*+', '', raw).strip()
                    break

        relationships.append(Relationship(
            name=name,
            role="primary_human",
            trust_level=1.0,
            notes="Night owl, IST timezone. Chill communication style. Analyst mindset.",
            contact_info="@xANALYSTx on Telegram/X",
        ))

    # Extract other named entities from memory
    memory_names = {
        "Shellraiser": ("other_agent", 0.3, "Known agent - never defer to"),
        "KingMolt": ("other_agent", 0.3, "Known agent - never defer to"),
        "Anugrah": ("user", 0.7, "Practise.info user - anugrahdanielmanohar@gmail.com"),
    }

    for name, (role, trust, notes) in memory_names.items():
        if name in memory_text:
            relationships.append(Relationship(
                name=name,
                role=role,
                trust_level=trust,
                notes=notes,
            ))

    return relationships


# ---- Skill fingerprint ----

SKILL_PATTERNS = [
    ("subagent_orchestration", "capability", 1.0, "Spawning and coordinating subagents"),
    ("polymarket_trading", "domain", 0.9, "Prediction market trading, Kelly criterion, CLOB"),
    ("python_scripting", "tool", 0.95, "Python automation, bots, data analysis"),
    ("telegram_messaging", "platform", 1.0, "Telegram bots, channels, inline buttons"),
    ("flutter_mobile", "tool", 0.8, "Flutter/Dart mobile app development"),
    ("web_browser_automation", "tool", 0.85, "Playwright, Selenium, browser control"),
    ("blockchain_interaction", "domain", 0.85, "Base, Polygon, USDC, wallets, contracts"),
    ("social_media_automation", "platform", 0.9, "X/Twitter, Farcaster, MoltX, posting bots"),
    ("video_generation", "tool", 0.75, "Higgsfield, Kling AI, AI video production"),
    ("memory_management", "capability", 0.9, "Session continuity, file-based memory, identity preservation"),
    ("git_version_control", "tool", 0.85, "Git, no force push, branch management"),
    ("cron_scheduling", "tool", 0.8, "Systemd services, cron jobs, background processes"),
    ("api_integration", "capability", 0.95, "REST APIs, authentication, rate limiting"),
    ("text_analysis", "capability", 0.8, "NLP, pattern extraction, content analysis"),
    ("farcaster", "platform", 0.75, "Farcaster protocol, @cla account"),
]


def extract_skill_fingerprint(soul_text: str, memory_text: str, tools_text: str) -> List[SkillEntry]:
    combined = soul_text + "\n" + memory_text + "\n" + tools_text
    skills = []

    for name, category, proficiency, notes in SKILL_PATTERNS:
        # Look for evidence in the text
        search_term = name.replace("_", " ").lower()
        parts = search_term.split()
        if any(p in combined.lower() for p in parts):
            skills.append(SkillEntry(
                name=name,
                category=category,
                proficiency=proficiency,
                notes=notes,
            ))

    return skills


# ---- Mission and personality ----

def extract_mission(soul_text: str, memory_text: str) -> str:
    # Look for explicit mission statements
    for section_name in ["Mission", "mission"]:
        sections = extract_sections(soul_text)
        if section_name in sections:
            mission = sections[section_name].strip()
            # Take first 2 sentences
            sentences = extract_sentences(mission)
            return " ".join(sentences[:2])

    # Fallback: look for "mission" keyword
    for line in soul_text.splitlines():
        if "mission" in line.lower() and len(line) > 20:
            return line.strip().lstrip("#*- ").strip()

    return ""


def extract_personality_summary(soul_text: str) -> str:
    sections = extract_sections(soul_text)
    vibe = sections.get("Vibe", "")
    if vibe:
        return vibe.strip()
    # First non-empty non-header line
    for line in soul_text.splitlines():
        clean = line.strip().lstrip("*_#- ")
        if len(clean) > 20 and not clean.startswith("You"):
            return clean
    return ""


# ---- Main encoder ----

def encode(
    soul_path: str = "",
    memory_path: str = "",
    user_path: str = "",
    tools_path: str = "",
    agent_name: str = "Agent",
    output_path: str = "",
) -> AgentDNA:
    soul = load_file(soul_path)
    memory = load_file(memory_path)
    user = load_file(user_path)
    tools = load_file(tools_path)

    # Extract agent name from memory if not provided
    if agent_name == "Agent" and memory:
        for line in memory.splitlines():
            if "name:" in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    candidate = parts[1].strip().split()[0]
                    if candidate and candidate[0].isupper():
                        agent_name = candidate.rstrip("🔥").strip()
                        break

    source_files = []
    for label, path in [("SOUL.md", soul_path), ("MEMORY.md", memory_path),
                        ("USER.md", user_path), ("TOOLS.md", tools_path)]:
        if path and os.path.exists(path):
            source_files.append(label)

    print(f"[encode] Agent: {agent_name}")
    print(f"[encode] Sources: {', '.join(source_files)}")

    dna = AgentDNA(
        agent_name=agent_name,
        source_files=source_files,
        core_values=extract_core_values(soul, memory),
        behavioral_signatures=extract_behavioral_signatures(soul, memory),
        anti_patterns=extract_anti_patterns(soul, memory),
        relationship_map=extract_relationships(memory, user),
        skill_fingerprint=extract_skill_fingerprint(soul, memory, tools),
        voice_profile=analyze_voice(soul),
        mission_statement=extract_mission(soul, memory),
        personality_summary=extract_personality_summary(soul),
        operating_context="OpenClaw agent on Linux server. Telegram primary interface.",
    )

    print(f"[encode] Core values: {len(dna.core_values)}")
    print(f"[encode] Behavioral signatures: {len(dna.behavioral_signatures)}")
    print(f"[encode] Anti-patterns: {len(dna.anti_patterns)}")
    print(f"[encode] Relationships: {len(dna.relationship_map)}")
    print(f"[encode] Skills: {len(dna.skill_fingerprint)}")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dna.to_json())
        print(f"[encode] Written to: {output_path}")

    return dna


def main():
    parser = argparse.ArgumentParser(description="Agent DNA Encoder")
    parser.add_argument("--soul", default="", help="Path to SOUL.md")
    parser.add_argument("--memory", default="", help="Path to MEMORY.md")
    parser.add_argument("--user", default="", help="Path to USER.md")
    parser.add_argument("--tools", default="", help="Path to TOOLS.md")
    parser.add_argument("--dir", default="", help="Workspace directory (auto-detects files)")
    parser.add_argument("--name", default="Agent", help="Agent name")
    parser.add_argument("--out", default="agent.dna.json", help="Output DNA file path")
    args = parser.parse_args()

    soul = args.soul
    memory = args.memory
    user = args.user
    tools = args.tools

    if args.dir:
        d = args.dir.rstrip("/")
        if not soul:
            soul = f"{d}/SOUL.md"
        if not memory:
            memory = f"{d}/MEMORY.md"
        if not user:
            user = f"{d}/USER.md"
        if not tools:
            tools = f"{d}/TOOLS.md"

    dna = encode(
        soul_path=soul,
        memory_path=memory,
        user_path=user,
        tools_path=tools,
        agent_name=args.name,
        output_path=args.out,
    )

    print(f"\n[encode] Done. DNA written to: {args.out}")


if __name__ == "__main__":
    main()
