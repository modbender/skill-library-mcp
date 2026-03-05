#!/usr/bin/env python3
"""
SECURITY-CRITICAL: USDC transfer script for OpenClaw agents.

- Loads private key from FILE only (never from args/stdin/env)
- stdout outputs ONLY JSON result (never key material)
- Designed to be called via subprocess — DO NOT import this module
- All logs go to stderr

Usage:
    python3 sign_and_send.py --keypair-path PATH --to ADDRESS --amount AMOUNT
    python3 sign_and_send.py --keypair-path PATH --to ADDRESS --amount AMOUNT --dry-run

Output (stdout): JSON {"success": true, "tx_signature": "...", "amount": ...}
         or:     JSON {"success": false, "error": "..."}
"""

import argparse
import json
import os
import stat
import sys
import time
from decimal import Decimal


USDC_MINT_MAINNET = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_DECIMALS = 6
DEFAULT_RPC = "https://api.mainnet-beta.solana.com"

# Allowed mint addresses (whitelist — only USDC)
ALLOWED_MINTS = {
    USDC_MINT_MAINNET,
}

# Allowed RPC endpoints (whitelist — prevents SSRF via arbitrary URLs)
ALLOWED_RPC_URLS = {
    "https://api.mainnet-beta.solana.com",
    "https://api.devnet.solana.com",
    "https://api.testnet.solana.com",
}

# Solana program addresses
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ATA_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"


def log(msg: str) -> None:
    """Log to stderr (safe — never contains key material)."""
    print(f"[sign_and_send] {msg}", file=sys.stderr)


def output_result(success: bool, **kwargs) -> None:
    """Print structured JSON result to stdout."""
    result = {"success": success, **kwargs}
    print(json.dumps(result))


def main() -> int:
    parser = argparse.ArgumentParser(description="Send USDC on Solana via subprocess")
    parser.add_argument("--keypair-path", required=True, help="Path to wallet file")
    parser.add_argument("--to", required=True, help="Destination Solana address")
    parser.add_argument("--amount", required=True, type=str, help="USDC amount to send")
    parser.add_argument("--rpc-url", default=DEFAULT_RPC, help="Solana RPC URL")
    parser.add_argument("--mint", default=USDC_MINT_MAINNET, help="Token mint address")
    parser.add_argument("--dry-run", action="store_true", help="Build but don't send tx")
    args = parser.parse_args()

    # --- Validate amount ---
    try:
        amount = Decimal(args.amount)
    except Exception:
        output_result(False, error=f"Invalid amount: {args.amount}")
        return 1

    if amount <= 0:
        output_result(False, error="Amount must be positive")
        return 1

    # --- Validate mint whitelist ---
    if args.mint not in ALLOWED_MINTS:
        output_result(False, error=f"Disallowed mint address: {args.mint}. Only USDC is supported.")
        return 1

    # --- Validate RPC URL whitelist ---
    if args.rpc_url not in ALLOWED_RPC_URLS:
        output_result(False, error=f"RPC URL not in whitelist: {args.rpc_url}")
        return 1

    # --- Validate keypair file ---
    keypair_path = os.path.expanduser(args.keypair_path)
    if not os.path.exists(keypair_path):
        output_result(False, error=f"Wallet file not found: {keypair_path}")
        return 1

    # Check file permissions (warn if too open)
    try:
        file_stat = os.stat(keypair_path)
        if file_stat.st_mode & (stat.S_IRGRP | stat.S_IROTH):
            log("WARNING: Wallet file has group/other read permissions. Run: chmod 600 " + keypair_path)
    except OSError:
        pass

    # --- Import dependencies ---
    try:
        from solders.keypair import Keypair  # type: ignore[import-untyped]
        from solders.pubkey import Pubkey  # type: ignore[import-untyped]
        from solders.transaction import Transaction  # type: ignore[import-untyped]
        from solders.message import Message  # type: ignore[import-untyped]
        from solders.hash import Hash  # type: ignore[import-untyped]
        from solders.instruction import Instruction, AccountMeta  # type: ignore[import-untyped]
    except ImportError:
        output_result(False, error="solders not installed. Run: pip install \"solders>=0.21.0,<1.0\"")
        return 1

    try:
        import httpx
    except ImportError:
        output_result(False, error="httpx not installed. Run: pip install httpx")
        return 1

    # --- Load keypair from file ---
    try:
        kp = _load_keypair(keypair_path, Keypair)
    except Exception as e:
        output_result(False, error=f"Failed to load wallet: {e}")
        return 1

    sender_pubkey = kp.pubkey()

    # --- Validate destination address ---
    try:
        dest_pubkey = Pubkey.from_string(args.to)
    except Exception:
        output_result(False, error=f"Invalid destination address: {args.to}")
        return 1

    mint_pubkey = Pubkey.from_string(args.mint)
    token_program = Pubkey.from_string(TOKEN_PROGRAM_ID)
    ata_program = Pubkey.from_string(ATA_PROGRAM_ID)
    system_program = Pubkey.from_string(SYSTEM_PROGRAM_ID)

    # --- Derive ATAs ---
    sender_ata, _ = Pubkey.find_program_address(
        [bytes(sender_pubkey), bytes(token_program), bytes(mint_pubkey)],
        ata_program,
    )
    dest_ata, _ = Pubkey.find_program_address(
        [bytes(dest_pubkey), bytes(token_program), bytes(mint_pubkey)],
        ata_program,
    )

    log(f"From: {sender_pubkey} (ATA: {sender_ata})")
    log(f"To:   {args.to} (ATA: {dest_ata})")
    log(f"Amount: ${amount} USDC")
    log(f"Network: {args.rpc_url}")

    if args.dry_run:
        output_result(
            True,
            dry_run=True,
            from_wallet=str(sender_pubkey),
            from_ata=str(sender_ata),
            to_wallet=args.to,
            to_ata=str(dest_ata),
            amount=float(amount),
            mint=args.mint,
        )
        return 0

    # --- Build and send transaction ---
    try:
        client = httpx.Client(timeout=30)

        # Check sender ATA balance
        sender_balance = _get_token_balance(client, args.rpc_url, str(sender_ata))
        if sender_balance is None:
            output_result(False, error=f"Sender ATA {sender_ata} not found or has no balance")
            return 1

        if Decimal(str(sender_balance)) < amount:
            output_result(
                False,
                error=f"Insufficient balance: have ${sender_balance}, need ${amount}",
                balance=sender_balance,
            )
            return 1

        # Check if dest ATA exists
        dest_ata_exists = _account_exists(client, args.rpc_url, str(dest_ata))

        # Get recent blockhash
        blockhash_resp = _rpc_call(client, args.rpc_url, "getLatestBlockhash", [{"commitment": "finalized"}])
        blockhash = Hash.from_string(blockhash_resp["value"]["blockhash"])

        # Build instructions
        instructions = []

        # Create dest ATA if needed
        if not dest_ata_exists:
            log("Destination ATA does not exist, will create (costs ~0.002 SOL)")
            create_ata_ix = _build_create_ata_instruction(
                sender_pubkey, dest_pubkey, mint_pubkey,
                token_program, ata_program, system_program,
            )
            instructions.append(create_ata_ix)

        # Transfer USDC
        amount_raw = int(amount * (10 ** USDC_DECIMALS))
        transfer_ix = _build_transfer_checked_instruction(
            sender_pubkey, sender_ata, dest_ata, mint_pubkey,
            amount_raw, USDC_DECIMALS, token_program,
        )
        instructions.append(transfer_ix)

        # Build and sign transaction
        msg = Message.new_with_blockhash(instructions, sender_pubkey, blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([kp], blockhash)

        # Send
        tx_bytes = bytes(tx)
        import base64 as b64
        tx_b64 = b64.b64encode(tx_bytes).decode()

        send_resp = _rpc_call(client, args.rpc_url, "sendTransaction", [
            tx_b64,
            {"encoding": "base64", "skipPreflight": False, "preflightCommitment": "confirmed"},
        ])
        tx_sig = send_resp

        log(f"Transaction sent: {tx_sig}")
        log("Waiting for confirmation...")

        # Wait for confirmation (max 60s)
        confirmed = _wait_for_confirmation(client, args.rpc_url, tx_sig, timeout=60)
        if confirmed:
            log(f"Transaction confirmed: {tx_sig}")
            output_result(True, tx_signature=tx_sig, amount=float(amount))
            return 0
        else:
            log(f"Transaction may not be confirmed yet: {tx_sig}")
            output_result(False, tx_signature=tx_sig, amount=float(amount), error="confirmation_timeout")
            return 1

    except Exception as e:
        output_result(False, error=str(e))
        return 1


# --- Helper functions ---

def _load_keypair(path: str, keypair_cls):
    """Load keypair from wallet file (JSON array format with optional comment header)."""
    with open(path) as f:
        content = f.read()

    lines = [line for line in content.strip().split("\n") if not line.startswith("#")]
    raw = json.loads("".join(lines))

    if not isinstance(raw, list) or len(raw) != 64:
        raise ValueError(f"Invalid wallet file: expected 64-byte array, got {type(raw).__name__} of length {len(raw) if isinstance(raw, list) else 'N/A'}")
    if not all(isinstance(b, int) and 0 <= b <= 255 for b in raw):
        raise ValueError("Invalid wallet file: all values must be integers 0-255")

    return keypair_cls.from_bytes(bytes(raw))


def _rpc_call(client, rpc_url: str, method: str, params: list):
    """Make a JSON-RPC call to Solana."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    resp = client.post(rpc_url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data.get("result")


def _get_token_balance(client, rpc_url: str, ata_address: str):
    """Get USDC balance of a token account. Returns float or None."""
    try:
        result = _rpc_call(client, rpc_url, "getTokenAccountBalance", [ata_address])
        if result and result.get("value"):
            return float(result["value"]["uiAmount"])
    except Exception:
        pass
    return None


def _account_exists(client, rpc_url: str, address: str) -> bool:
    """Check if a Solana account exists."""
    try:
        result = _rpc_call(client, rpc_url, "getAccountInfo", [address, {"encoding": "base64"}])
        return result.get("value") is not None
    except Exception:
        return False


def _wait_for_confirmation(client, rpc_url: str, tx_sig: str, timeout: int = 60) -> bool:
    """Poll for transaction confirmation."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = _rpc_call(client, rpc_url, "getSignatureStatuses", [[tx_sig]])
            if result and result.get("value") and result["value"][0]:
                status = result["value"][0]
                if status.get("confirmationStatus") in ("confirmed", "finalized"):
                    return True
                if status.get("err"):
                    raise RuntimeError(f"Transaction failed: {status['err']}")
        except RuntimeError:
            raise
        except Exception:
            pass
        time.sleep(2)
    return False


def _build_create_ata_instruction(payer, owner, mint, token_program, ata_program, system_program):
    """Build a CreateAssociatedTokenAccount instruction."""
    from solders.instruction import Instruction, AccountMeta  # type: ignore[import-untyped]
    from solders.pubkey import Pubkey  # type: ignore[import-untyped]

    # Derive the ATA address
    ata, _ = Pubkey.find_program_address(
        [bytes(owner), bytes(token_program), bytes(mint)],
        ata_program,
    )

    return Instruction(
        program_id=ata_program,
        accounts=[
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
            AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
        ],
        data=b"",
    )


def _build_transfer_checked_instruction(
    owner, source_ata, dest_ata, mint, amount_raw: int, decimals: int, token_program,
):
    """Build a TransferChecked instruction for SPL tokens."""
    from solders.instruction import Instruction, AccountMeta  # type: ignore[import-untyped]
    import struct

    # TransferChecked instruction index = 12
    data = struct.pack("<B", 12) + struct.pack("<Q", amount_raw) + struct.pack("<B", decimals)

    return Instruction(
        program_id=token_program,
        accounts=[
            AccountMeta(pubkey=source_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=dest_ata, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner, is_signer=True, is_writable=False),
        ],
        data=data,
    )


if __name__ == "__main__":
    sys.exit(main())
