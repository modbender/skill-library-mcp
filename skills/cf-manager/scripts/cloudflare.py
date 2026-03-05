#!/usr/bin/env python3
"""
Cloudflare API CLI Tool

Usage:
    python3 cloudflare.py <resource> <action> [options]

Resources: zones, dns, ssl, rules, firewall, analytics, workers
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "https://api.cloudflare.com/client/v4"


def get_token():
    """Load API token from config file."""
    token_path = Path.home() / ".config" / "cloudflare" / "token"
    if not token_path.exists():
        print(f"Error: Token not found at {token_path}", file=sys.stderr)
        print("Create it with: echo -n 'YOUR_TOKEN' > ~/.config/cloudflare/token", file=sys.stderr)
        sys.exit(1)
    return token_path.read_text().strip()


def api_request(method, endpoint, data=None, token=None):
    """Make an API request to Cloudflare."""
    if token is None:
        token = get_token()
    
    url = f"{API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            errors = error_json.get('errors', [])
            if errors:
                print(f"API Error: {errors[0].get('message', error_body)}", file=sys.stderr)
            else:
                print(f"API Error: {e.code} - {error_body}", file=sys.stderr)
        except:
            print(f"API Error: {e.code} - {error_body}", file=sys.stderr)
        sys.exit(1)


def output(data):
    """Print JSON output."""
    print(json.dumps(data, indent=2))


def get_zone_id(domain):
    """Get zone ID for a domain name."""
    result = api_request("GET", f"zones?name={domain}")
    zones = result.get("result", [])
    if not zones:
        print(f"Error: Zone not found for {domain}", file=sys.stderr)
        sys.exit(1)
    return zones[0]["id"]


# === Zone Commands ===

def zones_list(args):
    """List all zones."""
    result = api_request("GET", "zones")
    zones = result.get("result", [])
    output([{"name": z["name"], "status": z["status"], "id": z["id"], 
             "nameservers": z.get("name_servers", [])} for z in zones])


def zones_get(args):
    """Get zone details."""
    zone_id = get_zone_id(args.domain)
    result = api_request("GET", f"zones/{zone_id}")
    output(result.get("result"))


def zones_add(args):
    """Add a new zone."""
    data = {"name": args.domain, "jump_start": True}
    result = api_request("POST", "zones", data)
    zone = result.get("result", {})
    output({
        "name": zone.get("name"),
        "status": zone.get("status"),
        "nameservers": zone.get("name_servers", []),
        "id": zone.get("id")
    })
    print(f"\nUpdate nameservers at your registrar to:", file=sys.stderr)
    for ns in zone.get("name_servers", []):
        print(f"  {ns}", file=sys.stderr)


def zones_delete(args):
    """Delete a zone."""
    zone_id = get_zone_id(args.domain)
    api_request("DELETE", f"zones/{zone_id}")
    print(f"Zone {args.domain} deleted")


def zones_status(args):
    """Check zone status."""
    zone_id = get_zone_id(args.domain)
    result = api_request("GET", f"zones/{zone_id}")
    zone = result.get("result", {})
    print(f"Domain: {zone.get('name')}")
    print(f"Status: {zone.get('status')}")
    print(f"Nameservers: {', '.join(zone.get('name_servers', []))}")
    if zone.get('status') == 'pending':
        print("\nZone is pending - update nameservers at your registrar")


def zones_purge(args):
    """Purge zone cache."""
    zone_id = get_zone_id(args.domain)
    if args.urls:
        data = {"files": args.urls}
    else:
        data = {"purge_everything": True}
    api_request("POST", f"zones/{zone_id}/purge_cache", data)
    print(f"Cache purged for {args.domain}")


# === DNS Commands ===

def dns_list(args):
    """List DNS records for a zone."""
    zone_id = get_zone_id(args.domain)
    result = api_request("GET", f"zones/{zone_id}/dns_records")
    records = result.get("result", [])
    output([{
        "id": r["id"],
        "type": r["type"],
        "name": r["name"],
        "content": r["content"],
        "proxied": r.get("proxied", False),
        "ttl": r["ttl"],
        "priority": r.get("priority")
    } for r in records])


def dns_add(args):
    """Add a DNS record."""
    zone_id = get_zone_id(args.domain)
    data = {
        "type": args.type,
        "name": args.name,
        "content": args.content,
        "ttl": args.ttl if args.ttl else 1,  # 1 = auto
    }
    if args.proxied:
        data["proxied"] = True
    elif args.no_proxy:
        data["proxied"] = False
    elif args.type in ["A", "AAAA", "CNAME"]:
        data["proxied"] = False  # Default to DNS-only for safety
    
    if args.priority is not None:
        data["priority"] = args.priority
    
    result = api_request("POST", f"zones/{zone_id}/dns_records", data)
    output(result.get("result"))


def dns_update(args):
    """Update a DNS record."""
    zone_id = get_zone_id(args.domain)
    
    # Get current record
    current = api_request("GET", f"zones/{zone_id}/dns_records/{args.record_id}")
    record = current.get("result", {})
    
    data = {
        "type": record["type"],
        "name": record["name"],
        "content": args.content if args.content else record["content"],
        "ttl": args.ttl if args.ttl else record["ttl"],
    }
    if "proxied" in record:
        data["proxied"] = record["proxied"]
    if args.priority is not None:
        data["priority"] = args.priority
    elif record.get("priority"):
        data["priority"] = record["priority"]
    
    result = api_request("PUT", f"zones/{zone_id}/dns_records/{args.record_id}", data)
    output(result.get("result"))


def dns_delete(args):
    """Delete a DNS record."""
    zone_id = get_zone_id(args.domain)
    api_request("DELETE", f"zones/{zone_id}/dns_records/{args.record_id}")
    print(f"Record {args.record_id} deleted")


def dns_proxy(args):
    """Toggle proxy status for a record."""
    zone_id = get_zone_id(args.domain)
    
    # Get current record
    current = api_request("GET", f"zones/{zone_id}/dns_records/{args.record_id}")
    record = current.get("result", {})
    
    data = {
        "type": record["type"],
        "name": record["name"],
        "content": record["content"],
        "ttl": record["ttl"],
        "proxied": args.on if args.on else not args.off
    }
    
    result = api_request("PUT", f"zones/{zone_id}/dns_records/{args.record_id}", data)
    status = "proxied" if result["result"]["proxied"] else "DNS only"
    print(f"Record {args.record_id} is now {status}")


# === SSL Commands ===

def ssl_get(args):
    """Get SSL settings."""
    zone_id = get_zone_id(args.domain)
    result = api_request("GET", f"zones/{zone_id}/settings/ssl")
    output(result.get("result"))


def ssl_set(args):
    """Set SSL mode."""
    zone_id = get_zone_id(args.domain)
    data = {"value": args.mode}
    result = api_request("PATCH", f"zones/{zone_id}/settings/ssl", data)
    print(f"SSL mode set to: {result['result']['value']}")


def ssl_https(args):
    """Toggle always use HTTPS."""
    zone_id = get_zone_id(args.domain)
    value = "on" if args.on else "off"
    data = {"value": value}
    result = api_request("PATCH", f"zones/{zone_id}/settings/always_use_https", data)
    print(f"Always use HTTPS: {result['result']['value']}")


# === Firewall Commands ===

def firewall_list(args):
    """List firewall access rules."""
    zone_id = get_zone_id(args.domain)
    result = api_request("GET", f"zones/{zone_id}/firewall/access_rules/rules")
    output(result.get("result", []))


def firewall_add(args, mode):
    """Add a firewall rule."""
    zone_id = get_zone_id(args.domain)
    
    if args.ip:
        target = {"target": "ip", "value": args.ip}
    elif args.country:
        target = {"target": "country", "value": args.country}
    else:
        print("Error: Must specify --ip or --country", file=sys.stderr)
        sys.exit(1)
    
    data = {
        "mode": mode,
        "configuration": target,
        "notes": args.note or ""
    }
    result = api_request("POST", f"zones/{zone_id}/firewall/access_rules/rules", data)
    output(result.get("result"))


def firewall_block(args):
    firewall_add(args, "block")

def firewall_allow(args):
    firewall_add(args, "whitelist")

def firewall_challenge(args):
    firewall_add(args, "challenge")


# === Analytics Commands ===

def analytics(args):
    """Get zone analytics."""
    zone_id = get_zone_id(args.domain)
    params = "since=-1440"  # Last 24 hours in minutes
    if args.since:
        params = f"since={args.since}T00:00:00Z"
        if args.until:
            params += f"&until={args.until}T23:59:59Z"
    
    result = api_request("GET", f"zones/{zone_id}/analytics/dashboard?{params}")
    output(result.get("result"))


def main():
    parser = argparse.ArgumentParser(description="Cloudflare API CLI")
    subparsers = parser.add_subparsers(dest="resource", help="Resource type")
    
    # Zones
    zones_parser = subparsers.add_parser("zones", help="Manage zones")
    zones_sub = zones_parser.add_subparsers(dest="action")
    
    zones_sub.add_parser("list").set_defaults(func=zones_list)
    
    get_p = zones_sub.add_parser("get")
    get_p.add_argument("domain")
    get_p.set_defaults(func=zones_get)
    
    add_p = zones_sub.add_parser("add")
    add_p.add_argument("domain")
    add_p.set_defaults(func=zones_add)
    
    del_p = zones_sub.add_parser("delete")
    del_p.add_argument("domain")
    del_p.set_defaults(func=zones_delete)
    
    status_p = zones_sub.add_parser("status")
    status_p.add_argument("domain")
    status_p.set_defaults(func=zones_status)
    
    purge_p = zones_sub.add_parser("purge")
    purge_p.add_argument("domain")
    purge_p.add_argument("--urls", nargs="+")
    purge_p.set_defaults(func=zones_purge)
    
    # DNS
    dns_parser = subparsers.add_parser("dns", help="Manage DNS records")
    dns_sub = dns_parser.add_subparsers(dest="action")
    
    list_p = dns_sub.add_parser("list")
    list_p.add_argument("domain")
    list_p.set_defaults(func=dns_list)
    
    add_dns = dns_sub.add_parser("add")
    add_dns.add_argument("domain")
    add_dns.add_argument("--type", required=True)
    add_dns.add_argument("--name", required=True)
    add_dns.add_argument("--content", required=True)
    add_dns.add_argument("--ttl", type=int)
    add_dns.add_argument("--priority", type=int)
    add_dns.add_argument("--proxied", action="store_true")
    add_dns.add_argument("--no-proxy", action="store_true")
    add_dns.set_defaults(func=dns_add)
    
    update_dns = dns_sub.add_parser("update")
    update_dns.add_argument("domain")
    update_dns.add_argument("record_id")
    update_dns.add_argument("--content")
    update_dns.add_argument("--ttl", type=int)
    update_dns.add_argument("--priority", type=int)
    update_dns.set_defaults(func=dns_update)
    
    del_dns = dns_sub.add_parser("delete")
    del_dns.add_argument("domain")
    del_dns.add_argument("record_id")
    del_dns.set_defaults(func=dns_delete)
    
    proxy_dns = dns_sub.add_parser("proxy")
    proxy_dns.add_argument("domain")
    proxy_dns.add_argument("record_id")
    proxy_dns.add_argument("--on", action="store_true")
    proxy_dns.add_argument("--off", action="store_true")
    proxy_dns.set_defaults(func=dns_proxy)
    
    # SSL
    ssl_parser = subparsers.add_parser("ssl", help="Manage SSL settings")
    ssl_sub = ssl_parser.add_subparsers(dest="action")
    
    ssl_get_p = ssl_sub.add_parser("get")
    ssl_get_p.add_argument("domain")
    ssl_get_p.set_defaults(func=ssl_get)
    
    ssl_set_p = ssl_sub.add_parser("set")
    ssl_set_p.add_argument("domain")
    ssl_set_p.add_argument("--mode", required=True, choices=["off", "flexible", "full", "strict"])
    ssl_set_p.set_defaults(func=ssl_set)
    
    ssl_https_p = ssl_sub.add_parser("https")
    ssl_https_p.add_argument("domain")
    ssl_https_p.add_argument("--on", action="store_true")
    ssl_https_p.add_argument("--off", action="store_true")
    ssl_https_p.set_defaults(func=ssl_https)
    
    # Firewall
    fw_parser = subparsers.add_parser("firewall", help="Manage firewall rules")
    fw_sub = fw_parser.add_subparsers(dest="action")
    
    fw_list = fw_sub.add_parser("list")
    fw_list.add_argument("domain")
    fw_list.set_defaults(func=firewall_list)
    
    for action, func in [("block", firewall_block), ("allow", firewall_allow), ("challenge", firewall_challenge)]:
        p = fw_sub.add_parser(action)
        p.add_argument("domain")
        p.add_argument("--ip")
        p.add_argument("--country")
        p.add_argument("--note")
        p.set_defaults(func=func)
    
    # Analytics
    analytics_parser = subparsers.add_parser("analytics", help="Zone analytics")
    analytics_parser.add_argument("domain")
    analytics_parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    analytics_parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    analytics_parser.set_defaults(func=analytics)
    
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
