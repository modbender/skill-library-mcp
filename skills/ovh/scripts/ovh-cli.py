#!/usr/bin/env python3
"""OVH CLI - Manage OVHcloud services"""

import argparse
import json
import os
import sys

try:
    import ovh
except ImportError:
    print("Error: pip install ovh", file=sys.stderr)
    sys.exit(1)


def get_client():
    """Create OVH client from environment variables."""
    endpoint = os.environ.get('OVH_ENDPOINT', 'ovh-ca')
    app_key = os.environ.get('OVH_APP_KEY')
    app_secret = os.environ.get('OVH_APP_SECRET')
    consumer_key = os.environ.get('OVH_CONSUMER_KEY')
    
    if not all([app_key, app_secret, consumer_key]):
        print("Error: Set OVH_APP_KEY, OVH_APP_SECRET, OVH_CONSUMER_KEY", file=sys.stderr)
        sys.exit(1)
    
    return ovh.Client(
        endpoint=endpoint,
        application_key=app_key,
        application_secret=app_secret,
        consumer_key=consumer_key
    )


def output(data, as_json=False):
    """Print output in appropriate format."""
    if as_json:
        print(json.dumps(data, indent=2, default=str))
    elif isinstance(data, dict):
        for k, v in data.items():
            print(f"{k}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(json.dumps(item, default=str))
            else:
                print(item)
    else:
        print(data)


def cmd_me(client, args):
    """Get account info."""
    me = client.get('/me')
    output(me, args.json)


def cmd_domains(client, args):
    """List domains."""
    domains = client.get('/domain')
    output(domains, args.json)


def cmd_domain(client, args):
    """Get domain info or perform action."""
    if args.action == 'renew':
        info = client.get(f'/domain/{args.domain}/serviceInfos')
        output({
            'domain': args.domain,
            'creation': info.get('creation'),
            'expiration': info.get('expiration'),
            'renew': info.get('renew'),
            'status': info.get('status')
        }, args.json)
    else:
        info = client.get(f'/domain/{args.domain}')
        output(info, args.json)


def cmd_dns_list(client, args):
    """List DNS records."""
    records = client.get(f'/domain/zone/{args.domain}/record')
    result = []
    for rid in records:
        rec = client.get(f'/domain/zone/{args.domain}/record/{rid}')
        result.append({
            'id': rid,
            'type': rec.get('fieldType'),
            'subdomain': rec.get('subDomain') or '@',
            'target': rec.get('target'),
            'ttl': rec.get('ttl')
        })
    output(result, args.json)


def cmd_dns_get(client, args):
    """Get specific DNS record."""
    rec = client.get(f'/domain/zone/{args.domain}/record/{args.record_id}')
    output(rec, args.json)


def cmd_dns_create(client, args):
    """Create DNS record."""
    data = {
        'fieldType': args.type,
        'subDomain': args.subdomain if args.subdomain != '@' else '',
        'target': args.target,
    }
    if args.ttl:
        data['ttl'] = args.ttl
    
    result = client.post(f'/domain/zone/{args.domain}/record', **data)
    print(f"Created record ID: {result}")
    print("Run 'dns <domain> refresh' to apply changes")


def cmd_dns_update(client, args):
    """Update DNS record."""
    data = {}
    if args.target:
        data['target'] = args.target
    if args.ttl:
        data['ttl'] = args.ttl
    if args.subdomain:
        data['subDomain'] = args.subdomain if args.subdomain != '@' else ''
    
    client.put(f'/domain/zone/{args.domain}/record/{args.record_id}', **data)
    print(f"Updated record {args.record_id}")
    print("Run 'dns <domain> refresh' to apply changes")


def cmd_dns_delete(client, args):
    """Delete DNS record."""
    client.delete(f'/domain/zone/{args.domain}/record/{args.record_id}')
    print(f"Deleted record {args.record_id}")
    print("Run 'dns <domain> refresh' to apply changes")


def cmd_dns_refresh(client, args):
    """Refresh DNS zone."""
    client.post(f'/domain/zone/{args.domain}/refresh')
    print(f"Zone {args.domain} refreshed")


def cmd_vps_list(client, args):
    """List VPS."""
    vps = client.get('/vps')
    output(vps, args.json)


def cmd_vps_info(client, args):
    """Get VPS info."""
    info = client.get(f'/vps/{args.name}')
    output(info, args.json)


def cmd_vps_status(client, args):
    """Get VPS status."""
    status = client.get(f'/vps/{args.name}/status')
    output(status, args.json)


def cmd_vps_action(client, args):
    """Perform VPS action."""
    if args.action == 'reboot':
        client.post(f'/vps/{args.name}/reboot')
        print(f"Rebooting {args.name}")
    elif args.action == 'start':
        client.post(f'/vps/{args.name}/start')
        print(f"Starting {args.name}")
    elif args.action == 'stop':
        client.post(f'/vps/{args.name}/stop')
        print(f"Stopping {args.name}")
    elif args.action == 'ips':
        ips = client.get(f'/vps/{args.name}/ips')
        output(ips, args.json)


def cmd_cloud_list(client, args):
    """List cloud projects."""
    projects = client.get('/cloud/project')
    output(projects, args.json)


def cmd_cloud_instances(client, args):
    """List cloud instances."""
    instances = client.get(f'/cloud/project/{args.project}/instance')
    output(instances, args.json)


def cmd_dedicated_list(client, args):
    """List dedicated servers."""
    servers = client.get('/dedicated/server')
    output(servers, args.json)


def cmd_dedicated_info(client, args):
    """Get dedicated server info."""
    info = client.get(f'/dedicated/server/{args.name}')
    output(info, args.json)


def cmd_dedicated_reboot(client, args):
    """Reboot dedicated server."""
    client.post(f'/dedicated/server/{args.name}/reboot')
    print(f"Rebooting {args.name}")


def cmd_ssl_list(client, args):
    """List SSL certificates."""
    certs = client.get('/ssl')
    output(certs, args.json)


def cmd_bills(client, args):
    """List bills."""
    bills = client.get('/me/bill')
    bills = bills[:args.limit] if args.limit else bills
    result = []
    for bill_id in bills:
        bill = client.get(f'/me/bill/{bill_id}')
        result.append({
            'id': bill_id,
            'date': bill.get('date'),
            'total': f"{bill.get('priceWithTax', {}).get('value', 0)} {bill.get('priceWithTax', {}).get('currencyCode', '')}",
            'url': bill.get('pdfUrl')
        })
    output(result, args.json)


def cmd_orders(client, args):
    """List orders."""
    orders = client.get('/me/order')
    orders = orders[:args.limit] if args.limit else orders
    result = []
    for order_id in orders:
        order = client.get(f'/me/order/{order_id}')
        result.append({
            'id': order_id,
            'date': order.get('date'),
            'total': f"{order.get('priceWithTax', {}).get('value', 0)} {order.get('priceWithTax', {}).get('currencyCode', '')}",
        })
    output(result, args.json)


def main():
    parser = argparse.ArgumentParser(description='OVH CLI')
    parser.add_argument('--json', action='store_true', help='JSON output')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # me
    subparsers.add_parser('me', help='Account info')
    
    # domains
    subparsers.add_parser('domains', help='List domains')
    
    # domain
    p_domain = subparsers.add_parser('domain', help='Domain info/actions')
    p_domain.add_argument('domain', help='Domain name')
    p_domain.add_argument('action', nargs='?', choices=['renew'], help='Action')
    
    # dns
    p_dns = subparsers.add_parser('dns', help='DNS management')
    p_dns.add_argument('domain', help='Domain name')
    p_dns.add_argument('action', nargs='?', choices=['get', 'create', 'update', 'delete', 'refresh'])
    p_dns.add_argument('record_id', nargs='?', help='Record ID')
    p_dns.add_argument('--type', help='Record type (A, AAAA, CNAME, TXT, MX, etc.)')
    p_dns.add_argument('--subdomain', help='Subdomain (@ for root)')
    p_dns.add_argument('--target', help='Target value')
    p_dns.add_argument('--ttl', type=int, help='TTL in seconds')
    
    # vps
    p_vps = subparsers.add_parser('vps', help='VPS management')
    p_vps.add_argument('name', nargs='?', help='VPS name')
    p_vps.add_argument('action', nargs='?', choices=['status', 'reboot', 'start', 'stop', 'ips'])
    
    # cloud
    p_cloud = subparsers.add_parser('cloud', help='Cloud projects')
    p_cloud.add_argument('project', nargs='?', help='Project ID')
    p_cloud.add_argument('action', nargs='?', choices=['instances'])
    
    # dedicated
    p_ded = subparsers.add_parser('dedicated', help='Dedicated servers')
    p_ded.add_argument('name', nargs='?', help='Server name')
    p_ded.add_argument('action', nargs='?', choices=['reboot'])
    
    # ssl
    subparsers.add_parser('ssl', help='SSL certificates')
    
    # bills
    p_bills = subparsers.add_parser('bills', help='Billing history')
    p_bills.add_argument('--limit', type=int, default=10, help='Limit results')
    
    # orders
    p_orders = subparsers.add_parser('orders', help='Order history')
    p_orders.add_argument('--limit', type=int, default=10, help='Limit results')
    
    args = parser.parse_args()
    client = get_client()
    
    try:
        if args.command == 'me':
            cmd_me(client, args)
        elif args.command == 'domains':
            cmd_domains(client, args)
        elif args.command == 'domain':
            cmd_domain(client, args)
        elif args.command == 'dns':
            if args.action == 'get':
                cmd_dns_get(client, args)
            elif args.action == 'create':
                cmd_dns_create(client, args)
            elif args.action == 'update':
                cmd_dns_update(client, args)
            elif args.action == 'delete':
                cmd_dns_delete(client, args)
            elif args.action == 'refresh':
                cmd_dns_refresh(client, args)
            else:
                cmd_dns_list(client, args)
        elif args.command == 'vps':
            if not args.name:
                cmd_vps_list(client, args)
            elif args.action:
                cmd_vps_action(client, args)
            elif args.action == 'status':
                cmd_vps_status(client, args)
            else:
                cmd_vps_info(client, args)
        elif args.command == 'cloud':
            if not args.project:
                cmd_cloud_list(client, args)
            elif args.action == 'instances':
                cmd_cloud_instances(client, args)
        elif args.command == 'dedicated':
            if not args.name:
                cmd_dedicated_list(client, args)
            elif args.action == 'reboot':
                cmd_dedicated_reboot(client, args)
            else:
                cmd_dedicated_info(client, args)
        elif args.command == 'ssl':
            cmd_ssl_list(client, args)
        elif args.command == 'bills':
            cmd_bills(client, args)
        elif args.command == 'orders':
            cmd_orders(client, args)
    except ovh.exceptions.APIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
