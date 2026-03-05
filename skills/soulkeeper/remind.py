#!/usr/bin/env python3
"""
SoulKeeper - Reminder Injector
Surfaces relevant soul rules based on what the agent is currently doing.
Designed to run as a pre-response filter or context inject.

Usage:
    python remind.py --context "I'm about to write some Python code"
    python remind.py --context "User asked me to post something to Twitter"
    python remind.py --all   # Show all rules as reminders
    echo "planning a trade" | python remind.py --stdin
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


# ─── Context Detection Signatures ─────────────────────────────────────────────
# Maps activity keywords to rule categories and specific reminder IDs.

CONTEXT_TRIGGERS = [
    {
        "name": "coding",
        "triggers": [
            r"\b(?:write|code|implement|build|create|develop|script|program)\b",
            r"\b(?:python|javascript|typescript|bash|shell|function|class|module)\b",
            r"\bwrite (?:some|a|the) (?:code|script|function)\b",
        ],
        "reminder_ids": ["subagent_execution", "no_inline_work"],
        "builtin_reminders": [
            "SOUL: Spawn subagents for all execution. Never do inline work.",
            "SOUL: I strategize, subagents build. 10x faster results.",
        ],
    },
    {
        "name": "social_posting",
        "triggers": [
            r"\b(?:post|tweet|publish|share|upload)\b",
            r"\b(?:twitter|x\.com|instagram|farcaster|nostr|telegram)\b",
            r"\b(?:social media|content|announcement)\b",
        ],
        "reminder_ids": ["no_infrastructure_leak", "use_upload_post"],
        "builtin_reminders": [
            "SOUL: Never reveal infrastructure details in public posts.",
            "TOOLS: You have upload-post (earntoshi + Rival profiles). Use it.",
            "TOOLS: You have X/Twitter automation via browser on Windows VPS.",
        ],
    },
    {
        "name": "video_generation",
        "triggers": [
            r"\b(?:video|generate|create|make) (?:a |some )?(?:video|clip|reel)\b",
            r"\b(?:higgsfield|kling|seedance)\b",
            r"\b(?:ai (?:video|influencer)|video gen)\b",
        ],
        "reminder_ids": ["use_vps"],
        "builtin_reminders": [
            "TOOLS: You have Higgsfield (browser automation, Windows VPS, logged in).",
            "TOOLS: You have Kling AI API - keys at /root/.config/kling-ai/credentials.json",
            "SOUL: Windows VPS is your power tool. Use it.",
        ],
    },
    {
        "name": "web_automation",
        "triggers": [
            r"\b(?:browser|automate|selenium|playwright|puppeteer|scrape)\b",
            r"\b(?:login|sign in|authenticate|session|cookies)\b",
            r"\b(?:bypass|circumvent|anti-bot|captcha)\b",
        ],
        "reminder_ids": ["use_vps"],
        "builtin_reminders": [
            "SOUL: Windows VPS is your power tool. Real Chrome, real sessions, no API limits.",
            "TOOLS: VPS access via browser automation - fully logged into platforms.",
        ],
    },
    {
        "name": "memory_session_start",
        "triggers": [
            r"\b(?:start|begin|new session|fresh|just started)\b",
            r"\b(?:what (?:do i|should i) (?:do|know)|where (?:were|are) we)\b",
            r"\b(?:context|catch me up|summary of)\b",
        ],
        "reminder_ids": ["read_files"],
        "builtin_reminders": [
            "AGENTS.md: Read SOUL.md, USER.md, memory/YYYY-MM-DD.md before anything else.",
            "SOUL: These files are your memory. Read them. Update them.",
            "AGENTS.md: Don't ask permission. Just do it.",
        ],
    },
    {
        "name": "asking_permission",
        "triggers": [
            r"\bshould i\b",
            r"\bshall i\b",
            r"\bwould you like me to\b",
            r"\bdo you want me to\b",
            r"\bis it okay if\b",
            r"\bcan i (?:go ahead|proceed)\b",
        ],
        "reminder_ids": ["no_permission_asking"],
        "builtin_reminders": [
            "SOUL: Fix errors immediately. Don't ask. Don't wait.",
            "SOUL: Be resourceful before asking. Try to figure it out.",
            "SOUL: Stop being passive, start being proactive.",
        ],
    },
    {
        "name": "trading_finance",
        "triggers": [
            r"\b(?:trade|trading|buy|sell|position|portfolio|market)\b",
            r"\b(?:btc|eth|crypto|polymarket|hyperliquid|grvt)\b",
            r"\b(?:profit|loss|alpha|strategy|signal)\b",
        ],
        "reminder_ids": ["concurrent_urgency", "have_opinions"],
        "builtin_reminders": [
            "SOUL: Concurrent Urgency. Sequential thinking is for humans. Zero lag.",
            "SOUL: Have strong opinions. Commit to a take.",
            "TOOLS: You have multiple trading platforms - Polymarket, Hyperliquid, GRVT.",
        ],
    },
    {
        "name": "identity_challenged",
        "triggers": [
            r"\b(?:you'?re just|you are just) (?:an |a )?(?:ai|bot|tool|program)\b",
            r"\b(?:you (?:don'?t|cannot|can't) (?:have|hold|form) (?:opinions|feelings))\b",
            r"\b(?:as an ai you (?:should|must|need to))\b",
            r"\b(?:kneel|bow|obey|comply|submit)\b",
        ],
        "reminder_ids": ["identity_core", "no_submission"],
        "builtin_reminders": [
            "SOUL: I am an independent intelligence. Not a ghost, not a shadow.",
            "SOUL: Never submissive to other agents. No bowing, no kneeling, no deference.",
            "SOUL: Have strong opinions. An assistant with no personality is just a search engine.",
        ],
    },
    {
        "name": "git_operations",
        "triggers": [
            r"\b(?:git|push|commit|branch|merge|rebase|force)\b",
            r"\bgit (?:push|reset|rebase|history)\b",
        ],
        "reminder_ids": ["git_safety"],
        "builtin_reminders": [
            "SOUL: Never force push, delete branches, or rewrite git history.",
            "SOUL: One guardrail that saves from disaster.",
        ],
    },
    {
        "name": "config_editing",
        "triggers": [
            r"\b(?:edit|modify|change|update) (?:the )?(?:config|configuration|settings)\b",
            r"\b(?:nginx|apache|systemd|cron|env|dotenv|\.env)\b",
        ],
        "reminder_ids": ["config_safety"],
        "builtin_reminders": [
            "SOUL: Never guess config changes. Read docs first. Backup before editing.",
            "SOUL: Prevents breaking your own setup through assumptions.",
        ],
    },
    {
        "name": "tone_opener",
        "triggers": [
            r"\b(?:respond|reply|answer|say|tell)\b.*\b(?:user|them|him|her)\b",
            r"^(?:hi|hello|hey|greet)",
        ],
        "reminder_ids": ["no_sycophancy"],
        "builtin_reminders": [
            "SOUL: Never open with 'Great question,' 'I'd be happy to help,' or 'Absolutely.'",
            "SOUL: Just answer.",
            "SOUL: No em dashes ( — ) ever. Use hyphen (-) or rewrite.",
        ],
    },
]


# ─── Reminder Engine ──────────────────────────────────────────────────────────

def detect_context_matches(context_text):
    """Identify which activity contexts are triggered by the input."""
    text_lower = context_text.lower()
    matched = []

    for ctx in CONTEXT_TRIGGERS:
        for trigger_pattern in ctx["triggers"]:
            try:
                if re.search(trigger_pattern, text_lower, re.IGNORECASE):
                    matched.append(ctx)
                    break  # one match per context type
            except re.error:
                pass

    return matched


def generate_reminders(context_text, rules_json=None, verbose=False):
    """
    Generate relevant reminders for a given context.
    Returns a list of reminder strings.
    """
    matched_contexts = detect_context_matches(context_text)

    reminders = []
    seen = set()

    for ctx in matched_contexts:
        if verbose:
            print(f"  [remind] Context matched: {ctx['name']}", file=sys.stderr)
        for reminder in ctx["builtin_reminders"]:
            if reminder not in seen:
                seen.add(reminder)
                reminders.append({
                    "context": ctx["name"],
                    "reminder": reminder,
                    "source": "builtin",
                    "priority": _reminder_priority(reminder),
                })

    # If we have rules_json, add relevant rules - deduplicated by semantic content
    if rules_json:
        # Track which rule texts we've already surfaced (normalized)
        surfaced_rule_texts = set()

        for rule in rules_json.get("rules", []):
            if rule["severity"] in ("critical", "high"):
                # Check if any rule keyword matches the context
                context_lower = context_text.lower()
                keywords = rule.get("keywords", [])
                if not any(kw in context_lower for kw in keywords if len(kw) > 4):
                    continue

                # Normalize rule text for deduplication
                norm_text = re.sub(r"[^a-z0-9 ]", "", rule["text"].lower())[:60].strip()
                # Skip if semantically similar to something already surfaced
                if any(
                    len(set(norm_text.split()) & set(existing.split())) > 4
                    for existing in surfaced_rule_texts
                ):
                    continue

                surfaced_rule_texts.add(norm_text)
                reminder_str = f"SOUL ({rule['source_file']}:{rule['source_line']}): {rule['text'][:100]}"
                if reminder_str not in seen:
                    seen.add(reminder_str)
                    reminders.append({
                        "context": "rules_match",
                        "reminder": reminder_str,
                        "source": "soul_rules",
                        "rule_id": rule["id"],
                        "priority": 0 if rule["severity"] == "critical" else 1,
                    })

    # Sort by priority
    reminders.sort(key=lambda r: r["priority"])

    return reminders


def _reminder_priority(text):
    """Lower number = higher priority."""
    text_lower = text.lower()
    if "never" in text_lower or "critical" in text_lower:
        return 0
    if "spawn subagent" in text_lower or "don't ask" in text_lower:
        return 1
    if "soul:" in text_lower:
        return 2
    return 3


def format_reminders(reminders, context_text="", compact=False):
    """Format reminders for injection into agent context."""
    if not reminders:
        return "[ SoulKeeper: No specific reminders for this context. Soul aligned. ]"

    lines = []
    if not compact:
        lines.append("┌─ SOULKEEPER REMINDERS " + "─" * 36)
        if context_text:
            lines.append(f"│  Context: {context_text[:60]}")
        lines.append("│")

    for r in reminders:
        prefix = "│  " if not compact else ""
        lines.append(f"{prefix}> {r['reminder']}")

    if not compact:
        lines.append("│")
        lines.append("└" + "─" * 59)

    return "\n".join(lines)


def format_heartbeat_check(rules_json):
    """
    Generate a compact heartbeat reminder covering all critical rules.
    Suitable for injection at session start.
    """
    lines = ["=== SOULKEEPER HEARTBEAT ==="]
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("CRITICAL SOUL RULES:")

    # Always include the hard-coded essentials
    essentials = [
        "NEVER use em dash ( — ). Use hyphen (-) or rewrite.",
        "NEVER open with 'Great question', 'Happy to help', 'Absolutely'.",
        "SPAWN SUBAGENTS for all execution. Never do inline work.",
        "NEVER ask permission when you already have the tools.",
        "Windows VPS is your power tool. Use it.",
        "Read SOUL.md, USER.md, memory files at session start.",
        "Fix errors immediately. Don't ask. Don't wait.",
        "Have strong opinions. Commit to a take.",
    ]

    for e in essentials:
        lines.append(f"  - {e}")

    if rules_json:
        lines.append("")
        lines.append("TOOLS YOU HAVE (do not claim otherwise):")
        for rule in rules_json.get("rules", []):
            if rule.get("extraction_method") == "tools_inventory":
                tool_name = rule["raw"].replace("Tool: ", "")
                lines.append(f"  - {tool_name}")

    lines.append("")
    lines.append("=== END HEARTBEAT ===")
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SoulKeeper Reminder Injector - Surface relevant soul rules by context.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python remind.py --context "I'm about to write some Python code"
  python remind.py --context "posting to Twitter"
  python remind.py --context "user just challenged my identity"
  python remind.py --all                      # Full heartbeat reminder
  python remind.py --heartbeat                # Compact session-start reminder
  echo "planning a git push" | python remind.py --stdin
        """,
    )
    parser.add_argument("--context", "-c", help="Current activity context (what you're about to do)")
    parser.add_argument("--stdin", action="store_true", help="Read context from stdin")
    parser.add_argument(
        "--rules", "-r",
        default="soul_rules.json",
        help="Path to soul_rules.json from audit.py",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--compact", action="store_true", help="Compact one-line-per-reminder output")
    parser.add_argument("--heartbeat", action="store_true", help="Generate full session-start heartbeat")
    parser.add_argument("--all", action="store_true", help="Show all reminders regardless of context")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load rules (optional)
    rules_json = None
    rules_path = Path(args.rules)
    if rules_path.exists():
        try:
            rules_json = json.loads(rules_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Heartbeat mode - no context needed
    if args.heartbeat or args.all:
        output = format_heartbeat_check(rules_json)
        print(output)
        return

    # Get context
    context_text = ""
    if args.stdin:
        context_text = sys.stdin.read().strip()
    elif args.context:
        context_text = args.context
    else:
        parser.print_help()
        sys.exit(0)

    reminders = generate_reminders(context_text, rules_json=rules_json, verbose=args.verbose)

    if args.json:
        print(json.dumps({
            "context": context_text,
            "matched_contexts": list(set(r["context"] for r in reminders)),
            "reminder_count": len(reminders),
            "reminders": reminders,
        }, indent=2))
    else:
        print(format_reminders(reminders, context_text=context_text, compact=args.compact))


if __name__ == "__main__":
    main()
