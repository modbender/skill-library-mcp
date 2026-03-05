#!/usr/bin/env python3
"""Clearbit CLI — Clearbit — person enrichment, company enrichment, prospecting, and reveal (identify website visitors).

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://person.clearbit.com"


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
    import base64
    token = get_env("CLEARBIT_API_KEY")
    if not token:
        print("Error: CLEARBIT_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    auth = base64.b64encode(f"{token}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_enrich_person(args):
    """Enrich person by email"""
    path = "/v2/people/find?email={email}"
    path = path.replace("{email}", str(args.email or ""))
    result = api("GET", path)
    out(result)

def cmd_enrich_company(args):
    """Enrich company by domain"""
    path = "/v2/companies/find?domain={domain}"
    path = path.replace("{domain}", str(args.domain or ""))
    result = api("GET", path)
    out(result)

def cmd_combined_lookup(args):
    """Combined person + company lookup"""
    path = "/v2/combined/find?email={email}"
    path = path.replace("{email}", str(args.email or ""))
    result = api("GET", path)
    out(result)

def cmd_prospect(args):
    """Prospect/search for leads"""
    path = "/v1/people/search"
    data = {}
    if args.query:
        data["query"] = args.query
    result = api("POST", path, data=data)
    out(result)

def cmd_reveal(args):
    """Reveal company by IP address"""
    path = "/v1/companies/find?ip={ip}"
    path = path.replace("{ip}", str(args.ip or ""))
    result = api("GET", path)
    out(result)

def cmd_name_to_domain(args):
    """Find company domain by name"""
    path = "/v1/companies/find?name={name}"
    path = path.replace("{name}", str(args.name or ""))
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Clearbit CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_enrich_person = sub.add_parser("enrich-person", help="Enrich person by email")
    p_enrich_person.add_argument("--email", required=True)
    p_enrich_person.set_defaults(func=cmd_enrich_person)

    p_enrich_company = sub.add_parser("enrich-company", help="Enrich company by domain")
    p_enrich_company.add_argument("--domain", required=True)
    p_enrich_company.set_defaults(func=cmd_enrich_company)

    p_combined_lookup = sub.add_parser("combined-lookup", help="Combined person + company lookup")
    p_combined_lookup.add_argument("--email", required=True)
    p_combined_lookup.set_defaults(func=cmd_combined_lookup)

    p_prospect = sub.add_parser("prospect", help="Prospect/search for leads")
    p_prospect.add_argument("--query", default="JSON filter object")
    p_prospect.set_defaults(func=cmd_prospect)

    p_reveal = sub.add_parser("reveal", help="Reveal company by IP address")
    p_reveal.add_argument("--ip", required=True)
    p_reveal.set_defaults(func=cmd_reveal)

    p_name_to_domain = sub.add_parser("name-to-domain", help="Find company domain by name")
    p_name_to_domain.add_argument("--name", required=True)
    p_name_to_domain.set_defaults(func=cmd_name_to_domain)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
