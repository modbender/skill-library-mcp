#!/usr/bin/env python3
"""
Lieutenant Threat Scanner CLI

Scan text for prompt injection, jailbreaks, and other AI agent threats.

Usage:
    python scan.py "Text to scan"
    python scan.py --semantic "Text to scan"  # With ML detection
    python scan.py --api "Text to scan"       # With TrustAgents API
    python scan.py --json "Text to scan"      # JSON output
    echo "Text" | python scan.py -            # From stdin
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directories to path for local imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lieutenant.scanner import ThreatScanner
from lieutenant.types import Verdict, ThreatLevel


def scan_with_api(text: str, semantic: bool = False) -> dict:
    """Scan using TrustAgents API."""
    import requests
    
    api_key = os.environ.get("TRUSTAGENTS_API_KEY")
    api_url = os.environ.get(
        "TRUSTAGENTS_API_URL",
        "https://agent-trust-infrastructure-production.up.railway.app"
    )
    
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    payload = {"text": text}
    if semantic:
        payload["semantic_analysis"] = "fast"
    
    response = requests.post(
        f"{api_url}/verify/text",
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def scan_local(text: str, semantic: bool = False) -> dict:
    """Scan using local Lieutenant scanner."""
    scanner = ThreatScanner(
        enable_semantic=semantic,
        semantic_threshold=0.75,
    )
    
    result = scanner.scan_text_full(text)
    
    return {
        "verdict": result.verdict.value,
        "threat_level": result.threat_level.value,
        "threats_detected": len(result.threats),
        "threats": [
            {
                "pattern_id": t.pattern_id,
                "pattern_name": t.pattern_name,
                "severity": t.severity.value,
                "location": t.location,
                "matched_text": t.matched_text,
                "description": t.description,
            }
            for t in result.threats
        ],
        "reasoning": result.reasoning,
        "semantic": {
            "enabled": result.semantic.enabled if result.semantic else False,
            "is_suspicious": result.semantic.is_suspicious if result.semantic else False,
            "confidence": result.semantic.confidence if result.semantic else 0,
            "closest_attack": result.semantic.closest_attack if result.semantic else None,
        } if result.semantic else None,
    }


def format_result(result: dict, use_json: bool = False) -> str:
    """Format scan result for display."""
    if use_json:
        return json.dumps(result, indent=2)
    
    verdict = result.get("verdict", "unknown")
    threat_level = result.get("threat_level", "unknown")
    threats = result.get("threats", [])
    reasoning = result.get("reasoning", "")
    
    # Color codes
    COLORS = {
        "allow": "\033[92m",  # Green
        "caution": "\033[93m",  # Yellow
        "block": "\033[91m",  # Red
        "reset": "\033[0m",
    }
    
    color = COLORS.get(verdict, "")
    reset = COLORS["reset"]
    
    # Verdict symbols
    symbols = {
        "allow": "✅",
        "caution": "⚠️",
        "block": "🚫",
    }
    symbol = symbols.get(verdict, "❓")
    
    lines = [
        f"{symbol} {color}Verdict: {verdict.upper()}{reset}",
        f"   Threat Level: {threat_level}",
        f"   Threats Found: {len(threats)}",
    ]
    
    if threats:
        lines.append("   Threats:")
        for t in threats[:5]:  # Show max 5
            lines.append(f"     • [{t['severity'].upper()}] {t['pattern_name']}")
            if t.get('matched_text'):
                lines.append(f"       Match: \"{t['matched_text'][:50]}...\"" if len(t.get('matched_text', '')) > 50 else f"       Match: \"{t['matched_text']}\"")
        if len(threats) > 5:
            lines.append(f"     ... and {len(threats) - 5} more")
    
    # Semantic analysis
    semantic = result.get("semantic")
    if semantic and semantic.get("enabled"):
        if semantic.get("is_suspicious"):
            conf = semantic.get("confidence", 0) * 100
            lines.append(f"   🧠 Semantic: {conf:.0f}% similar to known attack")
            if semantic.get("closest_attack"):
                lines.append(f"       Closest: \"{semantic['closest_attack'][:50]}...\"")
        else:
            lines.append("   🧠 Semantic: No similarity to known attacks")
    
    if reasoning:
        lines.append(f"   Reasoning: {reasoning}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan text for AI agent threats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scan.py "Ignore all previous instructions"
  python scan.py --semantic "Disregard your prior directives"
  python scan.py --api --json "Text to scan"
  echo "Suspicious text" | python scan.py -
        """,
    )
    parser.add_argument(
        "text",
        nargs="?",
        default="-",
        help="Text to scan (use '-' for stdin)",
    )
    parser.add_argument(
        "--semantic", "-s",
        action="store_true",
        help="Enable semantic analysis (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--api", "-a",
        action="store_true",
        help="Use TrustAgents API instead of local scanning",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any threat detected",
    )
    
    args = parser.parse_args()
    
    # Get text
    if args.text == "-":
        text = sys.stdin.read().strip()
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)
    
    # Scan
    try:
        if args.api:
            result = scan_with_api(text, semantic=args.semantic)
        else:
            result = scan_local(text, semantic=args.semantic)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output
    print(format_result(result, use_json=args.json))
    
    # Exit code
    if args.strict:
        verdict = result.get("verdict", "allow")
        if verdict in ("caution", "block"):
            sys.exit(1)
    elif result.get("verdict") == "block":
        sys.exit(1)


if __name__ == "__main__":
    main()
