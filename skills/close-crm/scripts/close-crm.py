#!/usr/bin/env python3
"""Close CRM API CLI. Zero dependencies beyond Python stdlib."""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse


def get_token():
    token = os.environ.get("CLOSE_API_KEY", "")
    if not token:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("CLOSE_API_KEY="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("Error: CLOSE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return token


import base64
API_URL = "https://api.close.com/api/v1"

def api(method, path, data=None, params=None):
    url = f"{API_URL}{path}"
    if params: url += "?" + urllib.parse.urlencode(params)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    creds = base64.b64encode(f"{get_token()}:".encode()).decode()
    req.add_header("Authorization", f"Basic {creds}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr); sys.exit(1)

def cmd_leads(a):
    d = api("GET", "/lead/", params={"_limit": a.limit})
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "display_name": x.get("display_name"), "status_label": x.get("status_label")}))

def cmd_lead_get(a): print(json.dumps(api("GET", f"/lead/{a.id}/"), indent=2))

def cmd_lead_create(a):
    d = {"name": a.name}
    if a.status: d["status"] = a.status
    contacts = []
    if a.contact_name:
        c = {"name": a.contact_name}
        if a.contact_email: c["emails"] = [{"type": "office", "email": a.contact_email}]
        contacts.append(c)
    if contacts: d["contacts"] = contacts
    print(json.dumps(api("POST", "/lead/", d), indent=2))

def cmd_contacts(a):
    d = api("GET", "/contact/", params={"_limit": a.limit})
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "name": x.get("name"), "emails": [e.get("email") for e in x.get("emails", [])]}))

def cmd_opportunities(a):
    d = api("GET", "/opportunity/", params={"_limit": a.limit})
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "lead_name": x.get("lead_name"), "value": x.get("value"), "status_type": x.get("status_type")}))

def cmd_tasks(a):
    d = api("GET", "/task/", params={"_limit": a.limit, "_is_complete": "false"})
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "text": x.get("text"), "is_complete": x.get("is_complete"), "date": x.get("date")}))

def cmd_task_create(a):
    d = {"text": a.text, "lead_id": a.lead_id}
    if a.date: d["date"] = a.date
    print(json.dumps(api("POST", "/task/", d), indent=2))

def cmd_activities(a):
    d = api("GET", "/activity/", params={"_limit": a.limit})
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "_type": x.get("_type"), "date_created": x.get("date_created")}))

def cmd_users(a):
    d = api("GET", "/user/")
    for x in d.get("data", []):
        print(json.dumps({"id": x["id"], "first_name": x.get("first_name"), "last_name": x.get("last_name"), "email": x.get("email")}))

def cmd_me(a): print(json.dumps(api("GET", "/me/"), indent=2))

def main():
    p = argparse.ArgumentParser(description="Close CRM CLI")
    s = p.add_subparsers(dest="command")
    x = s.add_parser("leads"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("lead"); x.add_argument("id")
    x = s.add_parser("lead-create"); x.add_argument("name"); x.add_argument("--status"); x.add_argument("--contact-name"); x.add_argument("--contact-email")
    x = s.add_parser("contacts"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("opportunities"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("tasks"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("task-create"); x.add_argument("text"); x.add_argument("lead_id"); x.add_argument("--date")
    x = s.add_parser("activities"); x.add_argument("--limit", type=int, default=50)
    s.add_parser("users"); s.add_parser("me")
    a = p.parse_args()
    c = {"leads":cmd_leads,"lead":cmd_lead_get,"lead-create":cmd_lead_create,"contacts":cmd_contacts,"opportunities":cmd_opportunities,"tasks":cmd_tasks,"task-create":cmd_task_create,"activities":cmd_activities,"users":cmd_users,"me":cmd_me}
    if a.command in c: c[a.command](a)
    else: p.print_help()

if __name__ == "__main__": main()
