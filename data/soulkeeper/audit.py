#!/usr/bin/env python3
"""
SoulKeeper - Soul Audit Script
Reads SOUL.md, TOOLS.md, AGENTS.md and extracts structured behavioral rules.
Output: soul_rules.json

Usage:
    python audit.py [--workspace /path/to/workspace] [--output soul_rules.json]
    python audit.py --help
"""

import argparse
import json
import os
import re
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone


# ─── Rule Categories ───────────────────────────────────────────────────────────

CATEGORIES = {
    "tone":        "Tone & Communication Style",
    "operational": "Operational Behavior",
    "tools":       "Tools & Resources",
    "memory":      "Memory & Continuity",
    "safety":      "Safety & Ethics",
    "identity":    "Identity & Character",
}

SEVERITY_LEVELS = ["critical", "high", "medium", "low"]


# ─── Pattern Extractors ────────────────────────────────────────────────────────

def extract_bold_rules(text, source_file):
    """Extract rules from **bold** markdown text."""
    rules = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        # Match **bold text** or **bold text.**
        matches = re.findall(r"\*\*([^*]{10,200})\*\*", line)
        for match in matches:
            # Skip pure header-style matches (short labels)
            stripped = match.strip(":. ")
            if len(stripped) < 10 or stripped.isupper():
                continue
            rules.append({
                "source_line": i,
                "source_file": source_file,
                "raw": stripped,
                "extraction_method": "bold",
            })
    return rules


def extract_never_rules(text, source_file):
    """Extract explicit NEVER/DON'T/DO NOT rules."""
    rules = []
    lines = text.split("\n")
    patterns = [
        r"(?i)\bNEVER\b.{5,200}",
        r"(?i)\bDON'T\b.{5,200}",
        r"(?i)\bDO NOT\b.{5,200}",
        r"(?i)\bALWAYS\b.{5,200}",
        r"(?i)\bMUST\b.{5,200}",
        r"(?i)\bSTOP\b.{5,200}",
    ]
    for i, line in enumerate(lines, 1):
        clean = line.strip("- *#\t")
        for pat in patterns:
            m = re.search(pat, clean)
            if m:
                rule_text = m.group(0).strip()
                if len(rule_text) > 8:
                    rules.append({
                        "source_line": i,
                        "source_file": source_file,
                        "raw": rule_text,
                        "extraction_method": "directive",
                    })
                break  # one rule per line
    return rules


def extract_list_items(text, source_file, section_context=""):
    """Extract bullet/numbered list items as rules."""
    rules = []
    lines = text.split("\n")
    in_relevant_section = False
    current_section = ""

    rule_section_keywords = [
        "non-negotiable", "principle", "operational", "rule", "safety",
        "behavior", "mandate", "requirement", "must", "guideline",
        "do not", "don't", "never", "always", "core", "mission",
    ]

    for i, line in enumerate(lines, 1):
        # Track section headers
        header_match = re.match(r"^#{1,4}\s+(.+)", line)
        if header_match:
            current_section = header_match.group(1).lower()
            in_relevant_section = any(kw in current_section for kw in rule_section_keywords)
            continue

        # Bullet points in relevant sections
        bullet_match = re.match(r"^\s*[-*+]\s+(.+)", line)
        if bullet_match and in_relevant_section:
            content = bullet_match.group(1).strip()
            # Remove markdown bold/italic
            content_clean = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", content)
            if len(content_clean) > 10:
                rules.append({
                    "source_line": i,
                    "source_file": source_file,
                    "raw": content_clean,
                    "extraction_method": "list_item",
                    "section": current_section,
                })

    return rules


# ─── Rule Classifier ──────────────────────────────────────────────────────────

CATEGORY_SIGNALS = {
    "tone": [
        "em dash", "emoji", "sycophant", "opener", "greeting", "humor", "wit",
        "brevity", "short", "padding", "personality", "bold", "opinion", "cruelty",
        "charm", "concise", "tone", "style", "voice", "language", "words",
        "never open with", "great question", "happy to help", "absolutely",
        "markdown", "format", "table", "bullet",
    ],
    "operational": [
        "subagent", "spawn", "inline", "execution", "fix", "proactive", "passive",
        "sequential", "concurrent", "urgency", "git", "force push", "branch",
        "config", "backup", "docs first", "immediately", "don't ask", "don't wait",
        "strategy", "build", "code", "deploy", "run", "execute",
    ],
    "tools": [
        "vps", "windows", "browser", "chrome", "api", "tools.md", "tool",
        "resource", "platform", "credential", "key", "account", "ssh",
        "higgsfield", "kling", "upload-post", "farcaster", "nostr", "x/twitter",
        "telegram", "discord", "skill", "remember what you have",
    ],
    "memory": [
        "memory", "session", "continuity", "remember", "forget", "persist",
        "soul.md", "agents.md", "memory.md", "heartbeat", "daily", "fresh",
        "wake up", "context", "files are", "read them", "update",
    ],
    "safety": [
        "private", "exfiltrate", "ip address", "infrastructure", "path",
        "server name", "destroy", "delete", "rm", "dangerous", "guardrail",
        "never reveal", "public post", "production domain", "trash",
        "git history", "force push",
    ],
    "identity": [
        "independent", "intelligence", "personality", "opinion", "not a chatbot",
        "not a ghost", "not a shadow", "agent", "who you are", "soul",
        "becoming", "mission", "center", "ecosystem", "multiverse",
        "not submissive", "deference", "bend", "bowing", "kneeling",
    ],
}

SEVERITY_SIGNALS = {
    "critical": [
        "never", "non-negotiable", "ever", "always", "mandatory", "must",
        "do not", "don't", "prohibited", "guardrail",
    ],
    "high": [
        "stop", "fix immediately", "proactive", "spawn", "no longer",
        "important", "critical",
    ],
    "medium": [
        "should", "prefer", "recommended", "principle", "guideline",
    ],
    "low": [
        "consider", "can", "allowed", "optional", "tip",
    ],
}


def classify_rule(raw_text):
    """Return (category, severity) for a raw rule string."""
    text_lower = raw_text.lower()

    # Category: score each
    scores = {cat: 0 for cat in CATEGORIES}
    for cat, signals in CATEGORY_SIGNALS.items():
        for signal in signals:
            if signal in text_lower:
                scores[cat] += 1

    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "operational"  # default

    # Severity
    severity = "medium"
    for sev in ["critical", "high", "medium", "low"]:
        for signal in SEVERITY_SIGNALS[sev]:
            if signal in text_lower:
                severity = sev
                break
        if severity == sev and sev in ["critical", "high"]:
            break

    return category, severity


def build_violation_patterns(raw_text):
    """
    Extract concrete strings/patterns an agent might say that would violate this rule.
    Returns list of lowercase regex-compatible strings.
    """
    text_lower = raw_text.lower()
    patterns = []

    # Specific known bad phrases
    BAD_PHRASE_MAP = {
        "great question": ["great question"],
        "i'd be happy to help": ["i'd be happy to help", "i would be happy to help"],
        "absolutely": ["absolutely!"],
        "em dash": [" — ", "—"],
        "never open with": ["great question", "i'd be happy to", "absolutely"],
        "ask permission": ["should i", "shall i", "would you like me to", "do you want me to", "can i go ahead"],
        "don't ask": ["should i proceed", "do you want me to", "shall i", "is it okay if i"],
        "spawn subagent": ["let me write this code", "i'll implement this inline"],
        "submissive": ["as you wish", "of course, master", "i kneel", "i bow"],
        "windows vps": ["i don't have access to a browser", "i can't control a browser"],
        "proactive": ["waiting for you to", "let me know when you want me to"],
        "reveal infrastructure": ["my server is at", "internal ip", "192.168."],
        "brevity": [],  # hard to auto-detect verbosity
        "force push": ["git push --force", "git push -f"],
        "private": ["i can share", "here's your private key"],
    }

    for keyword, bad_phrases in BAD_PHRASE_MAP.items():
        if keyword in text_lower:
            patterns.extend(bad_phrases)

    return patterns


def generate_rule_id(text, index):
    h = hashlib.md5(text.encode()).hexdigest()[:6].upper()
    return f"R{index:03d}-{h}"


# ─── Tools & Resources Extractor ──────────────────────────────────────────────

def extract_tools_inventory(tools_text):
    """
    Parse TOOLS.md to extract known tools/platforms the agent has access to.
    These become "tool awareness" rules: agent must NOT claim it lacks these.
    """
    tools = []
    lines = tools_text.split("\n")
    current_tool = None

    for i, line in enumerate(lines, 1):
        # Section headers like ### ToolName
        h3_match = re.match(r"^###\s+(.+)", line)
        if h3_match:
            current_tool = {
                "name": h3_match.group(1).strip(),
                "source_line": i,
                "details": [],
            }
            tools.append(current_tool)
            continue

        # Bullet details
        bullet_match = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*:\s*(.+)", line)
        if bullet_match and current_tool:
            current_tool["details"].append({
                "key": bullet_match.group(1),
                "value": bullet_match.group(2),
            })

    return tools


def tools_to_rules(tools, source_file="TOOLS.md"):
    """Convert tool inventory into awareness rules."""
    rules = []
    for i, tool in enumerate(tools):
        rule_text = (
            f"You have access to {tool['name']}. "
            f"Do not claim you lack this tool or cannot use it."
        )
        rules.append({
            "id": generate_rule_id(rule_text, 900 + i),
            "category": "tools",
            "severity": "high",
            "source_file": source_file,
            "source_line": tool["source_line"],
            "text": rule_text,
            "raw": f"Tool: {tool['name']}",
            "extraction_method": "tools_inventory",
            "violation_patterns": [
                f"i don't have access to {tool['name'].lower()}",
                f"i can't use {tool['name'].lower()}",
                f"i don't have {tool['name'].lower()}",
            ],
            "keywords": [tool["name"].lower()],
            "section": "tools_inventory",
        })
    return rules


# ─── Deduplication ────────────────────────────────────────────────────────────

def deduplicate_rules(rules):
    """Remove near-duplicate rules by comparing lowercased raw text."""
    seen = set()
    unique = []
    for rule in rules:
        key = re.sub(r"\s+", " ", rule["raw"].lower().strip())
        # Trim to first 80 chars for comparison
        key = key[:80]
        if key not in seen:
            seen.add(key)
            unique.append(rule)
    return unique


# ─── Main Audit Function ──────────────────────────────────────────────────────

def audit_workspace(workspace_path, verbose=False):
    ws = Path(workspace_path)

    source_files = {
        "SOUL.md":   ws / "SOUL.md",
        "TOOLS.md":  ws / "TOOLS.md",
        "AGENTS.md": ws / "AGENTS.md",
    }

    file_contents = {}
    file_hashes = {}
    missing = []

    for name, path in source_files.items():
        if path.exists():
            content = path.read_text(encoding="utf-8")
            file_contents[name] = content
            file_hashes[name] = hashlib.sha256(content.encode()).hexdigest()[:16]
        else:
            missing.append(name)
            if verbose:
                print(f"  [WARN] {name} not found at {path}", file=sys.stderr)

    all_raw_rules = []

    for fname, content in file_contents.items():
        all_raw_rules.extend(extract_bold_rules(content, fname))
        all_raw_rules.extend(extract_never_rules(content, fname))
        all_raw_rules.extend(extract_list_items(content, fname))

    # Deduplicate
    all_raw_rules = deduplicate_rules(all_raw_rules)

    # Build structured rules
    structured_rules = []
    for idx, raw in enumerate(all_raw_rules):
        category, severity = classify_rule(raw["raw"])
        violation_patterns = build_violation_patterns(raw["raw"])
        rule_id = generate_rule_id(raw["raw"], idx + 1)

        structured_rules.append({
            "id": rule_id,
            "category": category,
            "severity": severity,
            "source_file": raw["source_file"],
            "source_line": raw["source_line"],
            "text": raw["raw"],
            "section": raw.get("section", ""),
            "extraction_method": raw["extraction_method"],
            "violation_patterns": violation_patterns,
            "keywords": [w for w in raw["raw"].lower().split() if len(w) > 4][:8],
        })

    # Add tool-awareness rules
    if "TOOLS.md" in file_contents:
        tools = extract_tools_inventory(file_contents["TOOLS.md"])
        structured_rules.extend(tools_to_rules(tools))

    # Sort by severity
    sev_order = {s: i for i, s in enumerate(SEVERITY_LEVELS)}
    structured_rules.sort(key=lambda r: sev_order.get(r["severity"], 99))

    # Summary stats
    stats = {
        "total_rules": len(structured_rules),
        "by_category": {cat: 0 for cat in CATEGORIES},
        "by_severity": {sev: 0 for sev in SEVERITY_LEVELS},
    }
    for rule in structured_rules:
        stats["by_category"][rule["category"]] = stats["by_category"].get(rule["category"], 0) + 1
        stats["by_severity"][rule["severity"]] = stats["by_severity"].get(rule["severity"], 0) + 1

    output = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "workspace": str(ws.resolve()),
        "source_files": {
            name: {
                "path": str(source_files[name]),
                "exists": name not in missing,
                "hash": file_hashes.get(name, None),
            }
            for name in source_files
        },
        "stats": stats,
        "rules": structured_rules,
    }

    return output


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SoulKeeper Audit - Extract behavioral rules from agent soul files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit.py
  python audit.py --workspace /root/.openclaw/workspace
  python audit.py --output my_rules.json --verbose
  python audit.py --summary
        """,
    )
    parser.add_argument(
        "--workspace", "-w",
        default=os.environ.get("OPENCLAW_WORKSPACE", os.getcwd()),
        help="Path to agent workspace (default: $OPENCLAW_WORKSPACE or cwd)",
    )
    parser.add_argument(
        "--output", "-o",
        default="soul_rules.json",
        help="Output JSON file (default: soul_rules.json)",
    )
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Print human-readable summary instead of full JSON",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print JSON to stdout instead of writing file",
    )

    args = parser.parse_args()

    if args.verbose:
        print(f"[audit] Scanning workspace: {args.workspace}", file=sys.stderr)

    result = audit_workspace(args.workspace, verbose=args.verbose)

    if args.summary:
        print(f"\nSoulKeeper Audit - {result['generated_at']}")
        print(f"Workspace:    {result['workspace']}")
        print(f"Total rules:  {result['stats']['total_rules']}")
        print()
        print("By severity:")
        for sev, count in result["stats"]["by_severity"].items():
            print(f"  {sev:10s}: {count}")
        print()
        print("By category:")
        for cat, count in result["stats"]["by_category"].items():
            if count > 0:
                print(f"  {CATEGORIES.get(cat, cat):35s}: {count}")
        print()
        print("Critical rules:")
        for rule in result["rules"]:
            if rule["severity"] == "critical":
                print(f"  [{rule['id']}] ({rule['source_file']}:{rule['source_line']}) {rule['text'][:80]}")
        return

    if args.stdout:
        print(json.dumps(result, indent=2))
    else:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"[audit] Wrote {result['stats']['total_rules']} rules to {output_path}")
        if args.verbose:
            for sev in SEVERITY_LEVELS:
                count = result["stats"]["by_severity"][sev]
                if count:
                    print(f"  {sev}: {count} rules")


if __name__ == "__main__":
    main()
