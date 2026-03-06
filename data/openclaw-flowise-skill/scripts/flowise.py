#!/usr/bin/env python3
"""
Flowise API Client - Interact with Flowise AI workflows

Usage:
    # Send a prediction
    python flowise.py predict --url http://localhost:3000 --flow-id abc123 --question "Hello"
    
    # List all chatflows
    python flowise.py list --url http://localhost:3000
    
    # Get chatflow details
    python flowise.py get --url http://localhost:3000 --flow-id abc123
    
    # With API key
    python flowise.py predict --url http://localhost:3000 --api-key xxx --flow-id abc123 --question "Hello"
    
    # With session for conversation memory
    python flowise.py predict --url http://localhost:3000 --flow-id abc123 --question "Hello" --session-id user123
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


def make_request(url: str, method: str = "GET", data: dict = None, api_key: str = None) -> dict:
    """Make HTTP request to Flowise API"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": True, "status": e.code, "message": e.reason, "detail": error_body}
    except urllib.error.URLError as e:
        return {"error": True, "message": str(e.reason)}
    except Exception as e:
        return {"error": True, "message": str(e)}


def predict(url: str, flow_id: str, question: str, api_key: str = None, 
            session_id: str = None, streaming: bool = False) -> dict:
    """Send a prediction request to a Flowise chatflow"""
    endpoint = f"{url.rstrip('/')}/api/v1/prediction/{flow_id}"
    payload = {"question": question}
    
    if session_id:
        payload["sessionId"] = session_id
    if streaming:
        payload["streaming"] = True
    
    return make_request(endpoint, method="POST", data=payload, api_key=api_key)


def list_chatflows(url: str, api_key: str = None) -> dict:
    """List all available chatflows"""
    endpoint = f"{url.rstrip('/')}/api/v1/chatflows"
    return make_request(endpoint, api_key=api_key)


def get_chatflow(url: str, flow_id: str, api_key: str = None) -> dict:
    """Get details of a specific chatflow"""
    endpoint = f"{url.rstrip('/')}/api/v1/chatflows/{flow_id}"
    return make_request(endpoint, api_key=api_key)


def ping(url: str) -> dict:
    """Check if Flowise server is running"""
    endpoint = f"{url.rstrip('/')}/api/v1/ping"
    return make_request(endpoint)


def main():
    parser = argparse.ArgumentParser(description="Flowise API Client")
    parser.add_argument("--url", "-u", required=True, help="Flowise server URL")
    parser.add_argument("--api-key", "-k", help="API key for authentication")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # predict command
    pred_parser = subparsers.add_parser("predict", help="Send a prediction")
    pred_parser.add_argument("--flow-id", "-f", required=True, help="Chatflow ID")
    pred_parser.add_argument("--question", "-q", required=True, help="Question to ask")
    pred_parser.add_argument("--session-id", "-s", help="Session ID for conversation memory")
    pred_parser.add_argument("--streaming", action="store_true", help="Enable streaming")
    
    # list command
    subparsers.add_parser("list", help="List all chatflows")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get chatflow details")
    get_parser.add_argument("--flow-id", "-f", required=True, help="Chatflow ID")
    
    # ping command
    subparsers.add_parser("ping", help="Check server status")
    
    args = parser.parse_args()
    
    if args.command == "predict":
        result = predict(
            args.url, args.flow_id, args.question, 
            api_key=args.api_key, session_id=args.session_id, streaming=args.streaming
        )
    elif args.command == "list":
        result = list_chatflows(args.url, api_key=args.api_key)
    elif args.command == "get":
        result = get_chatflow(args.url, args.flow_id, api_key=args.api_key)
    elif args.command == "ping":
        result = ping(args.url)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if isinstance(result, dict) and result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
