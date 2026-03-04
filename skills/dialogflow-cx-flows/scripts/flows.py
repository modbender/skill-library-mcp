#!/usr/bin/env python3
"""
Dialogflow CX Flows CLI - Flows and Pages management

Usage:
    python flows.py list-flows --agent AGENT_NAME
    python flows.py list-pages --flow FLOW_NAME
    python flows.py get-flow --flow FLOW_NAME
    python flows.py get-page --page PAGE_NAME

Requires:
    - google-cloud-dialogflow-cx
    - google-auth

Install:
    pip install google-cloud-dialogflow-cx google-auth
"""

import argparse
import json
import sys

try:
    from google.cloud.dialogflowcx_v3beta1 import FlowsClient, PagesClient
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: google-cloud-dialogflow-cx not installed")
    print("Run: pip install google-cloud-dialogflow-cx google-auth")
    sys.exit(1)


def list_flows(agent_name: str):
    """List all flows in an agent."""
    client = FlowsClient()
    
    print(f"Listing flows for {agent_name}...\n")
    
    for flow in client.list_flows(parent=agent_name):
        print(f"  {flow.display_name}")
        print(f"    Name: {flow.name}")
        print()


def get_flow(flow_name: str):
    """Get flow details."""
    client = FlowsClient()
    
    flow = client.get_flow(name=flow_name)
    print(json.dumps(MessageToDict(flow._pb), indent=2))


def list_pages(flow_name: str):
    """List all pages in a flow."""
    client = PagesClient()
    
    print(f"Listing pages for {flow_name}...\n")
    
    for page in client.list_pages(parent=flow_name):
        print(f"  {page.display_name}")
        print(f"    Name: {page.name}")
        print()


def get_page(page_name: str):
    """Get page details."""
    client = PagesClient()
    
    page = client.get_page(name=page_name)
    print(json.dumps(MessageToDict(page._pb), indent=2))


def main():
    parser = argparse.ArgumentParser(description="Dialogflow CX Flows CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-flows
    p = subparsers.add_parser("list-flows", help="List flows")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    # get-flow
    p = subparsers.add_parser("get-flow", help="Get flow details")
    p.add_argument("--flow", required=True, help="Full flow name")
    
    # list-pages
    p = subparsers.add_parser("list-pages", help="List pages in flow")
    p.add_argument("--flow", required=True, help="Full flow name")
    
    # get-page
    p = subparsers.add_parser("get-page", help="Get page details")
    p.add_argument("--page", required=True, help="Full page name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list-flows":
        list_flows(args.agent)
    elif args.command == "get-flow":
        get_flow(args.flow)
    elif args.command == "list-pages":
        list_pages(args.flow)
    elif args.command == "get-page":
        get_page(args.page)


if __name__ == "__main__":
    main()