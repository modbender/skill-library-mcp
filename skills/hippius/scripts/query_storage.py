#!/usr/bin/env python3
"""
Hippius Storage Query Script

Query storage information via:
1. S3 endpoint (s3.hippius.com) — for bucket/object listing (recommended)
2. Hippius RPC API (api.hippius.io) — for blockchain-level file/credit info

Requires either:
- S3: HIPPIUS_S3_ACCESS_KEY + HIPPIUS_S3_SECRET_KEY env vars (and aws CLI)
- RPC: Account address in SS58 format
"""

import json
import os
import subprocess
import sys
import argparse
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_error(message: str) -> None:
    print(f"{Colors.RED}ERROR: {message}{Colors.NC}", file=sys.stderr)


def print_success(message: str) -> None:
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_warning(message: str) -> None:
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def print_info(message: str) -> None:
    print(f"{Colors.BLUE}{message}{Colors.NC}")


def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


# ---------------------------------------------------------------------------
# S3 Queries (recommended)
# ---------------------------------------------------------------------------

def get_s3_env() -> dict:
    """Get S3 environment variables for aws CLI calls."""
    access_key = os.environ.get("HIPPIUS_S3_ACCESS_KEY", "")
    secret_key = os.environ.get("HIPPIUS_S3_SECRET_KEY", "")
    if not access_key or not secret_key:
        return {}
    return {
        **os.environ,
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
    }


def s3_cmd(args: list, env: dict) -> Optional[str]:
    """Run an aws s3 command and return stdout."""
    cmd = [
        "aws", "--endpoint-url", "https://s3.hippius.com",
        "--region", "decentralized",
    ] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print_error(f"aws s3 command failed: {result.stderr.strip()}")
            return None
        return result.stdout
    except FileNotFoundError:
        print_error("AWS CLI not found. Install with: pip install awscli")
        return None


def query_s3_buckets(env: dict) -> None:
    """List S3 buckets."""
    print_info("Listing S3 buckets...")
    print()
    output = s3_cmd(["s3", "ls"], env)
    if output is None:
        return
    if not output.strip():
        print_warning("No buckets found")
        return

    print("=" * 60)
    print("  S3 Buckets")
    print("=" * 60)
    print()
    lines = output.strip().split("\n")
    for line in lines:
        print(f"  {line}")
    print()
    print_success(f"Total buckets: {len(lines)}")


def query_s3_objects(bucket: str, env: dict, prefix: str = "") -> None:
    """List objects in an S3 bucket."""
    target = f"s3://{bucket}/{prefix}"
    print_info(f"Listing objects in {target}...")
    print()
    output = s3_cmd(["s3", "ls", target, "--recursive", "--human-readable"], env)
    if output is None:
        return
    if not output.strip():
        print_warning(f"No objects found in {target}")
        return

    print("=" * 60)
    print(f"  Objects in {target}")
    print("=" * 60)
    print()
    lines = output.strip().split("\n")
    for line in lines:
        print(f"  {line}")
    print()
    print_success(f"Total objects: {len(lines)}")


# ---------------------------------------------------------------------------
# RPC Queries (blockchain-level)
# ---------------------------------------------------------------------------

def rpc_call(method: str, params: list, api_url: str = "http://api.hippius.io") -> Optional[Dict[str, Any]]:
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    headers = {"Content-Type": "application/json"}
    try:
        request = Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers
        )
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "error" in data:
                print_error(f"RPC Error: {data['error']}")
                return None
            return data.get("result")
    except HTTPError as e:
        print_error(f"HTTP Error: {e.code} - {e.reason}")
        return None
    except URLError as e:
        print_error(f"Connection Error: {e.reason}")
        return None
    except json.JSONDecodeError:
        print_error("Failed to parse API response")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return None


def query_user_files(account_id: str) -> None:
    print_info(f"Querying files for account: {account_id}")
    print()
    result = rpc_call("get_user_files", [account_id])
    if result is None:
        print_error("Failed to retrieve user files")
        return
    if not result or len(result) == 0:
        print_warning("No files found for this account")
        return

    print("=" * 60)
    print("  User Files (IPFS/Blockchain)")
    print("=" * 60)
    print()
    for idx, file_info in enumerate(result, 1):
        print(f"File #{idx}")
        print(f"  Hash: {file_info.get('hash', 'N/A')}")
        print(f"  Name: {file_info.get('name', 'N/A')}")
        print(f"  Size: {format_bytes(file_info.get('size', 0))}")
        miners = file_info.get('miners', [])
        print(f"  Pinning Miners: {', '.join(miners) if miners else 'None'}")
        print()
    print_success(f"Total files: {len(result)}")


def query_total_storage(account_id: str) -> None:
    print_info(f"Querying total storage for account: {account_id}")
    print()
    result = rpc_call("calculate_total_file_size", [account_id])
    if result is None:
        print_error("Failed to retrieve total storage")
        return

    print("=" * 60)
    print("  Total Storage Used (Blockchain)")
    print("=" * 60)
    print()
    total_bytes = int(result)
    print(f"  Total: {format_bytes(total_bytes)} ({total_bytes:,} bytes)")
    print()
    print_success("Storage query complete")


def query_account_credits(account_id: str) -> None:
    print_info(f"Querying credits for account: {account_id}")
    print()
    result = rpc_call("get_free_credits_rpc", [account_id])
    if result is None:
        print_error("Failed to retrieve account credits")
        return

    print("=" * 60)
    print("  Account Credits")
    print("=" * 60)
    print()
    credits = float(result) if result else 0.0
    print(f"  Free Credits: {credits:.4f}")
    print()
    if credits < 1.0:
        print_warning("Low credit balance - consider adding credits")
    else:
        print_success("Credit balance is healthy")


def main():
    parser = argparse.ArgumentParser(
        description="Query Hippius storage information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List S3 buckets (requires HIPPIUS_S3_ACCESS_KEY/SECRET_KEY)
  %(prog)s --s3-buckets

  # List objects in an S3 bucket
  %(prog)s --s3-objects my-bucket

  # List objects with a prefix
  %(prog)s --s3-objects my-bucket --prefix snapshots/

  # Query blockchain files for an account
  %(prog)s --account 5GrwvaEF... --files

  # Query credits for an account
  %(prog)s --account 5GrwvaEF... --credits

  # Query all blockchain info for an account
  %(prog)s --account 5GrwvaEF...
        """
    )

    # S3 queries
    s3_group = parser.add_argument_group("S3 queries (recommended)")
    s3_group.add_argument(
        "--s3-buckets",
        action="store_true",
        help="List S3 buckets"
    )
    s3_group.add_argument(
        "--s3-objects",
        metavar="BUCKET",
        help="List objects in an S3 bucket"
    )
    s3_group.add_argument(
        "--prefix",
        default="",
        help="Key prefix filter for --s3-objects"
    )

    # RPC queries
    rpc_group = parser.add_argument_group("Blockchain/RPC queries")
    rpc_group.add_argument(
        "--account",
        metavar="ADDRESS",
        help="Hippius account address (SS58 format)"
    )
    rpc_group.add_argument(
        "--files",
        action="store_true",
        help="Query user files (requires --account)"
    )
    rpc_group.add_argument(
        "--storage",
        action="store_true",
        help="Query total storage used (requires --account)"
    )
    rpc_group.add_argument(
        "--credits",
        action="store_true",
        help="Query account credits (requires --account)"
    )
    rpc_group.add_argument(
        "--api-url",
        default="http://api.hippius.io",
        help="Hippius RPC API URL (default: http://api.hippius.io)"
    )

    args = parser.parse_args()

    ran_something = False

    # S3 queries
    s3_env = get_s3_env()
    if args.s3_buckets:
        if not s3_env:
            print_error("Set HIPPIUS_S3_ACCESS_KEY and HIPPIUS_S3_SECRET_KEY environment variables")
            sys.exit(1)
        query_s3_buckets(s3_env)
        ran_something = True

    if args.s3_objects:
        if not s3_env:
            print_error("Set HIPPIUS_S3_ACCESS_KEY and HIPPIUS_S3_SECRET_KEY environment variables")
            sys.exit(1)
        query_s3_objects(args.s3_objects, s3_env, args.prefix)
        ran_something = True

    # RPC queries
    if args.account:
        specific = args.files or args.storage or args.credits
        if not specific:
            # Query all
            query_user_files(args.account)
            print()
            query_total_storage(args.account)
            print()
            query_account_credits(args.account)
        else:
            if args.files:
                query_user_files(args.account)
                print()
            if args.storage:
                query_total_storage(args.account)
                print()
            if args.credits:
                query_account_credits(args.account)
                print()
        ran_something = True

    if not ran_something:
        # Default: try S3 buckets if creds available, otherwise show help
        if s3_env:
            query_s3_buckets(s3_env)
        else:
            parser.print_help()
            print()
            print_info("Quick start:")
            print("  Set HIPPIUS_S3_ACCESS_KEY and HIPPIUS_S3_SECRET_KEY, then run:")
            print(f"  {sys.argv[0]} --s3-buckets")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
