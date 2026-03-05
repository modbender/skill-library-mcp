#!/usr/bin/env python3
"""
Hostinger API CLI wrapper

Provides command-line access to Hostinger API for VPS, DNS, domains, hosting, and billing.
Token is read from ~/.config/hostinger/token
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://developers.hostinger.com"

def get_token():
    """Read API token from config file."""
    token_path = Path.home() / ".config" / "hostinger" / "token"
    if not token_path.exists():
        print(f"Error: Token not found at {token_path}", file=sys.stderr)
        print("Get your token from: https://hpanel.hostinger.com/profile/api", file=sys.stderr)
        print(f"Then: mkdir -p ~/.config/hostinger && echo -n 'YOUR_TOKEN' > {token_path}", file=sys.stderr)
        sys.exit(1)
    return token_path.read_text().strip()

def api_request(method, endpoint, data=None, params=None):
    """Make API request with authentication."""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{BASE_URL}{endpoint}"
    
    try:
        resp = requests.request(method, url, headers=headers, json=data, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.text else {}
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            print(f"API Error: {error_data.get('error', str(e))}", file=sys.stderr)
        except:
            print(f"HTTP Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)

def output(data):
    """Output data as formatted JSON."""
    print(json.dumps(data, indent=2))

# VPS Commands
def vps_list(args):
    """List all VPS instances."""
    data = api_request("GET", "/api/vps/v1/virtual-machines")
    output(data)

def vps_get(args):
    """Get VPS details."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}")
    output(data)

def vps_start(args):
    """Start a VPS."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/start")
    output(data)

def vps_stop(args):
    """Stop a VPS."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/stop")
    output(data)

def vps_restart(args):
    """Restart a VPS."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/restart")
    output(data)

def vps_snapshot_create(args):
    """Create VPS snapshot."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/snapshot")
    output(data)

def vps_snapshot_get(args):
    """Get VPS snapshot."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/snapshot")
    output(data)

def vps_snapshot_restore(args):
    """Restore VPS from snapshot."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/snapshot/restore")
    output(data)

def vps_snapshot_delete(args):
    """Delete VPS snapshot."""
    data = api_request("DELETE", f"/api/vps/v1/virtual-machines/{args.vm_id}/snapshot")
    output(data)

def vps_backups(args):
    """List VPS backups."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/backups")
    output(data)

def vps_backup_restore(args):
    """Restore VPS from backup."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/backups/{args.backup_id}/restore")
    output(data)

def vps_metrics(args):
    """Get VPS metrics."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/metrics")
    output(data)

def vps_hostname_set(args):
    """Set VPS hostname."""
    data = api_request("PUT", f"/api/vps/v1/virtual-machines/{args.vm_id}/hostname", {"hostname": args.hostname})
    output(data)

def vps_password_set(args):
    """Set VPS root password."""
    data = api_request("PUT", f"/api/vps/v1/virtual-machines/{args.vm_id}/root-password", {"password": args.password})
    output(data)

def vps_recreate(args):
    """Recreate VPS with new OS template."""
    payload = {"template_id": args.template_id}
    if args.password:
        payload["password"] = args.password
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/recreate", payload)
    output(data)

def vps_templates(args):
    """List available OS templates."""
    data = api_request("GET", "/api/vps/v1/templates")
    output(data)

def vps_datacenters(args):
    """List available datacenters."""
    data = api_request("GET", "/api/vps/v1/data-centers")
    output(data)

# DNS Commands
def dns_get(args):
    """Get DNS records for domain."""
    data = api_request("GET", f"/api/dns/v1/zones/{args.domain}")
    output(data)

def dns_update(args):
    """Update DNS records from JSON file."""
    with open(args.records_file) as f:
        records_data = json.load(f)
    data = api_request("PUT", f"/api/dns/v1/zones/{args.domain}", records_data)
    output(data)

def dns_delete(args):
    """Delete DNS records."""
    payload = {"records": args.records} if args.records else {}
    data = api_request("DELETE", f"/api/dns/v1/zones/{args.domain}", payload if payload else None)
    output(data)

def dns_reset(args):
    """Reset DNS records to defaults."""
    data = api_request("POST", f"/api/dns/v1/zones/{args.domain}/reset")
    output(data)

def dns_validate(args):
    """Validate DNS records."""
    with open(args.records_file) as f:
        records_data = json.load(f)
    data = api_request("POST", f"/api/dns/v1/zones/{args.domain}/validate", records_data)
    output(data)

def dns_snapshots(args):
    """List DNS snapshots."""
    data = api_request("GET", f"/api/dns/v1/snapshots/{args.domain}")
    output(data)

def dns_snapshot_get(args):
    """Get specific DNS snapshot."""
    data = api_request("GET", f"/api/dns/v1/snapshots/{args.domain}/{args.snapshot_id}")
    output(data)

def dns_snapshot_restore(args):
    """Restore DNS snapshot."""
    data = api_request("POST", f"/api/dns/v1/snapshots/{args.domain}/{args.snapshot_id}/restore")
    output(data)

# Domain Commands
def domains_list(args):
    """List all domains."""
    data = api_request("GET", "/api/domains/v1/portfolio")
    output(data)

def domains_get(args):
    """Get domain details."""
    data = api_request("GET", f"/api/domains/v1/portfolio/{args.domain}")
    output(data)

def domains_nameservers(args):
    """Update domain nameservers."""
    data = api_request("PUT", f"/api/domains/v1/portfolio/{args.domain}/nameservers", 
                       {"nameservers": args.nameservers})
    output(data)

def domains_lock_enable(args):
    """Enable domain lock."""
    data = api_request("PUT", f"/api/domains/v1/portfolio/{args.domain}/domain-lock")
    output(data)

def domains_lock_disable(args):
    """Disable domain lock."""
    data = api_request("DELETE", f"/api/domains/v1/portfolio/{args.domain}/domain-lock")
    output(data)

def domains_privacy_enable(args):
    """Enable privacy protection."""
    data = api_request("PUT", f"/api/domains/v1/portfolio/{args.domain}/privacy-protection")
    output(data)

def domains_privacy_disable(args):
    """Disable privacy protection."""
    data = api_request("DELETE", f"/api/domains/v1/portfolio/{args.domain}/privacy-protection")
    output(data)

def domains_check(args):
    """Check domain availability."""
    data = api_request("POST", "/api/domains/v1/availability", {"domains": args.domains})
    output(data)

def domains_forwarding_get(args):
    """Get domain forwarding."""
    data = api_request("GET", f"/api/domains/v1/forwarding/{args.domain}")
    output(data)

def domains_forwarding_create(args):
    """Create domain forwarding."""
    payload = {
        "domain": args.domain,
        "redirect_url": args.url,
        "redirect_type": args.type or "permanent"
    }
    data = api_request("POST", "/api/domains/v1/forwarding", payload)
    output(data)

def domains_forwarding_delete(args):
    """Delete domain forwarding."""
    data = api_request("DELETE", f"/api/domains/v1/forwarding/{args.domain}")
    output(data)

# WHOIS Commands
def whois_list(args):
    """List WHOIS profiles."""
    data = api_request("GET", "/api/domains/v1/whois")
    output(data)

def whois_get(args):
    """Get WHOIS profile."""
    data = api_request("GET", f"/api/domains/v1/whois/{args.whois_id}")
    output(data)

# Docker Commands
def docker_list(args):
    """List Docker projects on VPS."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker")
    output(data)

def docker_get(args):
    """Get Docker project details."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}")
    output(data)

def docker_deploy(args):
    """Deploy Docker project from compose file or URL."""
    payload = {"project_name": args.project}
    if args.url:
        payload["url"] = args.url
    elif args.file:
        with open(args.file) as f:
            payload["content"] = f.read()
    else:
        print("Error: Must provide --url or --file", file=sys.stderr)
        sys.exit(1)
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker", payload)
    output(data)

def docker_start(args):
    """Start Docker project."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/start")
    output(data)

def docker_stop(args):
    """Stop Docker project."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/stop")
    output(data)

def docker_restart(args):
    """Restart Docker project."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/restart")
    output(data)

def docker_update(args):
    """Update Docker project."""
    data = api_request("POST", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/update")
    output(data)

def docker_down(args):
    """Delete Docker project."""
    data = api_request("DELETE", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/down")
    output(data)

def docker_logs(args):
    """Get Docker project logs."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/logs")
    output(data)

def docker_containers(args):
    """List Docker project containers."""
    data = api_request("GET", f"/api/vps/v1/virtual-machines/{args.vm_id}/docker/{args.project}/containers")
    output(data)

# Firewall Commands
def firewall_list(args):
    """List firewalls."""
    data = api_request("GET", "/api/vps/v1/firewall")
    output(data)

def firewall_get(args):
    """Get firewall details."""
    data = api_request("GET", f"/api/vps/v1/firewall/{args.firewall_id}")
    output(data)

def firewall_create(args):
    """Create firewall."""
    data = api_request("POST", "/api/vps/v1/firewall", {"name": args.name})
    output(data)

def firewall_delete(args):
    """Delete firewall."""
    data = api_request("DELETE", f"/api/vps/v1/firewall/{args.firewall_id}")
    output(data)

def firewall_activate(args):
    """Activate firewall on VPS."""
    data = api_request("POST", f"/api/vps/v1/firewall/{args.firewall_id}/activate/{args.vm_id}")
    output(data)

def firewall_deactivate(args):
    """Deactivate firewall on VPS."""
    data = api_request("POST", f"/api/vps/v1/firewall/{args.firewall_id}/deactivate/{args.vm_id}")
    output(data)

def firewall_sync(args):
    """Sync firewall rules to VPS."""
    data = api_request("POST", f"/api/vps/v1/firewall/{args.firewall_id}/sync/{args.vm_id}")
    output(data)

def firewall_add_rule(args):
    """Add firewall rule."""
    payload = {
        "protocol": args.protocol,
        "port": args.port,
        "source": args.source,
        "source_detail": args.source_detail or ""
    }
    data = api_request("POST", f"/api/vps/v1/firewall/{args.firewall_id}/rules", payload)
    output(data)

def firewall_update_rule(args):
    """Update firewall rule."""
    payload = {}
    if args.protocol:
        payload["protocol"] = args.protocol
    if args.port:
        payload["port"] = args.port
    if args.source:
        payload["source"] = args.source
    data = api_request("PUT", f"/api/vps/v1/firewall/{args.firewall_id}/rules/{args.rule_id}", payload)
    output(data)

def firewall_delete_rule(args):
    """Delete firewall rule."""
    data = api_request("DELETE", f"/api/vps/v1/firewall/{args.firewall_id}/rules/{args.rule_id}")
    output(data)

# SSH Keys Commands
def ssh_keys_list(args):
    """List SSH public keys."""
    data = api_request("GET", "/api/vps/v1/public-keys")
    output(data)

def ssh_keys_add(args):
    """Add SSH public key."""
    key_content = args.key
    if os.path.exists(args.key):
        with open(args.key) as f:
            key_content = f.read().strip()
    data = api_request("POST", "/api/vps/v1/public-keys", {
        "name": args.name,
        "key": key_content
    })
    output(data)

def ssh_keys_delete(args):
    """Delete SSH public key."""
    data = api_request("DELETE", f"/api/vps/v1/public-keys/{args.key_id}")
    output(data)

def ssh_keys_attach(args):
    """Attach SSH key to VPS."""
    data = api_request("POST", f"/api/vps/v1/public-keys/attach/{args.vm_id}", {
        "public_key_ids": args.key_ids
    })
    output(data)

# Hosting Commands
def hosting_websites(args):
    """List websites."""
    data = api_request("GET", "/api/hosting/v1/websites")
    output(data)

def hosting_datacenters(args):
    """List hosting datacenters."""
    data = api_request("GET", "/api/hosting/v1/datacenters")
    output(data)

def hosting_orders(args):
    """List hosting orders."""
    data = api_request("GET", "/api/hosting/v1/orders")
    output(data)

# Billing Commands
def billing_subscriptions(args):
    """List subscriptions."""
    data = api_request("GET", "/api/billing/v1/subscriptions")
    output(data)

def billing_payment_methods(args):
    """List payment methods."""
    data = api_request("GET", "/api/billing/v1/payment-methods")
    output(data)

def billing_catalog(args):
    """List catalog items."""
    params = {}
    if args.category:
        params["category"] = args.category
    if args.name:
        params["name"] = args.name
    data = api_request("GET", "/api/billing/v1/catalog", params=params)
    output(data)


def main():
    parser = argparse.ArgumentParser(description="Hostinger API CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # VPS commands
    vps_parser = subparsers.add_parser("vps", help="VPS operations")
    vps_sub = vps_parser.add_subparsers(dest="action")
    
    vps_sub.add_parser("list", help="List VPS instances").set_defaults(func=vps_list)
    vps_sub.add_parser("templates", help="List OS templates").set_defaults(func=vps_templates)
    vps_sub.add_parser("datacenters", help="List datacenters").set_defaults(func=vps_datacenters)
    
    p = vps_sub.add_parser("get", help="Get VPS details")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_get)
    
    p = vps_sub.add_parser("start", help="Start VPS")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_start)
    
    p = vps_sub.add_parser("stop", help="Stop VPS")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_stop)
    
    p = vps_sub.add_parser("restart", help="Restart VPS")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_restart)
    
    p = vps_sub.add_parser("metrics", help="Get VPS metrics")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_metrics)
    
    p = vps_sub.add_parser("snapshot-create", help="Create snapshot")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_snapshot_create)
    
    p = vps_sub.add_parser("snapshot-get", help="Get snapshot")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_snapshot_get)
    
    p = vps_sub.add_parser("snapshot-restore", help="Restore snapshot")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_snapshot_restore)
    
    p = vps_sub.add_parser("snapshot-delete", help="Delete snapshot")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_snapshot_delete)
    
    p = vps_sub.add_parser("backups", help="List backups")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=vps_backups)
    
    p = vps_sub.add_parser("backup-restore", help="Restore backup")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("backup_id", help="Backup ID")
    p.set_defaults(func=vps_backup_restore)
    
    p = vps_sub.add_parser("hostname", help="Set hostname")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("hostname", help="New hostname")
    p.set_defaults(func=vps_hostname_set)
    
    p = vps_sub.add_parser("password", help="Set root password")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("password", help="New password")
    p.set_defaults(func=vps_password_set)
    
    p = vps_sub.add_parser("recreate", help="Recreate VPS with new template")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("template_id", type=int, help="Template ID")
    p.add_argument("--password", help="New root password")
    p.set_defaults(func=vps_recreate)

    # DNS commands
    dns_parser = subparsers.add_parser("dns", help="DNS operations")
    dns_sub = dns_parser.add_subparsers(dest="action")
    
    p = dns_sub.add_parser("get", help="Get DNS records")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=dns_get)
    
    p = dns_sub.add_parser("update", help="Update DNS records")
    p.add_argument("domain", help="Domain name")
    p.add_argument("records_file", help="JSON file with records")
    p.set_defaults(func=dns_update)
    
    p = dns_sub.add_parser("delete", help="Delete DNS records")
    p.add_argument("domain", help="Domain name")
    p.add_argument("--records", nargs="+", help="Specific record IDs to delete")
    p.set_defaults(func=dns_delete)
    
    p = dns_sub.add_parser("reset", help="Reset DNS to defaults")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=dns_reset)
    
    p = dns_sub.add_parser("validate", help="Validate DNS records")
    p.add_argument("domain", help="Domain name")
    p.add_argument("records_file", help="JSON file with records")
    p.set_defaults(func=dns_validate)
    
    p = dns_sub.add_parser("snapshots", help="List DNS snapshots")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=dns_snapshots)
    
    p = dns_sub.add_parser("snapshot-get", help="Get DNS snapshot")
    p.add_argument("domain", help="Domain name")
    p.add_argument("snapshot_id", help="Snapshot ID")
    p.set_defaults(func=dns_snapshot_get)
    
    p = dns_sub.add_parser("snapshot-restore", help="Restore DNS snapshot")
    p.add_argument("domain", help="Domain name")
    p.add_argument("snapshot_id", help="Snapshot ID")
    p.set_defaults(func=dns_snapshot_restore)

    # Domain commands
    domains_parser = subparsers.add_parser("domains", help="Domain operations")
    domains_sub = domains_parser.add_subparsers(dest="action")
    
    domains_sub.add_parser("list", help="List domains").set_defaults(func=domains_list)
    
    p = domains_sub.add_parser("get", help="Get domain details")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_get)
    
    p = domains_sub.add_parser("nameservers", help="Update nameservers")
    p.add_argument("domain", help="Domain name")
    p.add_argument("nameservers", nargs="+", help="Nameservers")
    p.set_defaults(func=domains_nameservers)
    
    p = domains_sub.add_parser("lock", help="Enable domain lock")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_lock_enable)
    
    p = domains_sub.add_parser("unlock", help="Disable domain lock")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_lock_disable)
    
    p = domains_sub.add_parser("privacy-on", help="Enable privacy protection")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_privacy_enable)
    
    p = domains_sub.add_parser("privacy-off", help="Disable privacy protection")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_privacy_disable)
    
    p = domains_sub.add_parser("check", help="Check domain availability")
    p.add_argument("domains", nargs="+", help="Domains to check")
    p.set_defaults(func=domains_check)
    
    p = domains_sub.add_parser("forwarding-get", help="Get domain forwarding")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_forwarding_get)
    
    p = domains_sub.add_parser("forwarding-create", help="Create domain forwarding")
    p.add_argument("domain", help="Domain name")
    p.add_argument("url", help="Redirect URL")
    p.add_argument("--type", choices=["permanent", "temporary"], help="Redirect type")
    p.set_defaults(func=domains_forwarding_create)
    
    p = domains_sub.add_parser("forwarding-delete", help="Delete domain forwarding")
    p.add_argument("domain", help="Domain name")
    p.set_defaults(func=domains_forwarding_delete)

    # WHOIS commands
    whois_parser = subparsers.add_parser("whois", help="WHOIS operations")
    whois_sub = whois_parser.add_subparsers(dest="action")
    
    whois_sub.add_parser("list", help="List WHOIS profiles").set_defaults(func=whois_list)
    
    p = whois_sub.add_parser("get", help="Get WHOIS profile")
    p.add_argument("whois_id", help="WHOIS profile ID")
    p.set_defaults(func=whois_get)

    # Docker commands
    docker_parser = subparsers.add_parser("docker", help="Docker operations")
    docker_sub = docker_parser.add_subparsers(dest="action")
    
    p = docker_sub.add_parser("list", help="List Docker projects")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=docker_list)
    
    p = docker_sub.add_parser("get", help="Get Docker project details")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_get)
    
    p = docker_sub.add_parser("deploy", help="Deploy Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.add_argument("--url", help="URL to docker-compose.yml (e.g., GitHub raw URL)")
    p.add_argument("--file", help="Local docker-compose.yml file")
    p.set_defaults(func=docker_deploy)
    
    p = docker_sub.add_parser("start", help="Start Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_start)
    
    p = docker_sub.add_parser("stop", help="Stop Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_stop)
    
    p = docker_sub.add_parser("restart", help="Restart Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_restart)
    
    p = docker_sub.add_parser("update", help="Update Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_update)
    
    p = docker_sub.add_parser("down", help="Delete Docker project")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_down)
    
    p = docker_sub.add_parser("logs", help="Get Docker project logs")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_logs)
    
    p = docker_sub.add_parser("containers", help="List Docker containers")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("project", help="Project name")
    p.set_defaults(func=docker_containers)

    # Firewall commands
    fw_parser = subparsers.add_parser("firewall", help="Firewall operations")
    fw_sub = fw_parser.add_subparsers(dest="action")
    
    fw_sub.add_parser("list", help="List firewalls").set_defaults(func=firewall_list)
    
    p = fw_sub.add_parser("get", help="Get firewall details")
    p.add_argument("firewall_id", help="Firewall ID")
    p.set_defaults(func=firewall_get)
    
    p = fw_sub.add_parser("create", help="Create firewall")
    p.add_argument("name", help="Firewall name")
    p.set_defaults(func=firewall_create)
    
    p = fw_sub.add_parser("delete", help="Delete firewall")
    p.add_argument("firewall_id", help="Firewall ID")
    p.set_defaults(func=firewall_delete)
    
    p = fw_sub.add_parser("activate", help="Activate firewall on VPS")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=firewall_activate)
    
    p = fw_sub.add_parser("deactivate", help="Deactivate firewall on VPS")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=firewall_deactivate)
    
    p = fw_sub.add_parser("sync", help="Sync firewall rules")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("vm_id", help="VPS ID")
    p.set_defaults(func=firewall_sync)
    
    p = fw_sub.add_parser("add-rule", help="Add firewall rule")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("--protocol", required=True, choices=["tcp", "udp", "icmp", "gre"], help="Protocol")
    p.add_argument("--port", required=True, help="Port or range (e.g., 443 or 8000-8999)")
    p.add_argument("--source", required=True, help="Source (e.g., any, custom)")
    p.add_argument("--source-detail", help="Source detail (e.g., 0.0.0.0/0)")
    p.set_defaults(func=firewall_add_rule)
    
    p = fw_sub.add_parser("update-rule", help="Update firewall rule")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("rule_id", help="Rule ID")
    p.add_argument("--protocol", choices=["tcp", "udp", "icmp", "gre"])
    p.add_argument("--port")
    p.add_argument("--source")
    p.set_defaults(func=firewall_update_rule)
    
    p = fw_sub.add_parser("delete-rule", help="Delete firewall rule")
    p.add_argument("firewall_id", help="Firewall ID")
    p.add_argument("rule_id", help="Rule ID")
    p.set_defaults(func=firewall_delete_rule)

    # SSH Keys commands
    ssh_parser = subparsers.add_parser("ssh-keys", help="SSH key operations")
    ssh_sub = ssh_parser.add_subparsers(dest="action")
    
    ssh_sub.add_parser("list", help="List SSH keys").set_defaults(func=ssh_keys_list)
    
    p = ssh_sub.add_parser("add", help="Add SSH key")
    p.add_argument("name", help="Key name")
    p.add_argument("key", help="Public key content or path to .pub file")
    p.set_defaults(func=ssh_keys_add)
    
    p = ssh_sub.add_parser("delete", help="Delete SSH key")
    p.add_argument("key_id", help="Key ID")
    p.set_defaults(func=ssh_keys_delete)
    
    p = ssh_sub.add_parser("attach", help="Attach SSH keys to VPS")
    p.add_argument("vm_id", help="VPS ID")
    p.add_argument("key_ids", nargs="+", type=int, help="Key IDs")
    p.set_defaults(func=ssh_keys_attach)

    # Hosting commands
    hosting_parser = subparsers.add_parser("hosting", help="Hosting operations")
    hosting_sub = hosting_parser.add_subparsers(dest="action")
    
    hosting_sub.add_parser("websites", help="List websites").set_defaults(func=hosting_websites)
    hosting_sub.add_parser("datacenters", help="List datacenters").set_defaults(func=hosting_datacenters)
    hosting_sub.add_parser("orders", help="List orders").set_defaults(func=hosting_orders)

    # Billing commands
    billing_parser = subparsers.add_parser("billing", help="Billing operations")
    billing_sub = billing_parser.add_subparsers(dest="action")
    
    billing_sub.add_parser("subscriptions", help="List subscriptions").set_defaults(func=billing_subscriptions)
    billing_sub.add_parser("payment-methods", help="List payment methods").set_defaults(func=billing_payment_methods)
    
    p = billing_sub.add_parser("catalog", help="List catalog")
    p.add_argument("--category", help="Filter by category")
    p.add_argument("--name", help="Filter by name (use * for wildcard)")
    p.set_defaults(func=billing_catalog)

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.parse_args([args.command, "-h"])


if __name__ == "__main__":
    main()
