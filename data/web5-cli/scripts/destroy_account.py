#!/usr/bin/env python3
"""
Create a complete Web5 account - full workflow script
Usage: python create_account.py <username> <pds-hostname>
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple


def run_command(cmd: list, check: bool = True) -> Optional[dict]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )
    if check and result.returncode != 0:
        print(f"Error running: {' '.join(cmd)}", file=sys.stderr)
        print(f"stderr: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    try:
        # Try to parse the output as JSON
        ret = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}", file=sys.stderr)
        print(f"Output was: {output}", file=sys.stderr)
        return None
    return ret


'''
# web5-cli pds get-did-by-username --username david3 --pds web5.bbsfans.dev
{
  "success": true,
  "data": "did:ckb:qic3ao6eugrrsosddr3kdoe3mpn6ujf3"
}
'''
def get_did_by_username(username: str, pds: str) -> Optional[str]:
    """Get DID for a username from PDS."""
    ret = run_command(
        ['web5-cli', 'pds', 'get-did-by-username', '--username', username, '--pds', pds],
        check=False
    )
    if not ret or not ret.get('success'):
        print(f"Username check failed: {ret}", file=sys.stderr)
        return None
    did = ret.get('data')
    print(f"✓ DID for username '{username}': {did}")
    return did


'''
# web5-cli keystore get
{
  "success": true,
  "data": "did:key:zQ3shQ5Cf4nECdEmw4rx17EH97pBNwYbAWBmz31sVjAgJEmTS"
}
'''
def get_didkey_from_keystore() -> Optional[str]:
    """Get didkey from keystore."""
    ret = run_command(['web5-cli', 'keystore', 'get'])
    if not ret or not ret.get('success'):
        print(f"Error: Failed to get didkey from keystore", file=sys.stderr)
        return None
    didkey = ret.get('data')
    print(f"✓ Retrieved didkey from keystore: {didkey}")
    return didkey


'''
# web5-cli wallet get
{
  "success": true,
  "data": "ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvedp8eum9zyn44tegsudhn8a3em5lhj3spm3p90"
}
'''
def get_ckb_address_from_wallet() -> Optional[str]:
    """Get CKB address from wallet."""
    ret = run_command(['web5-cli', 'wallet', 'get'])
    if not ret or not ret.get('success'):
        print(f"Error: Failed to get CKB address from wallet", file=sys.stderr)
        return None
    ckb_addr = ret.get('data')
    print(f"✓ Retrieved CKB address from wallet: {ckb_addr}")
    return ckb_addr


def delete_pds_account(pds: str, did: str, didkey: str, ckb_address: str) -> bool:
    """Delete account from PDS."""
    ret = run_command([
        'web5-cli', 'pds', 'delete-account',
        '--did', did,
        '--didkey', didkey,
        '--ckb-address', ckb_address,
        '--pds', pds
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error deleting PDS account: {ret}", file=sys.stderr)
        return False
    print(f"✓ PDS account deletion requested for DID: {did}")
    return True

'''
# web5-cli did list --ckb-addr ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvedp8eum9zyn44tegsudhn8a3em5lhj3spm3p90
{
  "success": true,
  "data": [
    {
      "txHash": "0x6b30d851b246d0aeff6ca74db39b8127084eb836fe4518e0d144f36e79fe3edb",
      "index": 0,
      "capacity": "372",
      "args": "0x8205b03bc4a1a3193a431c76a1b89b63dbea24bb",
      "did": "did:ckb:qic3ao6eugrrsosddr3kdoe3mpn6ujf3",
      "didMetadata": "{\"services\":{\"atproto_pds\":{\"type\":\"AtprotoPersonalDataServer\",\"endpoint\":\"https://web5.bbsfans.dev\"}},\"alsoKnownAs\":[\"at://david3.web5.bbsfans.dev\"],\"verificationMethods\":{\"atproto\":\"did:key:zQ3shQ5Cf4nECdEmw4rx17EH97pBNwYbAWBmz31sVjAgJEmTS\"}}"
    }
  ]
}
'''
def list_dids_by_ckb_address(ckb_address: str) -> Optional[list]:
    """List DIDs associated with a CKB address."""
    ret = run_command(['web5-cli', 'did', 'list', '--ckb-addr', ckb_address], check=False)
    if not ret or not ret.get('success'):
        print(f"Error listing DIDs: {ret}", file=sys.stderr)
        return None
    did_list = ret.get('data')
    print(f"✓ Listed DIDs for CKB address {ckb_address}: {did_list}")
    return did_list


def build_destroy_did_transaction(
    args: str,
    output_path: str
) -> bool:
    """Build DID destroy transaction."""
    ret = run_command([
        'web5-cli', 'did', 'build-destroy-tx',
        '--args', args,
        '--output-path', output_path
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error building DID destroy transaction: {ret}", file=sys.stderr)
        return False
    print(f"✓ Built DID destroy transaction with args: {args}, output path: {output_path}")
    return True


def send_transaction(tx_path: str) -> Optional[str]:
    """Send transaction and return tx hash."""
    ret = run_command([
        'web5-cli', 'wallet', 'send-tx',
        '--tx-path', tx_path
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error sending transaction: {ret}", file=sys.stderr)
        return None
    tx_hash = ret.get('data')
    print(f"✓ Transaction sent, hash: {tx_hash}")
    return tx_hash


def wait_for_confirmation(tx_hash: str, max_retries: int = 30, retry_delay: int = 10) -> bool:
    """Wait for transaction to be confirmed."""
    print("Checking transaction status (this may take a few minutes)...")
    
    for attempt in range(max_retries):
        ret = run_command([
            'web5-cli', 'wallet', 'check-tx',
            '--tx-hash', tx_hash
        ], check=False)
        
        if ret and ret.get('success') and 'committed' in str(ret.get('data', '')).lower():
            print("✓ Transaction committed!")
            return True
        
        remaining = max_retries - attempt - 1
        print(f"Transaction pending... ({remaining} retries left)")
        time.sleep(retry_delay)
    
    print("⚠️  Timeout waiting for transaction", file=sys.stderr)
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Destroy an existing Web5 account',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  CKB_NETWORK    CKB network to use (default: ckb_testnet)

Example:
  python destroy_account.py alice web5.bbsfans.dev
        """
    )
    parser.add_argument('username', help='Username for the account to destroy')
    parser.add_argument('pds', nargs='?', default='web5.bbsfans.dev',
                        help='PDS hostname (default: web5.bbsfans.dev)')
    
    args = parser.parse_args()
    
    ckb_network = os.environ.get('CKB_NETWORK', 'ckb_testnet')
    
    print("=" * 50)
    print("Web5 Account Destruction Workflow")
    print("=" * 50)
    print(f"Username: {args.username}")
    print(f"PDS: {args.pds}")
    print(f"Network: {ckb_network}")
    print("")
    
    print("Step 1: Check username exists")
    did = get_did_by_username(args.username, args.pds)
    if not did.startswith("did:ckb:"):
        print(f"\n❌ Username '{args.username}' does not exist")
        sys.exit(1)
    
    print("Step 2: Get didkey from keystore")
    didkey = get_didkey_from_keystore()
    if not didkey:
        print("\n❌ Failed to get didkey from keystore", file=sys.stderr)
        sys.exit(1)
    
    print("Step 3: Get CKB address from wallet")
    ckb_addr = get_ckb_address_from_wallet()
    if not ckb_addr:
        print("\n❌ Failed to get CKB address from wallet", file=sys.stderr)
        sys.exit(1)
    
    print("Step 4: Delete PDS account")
    if not delete_pds_account(args.pds, did, didkey, ckb_addr):
        print("\n❌ Failed to delete PDS account", file=sys.stderr)
        sys.exit(1)
    
    print("Step 5: List DIDs by CKB address")
    did_list = list_dids_by_ckb_address(ckb_addr)
    if did_list is None:
        print("\n❌ Failed to list DIDs by CKB address", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Found DIDs for CKB address {ckb_addr}:")
        found = False
        did_args = ""
        for item in did_list:
            if item['did'] == did:
                found = True
                did_args = item['args']
                break
        if not found:
            print(f"⚠️  DID {did} not found in list of DIDs for CKB address {ckb_addr}")
            sys.exit(1)
    
    print("Step 6: Build destroy DID transaction")
    now = int(time.time())
    tx_file = tempfile.mktemp(suffix='.json', prefix=f'did-destroy-{args.username}-{now}-')
    if not build_destroy_did_transaction(did_args, tx_file):
        print("\n❌ Failed to build DID destroy transaction")
        sys.exit(1)
    
    print("Step 7: Send transaction")
    tx_hash = send_transaction(tx_file)
    if not tx_hash:
        print("\n❌ Failed to send DID destroy transaction")
        sys.exit(1)
    
    print("Step 8: Wait for confirmation")
    if not wait_for_confirmation(tx_hash):
        print("\n⚠️  DID destroy transaction not confirmed in time")
        sys.exit(1)

    # Success
    print("\n" + "=" * 50)
    print("Account destruction Complete!")
    print("=" * 50)
    print(f"Username: {args.username}")
    print(f"DID: {did}")
    print(f"CKB Address: {ckb_addr}")
    print(f"PDS: {args.pds}")
    print("")


if __name__ == '__main__':
    main()
