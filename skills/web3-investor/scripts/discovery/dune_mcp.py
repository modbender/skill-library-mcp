#!/usr/bin/env python3
"""
Dune MCP Adapter for Web3 Investor Skill

Provides a clean interface to interact with Dune's MCP server
for blockchain data discovery and analysis.

Usage:
    python dune_mcp.py search "aave lending ethereum" --category spell
    python dune_mcp.py query 12345  # Execute a query by ID
    python dune_mcp.py results <execution_id>  # Get execution results
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

# Dune MCP Configuration
DUNE_MCP_URL = "https://api.dune.com/mcp/v1"
DUNE_API_KEY = "v9j8OB9igHEm46MDI9PvxA4nSKu8ZuCI"  # TODO: Move to env variable


def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call a Dune MCP tool and return the result.
    
    Handles SSE (Server-Sent Events) response format.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    headers = {
        "x-dune-api-key": DUNE_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(DUNE_MCP_URL, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=120) as response:
            # Handle SSE response
            response_text = response.read().decode('utf-8')
            
            # Parse SSE format: "event: message\nid: xxx\ndata: {...}"
            result = None
            for line in response_text.split('\n'):
                if line.startswith('data: '):
                    try:
                        parsed = json.loads(line[6:])
                        if 'result' in parsed:
                            result = parsed['result']
                        elif 'error' in parsed:
                            return {"error": parsed['error']}
                    except json.JSONDecodeError:
                        continue
            
            return result or {"error": "No result found in response"}
            
    except urllib.error.URLError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def search_tables(
    query: str,
    categories: Optional[List[str]] = None,
    blockchains: Optional[List[str]] = None,
    limit: int = 20,
    include_schema: bool = False
) -> Dict[str, Any]:
    """
    Search for Dune tables matching the query.
    
    Args:
        query: Natural language query (e.g., "aave lending ethereum")
        categories: Filter by category (canonical, decoded, spell, community)
        blockchains: Filter by blockchain (e.g., ethereum, arbitrum)
        limit: Maximum number of results
        include_schema: Include column schema in results
    
    Returns:
        Dict with search results
    """
    arguments = {
        "query": query,
        "limit": limit,
        "includeSchema": include_schema
    }
    
    if categories:
        arguments["categories"] = categories
    if blockchains:
        arguments["blockchains"] = blockchains
    
    return call_mcp_tool("searchTables", arguments)


def execute_query(query_id: int, parameters: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Execute a Dune query by ID.
    
    Args:
        query_id: The numeric ID of the query
        parameters: Optional query parameters
    
    Returns:
        Dict with execution_id and state
    """
    arguments = {"query_id": query_id}
    if parameters:
        arguments["query_parameters"] = parameters
    
    return call_mcp_tool("executeQueryById", arguments)


def get_execution_results(execution_id: str, limit: int = 100, timeout: int = 60) -> Dict[str, Any]:
    """
    Get results of a query execution.
    
    Args:
        execution_id: The execution ID
        limit: Maximum number of rows to return
        timeout: Seconds to wait for completion
    
    Returns:
        Dict with execution results
    """
    arguments = {
        "executionId": execution_id,
        "limit": limit,
        "timeout": timeout
    }
    
    return call_mcp_tool("getExecutionResults", arguments)


def create_query(name: str, sql: str, description: str = "", is_temp: bool = True) -> Dict[str, Any]:
    """
    Create a new Dune query.
    
    Args:
        name: Query title
        sql: SQL query text
        description: Query description
        is_temp: Whether to create as temporary query
    
    Returns:
        Dict with query_id
    """
    arguments = {
        "name": name,
        "query": sql,
        "is_temp": is_temp
    }
    if description:
        arguments["description"] = description
    
    return call_mcp_tool("createDuneQuery", arguments)


def list_blockchains(categories: Optional[List[str]] = None, query: str = "*") -> Dict[str, Any]:
    """
    List available blockchains with table counts.
    
    Args:
        categories: Filter by category
        query: Semantic filter
    
    Returns:
        Dict with blockchain list
    """
    arguments = {"query": query}
    if categories:
        arguments["categories"] = categories
    
    return call_mcp_tool("listBlockchains", arguments)


def get_usage() -> Dict[str, Any]:
    """
    Get current billing period usage.
    
    Returns:
        Dict with usage information
    """
    return call_mcp_tool("getUsage", {})


# ============================================================================
# Convenience functions for Web3 Investor Skill
# ============================================================================

def find_yield_pools(chain: str = "ethereum", limit: int = 20) -> List[Dict]:
    """
    Find DeFi yield pools using Dune's curated datasets.
    
    Returns structured opportunity data compatible with find_opportunities.py
    """
    # Search for yield/lending related tables
    result = search_tables(
        query="defi yield lending APY",
        categories=["spell"],
        blockchains=[chain],
        limit=limit,
        include_schema=True
    )
    
    if "error" in result:
        return []
    
    return result.get("results", [])


def format_table_results(results: List[Dict]) -> str:
    """Format table search results for display."""
    if not results:
        return "No tables found."
    
    lines = ["# Dune Tables Found\n"]
    for table in results:
        lines.append(f"## {table.get('full_name', 'N/A')}")
        lines.append(f"- **Category**: {table.get('category', 'N/A')}")
        lines.append(f"- **Blockchains**: {', '.join(table.get('blockchains', []))}")
        if table.get('description'):
            lines.append(f"- **Description**: {table['description']}")
        if table.get('partition_columns'):
            lines.append(f"- **Partition Columns**: {', '.join(table['partition_columns'])}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dune MCP Adapter for Web3 Investor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search tables
    search_parser = subparsers.add_parser("search", help="Search Dune tables")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", "-c", action="append", help="Filter by category (spell, decoded, canonical, community)")
    search_parser.add_argument("--chain", help="Filter by blockchain")
    search_parser.add_argument("--limit", "-n", type=int, default=20, help="Number of results")
    search_parser.add_argument("--schema", action="store_true", help="Include column schema")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Execute query
    exec_parser = subparsers.add_parser("exec", help="Execute a Dune query")
    exec_parser.add_argument("query_id", type=int, help="Query ID to execute")
    
    # Get results
    results_parser = subparsers.add_parser("results", help="Get execution results")
    results_parser.add_argument("execution_id", help="Execution ID")
    results_parser.add_argument("--limit", "-n", type=int, default=100, help="Number of rows")
    
    # List chains
    subparsers.add_parser("chains", help="List available blockchains")
    
    # Usage
    subparsers.add_parser("usage", help="Get API usage info")
    
    args = parser.parse_args()
    
    if args.command == "search":
        blockchains = [args.chain] if args.chain else None
        result = search_tables(
            query=args.query,
            categories=args.category,
            blockchains=blockchains,
            limit=args.limit,
            include_schema=args.schema
        )
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}", file=sys.stderr)
            elif "results" in result:
                print(format_table_results(result["results"]))
            else:
                print(json.dumps(result, indent=2))
    
    elif args.command == "exec":
        result = execute_query(args.query_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == "results":
        result = get_execution_results(args.execution_id, limit=args.limit)
        print(json.dumps(result, indent=2))
    
    elif args.command == "chains":
        result = list_blockchains()
        print(json.dumps(result, indent=2))
    
    elif args.command == "usage":
        result = get_usage()
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()