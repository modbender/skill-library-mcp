#!/usr/bin/env python3
"""
DigitalOcean API CLI Tool

Usage:
    python3 digitalocean.py <resource> <action> [options]

Resources: droplets, dns, firewalls, databases, account, billing, ssh-keys, images, regions, sizes, spaces
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

API_BASE = "https://api.digitalocean.com/v2"


def get_token():
    """Load API token from config file."""
    token_path = Path.home() / ".config" / "digitalocean" / "token"
    if not token_path.exists():
        print(f"Error: Token not found at {token_path}", file=sys.stderr)
        print("Create it with: echo -n 'YOUR_TOKEN' > ~/.config/digitalocean/token", file=sys.stderr)
        sys.exit(1)
    return token_path.read_text().strip()


def api_request(method, endpoint, data=None, token=None):
    """Make an API request to DigitalOcean."""
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
            if resp.status == 204:
                return None
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            print(f"API Error: {e.code} - {error_json.get('message', error_body)}", file=sys.stderr)
        except:
            print(f"API Error: {e.code} - {error_body}", file=sys.stderr)
        sys.exit(1)


def output(data):
    """Print JSON output."""
    print(json.dumps(data, indent=2))


# === Droplet Commands ===

def droplets_list(args):
    """List all droplets."""
    result = api_request("GET", "droplets")
    output(result.get("droplets", []))


def droplets_get(args):
    """Get droplet details."""
    result = api_request("GET", f"droplets/{args.droplet_id}")
    output(result.get("droplet"))


def droplets_create(args):
    """Create a new droplet."""
    data = {
        "name": args.name,
        "region": args.region,
        "size": args.size,
        "image": args.image,
    }
    if args.ssh_keys:
        data["ssh_keys"] = args.ssh_keys.split(",")
    if args.tags:
        data["tags"] = args.tags.split(",")
    if args.user_data:
        data["user_data"] = args.user_data
    
    result = api_request("POST", "droplets", data)
    output(result.get("droplet"))


def droplets_destroy(args):
    """Destroy a droplet."""
    api_request("DELETE", f"droplets/{args.droplet_id}")
    print(f"Droplet {args.droplet_id} destroyed")


def droplets_action(args, action_type):
    """Perform a droplet action."""
    data = {"type": action_type}
    if hasattr(args, 'size') and args.size:
        data["size"] = args.size
    if hasattr(args, 'name') and args.name:
        data["name"] = args.name
    
    result = api_request("POST", f"droplets/{args.droplet_id}/actions", data)
    output(result.get("action"))


def droplets_power_on(args):
    droplets_action(args, "power_on")

def droplets_power_off(args):
    droplets_action(args, "power_off")

def droplets_reboot(args):
    droplets_action(args, "reboot")

def droplets_resize(args):
    droplets_action(args, "resize")

def droplets_snapshot(args):
    droplets_action(args, "snapshot")


# === DNS Commands ===

def dns_list(args):
    """List all domains."""
    result = api_request("GET", "domains")
    output(result.get("domains", []))


def dns_records(args):
    """List records for a domain."""
    result = api_request("GET", f"domains/{args.domain}/records")
    output(result.get("domain_records", []))


def dns_add(args):
    """Add a DNS record."""
    data = {
        "type": args.type,
        "name": args.name,
        "data": args.data,
        "ttl": args.ttl,
    }
    if args.priority is not None:
        data["priority"] = args.priority
    if args.port is not None:
        data["port"] = args.port
    if args.weight is not None:
        data["weight"] = args.weight
    
    result = api_request("POST", f"domains/{args.domain}/records", data)
    output(result.get("domain_record"))


def dns_update(args):
    """Update a DNS record."""
    data = {}
    if args.data:
        data["data"] = args.data
    if args.name:
        data["name"] = args.name
    if args.ttl:
        data["ttl"] = args.ttl
    if args.priority is not None:
        data["priority"] = args.priority
    
    result = api_request("PUT", f"domains/{args.domain}/records/{args.record_id}", data)
    output(result.get("domain_record"))


def dns_delete(args):
    """Delete a DNS record."""
    api_request("DELETE", f"domains/{args.domain}/records/{args.record_id}")
    print(f"Record {args.record_id} deleted from {args.domain}")


def dns_create(args):
    """Create a new domain."""
    data = {"name": args.domain}
    if args.ip:
        data["ip_address"] = args.ip
    result = api_request("POST", "domains", data)
    output(result.get("domain"))


# === Firewall Commands ===

def firewalls_list(args):
    """List all firewalls."""
    result = api_request("GET", "firewalls")
    output(result.get("firewalls", []))


def firewalls_get(args):
    """Get firewall details."""
    result = api_request("GET", f"firewalls/{args.firewall_id}")
    output(result.get("firewall"))


def firewalls_create(args):
    """Create a firewall."""
    inbound_rules = []
    outbound_rules = []
    
    if args.inbound:
        for rule in args.inbound:
            parts = rule.split(":")
            protocol = parts[0]
            ports = parts[1] if len(parts) > 1 else "all"
            sources = parts[2] if len(parts) > 2 else "0.0.0.0/0,::/0"
            
            inbound_rules.append({
                "protocol": protocol,
                "ports": ports,
                "sources": {"addresses": sources.split(",")}
            })
    
    # Default outbound: allow all
    outbound_rules = [
        {"protocol": "tcp", "ports": "all", "destinations": {"addresses": ["0.0.0.0/0", "::/0"]}},
        {"protocol": "udp", "ports": "all", "destinations": {"addresses": ["0.0.0.0/0", "::/0"]}},
        {"protocol": "icmp", "destinations": {"addresses": ["0.0.0.0/0", "::/0"]}},
    ]
    
    data = {
        "name": args.name,
        "inbound_rules": inbound_rules,
        "outbound_rules": outbound_rules,
    }
    
    result = api_request("POST", "firewalls", data)
    output(result.get("firewall"))


def firewalls_add_droplet(args):
    """Add a droplet to a firewall."""
    data = {"droplet_ids": [int(args.droplet_id)]}
    api_request("POST", f"firewalls/{args.firewall_id}/droplets", data)
    print(f"Droplet {args.droplet_id} added to firewall {args.firewall_id}")


# === Database Commands ===

def databases_list(args):
    """List database clusters."""
    result = api_request("GET", "databases")
    output(result.get("databases", []))


def databases_get(args):
    """Get database cluster details."""
    result = api_request("GET", f"databases/{args.db_id}")
    output(result.get("database"))


# === Account Commands ===

def account_info(args):
    """Get account information."""
    result = api_request("GET", "account")
    output(result.get("account"))


# === Billing Commands ===

def billing_balance(args):
    """Get account balance."""
    result = api_request("GET", "customers/my/balance")
    output(result)


def billing_history(args):
    """Get billing history."""
    result = api_request("GET", "customers/my/billing_history")
    output(result.get("billing_history", []))


# === SSH Key Commands ===

def ssh_keys_list(args):
    """List SSH keys."""
    result = api_request("GET", "account/keys")
    output(result.get("ssh_keys", []))


def ssh_keys_add(args):
    """Add an SSH key."""
    data = {
        "name": args.name,
        "public_key": args.key,
    }
    result = api_request("POST", "account/keys", data)
    output(result.get("ssh_key"))


# === Image Commands ===

def images_list(args):
    """List available images."""
    result = api_request("GET", "images?type=distribution")
    output(result.get("images", []))


def images_snapshots(args):
    """List your snapshots."""
    result = api_request("GET", "images?private=true")
    output(result.get("images", []))


def images_delete(args):
    """Delete an image/snapshot."""
    api_request("DELETE", f"images/{args.image_id}")
    print(f"Image {args.image_id} deleted")


# === Region/Size Commands ===

def regions_list(args):
    """List available regions."""
    result = api_request("GET", "regions")
    output(result.get("regions", []))


def sizes_list(args):
    """List available droplet sizes."""
    result = api_request("GET", "sizes")
    output(result.get("sizes", []))


def main():
    parser = argparse.ArgumentParser(description="DigitalOcean API CLI")
    subparsers = parser.add_subparsers(dest="resource", help="Resource type")
    
    # Droplets
    droplets_parser = subparsers.add_parser("droplets", help="Manage droplets")
    droplets_sub = droplets_parser.add_subparsers(dest="action")
    
    droplets_sub.add_parser("list", help="List droplets").set_defaults(func=droplets_list)
    
    get_p = droplets_sub.add_parser("get", help="Get droplet")
    get_p.add_argument("droplet_id")
    get_p.set_defaults(func=droplets_get)
    
    create_p = droplets_sub.add_parser("create", help="Create droplet")
    create_p.add_argument("name")
    create_p.add_argument("--region", required=True)
    create_p.add_argument("--size", required=True)
    create_p.add_argument("--image", required=True)
    create_p.add_argument("--ssh-keys")
    create_p.add_argument("--tags")
    create_p.add_argument("--user-data")
    create_p.set_defaults(func=droplets_create)
    
    destroy_p = droplets_sub.add_parser("destroy", help="Destroy droplet")
    destroy_p.add_argument("droplet_id")
    destroy_p.set_defaults(func=droplets_destroy)
    
    for action in ["power-on", "power-off", "reboot"]:
        p = droplets_sub.add_parser(action)
        p.add_argument("droplet_id")
        p.set_defaults(func=globals()[f"droplets_{action.replace('-', '_')}"])
    
    resize_p = droplets_sub.add_parser("resize")
    resize_p.add_argument("droplet_id")
    resize_p.add_argument("--size", required=True)
    resize_p.set_defaults(func=droplets_resize)
    
    snap_p = droplets_sub.add_parser("snapshot")
    snap_p.add_argument("droplet_id")
    snap_p.add_argument("--name", required=True)
    snap_p.set_defaults(func=droplets_snapshot)
    
    # DNS
    dns_parser = subparsers.add_parser("dns", help="Manage DNS")
    dns_sub = dns_parser.add_subparsers(dest="action")
    
    dns_sub.add_parser("list", help="List domains").set_defaults(func=dns_list)
    
    records_p = dns_sub.add_parser("records", help="List records")
    records_p.add_argument("domain")
    records_p.set_defaults(func=dns_records)
    
    add_p = dns_sub.add_parser("add", help="Add record")
    add_p.add_argument("domain")
    add_p.add_argument("--type", required=True)
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--data", required=True)
    add_p.add_argument("--ttl", type=int, default=300)
    add_p.add_argument("--priority", type=int)
    add_p.add_argument("--port", type=int)
    add_p.add_argument("--weight", type=int)
    add_p.set_defaults(func=dns_add)
    
    update_p = dns_sub.add_parser("update", help="Update record")
    update_p.add_argument("domain")
    update_p.add_argument("record_id")
    update_p.add_argument("--data")
    update_p.add_argument("--name")
    update_p.add_argument("--ttl", type=int)
    update_p.add_argument("--priority", type=int)
    update_p.set_defaults(func=dns_update)
    
    delete_p = dns_sub.add_parser("delete", help="Delete record")
    delete_p.add_argument("domain")
    delete_p.add_argument("record_id")
    delete_p.set_defaults(func=dns_delete)
    
    create_domain_p = dns_sub.add_parser("create", help="Create domain")
    create_domain_p.add_argument("domain")
    create_domain_p.add_argument("--ip")
    create_domain_p.set_defaults(func=dns_create)
    
    # Firewalls
    fw_parser = subparsers.add_parser("firewalls", help="Manage firewalls")
    fw_sub = fw_parser.add_subparsers(dest="action")
    
    fw_sub.add_parser("list").set_defaults(func=firewalls_list)
    
    fw_get = fw_sub.add_parser("get")
    fw_get.add_argument("firewall_id")
    fw_get.set_defaults(func=firewalls_get)
    
    fw_create = fw_sub.add_parser("create")
    fw_create.add_argument("name")
    fw_create.add_argument("--inbound", action="append", help="protocol:ports:sources")
    fw_create.set_defaults(func=firewalls_create)
    
    fw_add = fw_sub.add_parser("add-droplet")
    fw_add.add_argument("firewall_id")
    fw_add.add_argument("droplet_id")
    fw_add.set_defaults(func=firewalls_add_droplet)
    
    # Databases
    db_parser = subparsers.add_parser("databases", help="Manage databases")
    db_sub = db_parser.add_subparsers(dest="action")
    
    db_sub.add_parser("list").set_defaults(func=databases_list)
    
    db_get = db_sub.add_parser("get")
    db_get.add_argument("db_id")
    db_get.set_defaults(func=databases_get)
    
    # Account
    account_parser = subparsers.add_parser("account", help="Account info")
    account_parser.set_defaults(func=account_info)
    
    # Billing
    billing_parser = subparsers.add_parser("billing", help="Billing info")
    billing_sub = billing_parser.add_subparsers(dest="action")
    
    billing_sub.add_parser("balance").set_defaults(func=billing_balance)
    billing_sub.add_parser("history").set_defaults(func=billing_history)
    
    # SSH Keys
    ssh_parser = subparsers.add_parser("ssh-keys", help="Manage SSH keys")
    ssh_sub = ssh_parser.add_subparsers(dest="action")
    
    ssh_sub.add_parser("list").set_defaults(func=ssh_keys_list)
    
    ssh_add = ssh_sub.add_parser("add")
    ssh_add.add_argument("name")
    ssh_add.add_argument("--key", required=True)
    ssh_add.set_defaults(func=ssh_keys_add)
    
    # Images
    images_parser = subparsers.add_parser("images", help="Manage images")
    images_sub = images_parser.add_subparsers(dest="action")
    
    images_sub.add_parser("list").set_defaults(func=images_list)
    images_sub.add_parser("snapshots").set_defaults(func=images_snapshots)
    
    img_del = images_sub.add_parser("delete")
    img_del.add_argument("image_id")
    img_del.set_defaults(func=images_delete)
    
    # Regions
    regions_parser = subparsers.add_parser("regions", help="List regions")
    regions_parser.set_defaults(func=regions_list)
    
    # Sizes
    sizes_parser = subparsers.add_parser("sizes", help="List sizes")
    sizes_parser.set_defaults(func=sizes_list)
    
    args = parser.parse_args()
    
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
