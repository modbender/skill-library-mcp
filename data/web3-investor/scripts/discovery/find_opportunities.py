#!/usr/bin/env python3
"""
Find investment opportunities from DefiLlama API.

Version: 0.2.0 - Refactored for LLM-based risk analysis

Key Changes:
- Removed local risk scoring (calculate_risk_score)
- Added actionable_addresses for execution readiness
- Integrated protocol registry from references/protocols.md
- Enhanced null/type safety for external API data

Usage:
    python find_opportunities.py --min-apy 5 --chain ethereum
    python find_opportunities.py --protocol aave-v3 --output json
    python find_opportunities.py --llm-ready  # Output optimized for LLM analysis
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error

# ============================================================================
# Configuration
# ============================================================================

DEFILLAMA_BASE = "https://yields.llama.fi"
DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"
MAX_SAFE_APY_DEFAULT = 100  # Filter out extreme risks/scams by default

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROTOCOLS_MD_PATH = os.path.join(SCRIPT_DIR, "..", "..", "references", "protocols.md")
PROTOCOLS_JSON_PATH = os.path.join(SCRIPT_DIR, "..", "..", "config", "protocols.json")

# Chain mapping (DefiLlama naming)
CHAIN_MAPPING = {
    "ethereum": "Ethereum",
    "eth": "Ethereum",
    "base": "Base",
    "basechain": "Base",
    "arbitrum": "Arbitrum",
    "arb": "Arbitrum",
    "optimism": "Optimism",
    "op": "Optimism",
}


# ============================================================================
# Protocol Registry (Static Knowledge Layer)
# ============================================================================

def parse_protocols_md() -> Dict[str, Dict[str, Any]]:
    """
    Parse protocols.md into a static registry.
    
    Returns dict keyed by protocol name (lowercase).
    """
    registry = {}
    
    if not os.path.exists(PROTOCOLS_MD_PATH):
        return registry
    
    try:
        with open(PROTOCOLS_MD_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse protocol sections (### Protocol Name)
        pattern = r"### ([A-Za-z0-9\s\-\.]+)\n((?:(?!\n### ).)*?)(?=\n### |$)"
        matches = re.findall(pattern, content, re.DOTALL)
        
        for name, section in matches:
            name_lower = name.lower().strip()
            info = {"name": name.strip()}
            
            # Extract contract address
            contract_match = re.search(r"\*\*Contract\*\*:\s*(`?0x[a-fA-F0-9]{40}`?)", section)
            if contract_match:
                addr = contract_match.group(1).strip("`")
                info["primary_contract"] = addr
            
            # Extract category
            category_match = re.search(r"\*\*Category\*\*:\s*(\w+)", section)
            if category_match:
                info["category"] = category_match.group(1).lower()
            
            # Extract risk level (for reference, not computed)
            risk_match = re.search(r"\*\*Risk Level\*\*:\s*(\w+)", section)
            if risk_match:
                info["registry_risk"] = risk_match.group(1).lower()
            
            # Extract docs URL
            docs_match = re.search(r"\*\*Docs\*\*:\s*(https?://[^\s]+)", section)
            if docs_match:
                info["docs_url"] = docs_match.group(1)
            
            # Extract TVL (for reference)
            tvl_match = re.search(r"\*\*TVL\*\*:\s*>\s*\$?([\d.]+[BMK]?)", section)
            if tvl_match:
                info["registry_tvl"] = tvl_match.group(1)
            
            registry[name_lower] = info
            
            # Also add alternative keys
            if "aave" in name_lower:
                registry["aave-v3"] = info
                registry["aave v3"] = info
            if "compound" in name_lower:
                registry["compound-v3"] = info
                registry["compound v3"] = info
        
    except Exception as e:
        print(f"⚠️ Failed to parse protocols.md: {e}", file=sys.stderr)
    
    return registry


def load_protocols_json() -> Dict[str, Dict[str, Any]]:
    """Load protocols from JSON config if exists."""
    if not os.path.exists(PROTOCOLS_JSON_PATH):
        return {}
    
    try:
        with open(PROTOCOLS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_protocol_registry() -> Dict[str, Dict[str, Any]]:
    """
    Merge static registry from MD and JSON.
    JSON takes precedence for overrides.
    """
    registry = parse_protocols_md()
    json_registry = load_protocols_json()
    registry.update(json_registry)
    return registry


# ============================================================================
# DefiLlama API (Dynamic Data Layer)
# ============================================================================

def fetch_yields() -> Dict[str, Any]:
    """Fetch all yield data from DefiLlama."""
    url = f"{DEFILLAMA_BASE}/pools"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Web3-Investor/0.2.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"❌ Error fetching yields: {e}", file=sys.stderr)
        return {"data": []}
    except Exception as e:
        print(f"❌ Unexpected error fetching yields: {e}", file=sys.stderr)
        return {"data": []}


def fetch_protocols() -> List[Dict[str, Any]]:
    """Fetch protocol list from DefiLlama."""
    try:
        req = urllib.request.Request(
            DEFILLAMA_PROTOCOLS, 
            headers={"User-Agent": "Web3-Investor/0.2.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print(f"❌ Error fetching protocols: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"❌ Unexpected error fetching protocols: {e}", file=sys.stderr)
        return []


# ============================================================================
# Data Extraction & Normalization
# ============================================================================

def safe_get(data: Any, key: str, default: Any = None) -> Any:
    """
    Safely get value from dict with null/type protection.
    
    Handles:
    - None data
    - Missing keys
    - Null values
    """
    if data is None:
        return default
    if not isinstance(data, dict):
        return default
    value = data.get(key, default)
    return value if value is not None else default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float with null protection."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_list(value: Any) -> List[Any]:
    """Safely convert to list with null protection."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert to string with null protection."""
    if value is None:
        return default
    return str(value)


def normalize_chain(chain: str) -> str:
    """Normalize chain name to DefiLlama format."""
    return CHAIN_MAPPING.get(chain.lower(), chain)


# ============================================================================
# Actionable Addresses Extraction
# ============================================================================

def extract_actionable_addresses(
    pool: Dict[str, Any],
    protocol: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract actionable addresses for execution readiness.
    
    Priority:
    1. Pool-level addresses (from DefiLlama)
    2. Protocol-level addresses (from DefiLlama)
    3. Registry addresses (from protocols.md/json)
    """
    result = {
        "deposit_contract_candidates": [],
        "underlying_token_addresses": [],
        "reward_token_addresses": [],
        "has_actionable_address": False,
        "primary_contract": None,
        "protocol_registry_match": False,
        "docs_url": None
    }
    
    # 1. Pool-level addresses
    pool_addr = safe_get(pool, "pool")
    if pool_addr and pool_addr.startswith("0x"):
        result["deposit_contract_candidates"].append(pool_addr)
    
    # Underlying tokens
    underlying = safe_list(safe_get(pool, "underlyingTokens"))
    result["underlying_token_addresses"] = [
        addr for addr in underlying 
        if isinstance(addr, str) and addr.startswith("0x")
    ]
    
    # Reward tokens
    rewards = safe_list(safe_get(pool, "rewardTokens"))
    result["reward_token_addresses"] = [
        addr for addr in rewards 
        if isinstance(addr, str) and addr.startswith("0x")
    ]
    
    # 2. Protocol-level addresses (governance, tokens)
    protocol_tokens = safe_list(safe_get(protocol, "tokens"))
    for token in protocol_tokens:
        if isinstance(token, dict):
            addr = safe_get(token, "address")
            if addr and addr.startswith("0x"):
                result["underlying_token_addresses"].append(addr)
    
    # 3. Registry lookup
    protocol_name = safe_get(pool, "project", "").lower()
    registry_entry = registry.get(protocol_name, {})
    
    if registry_entry:
        result["protocol_registry_match"] = True
        
        primary = registry_entry.get("primary_contract")
        if primary and primary not in result["deposit_contract_candidates"]:
            result["deposit_contract_candidates"].insert(0, primary)
            result["primary_contract"] = primary
        
        docs = registry_entry.get("docs_url")
        if docs:
            result["docs_url"] = docs
    
    # Determine if actionable
    result["has_actionable_address"] = bool(
        result["deposit_contract_candidates"] or 
        result["underlying_token_addresses"]
    )
    
    return result


# ============================================================================
# Risk Data Collection (for LLM Analysis)
# ============================================================================

def detect_reward_type(pool: Dict[str, Any]) -> str:
    """Detect if product has single or multi-token rewards."""
    reward_tokens = safe_list(safe_get(pool, "rewardTokens"))
    if not reward_tokens:
        return "none"
    elif len(reward_tokens) == 1:
        return "single"
    else:
        return "multi"


def detect_il_risk(pool: Dict[str, Any], category: str) -> bool:
    """Detect if product has impermanent loss risk."""
    underlying = safe_list(safe_get(pool, "underlyingTokens"))
    
    # DEX LP products typically have IL risk
    dex_categories = ["dex", "dexs", "amm", "lp"]
    if any(dex in category.lower() for dex in dex_categories):
        return True
    
    # Multi-asset pools with volatile tokens have IL risk
    if len(underlying) >= 2 and not safe_get(pool, "stablecoin", False):
        return True
    
    return False


def detect_underlying_type(pool: Dict[str, Any], category: str, symbol: str) -> str:
    """Detect underlying asset type (RWA vs on-chain)."""
    # RWA keywords
    rwa_keywords = ["tbill", "treasury", "bond", "real-world", "rwa", "usdyc", "usdy"]
    symbol_lower = symbol.lower()
    
    for keyword in rwa_keywords:
        if keyword in symbol_lower:
            return "rwa"
    
    # Check category
    if "rwa" in category.lower():
        return "rwa"
    
    # Pure lending/yield protocols are on-chain
    onchain_categories = ["lending", "yield", "staking", "liquid staking"]
    if any(oc in category.lower() for oc in onchain_categories):
        return "onchain"
    
    # Mixed or unknown
    underlying = safe_list(safe_get(pool, "underlyingTokens"))
    if len(underlying) > 1:
        return "mixed"
    
    return "unknown"


def collect_risk_signals(
    pool: Dict[str, Any],
    protocol: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Collect risk-related signals WITHOUT computing a score.
    
    LLM will analyze these signals to determine risk.
    """
    protocol_name = safe_get(pool, "project", "").lower()
    registry_entry = registry.get(protocol_name, {})
    category = registry_entry.get("category") or safe_get(protocol, "category", "")
    symbol = safe_str(safe_get(pool, "symbol"))
    
    return {
        # Protocol maturity signals
        "audits": safe_list(safe_get(protocol, "audits")),
        "audit_count": len(safe_list(safe_get(protocol, "audits"))),
        "has_audit": bool(safe_get(protocol, "audits")),
        "audit_notes": safe_str(safe_get(protocol, "audit_note")),
        
        # TVL signals
        "tvl_usd": safe_float(safe_get(pool, "tvlUsd")),
        "protocol_tvl": safe_float(safe_get(protocol, "tvl")),
        
        # Age/maturity signals
        "protocol_slug": safe_get(protocol, "slug"),
        "known_protocol": bool(registry_entry),
        "category": category,
        
        # APY signals (high APY may indicate risk)
        "apy": safe_float(safe_get(pool, "apy")),
        "apy_base": safe_float(safe_get(pool, "apyBase")),
        "apy_reward": safe_float(safe_get(pool, "apyReward")),
        "apy_composition": "base+rewards" if safe_get(pool, "apyReward") else "base_only",
        
        # Asset type signals
        "stablecoin": safe_get(pool, "stablecoin", False),
        "symbol": symbol,
        
        # Chain signals
        "chain": safe_str(safe_get(pool, "chain")),
        
        # NEW in v0.2.1: Investment preference signals
        "reward_type": detect_reward_type(pool),  # "none" | "single" | "multi"
        "has_il_risk": detect_il_risk(pool, category),  # True | False
        "underlying_type": detect_underlying_type(pool, category, symbol),  # "rwa" | "onchain" | "mixed" | "unknown"
        
        # Governance signals
        "governance": safe_get(protocol, "governance"),
        "has_gov_token": bool(safe_get(protocol, "governance")),
        
        # Registry reference (if available)
        "registry_risk": registry_entry.get("registry_risk"),
        "registry_category": registry_entry.get("category"),
    }


# ============================================================================
# Main Opportunity Finder
# ============================================================================

def find_opportunities(
    min_apy: float = 0,
    max_apy: float = MAX_SAFE_APY_DEFAULT,
    chain: str = "Ethereum",
    min_tvl: float = 0,
    limit: int = 20,
    allow_high_apy: bool = False,
    include_risk_signals: bool = True
) -> List[Dict[str, Any]]:
    """
    Find investment opportunities matching criteria.
    
    Returns structured data for LLM-based risk analysis.
    
    Args:
        min_apy: Minimum APY percentage
        max_apy: Maximum APY percentage (default 100% to filter scams)
        chain: Blockchain to search
        min_tvl: Minimum TVL in USD
        limit: Maximum results to return
        allow_high_apy: If True, allow APY > 100%
        include_risk_signals: Include risk_signals for LLM analysis
    
    Returns:
        List of opportunity dicts with actionable_addresses and risk_signals
    """
    # Fetch data
    yields_data = fetch_yields()
    protocols_data = fetch_protocols()
    
    if not yields_data.get("data"):
        print("⚠️ No yield data received", file=sys.stderr)
        return []
    
    # Build protocol lookup
    protocol_map = {}
    for p in protocols_data:
        slug = safe_get(p, "slug", safe_get(p, "name", "")).lower()
        protocol_map[slug] = p
        protocol_map[safe_get(p, "name", "").lower()] = p
    
    # Load static registry
    registry = get_protocol_registry()
    
    opportunities = []
    normalized_chain = normalize_chain(chain)
    
    for pool in yields_data.get("data", []):
        # Filter by chain
        pool_chain = safe_str(safe_get(pool, "chain", "")).lower()
        if normalized_chain.lower() not in pool_chain and chain.lower() not in pool_chain:
            continue
        
        # Filter by APY
        apy = safe_float(safe_get(pool, "apy"))
        if apy < min_apy:
            continue
        if not allow_high_apy and apy > max_apy:
            continue
        
        # Filter by TVL
        tvl = safe_float(safe_get(pool, "tvlUsd"))
        if tvl < min_tvl:
            continue
        
        # Get protocol info
        protocol_name = safe_str(safe_get(pool, "project"))
        protocol = protocol_map.get(protocol_name.lower(), {})
        
        # Extract actionable addresses
        actionable = extract_actionable_addresses(pool, protocol, registry)
        
        # Build opportunity record
        opp = {
            # Core identifiers
            "pool": safe_str(safe_get(pool, "pool")),
            "protocol": protocol_name,
            "protocol_name": safe_get(protocol, "name", protocol_name),
            "chain": safe_get(pool, "chain", "Ethereum"),
            "symbol": safe_str(safe_get(pool, "symbol")),
            
            # Yield metrics
            "apy": round(apy, 2),
            "apy_base": round(safe_float(safe_get(pool, "apyBase")), 2),
            "apy_reward": round(safe_float(safe_get(pool, "apyReward")), 2),
            "tvl_usd": tvl,
            
            # Asset info
            "underlying_tokens": safe_list(safe_get(pool, "underlyingTokens")),
            "reward_tokens": safe_list(safe_get(pool, "rewardTokens")),
            "stablecoin": safe_get(pool, "stablecoin", False),
            
            # Execution readiness (NEW in v0.2.0)
            "actionable_addresses": actionable,
            
            # Links
            "url": f"https://defillama.com/yield/pool/{safe_get(pool, 'pool', '')}",
            
            # Legacy fields (for backward compatibility)
            "audited": bool(safe_get(protocol, "audits")),
        }
        
        # Add risk signals for LLM analysis
        if include_risk_signals:
            opp["risk_signals"] = collect_risk_signals(pool, protocol, registry)
        
        opportunities.append(opp)
    
    # Sort by APY (descending)
    opportunities.sort(key=lambda x: x["apy"], reverse=True)
    
    return opportunities[:limit]


# ============================================================================
# Output Formatting
# ============================================================================

def format_report(opportunities: List[Dict], output_format: str = "markdown") -> str:
    """Format opportunities as report."""
    if not opportunities:
        return "No opportunities found matching criteria."
    
    if output_format == "json":
        return json.dumps(opportunities, indent=2, ensure_ascii=False)
    
    # Markdown format
    lines = [
        "# 💰 Investment Opportunities",
        f"\n**Generated**: {datetime.now().isoformat()}",
        f"**Found**: {len(opportunities)} pools\n",
        "---\n"
    ]
    
    for i, opp in enumerate(opportunities, 1):
        lines.extend([
            f"## {i}. {opp['protocol']} - {opp['symbol']}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| APY | **{opp['apy']}%** |",
            f"| TVL | ${opp['tvl_usd']:,.0f} |",
            f"| Chain | {opp['chain']} |",
            f"| Stablecoin | {'✅' if opp['stablecoin'] else '❌'} |",
        ])
        
        # Show actionable status
        actionable = opp.get("actionable_addresses", {})
        if actionable.get("has_actionable_address"):
            lines.append(f"| Actionable | ✅ Ready for execution |")
            if actionable.get("primary_contract"):
                lines.append(f"| Primary Contract | `{actionable['primary_contract']}` |")
        else:
            lines.append(f"| Actionable | ⚠️ Needs address lookup |")
        
        lines.extend([
            "",
            f"**Pool**: `{opp['pool']}`",
            f"**Link**: {opp['url']}",
            ""
        ])
        
        # Show risk signals summary
        risk = opp.get("risk_signals", {})
        if risk:
            lines.extend([
                f"**Risk Signals**:",
                f"- Audited: {'✅' if risk.get('has_audit') else '❌'}",
                f"- Known Protocol: {'✅' if risk.get('known_protocol') else '❌'}",
                f"- APY Composition: {risk.get('apy_composition', 'unknown')}",
                ""
            ])
    
    return "\n".join(lines)


def format_llm_prompt(opportunities: List[Dict]) -> str:
    """
    Format opportunities as LLM-ready prompt for risk analysis.
    
    Output is optimized for LLM consumption.
    """
    if not opportunities:
        return "No opportunities to analyze."
    
    lines = [
        "# DeFi Investment Opportunities - Risk Analysis Request",
        "",
        "Please analyze the following investment opportunities and provide:",
        "1. Risk assessment (Low/Medium/High) with reasoning",
        "2. Key risk factors to watch",
        "3. Recommended actions",
        "",
        "---\n"
    ]
    
    for i, opp in enumerate(opportunities, 1):
        lines.append(f"## Opportunity {i}")
        lines.append("```json")
        lines.append(json.dumps(opp, indent=2, ensure_ascii=False))
        lines.append("```\n")
    
    return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Find DeFi investment opportunities (v0.2.0 - LLM-ready)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python find_opportunities.py --min-apy 5 --chain ethereum
  python find_opportunities.py --llm-ready --output json
  python find_opportunities.py --allow-high-apy --limit 50
        """
    )
    
    parser.add_argument("--min-apy", type=float, default=0, 
                        help="Minimum APY %%")
    parser.add_argument("--max-apy", type=float, default=MAX_SAFE_APY_DEFAULT, 
                        help=f"Maximum APY %% (default {MAX_SAFE_APY_DEFAULT}%)")
    parser.add_argument("--allow-high-apy", action="store_true",
                        help="Allow APY > 100%% (high risk)")
    parser.add_argument("--chain", default="Ethereum", 
                        help="Blockchain to search")
    parser.add_argument("--min-tvl", type=float, default=0, 
                        help="Minimum TVL in USD")
    parser.add_argument("--limit", type=int, default=20, 
                        help="Maximum results")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    parser.add_argument("--llm-ready", action="store_true",
                        help="Output LLM-ready prompt for risk analysis")
    parser.add_argument("--no-risk-signals", action="store_true",
                        help="Exclude risk signals from output")
    
    args = parser.parse_args()
    
    # Safety warning
    if args.allow_high_apy:
        print("⚠️ 警告: --allow-high-apy 已启用，可能包含高风险项目", file=sys.stderr)
    
    opportunities = find_opportunities(
        min_apy=args.min_apy,
        max_apy=args.max_apy,
        chain=args.chain,
        min_tvl=args.min_tvl,
        limit=args.limit,
        allow_high_apy=args.allow_high_apy,
        include_risk_signals=not args.no_risk_signals
    )
    
    # Output
    if args.llm_ready:
        print(format_llm_prompt(opportunities))
    elif args.output == "json":
        print(json.dumps(opportunities, indent=2, ensure_ascii=False))
    else:
        print(format_report(opportunities, "markdown"))


if __name__ == "__main__":
    main()