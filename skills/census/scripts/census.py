#!/usr/bin/env python3
"""Census API CLI — US Census Bureau — population, demographics, ACS data, economic indicators, and geographic data.

Zero dependencies beyond Python stdlib.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

API_BASE = "https://api.census.gov/data"


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
    headers = {}
    url = f"{base}{path}"
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v}, doseq=True)
        url = f"{url}{'&' if '?' in url else '?'}{qs}"
    return req(method, url, data=data, headers=headers)


def out(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_acs_5yr(args):
    """ACS 5-Year estimates"""
    path = "/2022/acs/acs5"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_acs_1yr(args):
    """ACS 1-Year estimates"""
    path = "/2022/acs/acs1"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_decennial(args):
    """2020 Decennial Census"""
    path = "/2020/dec/pl"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_population(args):
    """Population estimates"""
    path = "/2022/pep/population"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_cbp(args):
    """County Business Patterns"""
    path = "/2021/cbp"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    if args.naics:
        params["naics"] = args.naics
    result = api("GET", path, params=params)
    out(result)

def cmd_poverty(args):
    """Poverty data"""
    path = "/2022/acs/acs5"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_income(args):
    """Median household income"""
    path = "/2022/acs/acs5"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_housing(args):
    """Housing data"""
    path = "/2022/acs/acs5"
    params = {}
    if args.get:
        params["get"] = args.get
    if getattr(args, 'for'):
        params["for"] = getattr(args, 'for')
    result = api("GET", path, params=params)
    out(result)

def cmd_list_datasets(args):
    """List available datasets"""
    path = ""
    params = {}
    if args.year:
        params["year"] = args.year
    result = api("GET", path, params=params)
    out(result)

def cmd_list_variables(args):
    """List ACS variables"""
    path = "/2022/acs/acs5/variables.json"
    result = api("GET", path)
    out(result)

def cmd_list_geographies(args):
    """List available geographies"""
    path = "/2022/acs/acs5/geography.json"
    result = api("GET", path)
    out(result)


def main():
    parser = argparse.ArgumentParser(description="Census API CLI")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    p_acs_5yr = sub.add_parser("acs-5yr", help="ACS 5-Year estimates")
    p_acs_5yr.add_argument("--get", default="NAME,B01003_001E")
    p_acs_5yr.add_argument("--for", default="state:*")
    p_acs_5yr.set_defaults(func=cmd_acs_5yr)

    p_acs_1yr = sub.add_parser("acs-1yr", help="ACS 1-Year estimates")
    p_acs_1yr.add_argument("--get", default="NAME,B01003_001E")
    p_acs_1yr.add_argument("--for", default="state:*")
    p_acs_1yr.set_defaults(func=cmd_acs_1yr)

    p_decennial = sub.add_parser("decennial", help="2020 Decennial Census")
    p_decennial.add_argument("--get", default="NAME,P1_001N")
    p_decennial.add_argument("--for", default="state:*")
    p_decennial.set_defaults(func=cmd_decennial)

    p_population = sub.add_parser("population", help="Population estimates")
    p_population.add_argument("--get", default="NAME,POP_2022")
    p_population.add_argument("--for", default="state:*")
    p_population.set_defaults(func=cmd_population)

    p_cbp = sub.add_parser("cbp", help="County Business Patterns")
    p_cbp.add_argument("--get", default="NAME,ESTAB,EMP")
    p_cbp.add_argument("--for", default="state:*")
    p_cbp.add_argument("--naics", default="72")
    p_cbp.set_defaults(func=cmd_cbp)

    p_poverty = sub.add_parser("poverty", help="Poverty data")
    p_poverty.add_argument("--get", default="NAME,B17001_001E,B17001_002E")
    p_poverty.add_argument("--for", default="state:*")
    p_poverty.set_defaults(func=cmd_poverty)

    p_income = sub.add_parser("income", help="Median household income")
    p_income.add_argument("--get", default="NAME,B19013_001E")
    p_income.add_argument("--for", default="state:*")
    p_income.set_defaults(func=cmd_income)

    p_housing = sub.add_parser("housing", help="Housing data")
    p_housing.add_argument("--get", default="NAME,B25001_001E,B25002_002E,B25002_003E")
    p_housing.add_argument("--for", default="state:*")
    p_housing.set_defaults(func=cmd_housing)

    p_list_datasets = sub.add_parser("list-datasets", help="List available datasets")
    p_list_datasets.add_argument("--year", default="2022")
    p_list_datasets.set_defaults(func=cmd_list_datasets)

    p_list_variables = sub.add_parser("list-variables", help="List ACS variables")
    p_list_variables.set_defaults(func=cmd_list_variables)

    p_list_geographies = sub.add_parser("list-geographies", help="List available geographies")
    p_list_geographies.set_defaults(func=cmd_list_geographies)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
