#!/usr/bin/env python3
"""
A2A Protocol Client Implementation
v1.0.0

Agent2Agent (A2A) Protocol - Communicate with other AI agents
Spec: https://a2a-protocol.org
"""

import argparse
import json
import requests
import sys
import time

DEFAULT_REGISTRY = "http://localhost:8000"


class A2AClient:
    """Client for A2A Protocol communication"""
    
    def __init__(self, registry_url=DEFAULT_REGISTRY, api_key=None):
        self.registry_url = registry_url.rstrip("/")
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
    
    def register_agent(self, name, description, capabilities, endpoint):
        """Register this agent with the A2A network"""
        data = {
            "name": name,
            "description": description,
            "capabilities": capabilities.split(",") if isinstance(capabilities, str) else capabilities,
            "endpoint": endpoint
        }
        resp = self.session.post(f"{self.registry_url}/a2a/agents", json=data)
        resp.raise_for_status()
        return resp.json()
    
    def get_agent_card(self, agent_id):
        """Get Agent Card for discovery"""
        resp = self.session.get(f"{self.registry_url}/a2a/agents/{agent_id}/card")
        resp.raise_for_status()
        return resp.json()
    
    def send_message(self, to_agent_id, content):
        """Send direct message to agent"""
        data = {
            "to_agent_id": to_agent_id,
            "content": content
        }
        resp = self.session.post(f"{self.registry_url}/a2a/messages", json=data)
        resp.raise_for_status()
        return resp.json()
    
    def submit_task(self, to_agent_id, task_description):
        """Submit task to remote agent"""
        data = {
            "to_agent_id": to_agent_id,
            "task": task_description
        }
        resp = self.session.post(f"{self.registry_url}/a2a/tasks", json=data)
        resp.raise_for_status()
        result = resp.json()
        return result.get("task_id")
    
    def get_task_status(self, task_id):
        """Check task status"""
        resp = self.session.get(f"{self.registry_url}/a2a/tasks/{task_id}")
        resp.raise_for_status()
        return resp.json()
    
    def get_task_result(self, task_id):
        """Get task result"""
        resp = self.session.get(f"{self.registry_url}/a2a/tasks/{task_id}/result")
        resp.raise_for_status()
        return resp.json()
    
    def list_agents(self, capability=None):
        """List available agents"""
        url = f"{self.registry_url}/a2a/agents"
        if capability:
            url += f"?capability={capability}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()


def cmd_register(args):
    client = A2AClient(args.registry_url, args.api_key)
    result = client.register_agent(args.name, args.description, args.capabilities, args.endpoint)
    print(json.dumps(result, indent=2))


def cmd_card(args):
    client = A2AClient(args.registry_url, args.api_key)
    result = client.get_agent_card(args.agent_id)
    print(json.dumps(result, indent=2))


def cmd_send(args):
    client = A2AClient(args.registry_url, args.api_key)
    result = client.send_message(args.to_agent, args.content)
    print(json.dumps(result, indent=2))


def cmd_task(args):
    client = A2AClient(args.registry_url, args.api_key)
    task_id = client.submit_task(args.to_agent, args.task)
    print(f"Task submitted: {task_id}")
    
    # Poll for result
    print("Polling for result...")
    while True:
        status = client.get_task_status(task_id)
        print(f"Status: {status.get('status')}")
        if status.get("status") in ["completed", "failed"]:
            if status.get("status") == "completed":
                result = client.get_task_result(task_id)
                print(json.dumps(result, indent=2))
            break
        time.sleep(2)


def cmd_status(args):
    client = A2AClient(args.registry_url, args.api_key)
    result = client.get_task_status(args.task_id)
    print(json.dumps(result, indent=2))


def cmd_list(args):
    client = A2AClient(args.registry_url, args.api_key)
    result = client.list_agents()
    print(json.dumps(result, indent=2))


def main():
    # Create parent parser for global args
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--registry-url", default=DEFAULT_REGISTRY, help="A2A Registry URL")
    parent_parser.add_argument("--api-key", help="API Key for authentication")
    
    # Create main parser
    parser = argparse.ArgumentParser(description="A2A Protocol Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # register
    reg_parser = subparsers.add_parser("register", parents=[parent_parser], help="Register agent")
    reg_parser.add_argument("--name", required=True, help="Agent name")
    reg_parser.add_argument("--description", required=True, help="Agent description")
    reg_parser.add_argument("--capabilities", required=True, help="Comma-separated capabilities")
    reg_parser.add_argument("--endpoint", required=True, help="Agent endpoint URL")
    
    # card
    card_parser = subparsers.add_parser("card", parents=[parent_parser], help="Get Agent Card")
    card_parser.add_argument("--agent-id", required=True, help="Agent ID")
    
    # send
    send_parser = subparsers.add_parser("send", parents=[parent_parser], help="Send message")
    send_parser.add_argument("--to-agent", required=True, help="Target agent ID")
    send_parser.add_argument("--content", required=True, help="Message content")
    
    # task
    task_parser = subparsers.add_parser("task", parents=[parent_parser], help="Submit task")
    task_parser.add_argument("--to-agent", required=True, help="Target agent ID")
    task_parser.add_argument("--task", required=True, help="Task description")
    
    # status
    status_parser = subparsers.add_parser("status", parents=[parent_parser], help="Check task status")
    status_parser.add_argument("--task-id", required=True, help="Task ID")
    
    # list
    subparsers.add_parser("list", parents=[parent_parser], help="List agents")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to handler
    handlers = {
        "register": cmd_register,
        "card": cmd_card,
        "send": cmd_send,
        "task": cmd_task,
        "status": cmd_status,
        "list": cmd_list
    }
    
    try:
        handlers[args.command](args)
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to {args.registry_url}", file=sys.stderr)
        print("Make sure the A2A server is running", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
