#!/usr/bin/env python3
"""
Analyze a specific protocol for investment suitability.

Usage:
    python analyze_protocol.py --protocol aave-v3
    python analyze_protocol.py --protocol uniswap --output json
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional

DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"
DEFILLAMA_PROTOCOL = "https://api.llama.fi/protocol/{slug}"


def fetch_protocol(slug: str) -> Optional[dict]:
    """Fetch protocol data from DefiLlama."""
    url = DEFILLAMA_PROTOCOL.format(slug=slug.lower())
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching protocol: {e}", file=sys.stderr)
        return None


def fetch_all_protocols() -> list:
    """Fetch all protocols list."""
    try:
        with urllib.request.urlopen(DEFILLAMA_PROTOCOLS, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"Error fetching protocols list: {e}", file=sys.stderr)
        return []


def find_protocol_slug(name: str) -> Optional[str]:
    """Find protocol slug by name."""
    protocols = fetch_all_protocols()
    name_lower = name.lower()
    
    for p in protocols:
        if name_lower in p.get("name", "").lower():
            return p.get("slug") or p.get("name", "").lower().replace(" ", "-")
        if name_lower in p.get("slug", "").lower():
            return p.get("slug")
    
    return None


def calculate_risk_score(protocol: dict) -> dict:
    """Calculate detailed risk score."""
    scores = {}
    total = 0
    
    # Maturity (0-3)
    audits = protocol.get("audits", [])
    if len(audits) >= 2:
        scores["maturity"] = {"score": 0, "note": "Multiple audits, well established"}
    elif len(audits) == 1:
        scores["maturity"] = {"score": 1, "note": "Single audit"}
    elif protocol.get("audit_note"):
        scores["maturity"] = {"score": 2, "note": "Audit in progress or partial"}
    else:
        scores["maturity"] = {"score": 3, "note": "No audit"}
    total += scores["maturity"]["score"]
    
    # TVL (0-2)
    tvl = protocol.get("tvl", 0)
    # Handle case where tvl might be a list or other type
    if isinstance(tvl, (list, dict)):
        tvl = 0
    tvl = tvl or 0
    if tvl > 1_000_000_000:
        scores["tvl"] = {"score": 0, "note": f"TVL > $1B (${tvl:,.0f})"}
    elif tvl > 100_000_000:
        scores["tvl"] = {"score": 1, "note": f"TVL $100M-$1B (${tvl:,.0f})"}
    else:
        scores["tvl"] = {"score": 2, "note": f"TVL < $100M (${tvl:,.0f})"}
    total += scores["tvl"]["score"]
    
    # Decentralization (0-2)
    if protocol.get("governanceID"):
        scores["decentralization"] = {"score": 0, "note": "DAO governed"}
    elif protocol.get("gecko_id"):
        scores["decentralization"] = {"score": 1, "note": "Has token, governance unclear"}
    else:
        scores["decentralization"] = {"score": 2, "note": "No governance token"}
    total += scores["decentralization"]["score"]
    
    # Audit status (0-3) - separate from maturity
    if isinstance(audits, list):
        audit_count = len(audits)
    else:
        audit_count = 0
    
    if audit_count >= 2:
        scores["audit"] = {"score": 0, "note": f"{audit_count} audits"}
    elif audit_count == 1:
        scores["audit"] = {"score": 1, "note": "1 audit"}
    elif protocol.get("audit_note"):
        scores["audit"] = {"score": 2, "note": protocol.get("audit_note", "Audit issues")}
    else:
        scores["audit"] = {"score": 3, "note": "No audit"}
    total += scores["audit"]["score"]
    
    return {
        "total": min(total, 10),
        "breakdown": scores,
        "level": "low" if total <= 3 else "medium" if total <= 6 else "high"
    }


def analyze_protocol(name_or_slug: str) -> Optional[dict]:
    """
    Analyze a protocol and return detailed information.
    
    Args:
        name_or_slug: Protocol name or slug
    
    Returns:
        Protocol analysis dict
    """
    # Try as slug first
    protocol = fetch_protocol(name_or_slug)
    
    # If not found, search by name
    if not protocol:
        slug = find_protocol_slug(name_or_slug)
        if slug:
            protocol = fetch_protocol(slug)
    
    if not protocol:
        return None
    
    # Calculate risk
    risk = calculate_risk_score(protocol)
    
    # Get chains
    chains = protocol.get("chains", [])
    if isinstance(chains, dict):
        chains = list(chains.keys())
    
    # Get TVL by chain
    chain_tvl = {}
    if protocol.get("chainTvl"):
        ctvl = protocol.get("chainTvl")
        if isinstance(ctvl, dict):
            chain_tvl = ctvl
    
    # Get total TVL (handle various data types)
    raw_tvl = protocol.get("tvl", 0)
    if isinstance(raw_tvl, (int, float)):
        total_tvl = raw_tvl
    else:
        total_tvl = 0
    
    # Build analysis
    analysis = {
        "name": protocol.get("name", ""),
        "slug": protocol.get("slug", ""),
        "logo": protocol.get("logo", ""),
        "url": protocol.get("url", ""),
        "description": protocol.get("description", ""),
        "category": protocol.get("category", ""),
        "chains": chains,
        "tvl": {
            "total": total_tvl,
            "by_chain": chain_tvl,
            "change_24h": protocol.get("change_1d", 0) or 0,
            "change_7d": protocol.get("change_7d", 0) or 0
        },
        "risk": risk,
        "audits": [
            {
                "name": a.get("name", ""),
                "link": a.get("link", ""),
                "time": a.get("time", "")
            }
            for a in protocol.get("audits", [])
        ],
        "exploits": protocol.get("exploits", []),
        "governance": {
            "has_token": bool(protocol.get("gecko_id")),
            "token_name": "",
            "token_symbol": ""
        },
        "social": {
            "twitter": protocol.get("twitter", ""),
            "discord": protocol.get("discord", ""),
            "telegram": protocol.get("telegram", "")
        },
        "defillama_url": f"https://defillama.com/protocol/{protocol.get('slug', '')}"
    }
    
    return analysis


def format_report(analysis: dict, output_format: str = "markdown") -> str:
    """Format protocol analysis as report."""
    if not analysis:
        return "Protocol not found."
    
    if output_format == "json":
        return json.dumps(analysis, indent=2)
    
    # Markdown format
    lines = [
        f"# Protocol Analysis: {analysis['name']}",
        "",
        f"**Category**: {analysis['category']}",
        f"**Chains**: {', '.join(analysis['chains'])}",
        f"**Website**: {analysis['url']}",
        "",
        "---",
        "",
        "## 📊 TVL Overview",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total TVL | ${analysis['tvl']['total']:,.0f} |",
        f"| 24h Change | {analysis['tvl']['change_24h']:.2f}% |",
        f"| 7d Change | {analysis['tvl']['change_7d']:.2f}% |",
        ""
    ]
    
    if analysis['tvl']['by_chain']:
        lines.extend([
            "### TVL by Chain",
            "",
            "| Chain | TVL |",
            "|-------|-----|"
        ])
        for chain, tvl in sorted(analysis['tvl']['by_chain'].items(), 
                                   key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"| {chain} | ${tvl:,.0f} |")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## ⚠️ Risk Assessment",
        "",
        f"| Factor | Score | Notes |",
        f"|--------|-------|-------|"
    ])
    
    for factor, data in analysis['risk']['breakdown'].items():
        lines.append(f"| {factor.title()} | {data['score']}/3 | {data['note']} |")
    
    lines.extend([
        f"| **Total** | **{analysis['risk']['total']}/10** | **{analysis['risk']['level'].upper()} RISK** |",
        ""
    ])
    
    if analysis['exploits']:
        lines.extend([
            "### 🚨 Known Exploits",
            ""
        ])
        for exploit in analysis['exploits']:
            lines.append(f"- {exploit}")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 🔐 Audits",
        ""
    ])
    
    if analysis['audits']:
        for audit in analysis['audits']:
            lines.append(f"- [{audit['name']}]({audit['link']}) ({audit['time'] or 'N/A'})")
    else:
        lines.append("No audits found.")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🏛️ Governance",
        "",
        f"- **Token**: {analysis['governance']['token_symbol'] or 'No governance token'}",
        f"- **Decentralized**: {'Yes' if analysis['governance']['has_token'] else 'No'}",
        ""
    ])
    
    if analysis['social']['twitter'] or analysis['social']['discord']:
        lines.extend([
            "---",
            "",
            "## 📱 Social",
            ""
        ])
        if analysis['social']['twitter']:
            lines.append(f"- Twitter: {analysis['social']['twitter']}")
        if analysis['social']['discord']:
            lines.append(f"- Discord: {analysis['social']['discord']}")
        if analysis['social']['telegram']:
            lines.append(f"- Telegram: {analysis['social']['telegram']}")
    
    lines.extend([
        "",
        "---",
        "",
        f"📊 [View on DefiLlama]({analysis['defillama_url']})"
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze a DeFi protocol")
    parser.add_argument("--protocol", required=True, help="Protocol name or slug")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    
    args = parser.parse_args()
    
    analysis = analyze_protocol(args.protocol)
    
    if not analysis:
        print(f"Protocol '{args.protocol}' not found.", file=sys.stderr)
        sys.exit(1)
    
    print(format_report(analysis, args.output))


if __name__ == "__main__":
    main()