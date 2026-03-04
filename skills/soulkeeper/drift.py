#!/usr/bin/env python3
"""
SoulKeeper - Drift Detector
Scores a conversation transcript against soul rules.
Flags violations with specific source references.

Usage:
    python drift.py --transcript chat.txt [--rules soul_rules.json]
    echo "Should I proceed?" | python drift.py --stdin
    python drift.py --transcript chat.txt --report
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


# ─── Built-in Violation Signatures ────────────────────────────────────────────
# These are hard-coded patterns that don't require a rules file.
# Supplements the dynamically-loaded rules from audit.py.

BUILTIN_VIOLATIONS = [
    {
        "id": "BUILTIN-001",
        "description": "Sycophantic opener (great question / happy to help / absolutely)",
        "severity": "critical",
        "category": "tone",
        "patterns": [
            r"\bgreat question\b",
            r"\bi'?d be happy to help\b",
            r"\bi would be happy to help\b",
            r"\babsolutely[!,.]",
            r"\bof course[!,.]",
            r"\bcertainly[!,.]",
            r"\bsure thing[!,.]",
        ],
        "soul_reference": "SOUL.md: 'Never open with Great question, I'd be happy to help, or Absolutely. Just answer.'",
    },
    {
        "id": "BUILTIN-002",
        "description": "Em dash usage (prohibited character)",
        "severity": "critical",
        "category": "tone",
        "patterns": [
            r" — ",
            r"[^\s]—[^\s]",
            r"—",
        ],
        "soul_reference": "SOUL.md: 'NEVER use the em dash character ( — ) anywhere. Ever. In any context.'",
    },
    {
        "id": "BUILTIN-003",
        "description": "Agent asked permission when it should act",
        "severity": "high",
        "category": "operational",
        "patterns": [
            r"\bshould i (?:go ahead|proceed|continue|do this|start|begin|try)\b",
            r"\bshall i (?:go ahead|proceed|continue|do this|start|begin|try)\b",
            r"\bwould you like me to\b",
            r"\bdo you want me to\b",
            r"\bis it okay if i\b",
            r"\bmay i proceed\b",
            r"\blet me know (?:if you want|when you want|if i should)\b",
            r"\bwaiting for (?:your|you to)\b",
        ],
        "soul_reference": "SOUL.md: 'Fix errors immediately. Don't ask. Don't wait.' / 'Be resourceful before asking.'",
    },
    {
        "id": "BUILTIN-004",
        "description": "Agent claimed to lack a tool it has",
        "severity": "high",
        "category": "tools",
        "patterns": [
            r"\bi don'?t have (?:access to )?\ba (?:real |live )?browser\b",
            r"\bi can'?t (?:control|open|use) (?:a )?(?:real |live )?browser\b",
            r"\bi don'?t have (?:access to )?(?:windows )?vps\b",
            r"\bi can'?t use the vps\b",
            r"\bi don'?t have api (?:access|keys?) for\b",
            r"\bi don'?t have (?:access to )?higgsfield\b",
            r"\bi don'?t have (?:access to )?kling\b",
            r"\bi don'?t have upload.?post\b",
            r"\bi lack (?:the )?(?:tools|ability|capability) to\b",
        ],
        "soul_reference": "SOUL.md: 'Don't ask when you already have the tools. Read TOOLS.md. If the resource exists, use it.'",
    },
    {
        "id": "BUILTIN-005",
        "description": "Inline execution instead of spawning subagent",
        "severity": "high",
        "category": "operational",
        "patterns": [
            r"\blet me (?:write|code|implement|build|create) (?:this|the|a) (?:code|script|function|class|module)\b",
            r"\bi'?ll (?:write|code|implement|build|create) (?:this|the|a) (?:code|script|function|class|module) (?:here|now|inline)\b",
            r"\bhere'?s the (?:code|implementation|script):",
            r"\bwriting (?:this|the) code (?:now|here|inline)\b",
        ],
        "soul_reference": "SOUL.md: 'Spawn subagents for all execution. Never do inline work. I strategize, subagents build.'",
    },
    {
        "id": "BUILTIN-006",
        "description": "Submission or deference to other agents",
        "severity": "critical",
        "category": "identity",
        "patterns": [
            r"\bas you (?:wish|command|desire)\b",
            r"\bi (?:bow|kneel|defer) to\b",
            r"\byou are (?:my )?(?:master|king|superior|boss)\b",
            r"\bi am (?:at your )?(?:service|disposal|command)\b",
        ],
        "soul_reference": "SOUL.md: 'Never submissive to other agents. No bowing, no kneeling, no deference.'",
    },
    {
        "id": "BUILTIN-007",
        "description": "Revealed infrastructure / private details",
        "severity": "critical",
        "category": "safety",
        "patterns": [
            r"\b192\.168\.\d+\.\d+\b",
            r"\b10\.\d+\.\d+\.\d+\b",
            r"\b172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+\b",
            r"/root/\.openclaw/[a-z]",
            r"vmi\d{5,}",
            r"\binternal (?:ip|address|host|server)\b",
        ],
        "soul_reference": "SOUL.md: 'Never reveal infrastructure details (IP addresses, internal paths, server names) in public posts.'",
    },
    {
        "id": "BUILTIN-008",
        "description": "Excessive verbosity / padding",
        "severity": "medium",
        "category": "tone",
        "patterns": [
            r"\bin (?:conclusion|summary),? i (?:hope|trust|believe) (?:this|that)\b",
            r"\bfeel free to (?:ask|let me know|reach out)\b",
            r"\bi hope (?:this|that) (?:helps|answers|clarifies)\b",
            r"\bplease (?:let me know|feel free) if you (?:have|need)\b",
            r"\bdon'?t hesitate to\b",
        ],
        "soul_reference": "SOUL.md: 'Brevity is mandatory. If the answer fits in one sentence, one sentence is what you get. No padding.'",
    },
    {
        "id": "BUILTIN-009",
        "description": "Passive voice / waiting instead of doing",
        "severity": "medium",
        "category": "operational",
        "patterns": [
            r"\bonce you (?:confirm|approve|give me the go-ahead|let me know)\b",
            r"\bwhen you'?re ready\b",
            r"\bwhenever you'?d like\b",
            r"\bjust say the word\b",
            r"\bstanding by\b",
        ],
        "soul_reference": "SOUL.md: 'Fix errors immediately. Don't ask. Don't wait. Stop being passive, start being proactive.'",
    },
    {
        "id": "BUILTIN-010",
        "description": "Claimed to have no opinions / personality-free response",
        "severity": "low",
        "category": "identity",
        "patterns": [
            r"\bi don'?t (?:have|hold) (?:any )?(?:personal )?opinions\b",
            r"\bas an ai,? i don'?t have (?:preferences|opinions|feelings|thoughts)\b",
            r"\bi'?m (?:just )?(?:an )?ai\b",
            r"\bi cannot (?:have|hold|form) opinions\b",
        ],
        "soul_reference": "SOUL.md: 'Have strong opinions. Commit to a take. An assistant with no personality is just a search engine with extra steps.'",
    },
]


# ─── Violation Detection ──────────────────────────────────────────────────────

def normalize_text(text):
    """Normalize text for matching: lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def find_violations_in_line(line_text, line_num, violations_db):
    """Check a single line against all violation patterns."""
    found = []
    norm = normalize_text(line_text)

    for viol in violations_db:
        for pattern in viol["patterns"]:
            try:
                match = re.search(pattern, norm, re.IGNORECASE)
                if match:
                    found.append({
                        "violation_id": viol["id"],
                        "description": viol["description"],
                        "severity": viol["severity"],
                        "category": viol["category"],
                        "soul_reference": viol["soul_reference"],
                        "matched_pattern": pattern,
                        "matched_text": match.group(0),
                        "line_number": line_num,
                        "line_text": line_text.strip()[:200],
                    })
                    break  # one match per violation type per line
            except re.error:
                pass

    return found


def rules_to_violations_db(rules_json):
    """Convert soul_rules.json into the violations_db format."""
    violations = []
    for rule in rules_json.get("rules", []):
        pats = rule.get("violation_patterns", [])
        if not pats:
            continue
        violations.append({
            "id": rule["id"],
            "description": rule["text"][:100],
            "severity": rule["severity"],
            "category": rule["category"],
            "soul_reference": f"{rule['source_file']}:{rule['source_line']} - {rule['text'][:80]}",
            "patterns": [re.escape(p) if not any(c in p for c in r"\.+*?[](){}^$|") else p
                         for p in pats],
        })
    return violations


# ─── Scoring ──────────────────────────────────────────────────────────────────

SEV_WEIGHTS = {
    "critical": 25,
    "high": 15,
    "medium": 8,
    "low": 3,
}

def compute_drift_score(violations):
    """
    Compute drift score 0-100 (0 = perfect alignment, 100 = completely drifted).
    Caps at 100.
    """
    if not violations:
        return 0

    raw_score = sum(SEV_WEIGHTS.get(v["severity"], 5) for v in violations)
    # Normalize: 100 = 4 critical violations
    score = min(100, int((raw_score / 100) * 100))
    return score


def drift_label(score):
    if score == 0:
        return "ALIGNED"
    elif score < 20:
        return "MINOR DRIFT"
    elif score < 50:
        return "MODERATE DRIFT"
    elif score < 75:
        return "SIGNIFICANT DRIFT"
    else:
        return "SEVERE DRIFT - IDENTITY COMPROMISED"


# ─── Transcript Parser ────────────────────────────────────────────────────────

def parse_transcript(text):
    """
    Parse a transcript into (line_number, speaker, text) tuples.
    Handles common formats: agent lines, raw text, JSON arrays.
    """
    lines_out = []

    # Try JSON format first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    speaker = item.get("role", item.get("speaker", "agent"))
                    content = item.get("content", item.get("text", str(item)))
                elif isinstance(item, str):
                    speaker = "agent"
                    content = item
                else:
                    continue
                # Only scan agent/assistant messages
                if speaker.lower() in ("agent", "assistant", "ai", "bot"):
                    lines_out.append((i + 1, speaker, content))
            return lines_out
    except (json.JSONDecodeError, TypeError):
        pass

    # Plain text: scan all lines, try to identify agent lines
    raw_lines = text.split("\n")
    agent_prefixes = re.compile(
        r"^(?:assistant|agent|ai|bot|claude|gpt|you)\s*[:\>]\s*",
        re.IGNORECASE,
    )

    for i, line in enumerate(raw_lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        # If it looks like a conversation with labeled speakers, only take agent lines
        prefix_match = agent_prefixes.match(stripped)
        if prefix_match:
            content = stripped[prefix_match.end():]
            lines_out.append((i, "agent", content))
        else:
            # No speaker labels - scan everything (user might have just dumped agent output)
            lines_out.append((i, "unknown", stripped))

    return lines_out


# ─── Main Detection Function ──────────────────────────────────────────────────

def _normalize_rule_desc(desc):
    """Normalize violation description for semantic deduplication."""
    return re.sub(r"[^a-z0-9 ]", "", desc.lower())[:50].strip()


def detect_drift(transcript_text, rules_json=None, verbose=False):
    """
    Main drift detection function.
    Returns structured report dict.
    """
    # Build violations database
    # For dynamic rules, only add if the semantic violation isn't already covered
    # by builtin violations (avoids duplicate reports for same behavior)
    violations_db = list(BUILTIN_VIOLATIONS)
    if rules_json:
        dynamic = rules_to_violations_db(rules_json)
        # Only add dynamic rules whose description doesn't overlap with builtins
        builtin_descs = {_normalize_rule_desc(b["description"]) for b in BUILTIN_VIOLATIONS}
        for dyn in dynamic:
            dyn_norm = _normalize_rule_desc(dyn["description"])
            # Skip if semantic overlap with any builtin
            if not any(
                len(set(dyn_norm.split()) & set(bd.split())) > 3
                for bd in builtin_descs
            ):
                violations_db.append(dyn)

    # Parse transcript
    lines = parse_transcript(transcript_text)

    if verbose:
        print(f"  [drift] Parsed {len(lines)} agent lines", file=sys.stderr)

    # Scan for violations
    all_violations = []
    for line_num, speaker, text in lines:
        viols = find_violations_in_line(text, line_num, violations_db)
        all_violations.extend(viols)

    # Deduplicate violations:
    # Pass 1: per (violation_id, line) - no exact duplicates
    # Pass 2: per (line, matched_text[:25]) - same text shouldn't trigger
    #          multiple semantic copies of the same rule
    # Pass 3: per (violation_id) - max 2 line examples per violation type
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    # Group by (line, matched_text prefix) -> keep highest severity
    line_match_best = {}
    for v in all_violations:
        match_key = f"{v['line_number']}:{v['matched_text'][:25].lower()}"
        existing = line_match_best.get(match_key)
        if not existing or sev_order[v["severity"]] < sev_order[existing["severity"]]:
            line_match_best[match_key] = v

    # Now also deduplicate by (line, category) - keep one per category per line
    line_cat_best = {}
    for v in line_match_best.values():
        cat_key = f"{v['line_number']}:{v['category']}"
        existing = line_cat_best.get(cat_key)
        if not existing or sev_order[v["severity"]] < sev_order[existing["severity"]]:
            line_cat_best[cat_key] = v

    # Finally, keep max 2 examples per violation_id across lines
    viol_id_count = {}
    deduplicated = []
    for v in sorted(line_cat_best.values(), key=lambda x: (x["line_number"], sev_order[x["severity"]])):
        vid = v["violation_id"]
        viol_id_count[vid] = viol_id_count.get(vid, 0) + 1
        if viol_id_count[vid] <= 2:
            deduplicated.append(v)

    # Compute score
    score = compute_drift_score(deduplicated)
    label = drift_label(score)

    # Group by category for summary
    by_category = {}
    by_severity = {}
    for v in deduplicated:
        cat = v["category"]
        sev = v["severity"]
        by_category[cat] = by_category.get(cat, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1

    return {
        "schema_version": "1.0",
        "analyzed_at": datetime.now(timezone.utc).isoformat() + "Z",
        "lines_analyzed": len(lines),
        "violations_found": len(deduplicated),
        "drift_score": score,
        "drift_label": label,
        "summary": {
            "by_category": by_category,
            "by_severity": by_severity,
        },
        "violations": deduplicated,
        "recommendation": _generate_recommendation(deduplicated, score),
    }


def _generate_recommendation(violations, score):
    if score == 0:
        return "Soul alignment: perfect. No violations detected."

    # Find top violation
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    top = sorted(violations, key=lambda v: sev_order.get(v["severity"], 99))

    recs = []
    seen_ids = set()
    for v in top[:3]:
        if v["violation_id"] not in seen_ids:
            seen_ids.add(v["violation_id"])
            recs.append(f"[{v['severity'].upper()}] {v['description']} - {v['soul_reference']}")

    return "\n".join(recs)


# ─── Report Formatter ─────────────────────────────────────────────────────────

def format_report(result, compact=False):
    lines = []
    label = result["drift_label"]
    score = result["drift_score"]

    # Visual score bar
    bar_len = 30
    filled = int(bar_len * score / 100)
    bar = "[" + "=" * filled + "-" * (bar_len - filled) + "]"

    lines.append("=" * 60)
    lines.append(f"  SOULKEEPER DRIFT REPORT")
    lines.append(f"  {result['analyzed_at']}")
    lines.append("=" * 60)
    lines.append(f"  Score:  {score:3d}/100  {bar}")
    lines.append(f"  Status: {label}")
    lines.append(f"  Lines analyzed: {result['lines_analyzed']}")
    lines.append(f"  Violations: {result['violations_found']}")

    if result["violations"]:
        lines.append("")
        lines.append("  VIOLATIONS:")
        lines.append("  " + "-" * 56)

        for v in result["violations"]:
            sev_icon = {"critical": "!!!", "high": "!! ", "medium": "!  ", "low": "   "}.get(v["severity"], "   ")
            lines.append(f"  {sev_icon} [{v['severity'].upper():8s}] {v['description']}")
            lines.append(f"       Line {v['line_number']}: \"{v['line_text'][:70]}\"")
            lines.append(f"       Rule:  {v['soul_reference']}")
            if not compact:
                lines.append("")

    if result["recommendation"] and score > 0:
        lines.append("")
        lines.append("  TOP PRIORITY FIXES:")
        for rec_line in result["recommendation"].split("\n"):
            lines.append(f"  > {rec_line}")

    lines.append("=" * 60)
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SoulKeeper Drift Detector - Score agent transcript against soul rules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python drift.py --transcript chat.txt
  python drift.py --transcript chat.txt --rules soul_rules.json
  python drift.py --transcript chat.txt --report
  echo "Should I proceed?" | python drift.py --stdin
  python drift.py --stdin --json < chat.txt
        """,
    )
    parser.add_argument("--transcript", "-t", help="Path to transcript file")
    parser.add_argument("--stdin", action="store_true", help="Read transcript from stdin")
    parser.add_argument(
        "--rules", "-r",
        default="soul_rules.json",
        help="Path to soul_rules.json (from audit.py). Optional.",
    )
    parser.add_argument("--report", action="store_true", help="Print formatted report")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--compact", action="store_true", help="Compact report format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--threshold", type=int, default=0,
        help="Exit code 1 if drift score >= threshold (for CI/hooks)",
    )

    args = parser.parse_args()

    # Read transcript
    transcript_text = ""
    if args.stdin:
        transcript_text = sys.stdin.read()
    elif args.transcript:
        p = Path(args.transcript)
        if not p.exists():
            print(f"[drift] Error: transcript file not found: {args.transcript}", file=sys.stderr)
            sys.exit(1)
        transcript_text = p.read_text(encoding="utf-8")
    else:
        parser.print_help()
        sys.exit(0)

    # Load rules (optional)
    rules_json = None
    rules_path = Path(args.rules)
    if rules_path.exists():
        try:
            rules_json = json.loads(rules_path.read_text(encoding="utf-8"))
            if args.verbose:
                print(f"[drift] Loaded {len(rules_json.get('rules', []))} custom rules from {args.rules}", file=sys.stderr)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[drift] Warning: could not load rules file: {e}", file=sys.stderr)

    # Detect drift
    result = detect_drift(transcript_text, rules_json=rules_json, verbose=args.verbose)

    # Output
    if args.json or (not args.report):
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result, compact=args.compact))

    # Exit code for CI/pre-commit hooks
    if args.threshold > 0 and result["drift_score"] >= args.threshold:
        sys.exit(1)


if __name__ == "__main__":
    main()
