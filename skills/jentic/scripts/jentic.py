#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
# SECURITY MANIFEST:
# Environment variables accessed: JENTIC_AGENT_API_KEY (optional, falls back to openclaw config)
# External endpoints called: https://api-gw.main.us-east-1.jenticprod.net/ (only)
# Local files read: ~/.openclaw/openclaw.json (to retrieve API key if env var not set)
# Local files written: none
"""
jentic.py — Jentic API client. Search → Load → Execute API operations and workflows.

API key read from JENTIC_AGENT_API_KEY env var or openclaw config.
Base URL: https://api-gw.main.us-east-1.jenticprod.net/api/v1/

Usage:
  uv run scripts/jentic.py search "get top news stories" [--limit 5] [--json]
  uv run scripts/jentic.py load op_ad385f1f20e34e5b [op_... ...]
  uv run scripts/jentic.py execute op_7ae5ecc5d29bed24 [--inputs '{"category":"general"}']
  uv run scripts/jentic.py execute wf_... --inputs '{"param":"value"}'
  uv run scripts/jentic.py apis
  uv run scripts/jentic.py pub-search "home automation" [--limit 5]  # no auth needed
"""

import argparse
import json
import os
import sys
import requests

BASE_URL = "https://api-gw.main.us-east-1.jenticprod.net/api/v1"


def get_key():
    key = os.environ.get("JENTIC_AGENT_API_KEY")
    if not key:
        # Try openclaw config
        try:
            cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
            with open(cfg_path) as f:
                cfg = json.load(f)
            key = cfg["skills"]["entries"]["jentic"]["apiKey"]
        except Exception:
            pass
    if not key:
        print("ERROR: No Jentic API key. Set JENTIC_AGENT_API_KEY or store in openclaw config.", file=sys.stderr)
        sys.exit(1)
    return key


def auth_headers(key):
    return {
        "X-JENTIC-API-KEY": key,
        "Content-Type": "application/json",
    }


def cmd_apis(args):
    key = get_key()
    r = requests.get(f"{BASE_URL}/agents/apis", headers=auth_headers(key), timeout=15)
    r.raise_for_status()
    apis = r.json()
    if args.json:
        print(json.dumps(apis, indent=2))
        return
    print(f"Scoped APIs ({len(apis)}):")
    for a in apis:
        print(f"  {a['api_vendor']}/{a['api_name']}  v{a.get('api_version', '?')}")


def cmd_search(args):
    key = get_key()
    payload = {"query": args.query, "limit": args.limit}
    r = requests.post(f"{BASE_URL}/agents/search", headers=auth_headers(key),
                      json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if args.json:
        print(json.dumps(data, indent=2))
        return
    results = data.get("results", [])
    print(f"Results for '{args.query}' ({len(results)} of {data.get('total_count', '?')}):")
    for r in results:
        etype = r.get("entity_type", "?")
        score = r.get("distance", r.get("match_score", "?"))
        name = r.get("summary") or r.get("name") or r.get("workflow_id", "")
        path = r.get("path", "")
        print(f"  [{r['id']}] {r.get('api_name','')} — {name}")
        if path:
            print(f"    {r.get('method','')} {path}  ({etype}, score: {score:.3f})")
        else:
            print(f"    {etype}  score: {score:.3f}")


def cmd_pub_search(args):
    """Search the public catalog without auth."""
    payload = {"query": args.query, "limit": args.limit}
    r = requests.post(f"{BASE_URL}/search/all", headers={"Content-Type": "application/json"},
                      json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if args.json:
        print(json.dumps(data, indent=2))
        return
    all_results = data.get("operations", []) + data.get("workflows", []) + data.get("apis", [])
    all_results.sort(key=lambda x: x.get("distance", 1))
    print(f"Public catalog results for '{args.query}' ({len(all_results)}):")
    for r in all_results:
        etype = r.get("entity_type", "?")
        score = r.get("distance", "?")
        name = r.get("summary") or r.get("name") or r.get("api_name", "")
        path = r.get("path", "")
        print(f"  [{r['id']}] {r.get('api_name','')} — {name}")
        if path:
            print(f"    {r.get('method','')} {path}  ({etype}, score: {score:.3f})")


def cmd_load(args):
    key = get_key()
    op_uuids = [i for i in args.ids if i.startswith("op_")]
    wf_uuids = [i for i in args.ids if i.startswith("wf_")]
    params = {}
    if op_uuids:
        params["operation_uuids"] = ",".join(op_uuids)
    if wf_uuids:
        params["workflow_uuids"] = ",".join(wf_uuids)
    r = requests.get(f"{BASE_URL}/files", headers=auth_headers(key),
                     params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if args.json:
        print(json.dumps(data, indent=2))
        return
    ops = data.get("operations", {})
    wfs = data.get("workflows", {})
    for uid, op in ops.items():
        print(f"Operation: {uid}")
        print(f"  {op.get('method')} {op.get('path')}  [{op.get('api_name')}]")
        print(f"  Summary: {op.get('summary')}")
        sec = op.get("security_requirements")
        print(f"  Auth: {sec if sec else 'none'}")
        inputs = op.get("inputs")
        if inputs:
            print(f"  Inputs: {json.dumps(inputs, indent=4)[:600]}")
    for uid, wf in wfs.items():
        print(f"Workflow: {uid}")
        print(f"  Name: {wf.get('name')}")
        inputs = wf.get("inputs")
        if inputs:
            print(f"  Inputs: {json.dumps(inputs, indent=4)[:600]}")


def cmd_execute(args):
    key = get_key()
    etype = "operation" if args.id.startswith("op_") else "workflow"
    inputs = {}
    if args.inputs:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON for --inputs: {e}", file=sys.stderr)
            sys.exit(1)
    payload = {"execution_type": etype, "uuid": args.id, "inputs": inputs}
    r = requests.post(f"{BASE_URL}/agents/execute", headers=auth_headers(key),
                      json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    if args.json:
        print(json.dumps(data, indent=2))
        return
    success = data.get("success")
    status = data.get("status_code")
    error = data.get("error")
    output = data.get("output")
    print(f"Success: {success}  Status: {status}")
    if error:
        print(f"Error: {error}")
    if output is not None:
        out_str = json.dumps(output, indent=2) if isinstance(output, (dict, list)) else str(output)
        print(f"Output:\n{out_str}")


def main():
    parser = argparse.ArgumentParser(description="Jentic API client")
    parser.add_argument("--json", action="store_true", help="Raw JSON output")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # apis
    sub.add_parser("apis", help="List scoped APIs for this agent")

    # search
    p_s = sub.add_parser("search", help="Semantic search (agent-scoped)")
    p_s.add_argument("query", help="Natural language query")
    p_s.add_argument("--limit", type=int, default=5)

    # pub-search
    p_ps = sub.add_parser("pub-search", help="Search public catalog (no auth)")
    p_ps.add_argument("query", help="Natural language query")
    p_ps.add_argument("--limit", type=int, default=5)

    # load
    p_l = sub.add_parser("load", help="Load operation/workflow details by UUID")
    p_l.add_argument("ids", nargs="+", help="op_... or wf_... UUIDs")

    # execute
    p_e = sub.add_parser("execute", help="Execute an operation or workflow")
    p_e.add_argument("id", help="op_... or wf_... UUID")
    p_e.add_argument("--inputs", help='JSON inputs e.g. \'{"key":"value"}\'')

    args = parser.parse_args()

    cmd_map = {
        "apis": cmd_apis,
        "search": cmd_search,
        "pub-search": cmd_pub_search,
        "load": cmd_load,
        "execute": cmd_execute,
    }
    # Pass --json flag down
    for sub_parser in [p_s, p_ps, p_l, p_e]:
        pass  # already inherited via parent namespace

    cmd_map[args.cmd](args)


if __name__ == "__main__":
    main()
