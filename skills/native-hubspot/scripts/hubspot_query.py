#!/usr/bin/env python3
"""
HubSpot query script - calls api.hubapi.com directly.
No third-party proxy or SDK dependency.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.hubapi.com"

# Default properties to fetch per object type
DEFAULT_PROPS = {
    "contacts": ["email", "firstname", "lastname", "phone", "company", "hs_lead_status", "createdate", "lastmodifieddate"],
    "companies": ["name", "domain", "industry", "city", "country", "numberofemployees", "annualrevenue", "createdate"],
    "deals": ["dealname", "amount", "dealstage", "pipeline", "closedate", "hubspot_owner_id", "createdate"],
    "tickets": ["subject", "content", "hs_pipeline_stage", "hs_ticket_priority", "hubspot_owner_id", "createdate"],
}

TABLE_FIELDS = {
    "contacts": ["id", "email", "firstname", "lastname", "phone", "company"],
    "companies": ["id", "name", "domain", "industry", "city", "numberofemployees"],
    "deals": ["id", "dealname", "amount", "dealstage", "pipeline", "closedate"],
    "tickets": ["id", "subject", "hs_pipeline_stage", "hs_ticket_priority"],
}


def get_token():
    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        print("Error: HUBSPOT_TOKEN env var not set", file=sys.stderr)
        print("Create a private app at HubSpot → Settings → Integrations → Private Apps", file=sys.stderr)
        sys.exit(1)
    return token


def hs_request(method, path, data=None, params=None):
    token = get_token()
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = e.read().decode()
        try:
            msg = json.loads(error).get("message", error)
        except Exception:
            msg = error
        print(f"HubSpot API error {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)


def print_table(items, object_type):
    if not items:
        print("No results.")
        return

    fields = TABLE_FIELDS.get(object_type, ["id"])
    rows = []
    for item in items:
        props = item.get("properties", {})
        row = [str(item.get("id", ""))] + [str(props.get(f, "") or "") for f in fields[1:]]
        rows.append(row)

    widths = [max(len(f), max((len(r[i]) for r in rows), default=0)) for i, f in enumerate(fields)]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(f.ljust(widths[i]) for i, f in enumerate(fields)) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        print("| " + " | ".join(v[:widths[i]].ljust(widths[i]) for i, v in enumerate(row)) + " |")
    print(sep)
    print(f"\n{len(items)} results")


def cmd_list(args):
    props = DEFAULT_PROPS.get(args.object_type, [])
    params = {
        "limit": args.limit,
        "properties": ",".join(props),
    }
    result = hs_request("GET", f"/crm/v3/objects/{args.object_type}", params=params)
    items = result.get("results", [])
    print_table(items, args.object_type)
    if result.get("paging"):
        after = result["paging"].get("next", {}).get("after")
        if after:
            print(f"More results. Paginate with --after {after}")


def cmd_search(args):
    props = DEFAULT_PROPS.get(args.object_type, [])
    filters = []

    if args.email:
        filters.append({"propertyName": "email", "operator": "EQ", "value": args.email})
    elif args.query:
        # Use HubSpot's search query (searches default text fields)
        body = {
            "query": args.query,
            "limit": args.limit,
            "properties": props,
        }
        result = hs_request("POST", f"/crm/v3/objects/{args.object_type}/search", data=body)
        items = result.get("results", [])
        print_table(items, args.object_type)
        print(f"Total: {result.get('total', '?')}")
        return

    if filters:
        body = {
            "filterGroups": [{"filters": filters}],
            "limit": args.limit,
            "properties": props,
        }
        result = hs_request("POST", f"/crm/v3/objects/{args.object_type}/search", data=body)
        items = result.get("results", [])
        print_table(items, args.object_type)
        print(f"Total: {result.get('total', '?')}")
    else:
        print("Error: provide --query or --email", file=sys.stderr)
        sys.exit(1)


def cmd_get(args):
    props = DEFAULT_PROPS.get(args.object_type, [])
    params = {"properties": ",".join(props)}
    result = hs_request("GET", f"/crm/v3/objects/{args.object_type}/{args.id}", params=params)
    print(json.dumps(result, indent=2))


def cmd_create(args):
    props = {}
    # contacts
    if args.email:
        props["email"] = args.email
    if args.firstname:
        props["firstname"] = args.firstname
    if args.lastname:
        props["lastname"] = args.lastname
    if args.phone:
        props["phone"] = args.phone
    # companies
    if args.name:
        props["name"] = args.name
    if args.domain:
        props["domain"] = args.domain
    # deals
    if args.dealname:
        props["dealname"] = args.dealname
    if args.amount is not None:
        props["amount"] = str(args.amount)
    if args.pipeline:
        props["pipeline"] = args.pipeline
    if args.dealstage:
        props["dealstage"] = args.dealstage
    # tickets
    if args.subject:
        props["subject"] = args.subject

    if not props:
        print("Error: no properties provided", file=sys.stderr)
        sys.exit(1)

    result = hs_request("POST", f"/crm/v3/objects/{args.object_type}", data={"properties": props})
    print(f"Created {args.object_type[:-1]} with ID: {result['id']}")
    print(json.dumps(result, indent=2))


def cmd_update(args):
    props = {}
    if args.email:
        props["email"] = args.email
    if args.firstname:
        props["firstname"] = args.firstname
    if args.lastname:
        props["lastname"] = args.lastname
    if args.phone:
        props["phone"] = args.phone
    if args.name:
        props["name"] = args.name
    if args.dealname:
        props["dealname"] = args.dealname
    if args.dealstage:
        props["dealstage"] = args.dealstage
    if args.amount is not None:
        props["amount"] = str(args.amount)
    if args.subject:
        props["subject"] = args.subject

    if not props:
        print("Error: no fields to update", file=sys.stderr)
        sys.exit(1)

    result = hs_request("PATCH", f"/crm/v3/objects/{args.object_type}/{args.id}", data={"properties": props})
    print(f"Updated {args.object_type[:-1]} {args.id}")
    print(json.dumps(result, indent=2))


def cmd_associate(args):
    # Association type IDs: contact-company=1, contact-deal=4, company-deal=6, etc.
    ASSOC_TYPES = {
        ("contacts", "companies"): 1,
        ("contacts", "deals"): 4,
        ("contacts", "tickets"): 15,
        ("companies", "deals"): 6,
        ("companies", "contacts"): 2,
        ("deals", "contacts"): 3,
        ("deals", "companies"): 5,
        ("tickets", "contacts"): 16,
    }
    assoc_type = ASSOC_TYPES.get((args.from_type, args.to_type))
    if not assoc_type:
        print(f"Error: unsupported association {args.from_type} -> {args.to_type}", file=sys.stderr)
        sys.exit(1)

    path = f"/crm/v3/objects/{args.from_type}/{args.from_id}/associations/{args.to_type}/{args.to_id}/{assoc_type}"
    hs_request("PUT", path)
    print(f"Associated {args.from_type} {args.from_id} -> {args.to_type} {args.to_id}")


def cmd_pipelines(args):
    result = hs_request("GET", f"/crm/v3/pipelines/{args.object_type}")
    for pipeline in result.get("results", []):
        print(f"\nPipeline: {pipeline['label']} (id: {pipeline['id']})")
        print(f"  {'Stage ID':<30} {'Label':<30} {'Display Order'}")
        print(f"  {'-'*70}")
        for stage in sorted(pipeline.get("stages", []), key=lambda s: s.get("displayOrder", 0)):
            print(f"  {stage['id']:<30} {stage['label']:<30} {stage.get('displayOrder','')}")


def cmd_owners(args):
    result = hs_request("GET", "/crm/v3/owners")
    owners = result.get("results", [])
    print(f"{'ID':<15} {'Email':<35} {'Name'}")
    print("-" * 70)
    for o in owners:
        name = f"{o.get('firstName','')} {o.get('lastName','')}".strip()
        print(f"{o['id']:<15} {o.get('email',''):<35} {name}")
    print(f"\n{len(owners)} owners")


def main():
    parser = argparse.ArgumentParser(description="Query HubSpot CRM via REST API")
    sub = parser.add_subparsers(dest="command")

    # list
    list_p = sub.add_parser("list")
    list_p.add_argument("object_type", choices=["contacts", "companies", "deals", "tickets"])
    list_p.add_argument("--limit", type=int, default=20)
    list_p.add_argument("--after", help="Pagination cursor")

    # search
    search_p = sub.add_parser("search")
    search_p.add_argument("object_type", choices=["contacts", "companies", "deals", "tickets"])
    search_p.add_argument("--query", help="Full-text search")
    search_p.add_argument("--email", help="Filter by email (contacts)")
    search_p.add_argument("--limit", type=int, default=20)

    # get
    get_p = sub.add_parser("get")
    get_p.add_argument("object_type", choices=["contacts", "companies", "deals", "tickets"])
    get_p.add_argument("id")

    # create
    create_p = sub.add_parser("create")
    create_p.add_argument("object_type", choices=["contacts", "companies", "deals", "tickets"])
    create_p.add_argument("--email")
    create_p.add_argument("--firstname")
    create_p.add_argument("--lastname")
    create_p.add_argument("--phone")
    create_p.add_argument("--name")
    create_p.add_argument("--domain")
    create_p.add_argument("--dealname")
    create_p.add_argument("--amount", type=float)
    create_p.add_argument("--pipeline")
    create_p.add_argument("--dealstage")
    create_p.add_argument("--subject")

    # update
    update_p = sub.add_parser("update")
    update_p.add_argument("object_type", choices=["contacts", "companies", "deals", "tickets"])
    update_p.add_argument("id")
    update_p.add_argument("--email")
    update_p.add_argument("--firstname")
    update_p.add_argument("--lastname")
    update_p.add_argument("--phone")
    update_p.add_argument("--name")
    update_p.add_argument("--dealname")
    update_p.add_argument("--dealstage")
    update_p.add_argument("--amount", type=float)
    update_p.add_argument("--subject")

    # associate
    assoc_p = sub.add_parser("associate")
    assoc_p.add_argument("from_type")
    assoc_p.add_argument("from_id")
    assoc_p.add_argument("to_type")
    assoc_p.add_argument("to_id")

    # pipelines
    pipe_p = sub.add_parser("pipelines")
    pipe_p.add_argument("object_type", choices=["deals", "tickets"])

    # owners
    sub.add_parser("owners")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "list": cmd_list,
        "search": cmd_search,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "associate": cmd_associate,
        "pipelines": cmd_pipelines,
        "owners": cmd_owners,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
