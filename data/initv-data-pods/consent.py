#!/usr/bin/env python3
"""
Consent Layer CLI — Agent access control for Data Pods

Usage:
    python3 consent.py grant --pod <pod_name> --agent <agent_id> [--expires <days>]
    python3 consent.py revoke --pod <pod_name> --agent <agent_id>
    python3 consent.py list [--agent <agent_id>] [--pod <pod_name>]
    python3 consent.py check --pod <pod_name> --agent <agent_id>
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

CONSENT_DIR = Path.home() / ".config" / "data-pods" / "consents"
CONSENT_DIR.mkdir(parents=True, exist_ok=True)
GRANTS_FILE = CONSENT_DIR / "grants.json"


def load_grants():
    if GRANTS_FILE.exists():
        with open(GRANTS_FILE) as f:
            return json.load(f)
    return {}


def save_grants(grants):
    with open(GRANTS_FILE, "w") as f:
        json.dump(grants, f, indent=2)


def grant(pod: str, agent: str, expires_days: int = None):
    grants = load_grants()
    key = f"{pod}:{agent}"
    
    expires = None
    if expires_days:
        expires = (datetime.now() + timedelta(days=expires_days)).isoformat()
    
    grants[key] = {
        "pod": pod,
        "agent": agent,
        "granted_at": datetime.now().isoformat(),
        "expires": expires,
        "active": True
    }
    
    save_grants(grants)
    print(f"✅ Granted {agent} access to {pod}" + (f" (expires {expires})" if expires else ""))


def revoke(pod: str, agent: str):
    grants = load_grants()
    key = f"{pod}:{agent}"
    
    if key in grants:
        grants[key]["active"] = False
        grants[key]["revoked_at"] = datetime.now().isoformat()
        save_grants(grants)
        print(f"❌ Revoked {agent} access to {pod}")
    else:
        print(f"No grant found for {pod}:{agent}")


def list_grants(agent: str = None, pod: str = None):
    grants = load_grants()
    
    for key, grant in grants.items():
        if agent and grant["agent"] != agent:
            continue
        if pod and grant["pod"] != pod:
            continue
        
        status = "✅ active" if grant.get("active") else "❌ revoked"
        expires = grant.get("expires", "never")
        print(f"{grant['pod']}:{grant['agent']} — {status} — expires: {expires}")


def check(pod: str, agent: str) -> bool:
    grants = load_grants()
    key = f"{pod}:{agent}"
    
    if key not in grants:
        return False
    
    grant = grants[key]
    if not grant.get("active"):
        return False
    
    # Check expiration
    if grant.get("expires"):
        expires = datetime.fromisoformat(grant["expires"])
        if datetime.now() > expires:
            return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Data Pods Consent Layer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # grant
    grant_parser = subparsers.add_parser("grant", help="Grant agent access to pod")
    grant_parser.add_argument("--pod", required=True)
    grant_parser.add_argument("--agent", required=True)
    grant_parser.add_argument("--expires", type=int, help="Days until expiration")
    
    # revoke
    revoke_parser = subparsers.add_parser("revoke", help="Revoke agent access")
    revoke_parser.add_argument("--pod", required=True)
    revoke_parser.add_argument("--agent", required=True)
    
    # list
    list_parser = subparsers.add_parser("list", help="List grants")
    list_parser.add_argument("--agent", help="Filter by agent")
    list_parser.add_argument("--pod", help="Filter by pod")
    
    # check
    check_parser = subparsers.add_parser("check", help="Check if agent has access")
    check_parser.add_argument("--pod", required=True)
    check_parser.add_argument("--agent", required=True)
    
    args = parser.parse_args()
    
    if args.command == "grant":
        grant(args.pod, args.agent, args.expires)
    elif args.command == "revoke":
        revoke(args.pod, args.agent)
    elif args.command == "list":
        list_grants(args.agent, args.pod)
    elif args.command == "check":
        result = check(args.pod, args.agent)
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
