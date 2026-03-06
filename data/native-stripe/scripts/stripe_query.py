#!/usr/bin/env python3
"""
Stripe query script - calls api.stripe.com directly.
No third-party proxy or SDK dependency.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "https://api.stripe.com/v1"

# Fields to show in table output per resource
TABLE_FIELDS = {
    "charges": ["id", "amount", "currency", "status", "description", "created"],
    "customers": ["id", "email", "name", "created", "currency"],
    "invoices": ["id", "customer", "amount_due", "currency", "status", "created"],
    "subscriptions": ["id", "customer", "status", "current_period_end", "created"],
    "payment_intents": ["id", "amount", "currency", "status", "created"],
    "refunds": ["id", "charge", "amount", "currency", "status", "created"],
    "products": ["id", "name", "active", "created"],
    "prices": ["id", "product", "unit_amount", "currency", "type", "active"],
    "balance_transactions": ["id", "amount", "currency", "type", "status", "created"],
}


def get_api_key():
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        print("Error: STRIPE_SECRET_KEY env var not set", file=sys.stderr)
        print("Get your key at https://dashboard.stripe.com/apikeys", file=sys.stderr)
        sys.exit(1)
    return key


def stripe_request(method, path, params=None, data=None):
    api_key = get_api_key()
    url = f"{BASE_URL}/{path}"

    if params:
        url += "?" + urllib.parse.urlencode(params)

    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error = json.loads(e.read())
        msg = error.get("error", {}).get("message", str(error))
        print(f"Stripe API error {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)


def format_value(key, value):
    if value is None:
        return ""
    # Convert cents to dollars for amount fields
    if key in ("amount", "amount_due", "unit_amount") and isinstance(value, int):
        return f"{value / 100:.2f}"
    # Convert unix timestamps
    if key in ("created", "current_period_end") and isinstance(value, int):
        import datetime
        return datetime.datetime.utcfromtimestamp(value).strftime("%Y-%m-%d")
    return str(value)


def print_table(items, resource):
    if not items:
        print("No results.")
        return

    fields = TABLE_FIELDS.get(resource, list(items[0].keys())[:6])
    rows = [[format_value(f, item.get(f, "")) for f in fields] for item in items]
    widths = [max(len(f), max((len(r[i]) for r in rows), default=0)) for i, f in enumerate(fields)]

    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(f.ljust(widths[i]) for i, f in enumerate(fields)) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        print("| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(row)) + " |")
    print(sep)
    print(f"\n{len(items)} results")


def cmd_list(args):
    params = {"limit": args.limit}
    if args.email:
        params["email"] = args.email
    if args.status:
        params["status"] = args.status
    if args.customer:
        params["customer"] = args.customer

    result = stripe_request("GET", args.resource, params=params)
    items = result.get("data", [])

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_table(items, args.resource)
        if result.get("has_more"):
            print(f"More results available. Use --limit to increase or paginate with --starting_after {items[-1]['id']}")


def cmd_get(args):
    result = stripe_request("GET", f"{args.resource}/{args.id}")
    print(json.dumps(result, indent=2))


def cmd_create(args):
    data = {}
    if args.resource == "refunds":
        if args.charge:
            data["charge"] = args.charge
        if args.amount:
            data["amount"] = args.amount
    result = stripe_request("POST", args.resource, data=data)
    print(json.dumps(result, indent=2))


def cmd_update(args):
    data = {}
    if args.email:
        data["email"] = args.email
    if args.name:
        data["name"] = args.name
    if not data:
        print("Error: no fields to update", file=sys.stderr)
        sys.exit(1)
    result = stripe_request("POST", f"{args.resource}/{args.id}", data=data)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Query Stripe via REST API")
    sub = parser.add_subparsers(dest="command")

    # list
    list_p = sub.add_parser("charges"); list_p.set_defaults(command="list", resource="charges")
    for r in ["customers", "invoices", "subscriptions", "payment_intents", "refunds", "products", "prices", "balance_transactions"]:
        p = sub.add_parser(r); p.set_defaults(command="list", resource=r)

    # Shared list args — add to all list parsers
    for p in [sub._name_parser_map[r] for r in TABLE_FIELDS]:
        p.add_argument("--limit", type=int, default=20)
        p.add_argument("--email", help="Filter by email (customers)")
        p.add_argument("--status", help="Filter by status")
        p.add_argument("--customer", help="Filter by customer ID")
        p.add_argument("--json", action="store_true")

    # get
    get_p = sub.add_parser("get")
    get_p.set_defaults(command="get")
    get_p.add_argument("resource")
    get_p.add_argument("id")

    # create
    create_p = sub.add_parser("create")
    create_p.set_defaults(command="create")
    create_p.add_argument("resource")
    create_p.add_argument("--charge")
    create_p.add_argument("--amount", type=int)

    # update
    update_p = sub.add_parser("update")
    update_p.set_defaults(command="update")
    update_p.add_argument("resource")
    update_p.add_argument("id")
    update_p.add_argument("--email")
    update_p.add_argument("--name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list":
        cmd_list(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "create":
        cmd_create(args)
    elif args.command == "update":
        cmd_update(args)


if __name__ == "__main__":
    main()
