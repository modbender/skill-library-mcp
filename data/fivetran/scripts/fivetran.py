#!/usr/bin/env python3
"""Fivetran CLI — Fivetran — manage connectors, destinations, sync status, and groups via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.fivetran.com/v1"

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
    import base64
    key = get_env("FIVETRAN_API_KEY")
    secret = get_env("FIVETRAN_API_SECRET") if "FIVETRAN_API_SECRET" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



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


def cmd_connectors(args):
    """List connectors."""
    path = f"/groups/{args.group_id}/connectors"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_connector_get(args):
    """Get connector."""
    path = f"/connectors/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_connector_create(args):
    """Create connector."""
    path = "/connectors"
    body = {}
    if getattr(args, "service", None): body["service"] = try_json(args.service)
    if getattr(args, "group_id", None): body["group_id"] = try_json(args.group_id)
    if getattr(args, "config", None): body["config"] = try_json(args.config)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_connector_update(args):
    """Update connector."""
    path = f"/connectors/{args.id}"
    body = {}
    if getattr(args, "paused", None): body["paused"] = try_json(args.paused)
    data = req("PATCH", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_connector_delete(args):
    """Delete connector."""
    path = f"/connectors/{args.id}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_connector_sync(args):
    """Trigger sync."""
    path = f"/connectors/{args.id}/force"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_connector_schema(args):
    """Get schema."""
    path = f"/connectors/{args.id}/schemas"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_destinations(args):
    """List destinations."""
    path = "/destinations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_destination_get(args):
    """Get destination."""
    path = f"/destinations/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_groups(args):
    """List groups."""
    path = "/groups"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_group_get(args):
    """Get group."""
    path = f"/groups/{args.id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_group_create(args):
    """Create group."""
    path = "/groups"
    body = {}
    if getattr(args, "name", None): body["name"] = try_json(args.name)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_users(args):
    """List users."""
    path = "/users"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_metadata_connectors(args):
    """List connector types."""
    path = "/metadata/connectors"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_webhooks(args):
    """List webhooks."""
    path = "/webhooks"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Fivetran CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    connectors_p = sub.add_parser("connectors", help="List connectors")
    connectors_p.add_argument("group_id", help="Group ID")
    connectors_p.set_defaults(func=cmd_connectors)

    connector_get_p = sub.add_parser("connector-get", help="Get connector")
    connector_get_p.add_argument("id", help="Connector ID")
    connector_get_p.set_defaults(func=cmd_connector_get)

    connector_create_p = sub.add_parser("connector-create", help="Create connector")
    connector_create_p.add_argument("--service", help="Service type", default=None)
    connector_create_p.add_argument("--group_id", help="Group ID", default=None)
    connector_create_p.add_argument("--config", help="JSON config", default=None)
    connector_create_p.set_defaults(func=cmd_connector_create)

    connector_update_p = sub.add_parser("connector-update", help="Update connector")
    connector_update_p.add_argument("id", help="ID")
    connector_update_p.add_argument("--paused", help="true/false", default=None)
    connector_update_p.set_defaults(func=cmd_connector_update)

    connector_delete_p = sub.add_parser("connector-delete", help="Delete connector")
    connector_delete_p.add_argument("id", help="ID")
    connector_delete_p.set_defaults(func=cmd_connector_delete)

    connector_sync_p = sub.add_parser("connector-sync", help="Trigger sync")
    connector_sync_p.add_argument("id", help="Connector ID")
    connector_sync_p.set_defaults(func=cmd_connector_sync)

    connector_schema_p = sub.add_parser("connector-schema", help="Get schema")
    connector_schema_p.add_argument("id", help="Connector ID")
    connector_schema_p.set_defaults(func=cmd_connector_schema)

    destinations_p = sub.add_parser("destinations", help="List destinations")
    destinations_p.set_defaults(func=cmd_destinations)

    destination_get_p = sub.add_parser("destination-get", help="Get destination")
    destination_get_p.add_argument("id", help="Destination ID")
    destination_get_p.set_defaults(func=cmd_destination_get)

    groups_p = sub.add_parser("groups", help="List groups")
    groups_p.set_defaults(func=cmd_groups)

    group_get_p = sub.add_parser("group-get", help="Get group")
    group_get_p.add_argument("id", help="Group ID")
    group_get_p.set_defaults(func=cmd_group_get)

    group_create_p = sub.add_parser("group-create", help="Create group")
    group_create_p.add_argument("--name", help="Name", default=None)
    group_create_p.set_defaults(func=cmd_group_create)

    users_p = sub.add_parser("users", help="List users")
    users_p.set_defaults(func=cmd_users)

    metadata_connectors_p = sub.add_parser("metadata-connectors", help="List connector types")
    metadata_connectors_p.set_defaults(func=cmd_metadata_connectors)

    webhooks_p = sub.add_parser("webhooks", help="List webhooks")
    webhooks_p.set_defaults(func=cmd_webhooks)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
