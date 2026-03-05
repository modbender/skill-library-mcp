#!/usr/bin/env python3
"""FamilySearch API helper — search, fetch persons, ancestry, descendants."""

import argparse
import json
import subprocess
import sys
import urllib.parse
import urllib.request

def get_token():
    """Retrieve FamilySearch access token. Checks (in order):
    1. --token CLI arg (via FAMILYSEARCH_TOKEN_ARG, set by caller)
    2. FAMILYSEARCH_TOKEN environment variable
    3. macOS Keychain (if 'security' binary available)
    """
    import os, shutil

    # 1. Environment variable (works on all platforms)
    token = os.environ.get("FAMILYSEARCH_TOKEN")
    if token:
        return token.strip()

    # 2. macOS Keychain fallback
    if shutil.which("security"):
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-a", "familysearch-token",
                 "-s", "openclaw-familysearch-token", "-w"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

    print("ERROR: No FamilySearch token found.", file=sys.stderr)
    print("Options:", file=sys.stderr)
    print("  1. Set FAMILYSEARCH_TOKEN environment variable", file=sys.stderr)
    print("  2. (macOS) security add-generic-password -a familysearch-token -s openclaw-familysearch-token -w <TOKEN>", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.familysearch.org"

def api_get(path, token, accept="application/x-gedcomx-v1+json"):
    """Make authenticated GET request to FamilySearch API."""
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": accept,
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("Token expired. Re-authenticate and update Keychain.", file=sys.stderr)
        sys.exit(1)

def search_persons(query_parts, token):
    """Search for persons in the Family Tree."""
    q = "+".join(f"{k}:{v}" for k, v in query_parts.items() if v)
    data = api_get(f"/platform/tree/search?q={urllib.parse.quote(q)}", token,
                   accept="application/x-gedcomx-atom+json")
    entries = data.get("entries", [])
    results = []
    for entry in entries:
        content = entry.get("content", {})
        persons = content.get("gedcomx", {}).get("persons", [])
        for p in persons:
            d = p.get("display", {})
            results.append({
                "id": p.get("id"),
                "name": d.get("name"),
                "birthDate": d.get("birthDate"),
                "birthPlace": d.get("birthPlace"),
                "deathDate": d.get("deathDate"),
                "deathPlace": d.get("deathPlace"),
                "gender": d.get("gender"),
            })
    return results

def get_person(pid, token):
    """Get details for a specific person."""
    return api_get(f"/platform/tree/persons/{pid}", token)

def get_ancestry(pid, generations, token):
    """Get ascending pedigree."""
    return api_get(f"/platform/tree/ancestry?person={pid}&generations={generations}", token)

def get_descendants(pid, generations, token):
    """Get descending tree."""
    return api_get(f"/platform/tree/descendancy?person={pid}&generations={generations}", token)

def get_parents(pid, token):
    return api_get(f"/platform/tree/persons/{pid}/parents", token)

def get_spouses(pid, token):
    return api_get(f"/platform/tree/persons/{pid}/spouses", token)

def get_children(pid, token):
    return api_get(f"/platform/tree/persons/{pid}/children", token)

def main():
    parser = argparse.ArgumentParser(description="FamilySearch API helper")
    sub = parser.add_subparsers(dest="command", required=True)

    # Search
    s = sub.add_parser("search", help="Search for persons")
    s.add_argument("--given", help="Given name")
    s.add_argument("--surname", help="Surname")
    s.add_argument("--birth-date", help="Birth date")
    s.add_argument("--birth-place", help="Birth place")
    s.add_argument("--death-date", help="Death date")
    s.add_argument("--death-place", help="Death place")
    s.add_argument("--sex", help="Sex (Male/Female)")

    # Person
    p = sub.add_parser("person", help="Get person details")
    p.add_argument("pid", help="Person ID")

    # Ancestry
    a = sub.add_parser("ancestry", help="Get pedigree")
    a.add_argument("pid", help="Person ID")
    a.add_argument("--generations", type=int, default=4, help="Number of generations (1-8)")

    # Descendants
    d = sub.add_parser("descendants", help="Get descendants")
    d.add_argument("pid", help="Person ID")
    d.add_argument("--generations", type=int, default=2, help="Number of generations")

    # Parents/Spouses/Children
    for cmd in ["parents", "spouses", "children"]:
        c = sub.add_parser(cmd, help=f"Get {cmd}")
        c.add_argument("pid", help="Person ID")

    args = parser.parse_args()
    token = get_token()

    if args.command == "search":
        query = {
            "givenName": args.given,
            "surname": args.surname,
            "birthDate": args.birth_date,
            "birthPlace": args.birth_place,
            "deathDate": args.death_date,
            "deathPlace": args.death_place,
            "sex": args.sex,
        }
        results = search_persons(query, token)
        print(json.dumps(results, indent=2))

    elif args.command == "person":
        print(json.dumps(get_person(args.pid, token), indent=2))

    elif args.command == "ancestry":
        print(json.dumps(get_ancestry(args.pid, args.generations, token), indent=2))

    elif args.command == "descendants":
        print(json.dumps(get_descendants(args.pid, args.generations, token), indent=2))

    elif args.command in ("parents", "spouses", "children"):
        fn = {"parents": get_parents, "spouses": get_spouses, "children": get_children}[args.command]
        print(json.dumps(fn(args.pid, token), indent=2))

if __name__ == "__main__":
    main()
