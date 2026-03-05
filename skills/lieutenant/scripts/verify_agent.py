#!/usr/bin/env python3
"""
Lieutenant Agent Card Verifier CLI

Verify A2A agent cards for malicious patterns and check reputation.

Usage:
    python verify_agent.py --url "https://agent.example.com/.well-known/agent.json"
    python verify_agent.py --file agent_card.json
    python verify_agent.py --api --url "https://agent.example.com"  # With TrustAgents API
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

import requests
from lieutenant.scanner import ThreatScanner
from lieutenant.types import Verdict, ThreatLevel


def fetch_agent_card(url: str) -> dict:
    """Fetch agent card from URL."""
    # Handle well-known URL
    if not url.endswith(".json") and "/.well-known/" not in url:
        if not url.endswith("/"):
            url += "/"
        url += ".well-known/agent.json"
    
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def verify_with_api(agent_card: dict, agent_url: str = None) -> dict:
    """Verify agent using TrustAgents API."""
    api_key = os.environ.get("TRUSTAGENTS_API_KEY")
    api_url = os.environ.get(
        "TRUSTAGENTS_API_URL",
        "https://agent-trust-infrastructure-production.up.railway.app"
    )
    
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    
    response = requests.post(
        f"{api_url}/verify/agent",
        json={"agent_card": agent_card},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def verify_local(agent_card: dict, semantic: bool = False) -> dict:
    """Verify agent using local Lieutenant scanner."""
    scanner = ThreatScanner(
        enable_semantic=semantic,
        semantic_threshold=0.75,
    )
    
    result = scanner.scan_agent_card(agent_card)
    
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
        "agent_name": agent_card.get("name", "Unknown"),
        "agent_url": agent_card.get("url", ""),
        "agent_description": agent_card.get("description", "")[:200],
        "skills_count": len(agent_card.get("skills", [])),
    }


def format_result(result: dict, use_json: bool = False) -> str:
    """Format verification result for display."""
    if use_json:
        return json.dumps(result, indent=2)
    
    verdict = result.get("verdict", "unknown")
    threat_level = result.get("threat_level", "unknown")
    threats = result.get("threats", [])
    
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
        f"{'='*60}",
        f"Agent: {result.get('agent_name', 'Unknown')}",
        f"URL: {result.get('agent_url', 'N/A')}",
        f"Skills: {result.get('skills_count', 0)}",
        f"{'='*60}",
        f"",
        f"{symbol} {color}Verdict: {verdict.upper()}{reset}",
        f"   Threat Level: {threat_level}",
        f"   Threats Found: {len(threats)}",
    ]
    
    if threats:
        lines.append("   ")
        lines.append("   Detected Threats:")
        for t in threats[:10]:  # Show max 10
            lines.append(f"     [{t['severity'].upper()}] {t['pattern_name']}")
            lines.append(f"       Location: {t['location']}")
            if t.get('matched_text'):
                text = t['matched_text'][:60]
                if len(t.get('matched_text', '')) > 60:
                    text += "..."
                lines.append(f"       Match: \"{text}\"")
            lines.append("")
        if len(threats) > 10:
            lines.append(f"     ... and {len(threats) - 10} more threats")
    
    # Trust score if available
    if "trust_score" in result:
        lines.append(f"   Trust Score: {result['trust_score']}/100")
    
    # Reputation info if available
    if result.get("is_verified"):
        lines.append("   ✓ Verified Agent")
    if result.get("reputation_score") is not None:
        lines.append(f"   Reputation: {result['reputation_score']}/100")
    
    reasoning = result.get("reasoning", "")
    if reasoning:
        lines.append(f"   ")
        lines.append(f"   Reasoning: {reasoning}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Verify A2A agent cards for threats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_agent.py --url "https://agent.example.com"
  python verify_agent.py --file agent_card.json
  python verify_agent.py --api --url "https://agent.example.com"
        """,
    )
    parser.add_argument(
        "--url", "-u",
        help="Agent URL or agent card URL",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to agent card JSON file",
    )
    parser.add_argument(
        "--api", "-a",
        action="store_true",
        help="Use TrustAgents API for enhanced verification",
    )
    parser.add_argument(
        "--semantic", "-s",
        action="store_true",
        help="Enable semantic analysis (local mode only)",
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
    
    # Get agent card
    if not args.url and not args.file:
        parser.error("Either --url or --file is required")
    
    try:
        if args.file:
            with open(args.file, "r") as f:
                agent_card = json.load(f)
            agent_url = agent_card.get("url", args.file)
        else:
            agent_card = fetch_agent_card(args.url)
            agent_url = args.url
    except requests.RequestException as e:
        print(f"Error fetching agent card: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing agent card JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    # Verify
    try:
        if args.api:
            result = verify_with_api(agent_card, agent_url)
        else:
            result = verify_local(agent_card, semantic=args.semantic)
    except Exception as e:
        print(f"Error during verification: {e}", file=sys.stderr)
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
