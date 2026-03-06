#!/usr/bin/env python3
"""
Unified Search Interface for Web3 Investor Skill (v0.2.0)

Combines data from multiple sources:
1. DefiLlama API - Real-time yield data (with actionable addresses)
2. Dune Analytics - Deep on-chain analytics via MCP

Key Features:
- LLM-ready output format
- Actionable addresses for execution
- Risk signals collection (no local scoring)
- Protocol registry integration

Usage:
    python unified_search.py --min-apy 5 --chain ethereum
    python unified_search.py --source dune --query "aave lending"
    python unified_search.py --llm-ready --output json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

# Import existing modules
try:
    from find_opportunities import (
        find_opportunities, 
        format_report as format_defillama,
        format_llm_prompt,
        get_protocol_registry
    )
except ImportError:
    # Fallback if run from different directory
    import importlib.util
    spec = importlib.util.spec_from_file_location("find_opportunities", 
        __file__.replace("unified_search.py", "find_opportunities.py"))
    find_opps_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(find_opps_module)
    find_opportunities = find_opps_module.find_opportunities
    format_defillama = find_opps_module.format_report
    format_llm_prompt = getattr(find_opps_module, "format_llm_prompt", None)
    get_protocol_registry = getattr(find_opps_module, "get_protocol_registry", lambda: {})

# Import Dune MCP with fallback
try:
    from dune_mcp import (
        search_tables, 
        execute_query, 
        get_execution_results,
        create_query
    )
except ImportError:
    # Fallback for relative import
    try:
        from .dune_mcp import (
            search_tables, 
            execute_query, 
            get_execution_results,
            create_query
        )
    except ImportError:
        # Last resort: manual import
        import importlib.util
        dune_spec = importlib.util.spec_from_file_location("dune_mcp",
            __file__.replace("unified_search.py", "dune_mcp.py"))
        dune_module = importlib.util.module_from_spec(dune_spec)
        dune_spec.loader.exec_module(dune_module)
        search_tables = dune_module.search_tables
        execute_query = dune_module.execute_query
        get_execution_results = dune_module.get_execution_results
        create_query = dune_module.create_query


def search_defillama(
    min_apy: float = 0,
    max_risk: str = "medium",
    chain: str = "Ethereum",
    min_tvl: float = 0,
    limit: int = 20
) -> List[Dict]:
    """
    Search DefiLlama for yield opportunities.
    
    Returns standardized opportunity format.
    """
    opportunities = find_opportunities(
        min_apy=min_apy,
        max_risk=max_risk,
        chain=chain,
        min_tvl=min_tvl,
        limit=limit
    )
    
    # Add source identifier
    for opp in opportunities:
        opp["source"] = "defillama"
    
    return opportunities


def search_dune_tables(
    query: str,
    chain: str = "ethereum",
    categories: List[str] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Search Dune for relevant data tables.
    
    Returns table metadata for potential query execution.
    """
    if categories is None:
        categories = ["spell"]
    
    result = search_tables(
        query=query,
        categories=categories,
        blockchains=[chain],
        limit=limit,
        include_schema=True
    )
    
    tables = []
    
    # Handle MCP response format
    if "structuredContent" in result:
        results = result["structuredContent"].get("results", [])
    elif "content" in result:
        # Parse text content
        content = result["content"]
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get("text", "{}")
            try:
                parsed = json.loads(text)
                results = parsed.get("results", [])
            except json.JSONDecodeError:
                results = []
        else:
            results = []
    elif "results" in result:
        results = result["results"]
    else:
        results = []
    
    for table in results:
        tables.append({
            "source": "dune",
            "full_name": table.get("full_name", ""),
            "category": table.get("category", ""),
            "blockchains": table.get("blockchains", []),
            "description": table.get("description", ""),
            "partition_columns": table.get("partition_columns", []),
            "schema": table.get("schema", {}),
            "visibility": table.get("visibility", "public")
        })
    
    return tables


def find_aave_rates_via_dune(chain: str = "ethereum") -> Dict:
    """
    Get Aave lending rates using Dune's curated tables.
    
    This demonstrates executing a query on Dune data.
    """
    # First, find the relevant table
    tables = search_dune_tables("aave interest", chain=chain)
    
    # Check if aave_ethereum.interest exists
    aave_table = None
    for t in tables:
        if "aave" in t["full_name"].lower() and "interest" in t["full_name"].lower():
            aave_table = t
            break
    
    if not aave_table:
        return {"error": "Aave interest table not found"}
    
    # Create a query to get current rates
    # Note: This requires knowing the table schema
    sql = f"""
    SELECT 
        asset_symbol,
        asset_address,
        supply_rate,
        variable_borrow_rate,
        stable_borrow_rate,
        block_date
    FROM {aave_table['full_name']}
    WHERE block_date = (SELECT MAX(block_date) FROM {aave_table['full_name']})
    ORDER BY supply_rate DESC
    LIMIT 20
    """
    
    result = create_query(
        name=f"Aave {chain} Rates - {datetime.now().strftime('%Y-%m-%d')}",
        sql=sql,
        description="Current Aave lending rates",
        is_temp=True
    )
    
    return {
        "table": aave_table["full_name"],
        "query_result": result
    }


def unified_search(
    min_apy: float = 0,
    chain: str = "Ethereum",
    min_tvl: float = 0,
    sources: List[str] = None,
    limit: int = 20,
    include_risk_signals: bool = True
) -> Dict[str, Any]:
    """
    Search across all configured data sources.
    
    v0.2.0: Removed max_risk filter (LLM will analyze risk)
    
    Args:
        min_apy: Minimum APY percentage
        chain: Blockchain to search
        min_tvl: Minimum TVL in USD
        sources: Data sources to use (defillama, dune)
        limit: Maximum results per source
        include_risk_signals: Include risk signals for LLM analysis
    
    Returns:
        Dict with opportunities from each source
    """
    if sources is None:
        sources = ["defillama", "dune"]
    
    results = {
        "generated_at": datetime.now().isoformat(),
        "version": "0.2.0",
        "parameters": {
            "min_apy": min_apy,
            "chain": chain,
            "min_tvl": min_tvl,
            "sources": sources
        },
        "sources": {}
    }
    
    # DefiLlama - Real-time yields with actionable addresses
    if "defillama" in sources:
        try:
            opps = find_opportunities(
                min_apy=min_apy,
                chain=chain,
                min_tvl=min_tvl,
                limit=limit,
                include_risk_signals=include_risk_signals
            )
            results["sources"]["defillama"] = {
                "status": "success",
                "count": len(opps),
                "opportunities": opps
            }
        except Exception as e:
            results["sources"]["defillama"] = {
                "status": "error",
                "error": str(e)
            }
    
    # Dune - Data tables for custom analysis
    if "dune" in sources:
        try:
            tables = search_dune_tables(
                query=f"yield lending {chain}",
                chain=chain.lower(),
                limit=limit
            )
            results["sources"]["dune"] = {
                "status": "success",
                "count": len(tables),
                "tables": tables
            }
        except Exception as e:
            results["sources"]["dune"] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


def format_unified_report(results: Dict) -> str:
    """Format unified search results as markdown report (v0.2.0)."""
    lines = [
        "# 💰 Unified Investment Search Results",
        f"\n**Generated**: {results['generated_at']}",
        f"**Version**: {results.get('version', 'unknown')}",
        f"**Parameters**: min_apy={results['parameters']['min_apy']}%, "
        f"chain={results['parameters']['chain']}",
        "\n---\n"
    ]
    
    # DefiLlama results
    if "defillama" in results["sources"]:
        source = results["sources"]["defillama"]
        lines.append("## 📊 DefiLlama - Real-time Yields\n")
        
        if source["status"] == "success" and source.get("opportunities"):
            for opp in source["opportunities"]:
                # Actionable status
                actionable = opp.get("actionable_addresses", {})
                action_status = "✅ Ready" if actionable.get("has_actionable_address") else "⚠️ Needs lookup"
                
                lines.extend([
                    f"### {opp.get('protocol', 'N/A')} - {opp.get('symbol', 'N/A')}",
                    f"- **APY**: {opp.get('apy', 0):.2f}%",
                    f"- **TVL**: ${opp.get('tvl_usd', 0):,.0f}",
                    f"- **Chain**: {opp.get('chain', 'N/A')}",
                    f"- **Actionable**: {action_status}",
                    f"- **Link**: {opp.get('url', 'N/A')}",
                    ""
                ])
                
                # Risk signals summary
                risk = opp.get("risk_signals", {})
                if risk:
                    lines.append(f"**Risk Signals**: Audited={'✅' if risk.get('has_audit') else '❌'}, "
                                f"Known={'✅' if risk.get('known_protocol') else '❌'}, "
                                f"APY Type={risk.get('apy_composition', 'unknown')}")
                    lines.append("")
        else:
            lines.append(f"Status: {source.get('status', 'unknown')}")
            if source.get("error"):
                lines.append(f"Error: {source['error']}")
            lines.append("")
    
    # Dune results
    if "dune" in results["sources"]:
        source = results["sources"]["dune"]
        lines.append("## 🧙 Dune Analytics - Data Tables\n")
        
        if source["status"] == "success" and source.get("tables"):
            lines.append("Available tables for custom analysis:\n")
            for table in source["tables"]:
                chains = ", ".join(table.get("blockchains", [])[:3])
                lines.append(f"- `{table['full_name']}` ({table.get('category', 'N/A')}) - Chains: {chains}")
        else:
            lines.append(f"Status: {source.get('status', 'unknown')}")
            if source.get("error"):
                lines.append(f"Error: {source['error']}")
        lines.append("")
    
    return "\n".join(lines)


def format_llm_ready_output(results: Dict) -> str:
    """
    Format results as LLM-ready prompt for risk analysis.
    
    Optimized for LLM consumption with structured data.
    """
    lines = [
        "# DeFi Investment Search Results - LLM Analysis Request",
        f"\nGenerated: {results['generated_at']}",
        "",
        "## Task",
        "Analyze the following investment opportunities and provide:",
        "1. Risk assessment (Low/Medium/High) for each opportunity",
        "2. Key risk factors and warnings",
        "3. Recommended execution approach",
        "4. Any additional data needed for decision",
        "",
        "---\n"
    ]
    
    # DefiLlama opportunities
    if "defillama" in results["sources"]:
        source = results["sources"]["defillama"]
        if source["status"] == "success" and source.get("opportunities"):
            lines.append("## Opportunities from DefiLlama\n")
            for i, opp in enumerate(source["opportunities"], 1):
                lines.append(f"### Opportunity {i}")
                lines.append("```json")
                lines.append(json.dumps(opp, indent=2, ensure_ascii=False))
                lines.append("```\n")
    
    # Dune tables
    if "dune" in results["sources"]:
        source = results["sources"]["dune"]
        if source["status"] == "success" and source.get("tables"):
            lines.append("## Available Dune Data Tables\n")
            for table in source["tables"]:
                lines.append(f"- `{table['full_name']}`: {table.get('description', 'No description')}")
            lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Unified search across DefiLlama and Dune (v0.2.0 - LLM-ready)"
    )
    parser.add_argument("--min-apy", type=float, default=0, help="Minimum APY %%")
    parser.add_argument("--chain", default="Ethereum", help="Blockchain to search")
    parser.add_argument("--min-tvl", type=float, default=0, help="Minimum TVL in USD")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Results per source")
    parser.add_argument("--source", action="append", choices=["defillama", "dune"],
                        help="Specific sources to use (default: all)")
    parser.add_argument("--output", "-o", choices=["markdown", "json"], default="markdown",
                        help="Output format")
    parser.add_argument("--llm-ready", action="store_true",
                        help="Output LLM-ready prompt for risk analysis")
    parser.add_argument("--no-risk-signals", action="store_true",
                        help="Exclude risk signals from output")
    parser.add_argument("--dune-query", type=str, help="Custom Dune table search query")
    
    args = parser.parse_args()
    
    # Custom Dune search
    if args.dune_query:
        tables = search_dune_tables(
            query=args.dune_query,
            chain=args.chain.lower(),
            limit=args.limit
        )
        if args.output == "json":
            print(json.dumps(tables, indent=2))
        else:
            for t in tables:
                print(f"{t['full_name']:40} | {t['category']:10} | {', '.join(t['blockchains'][:2])}")
        return
    
    # Unified search
    sources = args.source if args.source else None
    results = unified_search(
        min_apy=args.min_apy,
        chain=args.chain,
        min_tvl=args.min_tvl,
        sources=sources,
        limit=args.limit,
        include_risk_signals=not args.no_risk_signals
    )
    
    # Output formatting
    if args.llm_ready:
        print(format_llm_ready_output(results))
    elif args.output == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_unified_report(results))


if __name__ == "__main__":
    main()