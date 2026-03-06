#!/usr/bin/env python3
"""Healthie CLI — Healthie — manage patients, appointments, goals, and documents via GraphQL API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.gethealthie.com/graphql"

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
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    token = get_env("HEALTHIE_API_KEY")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    pass
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_patients(args):
    """List patients."""
    path = "/users"
    params = {}
    if getattr(args, "offset", None): params["offset"] = args.offset
    if getattr(args, "keywords", None): params["keywords"] = args.keywords
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_patient_get(args):
    """Get patient."""
    path = f"/users/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_patient_create(args):
    """Create patient."""
    path = "/users"
    body = {}
    if getattr(args, "first_name", None): body["first_name"] = try_json(args.first_name)
    if getattr(args, "last_name", None): body["last_name"] = try_json(args.last_name)
    if getattr(args, "email", None): body["email"] = try_json(args.email)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_appointments(args):
    """List appointments."""
    path = "/appointments"
    params = {}
    if getattr(args, "provider_id", None): params["provider_id"] = args.provider_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_appointment_get(args):
    """Get appointment."""
    path = f"/appointments/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_appointment_create(args):
    """Create appointment."""
    path = "/appointments"
    body = {}
    if getattr(args, "patient_id", None): body["patient_id"] = try_json(args.patient_id)
    if getattr(args, "provider_id", None): body["provider_id"] = try_json(args.provider_id)
    if getattr(args, "datetime", None): body["datetime"] = try_json(args.datetime)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_appointment_delete(args):
    """Delete appointment."""
    path = f"/appointments/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_appointment_types(args):
    """List appointment types."""
    path = "/appointment_types"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_providers(args):
    """List providers."""
    path = "/providers"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_goals(args):
    """List goals."""
    path = "/goals"
    params = {}
    if getattr(args, "patient_id", None): params["patient_id"] = args.patient_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_goal_create(args):
    """Create goal."""
    path = "/goals"
    body = {}
    if getattr(args, "patient_id", None): body["patient_id"] = try_json(args.patient_id)
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_documents(args):
    """List documents."""
    path = "/documents"
    params = {}
    if getattr(args, "patient_id", None): params["patient_id"] = args.patient_id
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_forms(args):
    """List forms."""
    path = "/custom_modules"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_tags(args):
    """List tags."""
    path = "/tags"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Healthie CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    patients_p = sub.add_parser("patients", help="List patients")
    patients_p.add_argument("--offset", help="Offset", default=None)
    patients_p.add_argument("--keywords", help="Search", default=None)
    patients_p.set_defaults(func=cmd_patients)

    patient_get_p = sub.add_parser("patient-get", help="Get patient")
    patient_get_p.add_argument("id", help="Patient ID")
    patient_get_p.set_defaults(func=cmd_patient_get)

    patient_create_p = sub.add_parser("patient-create", help="Create patient")
    patient_create_p.add_argument("--first_name", help="First name", default=None)
    patient_create_p.add_argument("--last_name", help="Last name", default=None)
    patient_create_p.add_argument("--email", help="Email", default=None)
    patient_create_p.set_defaults(func=cmd_patient_create)

    appointments_p = sub.add_parser("appointments", help="List appointments")
    appointments_p.add_argument("--provider_id", help="Provider ID", default=None)
    appointments_p.set_defaults(func=cmd_appointments)

    appointment_get_p = sub.add_parser("appointment-get", help="Get appointment")
    appointment_get_p.add_argument("id", help="Appointment ID")
    appointment_get_p.set_defaults(func=cmd_appointment_get)

    appointment_create_p = sub.add_parser("appointment-create", help="Create appointment")
    appointment_create_p.add_argument("--patient_id", help="Patient ID", default=None)
    appointment_create_p.add_argument("--provider_id", help="Provider ID", default=None)
    appointment_create_p.add_argument("--datetime", help="ISO datetime", default=None)
    appointment_create_p.set_defaults(func=cmd_appointment_create)

    appointment_delete_p = sub.add_parser("appointment-delete", help="Delete appointment")
    appointment_delete_p.add_argument("id", help="Appointment ID")
    appointment_delete_p.set_defaults(func=cmd_appointment_delete)

    appointment_types_p = sub.add_parser("appointment-types", help="List appointment types")
    appointment_types_p.set_defaults(func=cmd_appointment_types)

    providers_p = sub.add_parser("providers", help="List providers")
    providers_p.set_defaults(func=cmd_providers)

    goals_p = sub.add_parser("goals", help="List goals")
    goals_p.add_argument("--patient_id", help="Patient ID", default=None)
    goals_p.set_defaults(func=cmd_goals)

    goal_create_p = sub.add_parser("goal-create", help="Create goal")
    goal_create_p.add_argument("--patient_id", help="Patient ID", default=None)
    goal_create_p.add_argument("--name", help="Goal name", default=None)
    goal_create_p.set_defaults(func=cmd_goal_create)

    documents_p = sub.add_parser("documents", help="List documents")
    documents_p.add_argument("--patient_id", help="Patient ID", default=None)
    documents_p.set_defaults(func=cmd_documents)

    forms_p = sub.add_parser("forms", help="List forms")
    forms_p.set_defaults(func=cmd_forms)

    tags_p = sub.add_parser("tags", help="List tags")
    tags_p.set_defaults(func=cmd_tags)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
