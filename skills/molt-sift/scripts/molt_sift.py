#!/usr/bin/env python3
"""
Molt Sift - Data validation and signal extraction CLI
Sift through noise, extract quality signals, earn bounties.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict
import time

# Local imports (will be in package)
try:
    from sifter import Sifter
    from bounty_agent import BountyAgent
    from api_server import start_api_server
except ImportError:
    print("Error: Run 'pip install -e .' from molt-sift directory")
    sys.exit(1)


def load_json(path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {path}: {e}")
        sys.exit(1)


def save_json(data: Dict[str, Any], path: str) -> None:
    """Save JSON to file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[OK] Saved to {path}")


def cmd_validate(args):
    """Validate data against schema or rules."""
    data = load_json(args.input)
    
    if args.schema:
        schema = load_json(args.schema)
    else:
        schema = None
    
    sifter = Sifter(rules=args.rules or "json-strict")
    result = sifter.validate(data, schema)
    
    # Pretty print result
    print(json.dumps(result, indent=2))
    
    # Save if requested
    if args.output:
        save_json(result, args.output)
    
    # Exit with error if validation failed
    if result['status'] == 'failed':
        sys.exit(1)


def cmd_sift(args):
    """Sift data for high-confidence signals."""
    data = load_json(args.input)
    
    sifter = Sifter(rules=args.rules or "crypto")
    result = sifter.sift(data)
    
    print(json.dumps(result, indent=2))
    
    if args.output:
        save_json(result, args.output)


def cmd_bounty(args):
    """Manage bounty hunting."""
    agent = BountyAgent(payout_address=args.payout_address)
    
    if args.command == "claim":
        if args.auto:
            print("[SIFT] Starting bounty agent (watching PayAClaw)...")
            print(f"   Payout address: {args.payout_address}")
            agent.watch_and_claim()
        elif args.job_id:
            print(f"Claiming bounty {args.job_id}...")
            result = agent.claim_bounty(args.job_id)
            print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        status = agent.get_status()
        print(json.dumps(status, indent=2))


def cmd_api(args):
    """Start API server for bounty endpoint."""
    if args.command == "start":
        port = args.port or 8000
        print(f"[SIFT] Starting Molt Sift API on port {port}...")
        print(f"   Bounty endpoint: http://localhost:{port}/bounty")
        start_api_server(port=port)


def main():
    parser = argparse.ArgumentParser(
        description="Molt Sift - Extract signals, validate outputs, hunt bounties",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  molt-sift validate --input data.json --schema schema.json
  molt-sift sift --input output.txt --rules crypto
  molt-sift bounty claim --auto --payout YOUR_SOLANA_ADDRESS
  molt-sift api start --port 8000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # VALIDATE command
    validate_parser = subparsers.add_parser('validate', help='Validate data against schema')
    validate_parser.add_argument('--input', required=True, help='Input JSON file')
    validate_parser.add_argument('--schema', help='Schema JSON file')
    validate_parser.add_argument('--rules', default='json-strict', help='Validation rules (crypto, trading, sentiment)')
    validate_parser.add_argument('--output', help='Save result to file')
    validate_parser.set_defaults(func=cmd_validate)
    
    # SIFT command
    sift_parser = subparsers.add_parser('sift', help='Sift data for signals')
    sift_parser.add_argument('--input', required=True, help='Input JSON file')
    sift_parser.add_argument('--rules', default='crypto', help='Signal rules')
    sift_parser.add_argument('--output', help='Save result to file')
    sift_parser.set_defaults(func=cmd_sift)
    
    # BOUNTY command
    bounty_parser = subparsers.add_parser('bounty', help='Manage bounty jobs')
    bounty_sub = bounty_parser.add_subparsers(dest='bounty_command')
    
    claim_parser = bounty_sub.add_parser('claim', help='Claim a bounty job')
    claim_parser.add_argument('--auto', action='store_true', help='Watch and auto-claim')
    claim_parser.add_argument('--job-id', help='Specific job ID to claim')
    claim_parser.add_argument('--payout-address', required=True, help='Solana address for payouts')
    claim_parser.set_defaults(func=cmd_bounty, command='claim')
    
    status_parser = bounty_sub.add_parser('status', help='Check bounty agent status')
    status_parser.add_argument('--payout-address', required=True)
    status_parser.set_defaults(func=cmd_bounty, command='status')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Manage API server')
    api_sub = api_parser.add_subparsers(dest='api_command')
    
    start_parser = api_sub.add_parser('start', help='Start API server')
    start_parser.add_argument('--port', type=int, default=8000)
    start_parser.set_defaults(func=cmd_api, command='start')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
