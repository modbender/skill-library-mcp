#!/usr/bin/env python3
"""
Vapi Voice AI Agent API wrapper for OpenClaw.
Requires: VAPI_API_KEY environment variable.

Usage:
    python3 vapi_agent.py create-agent '{"name":"My Agent","firstMessage":"Hello!",...}'
    python3 vapi_agent.py list-agents
    python3 vapi_agent.py call '{"assistantId":"...","phoneNumberId":"...","customer":{"number":"+1..."}}'
    python3 vapi_agent.py list-calls
    python3 vapi_agent.py get-call <callId>
"""

import os
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "https://api.vapi.ai"


def get_api_key():
    key = os.environ.get("VAPI_API_KEY")
    if not key:
        print(json.dumps({"error": "VAPI_API_KEY environment variable not set"}))
        sys.exit(1)
    return key


def api_request(method: str, path: str, data: dict = None) -> dict:
    """Make authenticated Vapi API request."""
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode()
            return json.loads(response_body) if response_body else {"status": "success"}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            return {"error": f"HTTP {e.code}", "details": json.loads(error_body)}
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "details": error_body}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


# ─── Assistant (Agent) Operations ───

def create_agent(config: dict) -> dict:
    """Create a new voice agent/assistant."""
    payload = {
        "name": config.get("name", "Unnamed Agent"),
        "firstMessage": config.get("firstMessage", "Hello! How can I help you?"),
        "model": config.get("model", {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": config.get("systemPrompt", "You are a helpful voice assistant. Keep responses brief and conversational.")}],
            "temperature": config.get("temperature", 0.7),
        }),
        "voice": config.get("voice", {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM",  # Rachel - default
        }),
        "endCallFunctionEnabled": config.get("endCallFunctionEnabled", True),
        "maxDurationSeconds": config.get("maxDurationSeconds", 600),
        "silenceTimeoutSeconds": config.get("silenceTimeoutSeconds", 30),
    }

    # Add optional fields
    if "serverUrl" in config:
        payload["serverUrl"] = config["serverUrl"]
    if "transcriber" in config:
        payload["transcriber"] = config["transcriber"]
    if "forwardingPhoneNumber" in config:
        payload["forwardingPhoneNumber"] = config["forwardingPhoneNumber"]

    return api_request("POST", "/assistant", payload)


def get_agent(assistant_id: str) -> dict:
    return api_request("GET", f"/assistant/{assistant_id}")


def list_agents() -> dict:
    return api_request("GET", "/assistant")


def update_agent(assistant_id: str, updates: dict) -> dict:
    return api_request("PATCH", f"/assistant/{assistant_id}", updates)


def delete_agent(assistant_id: str) -> dict:
    return api_request("DELETE", f"/assistant/{assistant_id}")


# ─── Call Operations ───

def make_call(config: dict) -> dict:
    """Make an outbound call."""
    payload = {
        "assistantId": config["assistantId"],
        "customer": config["customer"],
    }
    if "phoneNumberId" in config:
        payload["phoneNumberId"] = config["phoneNumberId"]
    if "assistantOverrides" in config:
        payload["assistantOverrides"] = config["assistantOverrides"]
    return api_request("POST", "/call/phone", payload)


def get_call(call_id: str) -> dict:
    return api_request("GET", f"/call/{call_id}")


def list_calls() -> dict:
    return api_request("GET", "/call")


# ─── Phone Number Operations ───

def list_phones() -> dict:
    return api_request("GET", "/phone-number")


def import_phone(config: dict) -> dict:
    return api_request("POST", "/phone-number", config)


def update_phone(config: dict) -> dict:
    phone_id = config.pop("id")
    return api_request("PATCH", f"/phone-number/{phone_id}", config)


# ─── CLI Router ───

def main():
    if len(sys.argv) < 2:
        print("Usage: vapi_agent.py <command> [args...]")
        print("Commands: create-agent, get-agent, list-agents, update-agent, delete-agent,")
        print("          call, get-call, list-calls, list-phones, import-phone, update-phone")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "create-agent": lambda: create_agent(json.loads(args[0])),
        "get-agent": lambda: get_agent(args[0]),
        "list-agents": lambda: list_agents(),
        "update-agent": lambda: update_agent(args[0], json.loads(args[1])),
        "delete-agent": lambda: delete_agent(args[0]),
        "call": lambda: make_call(json.loads(args[0])),
        "get-call": lambda: get_call(args[0]),
        "list-calls": lambda: list_calls(),
        "list-phones": lambda: list_phones(),
        "import-phone": lambda: import_phone(json.loads(args[0])),
        "update-phone": lambda: update_phone(json.loads(args[0])),
    }

    if command not in commands:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)

    try:
        result = commands[command]()
        print(json.dumps(result, indent=2))
    except IndexError:
        print(json.dumps({"error": f"Missing arguments for {command}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
