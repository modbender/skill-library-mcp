#!/usr/bin/env python3
"""
Dialogflow CX Agents CLI - Agent management operations

Usage:
    python agents.py list --project PROJECT_ID --location LOCATION
    python agents.py get --project PROJECT_ID --location LOCATION --agent AGENT_ID
    python agents.py create --project PROJECT_ID --location LOCATION --name "Agent Name" --language en --timezone "Asia/Kolkata"
    python agents.py update --agent AGENT_NAME --name "New Name"
    python agents.py delete --agent AGENT_NAME
    python agents.py export --agent AGENT_NAME --output agent.blob
    python agents.py validate --agent AGENT_NAME

Requires:
    - google-cloud-dialogflow-cx
    - google-auth

Install:
    pip install google-cloud-dialogflow-cx google-auth
"""

import argparse
import json
import sys
import os

try:
    from google.cloud.dialogflowcx_v3beta1 import AgentsClient, Agent
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: google-cloud-dialogflow-cx not installed")
    print("Run: pip install google-cloud-dialogflow-cx google-auth")
    sys.exit(1)


def get_agent_path(project: str, location: str, agent: str) -> str:
    """Build agent resource path."""
    return f"projects/{project}/locations/{location}/agents/{agent}"


def parse_agent_name(agent_name: str) -> tuple:
    """Parse full agent name to extract project, location, agent_id."""
    parts = agent_name.split("/")
    if len(parts) >= 6:
        return parts[1], parts[3], parts[5]
    raise ValueError(f"Invalid agent name format: {agent_name}")


def list_agents(project: str, location: str):
    """List all agents in a project/location."""
    client = AgentsClient()
    parent = f"projects/{project}/locations/{location}"
    
    print(f"Listing agents in {parent}...\n")
    
    for agent in client.list_agents(parent=parent):
        print(f"  Name: {agent.name}")
        print(f"  Display Name: {agent.display_name}")
        print(f"  Language: {agent.default_language_code}")
        print(f"  Timezone: {agent.time_zone}")
        print()


def get_agent(project: str, location: str, agent_id: str):
    """Get agent details."""
    client = AgentsClient()
    name = get_agent_path(project, location, agent_id)
    
    agent = client.get_agent(name=name)
    print(json.dumps(MessageToDict(agent._pb), indent=2))


def create_agent(project: str, location: str, display_name: str, language: str, timezone: str, description: str = ""):
    """Create a new agent."""
    client = AgentsClient()
    parent = f"projects/{project}/locations/{location}"
    
    agent = Agent(
        display_name=display_name,
        default_language_code=language,
        time_zone=timezone,
        description=description
    )
    
    result = client.create_agent(parent=parent, agent=agent)
    print(f"Created agent: {result.name}")
    print(f"Display name: {result.display_name}")


def update_agent(agent_name: str, display_name: str = None, description: str = None):
    """Update an existing agent."""
    client = AgentsClient()
    
    # Get current agent
    agent = client.get_agent(name=agent_name)
    
    # Update fields
    if display_name:
        agent.display_name = display_name
    if description is not None:
        agent.description = description
    
    result = client.update_agent(agent=agent)
    print(f"Updated agent: {result.name}")
    print(f"Display name: {result.display_name}")


def delete_agent(agent_name: str):
    """Delete an agent."""
    client = AgentsClient()
    
    client.delete_agent(name=agent_name)
    print(f"Deleted agent: {agent_name}")


def export_agent(agent_name: str, output_file: str):
    """Export agent to file."""
    client = AgentsClient()
    
    operation = client.export_agent(name=agent_name)
    response = operation.result()
    
    if response.agent_content:
        with open(output_file, "wb") as f:
            f.write(response.agent_content)
        print(f"Agent exported to: {output_file}")
    else:
        print(f"Agent exported to GCS: {response.agent_uri}")


def validate_agent(agent_name: str):
    """Validate an agent."""
    client = AgentsClient()
    
    result = client.validate_agent(name=agent_name)
    print("Validation result:")
    print(json.dumps(MessageToDict(result._pb), indent=2))


def main():
    parser = argparse.ArgumentParser(description="Dialogflow CX Agents CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list
    p = subparsers.add_parser("list", help="List all agents")
    p.add_argument("--project", required=True, help="GCP Project ID")
    p.add_argument("--location", default="global", help="Location (default: global)")
    
    # get
    p = subparsers.add_parser("get", help="Get agent details")
    p.add_argument("--project", required=True, help="GCP Project ID")
    p.add_argument("--location", default="global", help="Location")
    p.add_argument("--agent", required=True, help="Agent ID")
    
    # create
    p = subparsers.add_parser("create", help="Create agent")
    p.add_argument("--project", required=True, help="GCP Project ID")
    p.add_argument("--location", default="global", help="Location")
    p.add_argument("--name", required=True, help="Display name")
    p.add_argument("--language", default="en", help="Default language code")
    p.add_argument("--timezone", default="America/New_York", help="Timezone")
    p.add_argument("--description", default="", help="Description")
    
    # update
    p = subparsers.add_parser("update", help="Update agent")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--name", help="New display name")
    p.add_argument("--description", help="New description")
    
    # delete
    p = subparsers.add_parser("delete", help="Delete agent")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    # export
    p = subparsers.add_parser("export", help="Export agent")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--output", default="agent_export.blob", help="Output file")
    
    # validate
    p = subparsers.add_parser("validate", help="Validate agent")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_agents(args.project, args.location)
    elif args.command == "get":
        get_agent(args.project, args.location, args.agent)
    elif args.command == "create":
        create_agent(args.project, args.location, args.name, args.language, args.timezone, args.description)
    elif args.command == "update":
        update_agent(args.agent, args.name, args.description)
    elif args.command == "delete":
        delete_agent(args.agent)
    elif args.command == "export":
        export_agent(args.agent, args.output)
    elif args.command == "validate":
        validate_agent(args.agent)


if __name__ == "__main__":
    main()