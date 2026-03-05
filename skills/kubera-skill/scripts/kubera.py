#!/usr/bin/env python3
"""
Kubera API client for AI agents and CLI use.

Setup: Set KUBERA_API_KEY and KUBERA_SECRET environment variables,
       or pass --api-key and --secret arguments.

Usage:
  kubera.py portfolios                     List portfolios
  kubera.py summary [--portfolio ID]       Net worth + allocation + top holdings
  kubera.py json [--portfolio ID]          Full portfolio as JSON
  kubera.py assets [--portfolio ID] [--sheet NAME] [--sort value|name|gain] [--json]
  kubera.py search <query> [--portfolio ID] [--json]
  kubera.py update <ITEM_ID> --value NUM [--name STR] [--cost NUM] [--description STR]
"""

import time, math, hashlib, hmac, json, urllib.request, sys, os, argparse

def get_config(args):
    api_key = getattr(args, 'api_key', None) or os.environ.get('KUBERA_API_KEY')
    secret = getattr(args, 'secret', None) or os.environ.get('KUBERA_SECRET')
    if not api_key or not secret:
        print("Error: Set KUBERA_API_KEY and KUBERA_SECRET env vars, or use --api-key/--secret", file=sys.stderr)
        sys.exit(1)
    return api_key, secret

def make_request(api_key, secret, path, method="GET", body=None):
    timestamp = str(math.floor(time.time()))
    body_data = json.dumps(body, separators=(',', ':')) if body else ""
    data = f"{api_key}{timestamp}{method}{path}{body_data}"
    signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    req = urllib.request.Request(
        f"https://api.kubera.com{path}",
        data=body_data.encode() if body else None,
        headers={
            'Content-Type': 'application/json',
            'x-api-token': api_key,
            'x-timestamp': timestamp,
            'x-signature': signature
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 429:
            print("Error: Rate limit exceeded. Wait before retrying.", file=sys.stderr)
        elif e.code == 401:
            print("Error: Authentication failed. Check API key and secret.", file=sys.stderr)
        else:
            print(f"Error: HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)

def get_portfolio_id(api_key, secret, requested_id=None):
    if requested_id:
        return requested_id
    result = make_request(api_key, secret, "/api/v3/data/portfolio")
    portfolios = result.get('data', [])
    if not portfolios:
        print("No portfolios found.", file=sys.stderr)
        sys.exit(1)
    if len(portfolios) == 1:
        return portfolios[0]['id']
    print("Multiple portfolios found. Use --portfolio ID:", file=sys.stderr)
    for p in portfolios:
        print(f"  {p['id']}  {p['name']} ({p['currency']})", file=sys.stderr)
    sys.exit(1)

def cmd_portfolios(args):
    api_key, secret = get_config(args)
    result = make_request(api_key, secret, "/api/v3/data/portfolio")
    if getattr(args, 'json_out', False):
        print(json.dumps(result, indent=2))
        return
    for p in result.get('data', []):
        print(f"{p['id']}  {p['name']} ({p['currency']})")

def cmd_summary(args):
    api_key, secret = get_config(args)
    pid = get_portfolio_id(api_key, secret, args.portfolio)
    d = make_request(api_key, secret, f"/api/v3/data/portfolio/{pid}")['data']

    if getattr(args, 'json_out', False):
        print(json.dumps({
            'name': d['name'], 'currency': d['ticker'],
            'netWorth': d['netWorth'], 'assetTotal': d['assetTotal'],
            'debtTotal': d['debtTotal'], 'costBasis': d['costBasis'],
            'unrealizedGain': d['unrealizedGain'],
            'allocation': d.get('allocationByAssetClass', {}),
            'topHoldings': [{'name': a['name'], 'value': a['value']['amount'],
                             'sheet': a.get('sheetName', '')}
                            for a in sorted(d.get('asset', []),
                            key=lambda x: -x['value']['amount'])[:10]]
        }, indent=2))
        return

    print(f"Portfolio: {d['name']} ({d['ticker']})")
    print(f"Net Worth:        ${d['netWorth']:>15,.2f}")
    print(f"Total Assets:     ${d['assetTotal']:>15,.2f}")
    print(f"Total Debts:      ${d['debtTotal']:>15,.2f}")
    print(f"Cost Basis:       ${d['costBasis']:>15,.2f}")
    print(f"Unrealized Gain:  ${d['unrealizedGain']:>15,.2f}")

    alloc = d.get('allocationByAssetClass', {})
    if alloc:
        print(f"\nAllocation:")
        for k, v in alloc.items():
            if v and v > 0:
                print(f"  {k:20s} {v:>6.1f}%")

    sorted_assets = sorted(d.get('asset', []), key=lambda x: -x['value']['amount'])
    print(f"\nTop 10 Holdings:")
    for i, a in enumerate(sorted_assets[:10], 1):
        print(f"  {i:2d}. {a['name'][:40]:40s} ${a['value']['amount']:>12,.2f}")

    if d.get('debt'):
        print(f"\nDebts:")
        for debt in d['debt']:
            print(f"  {debt['name'][:50]:50s} ${debt['value']['amount']:>12,.2f}")

def cmd_json(args):
    api_key, secret = get_config(args)
    pid = get_portfolio_id(api_key, secret, args.portfolio)
    result = make_request(api_key, secret, f"/api/v3/data/portfolio/{pid}")
    print(json.dumps(result, indent=2))

def cmd_assets(args):
    api_key, secret = get_config(args)
    pid = get_portfolio_id(api_key, secret, args.portfolio)
    d = make_request(api_key, secret, f"/api/v3/data/portfolio/{pid}")['data']

    assets = d.get('asset', [])
    if args.sheet:
        assets = [a for a in assets if args.sheet.lower() in a.get('sheetName', '').lower()]

    sort_key = {
        'value': lambda x: -x['value']['amount'],
        'name': lambda x: x['name'].lower(),
        'gain': lambda x: -(x['value']['amount'] - x.get('cost', {}).get('amount', 0)),
    }.get(args.sort, lambda x: -x['value']['amount'])
    assets.sort(key=sort_key)

    if getattr(args, 'json_out', False):
        print(json.dumps([{
            'id': a['id'], 'name': a['name'],
            'value': a['value']['amount'], 'currency': a['value']['currency'],
            'cost': a.get('cost', {}).get('amount'), 'ticker': a.get('ticker'),
            'sheet': a.get('sheetName', ''), 'section': a.get('sectionName', ''),
            'subType': a.get('subType'), 'quantity': a.get('quantity'),
        } for a in assets], indent=2))
        return

    for a in assets:
        val = a['value']['amount']
        cost = a.get('cost', {}).get('amount', 0)
        gain = val - cost if cost else None
        gain_str = f"  gain: ${gain:>+,.2f}" if gain is not None and cost > 0 else ""
        print(f"{a['name'][:45]:45s} ${val:>12,.2f}{gain_str}  [{a.get('sheetName', '?')}]")

def cmd_search(args):
    api_key, secret = get_config(args)
    pid = get_portfolio_id(api_key, secret, args.portfolio)
    d = make_request(api_key, secret, f"/api/v3/data/portfolio/{pid}")['data']

    q = args.query.lower()
    matches = [a for a in d.get('asset', []) + d.get('debt', [])
               if q in a.get('name', '').lower() or q in a.get('ticker', '').lower()
               or q in a.get('sectionName', '').lower()]

    if not matches:
        print("No matches found.")
        return

    if getattr(args, 'json_out', False):
        print(json.dumps([{
            'id': a['id'], 'name': a['name'],
            'value': a['value']['amount'], 'currency': a['value']['currency'],
            'sheet': a.get('sheetName', ''), 'category': a.get('category'),
        } for a in sorted(matches, key=lambda x: -abs(x['value']['amount']))], indent=2))
        return

    for a in sorted(matches, key=lambda x: -abs(x['value']['amount'])):
        print(f"{a['name'][:45]:45s} ${a['value']['amount']:>12,.2f}  [{a.get('sheetName', '?')}]")

def cmd_update(args):
    api_key, secret = get_config(args)
    body = {}
    if args.value is not None: body['value'] = args.value
    if args.name is not None: body['name'] = args.name
    if args.cost is not None: body['cost'] = args.cost
    if args.description is not None: body['description'] = args.description
    if not body:
        print("Nothing to update. Use --value, --name, --cost, or --description.", file=sys.stderr)
        sys.exit(1)

    if not args.confirm:
        print(f"Update item {args.item_id} with: {json.dumps(body)}", file=sys.stderr)
        print("Add --confirm to execute this write operation.", file=sys.stderr)
        sys.exit(1)

    result = make_request(api_key, secret, f"/api/v3/data/item/{args.item_id}", method="POST", body=body)
    print(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Kubera portfolio CLI")
    parser.add_argument('--api-key', help='Kubera API key')
    parser.add_argument('--secret', help='Kubera API secret')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('portfolios')
    p.add_argument('--json', dest='json_out', action='store_true', help='JSON output')

    p = sub.add_parser('summary')
    p.add_argument('--portfolio', help='Portfolio ID')
    p.add_argument('--json', dest='json_out', action='store_true', help='JSON output')

    p = sub.add_parser('json')
    p.add_argument('--portfolio', help='Portfolio ID')

    p = sub.add_parser('assets')
    p.add_argument('--portfolio', help='Portfolio ID')
    p.add_argument('--sheet', help='Filter by sheet name (e.g. Crypto, Equities, Retirement)')
    p.add_argument('--sort', choices=['value', 'name', 'gain'], default='value')
    p.add_argument('--json', dest='json_out', action='store_true', help='JSON output')

    p = sub.add_parser('search')
    p.add_argument('query', help='Search by name, ticker, or account')
    p.add_argument('--portfolio', help='Portfolio ID')
    p.add_argument('--json', dest='json_out', action='store_true', help='JSON output')

    p = sub.add_parser('update')
    p.add_argument('item_id', help='Asset or debt ID')
    p.add_argument('--value', type=float)
    p.add_argument('--name', type=str)
    p.add_argument('--cost', type=float)
    p.add_argument('--description', type=str)
    p.add_argument('--confirm', action='store_true', help='Required to execute the write')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        'portfolios': cmd_portfolios, 'summary': cmd_summary,
        'json': cmd_json, 'assets': cmd_assets,
        'search': cmd_search, 'update': cmd_update
    }
    cmds[args.command](args)

if __name__ == "__main__":
    main()
