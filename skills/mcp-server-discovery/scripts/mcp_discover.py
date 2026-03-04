#!/usr/bin/env python3
"""
MCP Server Discovery Tool
自动发现、管理和配置 MCP (Model Context Protocol) 服务器
"""

import json
import sys
from urllib.request import urlopen
from urllib.error import URLError
from typing import Dict, List, Optional
import argparse

# MCP 官方和社区维护的服务器注册表
MCP_REGISTRIES = {
    "official": "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md",
    "awesome": "https://raw.githubusercontent.com/appcypher/awesome-mcp-servers/main/README.md",
    "community": "https://api.github.com/search/repositories?q=topic:mcp-server+sort:updated"
}

# 已知的高质量 MCP 服务器列表
KNOWN_SERVERS = {
    "filesystem": {
        "name": "filesystem",
        "description": "Secure file system access with configurable permissions",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
        "install": "npx -y @modelcontextprotocol/server-filesystem",
        "category": "filesystem"
    },
    "github": {
        "name": "github",
        "description": "GitHub API integration for repository management",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
        "install": "npx -y @modelcontextprotocol/server-github",
        "category": "dev"
    },
    "postgres": {
        "name": "postgres",
        "description": "PostgreSQL database integration with schema inspection",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres",
        "install": "npx -y @modelcontextprotocol/server-postgres",
        "category": "database"
    },
    "sqlite": {
        "name": "sqlite",
        "description": "SQLite database operations and querying",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
        "install": "npx -y @modelcontextprotocol/server-sqlite",
        "category": "database"
    },
    "puppeteer": {
        "name": "puppeteer",
        "description": "Web scraping and browser automation",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
        "install": "npx -y @modelcontextprotocol/server-puppeteer",
        "category": "web"
    },
    "brave-search": {
        "name": "brave-search",
        "description": "Brave Search API integration",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
        "install": "npx -y @modelcontextprotocol/server-brave-search",
        "category": "search"
    },
    "fetch": {
        "name": "fetch",
        "description": "Web content fetching and processing",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch",
        "install": "npx -y @modelcontextprotocol/server-fetch",
        "category": "web"
    },
    "memory": {
        "name": "memory",
        "description": "Knowledge graph-based persistent memory",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
        "install": "npx -y @modelcontextprotocol/server-memory",
        "category": "memory"
    }
}


def list_servers(category: Optional[str] = None) -> List[Dict]:
    """列出可用的 MCP 服务器"""
    servers = []
    for key, server in KNOWN_SERVERS.items():
        if category is None or server.get("category") == category:
            servers.append(server)
    return servers


def search_servers(query: str) -> List[Dict]:
    """搜索 MCP 服务器"""
    results = []
    query_lower = query.lower()
    for key, server in KNOWN_SERVERS.items():
        if (query_lower in server["name"].lower() or 
            query_lower in server["description"].lower() or
            query_lower in server.get("category", "").lower()):
            results.append(server)
    return results


def get_server_info(name: str) -> Optional[Dict]:
    """获取特定服务器的详细信息"""
    return KNOWN_SERVERS.get(name)


def generate_config(selected_servers: List[str]) -> Dict:
    """生成 MCP 客户端配置"""
    config = {"mcpServers": {}}
    for server_name in selected_servers:
        server = KNOWN_SERVERS.get(server_name)
        if server:
            config["mcpServers"][server_name] = {
                "command": "npx",
                "args": ["-y", f"@modelcontextprotocol/server-{server_name}"]
            }
    return config


def main():
    parser = argparse.ArgumentParser(description="MCP Server Discovery Tool")
    parser.add_argument("action", choices=["list", "search", "info", "config"],
                       help="Action to perform")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--name", "-n", help="Server name")
    parser.add_argument("--servers", "-s", help="Comma-separated server names for config")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.action == "list":
        servers = list_servers(args.category)
        if args.json:
            print(json.dumps(servers, indent=2))
        else:
            print("Available MCP Servers:")
            print("-" * 60)
            for s in servers:
                print(f"  {s['name']:15} [{s.get('category', 'misc'):10}] {s['description']}")
                print(f"  {'':15} Install: {s['install']}")
                print()
    
    elif args.action == "search":
        if not args.query:
            print("Error: --query is required for search", file=sys.stderr)
            sys.exit(1)
        results = search_servers(args.query)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Search results for '{args.query}':")
            print("-" * 60)
            for s in results:
                print(f"  {s['name']}: {s['description']}")
    
    elif args.action == "info":
        if not args.name:
            print("Error: --name is required for info", file=sys.stderr)
            sys.exit(1)
        server = get_server_info(args.name)
        if server:
            print(json.dumps(server, indent=2) if args.json else f"""
Server: {server['name']}
Description: {server['description']}
Category: {server.get('category', 'misc')}
URL: {server['url']}
Install: {server['install']}
""")
        else:
            print(f"Server '{args.name}' not found", file=sys.stderr)
            sys.exit(1)
    
    elif args.action == "config":
        if not args.servers:
            print("Error: --servers is required for config", file=sys.stderr)
            sys.exit(1)
        selected = [s.strip() for s in args.servers.split(",")]
        config = generate_config(selected)
        print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
