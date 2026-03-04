#!/usr/bin/env python3
"""Bandwidth CLI — Bandwidth — messaging, voice calls, phone numbers, and 911 services.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://messaging.bandwidth.com/api/v2/users/{account_id}"


def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return val


def req(method, url, data=None, headers=None, timeout=30):
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err}), file=sys.stderr)
        sys.exit(1)


def api(method, path, data=None, params=None):
    """Make authenticated API request."""
    base = API_BASE
    token = get_env("BANDWIDTH_API_TOKEN")
    if not token:
        print("Error: BANDWIDTH_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}"}
    acct = get_env("BANDWIDTH_ACCOUNT_ID")
    base = base.replace("{account_id}", acct)
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_send_message(args):
    """Send SMS/MMS"""
    path = "/messages"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.text:
        data["text"] = args.text
    if args.application_id:
        data["application-id"] = args.application_id
    result = api("POST", path, data=data)
    out(result)

def cmd_list_messages(args):
    """List messages"""
    path = "/messages"
    params = {}
    if getattr(args, 'from'):
        params["from"] = getattr(args, 'from')
    if args.to:
        params["to"] = args.to
    result = api("GET", path, params=params)
    out(result)

def cmd_create_call(args):
    """Create outbound call"""
    path = "/calls"
    data = {}
    if getattr(args, 'from'):
        data["from"] = getattr(args, 'from')
    if args.to:
        data["to"] = args.to
    if args.answer_url:
        data["answer-url"] = args.answer_url
    if args.application_id:
        data["application-id"] = args.application_id
    result = api("POST", path, data=data)
    out(result)

def cmd_get_call(args):
    """Get call details"""
    path = "/calls/{id}"
    path = path.replace("{id}", str(args.id))
    result = api("GET", path)
    out(result)

def cmd_list_numbers(args):
    """List phone numbers"""
    path = "/phoneNumbers"
    result = api("GET", path)
    out(result)

def cmd_search_numbers(args):
    """Search available numbers"""
    path = "/availableNumbers"
    params = {}
    if args.area_code:
        params["area-code"] = args.area_code
    if args.quantity:
        params["quantity"] = args.quantity
    result = api("GET", path, params=params)
    out(result)

def cmd_order_number(args):
    """Order phone number"""
    path = "/orders"
    data = {}
    if args.numbers:
        data["numbers"] = args.numbers
    result = api("POST", path, data=data)
    out(result)

def cmd_list_applications(args):
    """List applications"""
    path = "/applications"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Bandwidth CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_send_message = sub.add_parser("send-message", help="Send SMS/MMS")
    p_send_message.add_argument("--from", dest="from_addr", required=True)
    p_send_message.add_argument("--to", required=True)
    p_send_message.add_argument("--text", required=True)
    p_send_message.add_argument("--application-id", required=True)
    p_send_message.set_defaults(func=cmd_send_message)

    p_list_messages = sub.add_parser("list-messages", help="List messages")
    p_list_messages.add_argument("--from", dest="from_addr", required=True)
    p_list_messages.add_argument("--to", required=True)
    p_list_messages.set_defaults(func=cmd_list_messages)

    p_create_call = sub.add_parser("create-call", help="Create outbound call")
    p_create_call.add_argument("--from", dest="from_addr", required=True)
    p_create_call.add_argument("--to", required=True)
    p_create_call.add_argument("--answer-url", required=True)
    p_create_call.add_argument("--application-id", required=True)
    p_create_call.set_defaults(func=cmd_create_call)

    p_get_call = sub.add_parser("get-call", help="Get call details")
    p_get_call.add_argument("id")
    p_get_call.set_defaults(func=cmd_get_call)

    p_list_numbers = sub.add_parser("list-numbers", help="List phone numbers")
    p_list_numbers.set_defaults(func=cmd_list_numbers)

    p_search_numbers = sub.add_parser("search-numbers", help="Search available numbers")
    p_search_numbers.add_argument("--area-code", required=True)
    p_search_numbers.add_argument("--quantity", default="10")
    p_search_numbers.set_defaults(func=cmd_search_numbers)

    p_order_number = sub.add_parser("order-number", help="Order phone number")
    p_order_number.add_argument("--numbers", default="comma-separated")
    p_order_number.set_defaults(func=cmd_order_number)

    p_list_applications = sub.add_parser("list-applications", help="List applications")
    p_list_applications.set_defaults(func=cmd_list_applications)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
