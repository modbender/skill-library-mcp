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
        print(f"Error: Failed to get CKB address from wallet: {ret}", file=sys.stderr)
        return None
    ckb_addr = ret.get('data')
    print(f"✓ CKB address from wallet: {ckb_addr}")
    return ckb_addr


'''
# web5-cli pds check-username --username david
{
  "success": true,
  "data": "valid"
}
# web5-cli pds check-username --username xxx
{
  "success": true,
  "data": "invalid"
}
'''
def check_username_available(username: str) -> bool:
    """Check if username is available on PDS."""
    ret = run_command(
        ['web5-cli', 'pds', 'check-username', '--username', username],
        check=False
    )
    if not ret or not ret.get('success'):
        print(f"Username check failed: {ret}", file=sys.stderr)
        return False
    status = ret.get('data')
    if status != 'valid':
        print(f"Username '{username}' is not available (status: {status})", file=sys.stderr)
        return False
    print(f"✓ Username '{username}' is available")
    return True


'''
# web5-cli keystore get
{
  "success": true,
  "data": "did:key:zQ3shQ5Cf4nECdEmw4rx17EH97pBNwYbAWBmz31sVjAgJEmTS"
}
'''
def create_or_get_keystore() -> Optional[str]:
    """Create signing key and return didkey or get exist didkey."""
    ret = run_command(['web5-cli', 'keystore', 'new'])
    if not ret:
        print(f"Failed to run cmd keystore new", file=sys.stderr)
        return None
    if not ret.get('success') and ret.get('error') and "already exists" in ret.get('error'):
        print("Keystore already exists, trying to get existing didkey...")
        ret = run_command(['web5-cli', 'keystore', 'get'])
        if not ret or not ret.get('success'):
            print(f"Error: Failed to get existing didkey from keystore", file=sys.stderr)
            return None
    didkey = ret.get('data')
    print(f"✓ Keystore didkey: {didkey}")
    return didkey


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
# web5-cli did build-create-tx --username david3 --pds web5.bbsfans.dev --didkey did:key:zQ3shQ5Cf4nECdEmw4rx17EH97pBNwYbAWBmz31sVjAgJEmTS --output-path ./create-did-tx.json
{
  "success": true,
  "data": {
    "did": "did:ckb:hcmmt3cal2d2tlgyugbfmox4dsaecgke",
    "txPath": "./create-did-tx.json"
  }
}
'''
def build_create_did_transaction(
    username: str,
    pds: str,
    didkey: str,
    output_path: str
) -> Optional[str]:
    """Build DID create transaction."""
    ret = run_command([
        'web5-cli', 'did', 'build-create-tx',
        '--username', username,
        '--pds', pds,
        '--didkey', didkey,
        '--output-path', output_path
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error building DID create transaction: {ret}", file=sys.stderr)
        return None
    did = ret.get('data', {}).get('did')
    print(f"✓ Built create DID transaction for DID: {did}, output path: {output_path}")
    return did


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
        
        if ret and ret.get('success') and 'committed' in str(ret.get('data')).lower():
            print("✓ Transaction committed!")
            return True
        
        remaining = max_retries - attempt - 1
        print(f"Transaction pending... ({remaining} retries left)")
        time.sleep(retry_delay)
    
    print("⚠️  Timeout waiting for transaction", file=sys.stderr)
    return False


'''
pds create-account --pds web5.bbsfans.dev --username david2 --didkey did:key:zQ3shQmJ8bD79MGya89W1gdtWfHtohXKrrdxd3CEXQyJnzQmW --did did:ckb:xdif6yxk7v37usfdu4xhpacoutzr2mls --ckb-address ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqvwae5x73tj6gaqj8n33vft722usg062lg6ds5ky
{
  "success": true,
  "data": {
    "accessJwt": "eyJhbGciOiJFUzI1NksiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NzIzNjQ5NTksImV4cCI6MTc3MjM3MjE1OSwibmJmIjoxNzcyMzY0OTU5LCJzdWIiOiJkaWQ6Y2tiOnhkaWY2eXhrN3YzN3VzZmR1NHhocGFjb3V0enIybWxzIiwiYXVkIjoiZGlkOndlYjp3ZWI1LmJic2ZhbnMuZGV2Iiwic2NvcGUiOiJjb20uYXRwcm90by5hY2Nlc3MifQ.axniYN_SLJLxCBkv6vq_gO6UAfd2nLZbCStPsEi2CFsxT-tzrE1r3xyE_JSw73IdXSKRtjsQqMOnxo6_ILiKyg",
    "refreshJwt": "eyJhbGciOiJFUzI1NksiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NzIzNjQ5NTksImV4cCI6MTc4MDE0MDk1OSwibmJmIjoxNzcyMzY0OTU5LCJzdWIiOiJkaWQ6Y2tiOnhkaWY2eXhrN3YzN3VzZmR1NHhocGFjb3V0enIybWxzIiwiYXVkIjoiZGlkOndlYjp3ZWI1LmJic2ZhbnMuZGV2IiwianRpIjoidEhKalpQNk41TXBZRGl3TGg3TG53Y1VBakVoeXMxOXIiLCJzY29wZSI6ImNvbS5hdHByb3RvLnJlZnJlc2gifQ.ULoVjVoRcCj9IIHEDO_8pLJZudIJ0Q5u2l6RPIpMJfR12difjmvbDPEBZ6Qln2zQlb_8qgWEZEVav5RY0i6nrw",
    "handle": "david2.web5.bbsfans.dev",
    "did": "did:ckb:xdif6yxk7v37usfdu4xhpacoutzr2mls"
  }
}
'''
def create_pds_account(
    pds: str,
    username: str,
    didkey: str,
    did: str,
    ckb_addr: str
) -> Optional[dict]:
    """Create PDS account."""
    print("Waiting 30s for indexer to sync...")
    time.sleep(30)
    
    ret = run_command([
        'web5-cli', 'pds', 'create-account',
        '--pds', pds,
        '--username', username,
        '--didkey', didkey,
        '--did', did,
        '--ckb-address', ckb_addr
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error creating PDS account: {ret}", file=sys.stderr)
        return False
    
    userinfo = ret.get('data')
    print(f"✓ PDS account created: {userinfo}")
    return userinfo


'''
 pds write --pds web5.bbsfans.dev --accessJwt eyJhbGciOiJFUzI1NksiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NzIzNjY4NTcsImV4cCI6MTc3MjM3NDA1NywibmJmIjoxNzcyMzY2ODU3LCJzdWIiOiJkaWQ6Y2tiOnhkaWY2eXhrN3YzN3VzZmR1NHhocGFjb3V0enIybWxzIiwiYXVkIjoiZGlkOndlYjp3ZWI1LmJic2ZhbnMuZGV2Iiwic2NvcGUiOiJjb20uYXRwcm90by5hY2Nlc3MifQ.wJuJ9Q4HV7ooUKCr82rKUi4iJNSc5VrElEJM7Z17yv14VINwtpysWJgr-UyU-mX0RGVDAYzvfPFB27d6fv3kSg --didkey did:key:zQ3shQmJ8bD79MGya89W1gdtWfHtohXKrrdxd3CEXQyJnzQmW --did did:ckb:xdif6yxk7v37usfdu4xhpacoutzr2mls --rkey self --data '{"$type": "app.actor.profile",  "displayName": "david2", "handle": "david2.web5.bbsfans.dev" }'

{
  "success": true,
  "data": true
}
'''
def write_user_profile(
    username: str,
    pds: str,
    access_jwt: str,
    didkey: str,
    did: str,
    display_name: str
) -> bool:
    """Write user profile to PDS."""
    handle = f"{username}.{pds}"
    ret = run_command([
        'web5-cli', 'pds', 'write',
        '--pds', pds,
        '--accessJwt', access_jwt,
        '--didkey', didkey,
        '--did', did,
        '--rkey', 'self',
        '--data', json.dumps({
            "$type": "app.actor.profile",
            "displayName": display_name,
            "handle": handle
        })
    ], check=False)
    
    if not ret or not ret.get('success'):
        print(f"Error writing user profile: {ret}", file=sys.stderr)
        return False
    print(f"✓ User profile written to PDS for handle '{handle}' with display name '{display_name}'")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Create a complete Web5 account',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  CKB_NETWORK    CKB network to use (default: ckb_testnet)

Example:
  python create_account.py alice web5.bbsfans.dev
        """
    )
    parser.add_argument('username', help='Username for the new account')
    parser.add_argument('pds', nargs='?', default='web5.bbsfans.dev',
                        help='PDS hostname (default: web5.bbsfans.dev)')
    
    args = parser.parse_args()
    
    ckb_network = os.environ.get('CKB_NETWORK', 'ckb_testnet')
    
    print("=" * 50)
    print("Web5 Account Creation Workflow")
    print("=" * 50)
    print(f"Username: {args.username}")
    print(f"PDS: {args.pds}")
    print(f"Network: {ckb_network}")
    print("")

    print("Step 0: Get CKB address from wallet")
    ckb_addr = get_ckb_address_from_wallet()
    if not ckb_addr:
        print("\n❌ Failed to get CKB address from wallet", file=sys.stderr)
        sys.exit(1)
    
    print("Step 1: Checking username availability...")
    if not check_username_available(args.username):
        print(f"\n❌ Username '{args.username}' is not available")
        sys.exit(1)
    
    print("Step 2: Creating keystore...")
    didkey = create_or_get_keystore()
    if not didkey:
        print("\n❌ Failed to create or get keystore")
        sys.exit(1)

    print("Step 3: Checking username availability...")
    did = get_did_by_username(args.username, args.pds)
    if did is None:
        print(f"\n❌ Failed to check username availability for '{args.username}'")
        sys.exit(1)
    if did != "":
        print(f"\n❌ Username '{args.username}' already exists with DID {did}")
        sys.exit(1)
    
    print("Step 4: Creating build create did transaction...")
    now = int(time.time())
    tx_file = tempfile.mktemp(suffix='.json', prefix=f'did-create-{args.username}--{now}-')
    did = build_create_did_transaction(args.username, args.pds, didkey, tx_file)
    if not did:
        print("\n❌ Failed to build create DID transaction")
        sys.exit(1)
    
    print("Step 5: Sending transaction...")
    tx_hash = send_transaction(tx_file)
    if not tx_hash:
        print("\n❌ Failed to send transaction")
        sys.exit(1)
    
    print("Step 6: Waiting for transaction confirmation...")
    if not wait_for_confirmation(tx_hash):
        print("\n⚠️  Transaction not confirmed in time")
        sys.exit(1)
    
    print("Step 7: Create PDS account")
    userinfo = create_pds_account(args.pds, args.username, didkey, did, ckb_addr)
    if not userinfo:
        print("\n❌ Failed to create PDS account")
        sys.exit(1)
    
    print("Step 8: Writing user profile")
    acess_jwt = userinfo.get('accessJwt')
    if not acess_jwt:
        print("\n❌ Failed to get access JWT from PDS account creation response")
        sys.exit(1)
    display_name = f"{args.username}-openclaw"
    if not write_user_profile(args.username, args.pds, acess_jwt, didkey, did, display_name):
        print("\n❌ Failed to write user profile to PDS")
        sys.exit(1)
    
    # Success
    print("\n" + "=" * 50)
    print("Account Creation Complete!")
    print("=" * 50)
    print(f"Username: {args.username}")
    print(f"DID: {did}")
    print(f"Handle: {args.username}.{args.pds}")
    print(f"didkey: {didkey}")
    print(f"CKB Address: {ckb_addr}")
    print(f"PDS: {args.pds}")
    print("")


if __name__ == '__main__':
    main()
