#!/usr/bin/env python3
"""
signer.py — Helper for OpenClaw agents to sign and submit Solana transactions.

The Optionns API returns instructions array format. This module constructs, signs,
and submits transactions from those instructions.

Usage in agent code:
    from signer import sign_and_submit
    
    tx_sig = sign_and_submit(
        instructions=response['instructions'],
        keypair_path='~/.config/optionns/agent_keypair.json',
        rpc_url='https://api.devnet.solana.com'
    )
"""
import json
import base64
import time
from pathlib import Path
import urllib.request
import urllib.error


def _validate_devnet_rpc(rpc_url: str) -> None:
    """
    Enforce devnet-only operation by validating RPC URL.
    
    Raises:
        ValueError: If RPC URL does not contain a devnet pattern
    """
    ALLOWED_DEVNET_PATTERNS = [
        "devnet.solana.com",
        "api.devnet.solana.com",
        "devnet.helius-rpc.com",
        "rpc.devnet.soo.network",
        "devnet.rpcpool.com",
        "localhost",  # Allow local devnet validator
        "127.0.0.1"   # Allow local devnet validator
    ]
    
    # Check if URL contains any allowed devnet pattern
    url_lower = rpc_url.lower()
    if not any(pattern in url_lower for pattern in ALLOWED_DEVNET_PATTERNS):
        raise ValueError(
            f"SECURITY: RPC URL must be a devnet endpoint. Got: {rpc_url}\n"
            f"Allowed patterns: {', '.join(ALLOWED_DEVNET_PATTERNS)}\n"
            "This skill is devnet-only for security. Never use mainnet keys or endpoints."
        )


def sign_and_submit(
    instructions: list,
    keypair_path: str,
    rpc_url: str = "https://api.devnet.solana.com",
    timeout: int = 30,
    max_retries: int = 3
) -> str:
    """
    Construct, sign, and submit a Solana transaction from instructions array.
    
    Includes automatic retry with fresh blockhash on BlockhashNotFound errors,
    which commonly occur with the free Solana devnet RPC.
    
    Args:
        instructions: List of instruction dicts with programId, keys, data
        keypair_path: Path to Solana keypair JSON file
        rpc_url: Solana RPC endpoint
        timeout: Max seconds to wait for confirmation
        max_retries: Max attempts on blockhash-related failures
        
    Returns:
        Transaction signature on success
        
    Raises:
        Exception: If construction, signing, or submission fails
    """
    # Validate RPC URL is devnet-only
    _validate_devnet_rpc(rpc_url)
    
    try:
        from solders.keypair import Keypair
        from solders.transaction import Transaction
        from solders.message import Message
        from solders.instruction import Instruction, AccountMeta
        from solders.pubkey import Pubkey
        from solders.hash import Hash
    except ImportError:
        raise ImportError(
            "solders library required. Install with: pip install solders"
        )
    
    # Load keypair
    keypair_path = Path(keypair_path).expanduser()
    if not keypair_path.exists():
        raise FileNotFoundError(f"Keypair not found: {keypair_path}")
    
    with open(keypair_path, "r") as f:
        secret = json.load(f)
    
    kp = Keypair.from_bytes(bytes(secret))
    
    # Construct instructions from API response (only once — these don't change)
    solana_instructions = []
    for ix in instructions:
        program_id = Pubkey.from_string(ix["programId"])
        
        accounts = []
        for acc in ix["keys"]:
            accounts.append(AccountMeta(
                pubkey=Pubkey.from_string(acc["pubkey"]),
                is_signer=acc["isSigner"],
                is_writable=acc["isWritable"]
            ))
        
        data = base64.b64decode(ix["data"])
        
        solana_instructions.append(Instruction(
            program_id=program_id,
            accounts=accounts,
            data=data
        ))
    
    # Retry loop: fetch fresh blockhash → sign → send
    # Free devnet RPC often returns stale blockhashes, so retry is essential
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            # Fetch fresh blockhash
            blockhash_payload = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getLatestBlockhash",
                "params": [{"commitment": "confirmed"}]
            }).encode("utf-8")
            
            req = urllib.request.Request(
                rpc_url,
                data=blockhash_payload,
                headers={"Content-Type": "application/json"}
            )
            
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    blockhash_result = json.loads(resp.read().decode())
            except urllib.error.URLError as e:
                raise Exception(f"Failed to fetch blockhash: {e}")
            
            if "error" in blockhash_result:
                raise Exception(f"Blockhash RPC error: {blockhash_result['error']}")
            
            blockhash_str = blockhash_result["result"]["value"]["blockhash"]
            blockhash = Hash.from_string(blockhash_str)
            
            # Create message with payer = agent keypair
            msg = Message.new_with_blockhash(
                solana_instructions,
                kp.pubkey(),
                blockhash
            )
            
            # Sign and create transaction
            sig = kp.sign_message(bytes(msg))
            tx = Transaction.populate(msg, [sig])
            
            # Serialize signed tx
            tx_bytes = bytes(tx)
            tx_b64 = base64.b64encode(tx_bytes).decode("ascii")
            
            # Submit via JSON-RPC
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    tx_b64,
                    {"encoding": "base64", "preflightCommitment": "confirmed"}
                ]
            }).encode("utf-8")
            
            req = urllib.request.Request(
                rpc_url,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode())
            except urllib.error.URLError as e:
                raise Exception(f"RPC request failed: {e}")
            
            if "error" in result:
                error_msg = str(result["error"])
                # Retry on blockhash-related failures
                if any(keyword in error_msg.lower() for keyword in [
                    "blockhash not found", "blockhashnot found",
                    "blockhash_not_found", "block height exceeded"
                ]):
                    print(f"Stale blockhash (attempt {attempt}/{max_retries}), retrying with fresh blockhash...", file=__import__('sys').stderr)
                    last_error = Exception(f"RPC error: {result['error']}")
                    time.sleep(1 * attempt)  # Brief backoff
                    continue
                raise Exception(f"RPC error: {result['error']}")
            
            tx_sig = result.get("result", "")
            
            # Confirm the tx landed
            for _ in range(timeout // 2):
                time.sleep(2)
                confirm_payload = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "getSignatureStatuses",
                    "params": [[tx_sig], {"searchTransactionHistory": True}]
                }).encode("utf-8")
                
                confirm_req = urllib.request.Request(
                    rpc_url,
                    data=confirm_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                try:
                    with urllib.request.urlopen(confirm_req, timeout=10) as resp:
                        confirm_result = json.loads(resp.read().decode())
                    
                    statuses = confirm_result.get("result", {}).get("value", [None])
                    if statuses and statuses[0] is not None:
                        if statuses[0].get("err"):
                            err = statuses[0]["err"]
                            err_str = str(err)
                            # Retry on blockhash expiry detected at confirmation
                            if "blockhash" in err_str.lower():
                                print(f"Blockhash expired at confirmation (attempt {attempt}/{max_retries}), retrying...", file=__import__('sys').stderr)
                                last_error = Exception(f"Transaction failed on-chain: {err}")
                                time.sleep(1 * attempt)
                                break  # Break confirmation loop to retry
                            raise Exception(f"Transaction failed on-chain: {err}")
                        return tx_sig
                except Exception as e:
                    if "blockhash" in str(e).lower() and attempt < max_retries:
                        last_error = e
                        break
                    if "Transaction failed" in str(e):
                        raise
                    continue
            else:
                # Confirmation loop ended without confirming
                raise Exception(f"Transaction submitted but not confirmed after {timeout}s: {tx_sig}")
            
            # If we broke out of confirmation loop for retry, continue
            continue
            
        except Exception as e:
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["blockhash", "block height"]) and attempt < max_retries:
                last_error = e
                print(f"Blockhash error (attempt {attempt}/{max_retries}): {e}", file=__import__('sys').stderr)
                time.sleep(1 * attempt)
                continue
            raise
    
    # All retries exhausted
    raise last_error or Exception(f"Transaction failed after {max_retries} attempts")




if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Sign and submit Solana transactions')
    parser.add_argument('--stdin', action='store_true', required=True,
                        help='Read instructions JSON from stdin')
    parser.add_argument('--keypair', required=True, help='Path to keypair file')
    parser.add_argument('--rpc', default='https://api.devnet.solana.com', help='RPC URL')
    
    args = parser.parse_args()
    
    try:
        instructions_json = sys.stdin.read().strip()
        if not instructions_json:
            print("Error: No instructions provided via stdin", file=sys.stderr)
            sys.exit(1)
        
        # Normalize instructions
        instructions_raw = json.loads(instructions_json)
        instructions = []
        for ix in instructions_raw:
            normalized = {
                'programId': ix.get('programId') or ix.get('program_id'),
                'data': ix.get('data'),
                'keys': []
            }
            # Normalize accounts -> keys
            accounts = ix.get('accounts', ix.get('keys', []))
            for acc in accounts:
                normalized['keys'].append({
                    'pubkey': acc.get('pubkey'),
                    'isSigner': acc.get('is_signer') if acc.get('is_signer') is not None else acc.get('isSigner'),
                    'isWritable': acc.get('is_writable') if acc.get('is_writable') is not None else acc.get('isWritable')
                })
            instructions.append(normalized)
        
        tx_sig = sign_and_submit(
            instructions=instructions,
            keypair_path=args.keypair,
            rpc_url=args.rpc
        )
        print(tx_sig)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

