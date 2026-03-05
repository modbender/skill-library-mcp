#!/usr/bin/env python3
"""
Dialogflow CX Advanced CLI - Environments and webhooks

Usage:
    python advanced.py list-environments --agent AGENT_NAME
    python advanced.py list-webhooks --agent AGENT_NAME

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
    from google.cloud.dialogflowcx_v3beta1 import EnvironmentsClient, WebhooksClient
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: google-cloud-dialogflow-cx not installed")
    print("Run: pip install google-cloud-dialogflow-cx google-auth")
    sys.exit(1)


def list_environments(agent_name: str):
    """List all environments in an agent."""
    client = EnvironmentsClient()
    
    print(f"Listing environments for {agent_name}...\n")
    
    for env in client.list_environments(parent=agent_name):
        print(f"  {env.display_name}")
        print(f"    Name: {env.name}")
        print()


def list_webhooks(agent_name: str):
    """List all webhooks in an agent."""
    client = WebhooksClient()
    
    print(f"Listing webhooks for {agent_name}...\n")
    
    for webhook in client.list_webhooks(parent=agent_name):
        print(f"  {webhook.display_name}")
        print(f"    Name: {webhook.name}")
        if webhook.generic_web_service:
            print(f"    URI: {webhook.generic_web_service.uri}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Dialogflow CX Advanced CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-environments
    p = subparsers.add_parser("list-environments", help="List environments")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    # list-webhooks
    p = subparsers.add_parser("list-webhooks", help="List webhooks")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list-environments":
        list_environments(args.agent)
    elif args.command == "list-webhooks":
        list_webhooks(args.agent)


if __name__ == "__main__":
    main()