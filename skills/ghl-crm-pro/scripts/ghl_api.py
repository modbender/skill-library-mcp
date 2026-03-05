#!/usr/bin/env python3
"""
GoHighLevel CRM API v2 wrapper for OpenClaw agents.
Requires: GHL_API_KEY, GHL_LOCATION_ID environment variables.

Usage:
    python3 ghl_api.py contacts search "john@example.com"
    python3 ghl_api.py contacts create '{"firstName":"John","email":"j@x.com"}'
    python3 ghl_api.py pipelines list
    python3 ghl_api.py conversations send-sms <contactId> "Hello!"
    python3 ghl_api.py calendars slots <calendarId> --start 2026-02-16 --end 2026-02-17
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Optional

BASE_URL = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2


def get_config():
    api_key = os.environ.get("GHL_API_KEY")
    location_id = os.environ.get("GHL_LOCATION_ID")
    if not api_key:
        print(json.dumps({"error": "GHL_API_KEY environment variable not set"}))
        sys.exit(1)
    if not location_id:
        print(json.dumps({"error": "GHL_LOCATION_ID environment variable not set"}))
        sys.exit(1)
    return api_key, location_id


def api_request(method: str, path: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    """Make an authenticated GHL API request with retry logic."""
    api_key, _ = get_config()

    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": API_VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    body = json.dumps(data).encode() if data else None

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_body = resp.read().decode()
                if response_body:
                    return json.loads(response_body)
                return {"status": "success", "httpCode": resp.status}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                delay = RETRY_BASE_DELAY ** (attempt + 1)
                time.sleep(delay)
                continue
            try:
                error_data = json.loads(error_body)
            except (json.JSONDecodeError, ValueError):
                error_data = error_body
            return {"error": f"HTTP {e.code}", "details": error_data}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


# ─── Contact Operations ───

def contacts_search(query: str) -> dict:
    _, location_id = get_config()
    return api_request("GET", "/contacts/", params={"locationId": location_id, "query": query})


def contacts_get(contact_id: str) -> dict:
    return api_request("GET", f"/contacts/{contact_id}")


def contacts_create(data: dict) -> dict:
    _, location_id = get_config()
    data["locationId"] = location_id
    return api_request("POST", "/contacts/", data=data)


def contacts_update(contact_id: str, data: dict) -> dict:
    return api_request("PUT", f"/contacts/{contact_id}", data=data)


def contacts_delete(contact_id: str) -> dict:
    return api_request("DELETE", f"/contacts/{contact_id}")


def contacts_list(limit: int = 20) -> dict:
    _, location_id = get_config()
    return api_request("GET", "/contacts/", params={"locationId": location_id, "limit": str(limit)})


# ─── Pipeline Operations ───

def pipelines_list() -> dict:
    _, location_id = get_config()
    return api_request("GET", "/opportunities/pipelines", params={"locationId": location_id})


# ─── Opportunity Operations ───

def opportunities_list(pipeline_id: str) -> dict:
    _, location_id = get_config()
    return api_request("GET", "/opportunities/search", params={
        "location_id": location_id, "pipeline_id": pipeline_id
    })


def opportunities_get(opp_id: str) -> dict:
    return api_request("GET", f"/opportunities/{opp_id}")


def opportunities_create(data: dict) -> dict:
    return api_request("POST", "/opportunities/", data=data)


def opportunities_update(opp_id: str, data: dict) -> dict:
    return api_request("PUT", f"/opportunities/{opp_id}", data=data)


def opportunities_delete(opp_id: str) -> dict:
    return api_request("DELETE", f"/opportunities/{opp_id}")


# ─── Conversation Operations ───

def conversations_list() -> dict:
    _, location_id = get_config()
    return api_request("GET", "/conversations/search", params={"locationId": location_id})


def conversations_get(conv_id: str) -> dict:
    return api_request("GET", f"/conversations/{conv_id}/messages")


def conversations_send_sms(contact_id: str, message: str) -> dict:
    return api_request("POST", "/conversations/messages", data={
        "type": "SMS",
        "contactId": contact_id,
        "message": message,
    })


def conversations_send_email(contact_id: str, email_data: dict) -> dict:
    payload = {
        "type": "Email",
        "contactId": contact_id,
        **email_data,
    }
    return api_request("POST", "/conversations/messages", data=payload)


# ─── Calendar Operations ───

def calendars_list() -> dict:
    _, location_id = get_config()
    return api_request("GET", "/calendars/", params={"locationId": location_id})


def calendars_slots(calendar_id: str, start_date: str, end_date: str) -> dict:
    return api_request("GET", f"/calendars/{calendar_id}/free-slots", params={
        "startDate": start_date, "endDate": end_date
    })


# ─── Appointment Operations ───

def appointments_create(data: dict) -> dict:
    return api_request("POST", "/calendars/events/appointments", data=data)


def appointments_list(calendar_id: str) -> dict:
    _, location_id = get_config()
    return api_request("GET", "/calendars/events", params={
        "locationId": location_id, "calendarId": calendar_id
    })


def appointments_update(event_id: str, data: dict) -> dict:
    return api_request("PUT", f"/calendars/events/appointments/{event_id}", data=data)


def appointments_delete(event_id: str) -> dict:
    return api_request("DELETE", f"/calendars/events/appointments/{event_id}")


# ─── Workflow Operations ───

def workflows_add_contact(workflow_id: str, contact_id: str) -> dict:
    return api_request("POST", f"/workflows/{workflow_id}/contacts", data={"contactId": contact_id})


def workflows_remove_contact(workflow_id: str, contact_id: str) -> dict:
    return api_request("DELETE", f"/workflows/{workflow_id}/contacts/{contact_id}")


# ─── CLI Router ───

def parse_args(args: list[str]):
    """Extract --key value pairs and positional args."""
    positional = []
    named = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            named[args[i][2:]] = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1
    return positional, named


def main():
    if len(sys.argv) < 3:
        print("Usage: ghl_api.py <resource> <action> [args...]")
        print("Resources: contacts, pipelines, opportunities, conversations, calendars, appointments, workflows")
        sys.exit(1)

    resource = sys.argv[1]
    action = sys.argv[2]
    rest = sys.argv[3:]
    positional, named = parse_args(rest)

    result = None

    if resource == "contacts":
        if action == "search" and positional:
            result = contacts_search(positional[0])
        elif action == "get" and positional:
            result = contacts_get(positional[0])
        elif action == "create" and positional:
            result = contacts_create(json.loads(positional[0]))
        elif action == "update" and len(positional) >= 2:
            result = contacts_update(positional[0], json.loads(positional[1]))
        elif action == "delete" and positional:
            result = contacts_delete(positional[0])
        elif action == "list":
            limit = int(named.get("limit", "20"))
            result = contacts_list(limit)
        else:
            result = {"error": f"Unknown contacts action: {action}"}

    elif resource == "pipelines":
        if action == "list":
            result = pipelines_list()
        else:
            result = {"error": f"Unknown pipelines action: {action}"}

    elif resource == "opportunities":
        if action == "list" and positional:
            result = opportunities_list(positional[0])
        elif action == "get" and positional:
            result = opportunities_get(positional[0])
        elif action == "create" and positional:
            result = opportunities_create(json.loads(positional[0]))
        elif action == "update" and len(positional) >= 2:
            result = opportunities_update(positional[0], json.loads(positional[1]))
        elif action == "delete" and positional:
            result = opportunities_delete(positional[0])
        else:
            result = {"error": f"Unknown opportunities action: {action}"}

    elif resource == "conversations":
        if action == "list":
            result = conversations_list()
        elif action == "get" and positional:
            result = conversations_get(positional[0])
        elif action == "send-sms" and len(positional) >= 2:
            result = conversations_send_sms(positional[0], positional[1])
        elif action == "send-email" and len(positional) >= 2:
            result = conversations_send_email(positional[0], json.loads(positional[1]))
        else:
            result = {"error": f"Unknown conversations action: {action}"}

    elif resource == "calendars":
        if action == "list":
            result = calendars_list()
        elif action == "slots" and positional:
            start = named.get("start", "")
            end = named.get("end", "")
            if not start or not end:
                result = {"error": "slots requires --start and --end dates (YYYY-MM-DD)"}
            else:
                result = calendars_slots(positional[0], start, end)
        else:
            result = {"error": f"Unknown calendars action: {action}"}

    elif resource == "appointments":
        if action == "create" and positional:
            result = appointments_create(json.loads(positional[0]))
        elif action == "list" and positional:
            result = appointments_list(positional[0])
        elif action == "update" and len(positional) >= 2:
            result = appointments_update(positional[0], json.loads(positional[1]))
        elif action == "delete" and positional:
            result = appointments_delete(positional[0])
        else:
            result = {"error": f"Unknown appointments action: {action}"}

    elif resource == "workflows":
        if action == "add-contact" and len(positional) >= 2:
            result = workflows_add_contact(positional[0], positional[1])
        elif action == "remove-contact" and len(positional) >= 2:
            result = workflows_remove_contact(positional[0], positional[1])
        else:
            result = {"error": f"Unknown workflows action: {action}"}

    else:
        result = {"error": f"Unknown resource: {resource}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
