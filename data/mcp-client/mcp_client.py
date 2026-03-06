#!/usr/bin/env python3
"""
MCP Client Implementation
v1.0.0

Model Context Protocol (MCP) Client - Connect to tools and data sources
Spec: https://modelcontextprotocol.io
"""

import argparse
import json
import requests
import sys

DEFAULT_MCP_SERVER = "http://localhost:8080"


class MCPClient:
    """Client for Model Context Protocol"""
    
    def __init__(self, server_url=DEFAULT_MCP_SERVER, api_key=None):
        self.server_url = server_url.rstrip("/")
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    def connect(self):
        """Connect to MCP server"""
        resp = self.session.get(f"{self.server_url}/mcp/connect")
        resp.raise_for_status()
        return resp.json()
    
    def list_tools(self):
        """List available tools"""
        resp = self.session.get(f"{self.server_url}/mcp/tools")
        resp.raise_for_status()
        return resp.json()
    
    def call_tool(self, tool_name, arguments):
        """Call a tool"""
        data = {
            "tool": tool_name,
            "arguments": json.loads(arguments) if isinstance(arguments, str) else arguments
        }
        resp = self.session.post(f"{self.server_url}/mcp/call", json=data)
        resp.raise_for_status()
        return resp.json()
    
    def list_resources(self):
        """List available resources"""
        resp = self.session.get(f"{self.server_url}/mcp/resources")
        resp.raise_for_status()
        return resp.json()
    
    def read_resource(self, resource_uri):
        """Read a resource"""
        # Security: Warn about file:// URIs (could exfiltrate local files)
        if resource_uri.startswith("file://"):
            print("WARNING: file:// URIs can read local files from the MCP server.", file=sys.stderr)
            print("Only use with trusted MCP servers.", file=sys.stderr)
        resp = self.session.get(f"{self.server_url}/mcp/read?uri={resource_uri}")
        resp.raise_for_status()
        return resp.json()
    
    def list_prompts(self):
        """List prompt templates"""
        resp = self.session.get(f"{self.server_url}/mcp/prompts")
        resp.raise_for_status()
        return resp.json()


def cmd_connect(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.connect()
    print(json.dumps(result, indent=2))


def cmd_tools(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.list_tools()
    print(json.dumps(result, indent=2))


def cmd_call(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.call_tool(args.tool_name, args.arguments)
    print(json.dumps(result, indent=2))


def cmd_resources(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.list_resources()
    print(json.dumps(result, indent=2))


def cmd_read(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.read_resource(args.resource_uri)
    print(json.dumps(result, indent=2))


def cmd_prompts(args):
    client = MCPClient(args.server_url, args.api_key)
    result = client.list_prompts()
    print(json.dumps(result, indent=2))


def main():
    # Parent parser for global args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--server-url", default=DEFAULT_MCP_SERVER, help="MCP Server URL")
    parent_parser.add_argument("--api-key", help="API Key")
    
    parser = argparse.ArgumentParser(description="MCP Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    subparsers.add_parser("connect", parents=[parent_parser], help="Connect to server")
    subparsers.add_parser("tools", parents=[parent_parser], help="List tools")
    
    call_parser = subparsers.add_parser("call", parents=[parent_parser], help="Call tool")
    call_parser.add_argument("--tool-name", required=True, help="Tool name")
    call_parser.add_argument("--arguments", required=True, help="JSON arguments")
    
    subparsers.add_parser("resources", parents=[parent_parser], help="List resources")
    
    read_parser = subparsers.add_parser("read", parents=[parent_parser], help="Read resource")
    read_parser.add_argument("--resource-uri", required=True, help="Resource URI")
    
    subparsers.add_parser("prompts", parents=[parent_parser], help="List prompts")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    handlers = {
        "connect": cmd_connect,
        "tools": cmd_tools,
        "call": cmd_call,
        "resources": cmd_resources,
        "read": cmd_read,
        "prompts": cmd_prompts
    }
    
    try:
        handlers[args.command](args)
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to {args.server_url}", file=sys.stderr)
        print("Make sure the MCP server is running", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
