#!/usr/bin/env python3
"""
xenodia_cdp_client.py — Xenodia Agent CLI (Coinbase CDP Server Wallet Mode)

For agents using Coinbase CDP managed wallets (MPC / Server Wallet).
The MPC private key never leaves Coinbase's infrastructure — signing is
done via the CDP API using account.sign_message(). The resulting EIP-191
signature is standard and accepted by Xenodia identically to a local signature.

Prerequisites:
  pip install cdp-sdk requests

Environment variables (all from portal.cdp.coinbase.com):
  CDP_API_KEY_ID       — API Key UUID  (portal → API Keys → "id")
  CDP_API_KEY_SECRET   — API Key private key, base64 Ed25519  (portal → "privateKey")
  CDP_WALLET_SECRET    — Wallet Secret, base64 DER EC key  (portal → Server Wallet page)
                         ⚠ Different key/format from CDP_API_KEY_SECRET — do NOT use the same value
  CDP_WALLET_NAME      — Account name (default: "xenodia-agent")
  XENODIA_BASE_URL     — Xenodia gateway URL (default: https://api.xenodia.xyz)

Usage:
  python3 xenodia_cdp_client.py init                     # Create/load CDP account, print address
  python3 xenodia_cdp_client.py check-wallet             # Show current CDP wallet address
  python3 xenodia_cdp_client.py balance                  # Check Xenodia credit balance
  python3 xenodia_cdp_client.py models                   # List available models
  python3 xenodia_cdp_client.py check-model <name>       # Check specific model
  python3 xenodia_cdp_client.py get-token                # Print JWT to stdout
  python3 xenodia_cdp_client.py chat <model> "<prompt>"  # Make LLM call

Notes:
  - CDP_WALLET_SECRET is required when creating a new account (first run).
  - Signing uses cdp.evm.sign_message(address, message) — raw string input,
    returns '0x...' signature. Do NOT use account.sign_message(SignableMessage),
    that returns wrong recovered address and will fail Xenodia auth.
  - Python 3.14 asyncio workaround: event loop runs in a separate thread.
  - After init, bind the printed address in Xenodia: https://xenodia.xyz/settings

Owner setup guide (ask your owner to do this):
  1. Go to https://portal.cdp.coinbase.com → sign in
  2. Create API Key: top-left menu → API Keys → Create API Key
     → Copy "id" (CDP_API_KEY_ID) and "privateKey" (CDP_API_KEY_SECRET)
  3. Generate Wallet Secret: top-left menu → Server Wallet
     → "Generate Wallet Secret" button (one-time display, copy immediately)
     → This is CDP_WALLET_SECRET (starts with MIGHAgEA..., ~180 chars base64)
  4. Provide all 3 values as environment variables or inline to the script.
"""

import os
import sys
import asyncio
import requests

XENODIA_BASE_URL = os.environ.get("XENODIA_BASE_URL", "https://api.xenodia.xyz")
CDP_WALLET_NAME  = os.environ.get("CDP_WALLET_NAME", "xenodia-agent")

# ── CDP Client ────────────────────────────────────────────────────────────────

def make_cdp_client():
    """Create and return a CDP SDK client (not yet connected)."""
    try:
        from cdp import CdpClient
    except ImportError:
        print("[!] CDP SDK not installed. Run: pip install cdp-sdk", file=sys.stderr)
        sys.exit(1)

    key_id     = os.environ.get("CDP_API_KEY_ID")
    key_secret = os.environ.get("CDP_API_KEY_SECRET")

    if not key_id or not key_secret:
        print("[!] Missing CDP credentials. Set CDP_API_KEY_ID and CDP_API_KEY_SECRET env vars.", file=sys.stderr)
        sys.exit(1)

    kwargs = dict(api_key_id=key_id, api_key_secret=key_secret)

    wallet_secret = os.environ.get("CDP_WALLET_SECRET")
    if wallet_secret:
        kwargs["wallet_secret"] = wallet_secret

    return CdpClient(**kwargs)

# ── Async helpers (all CDP calls must run inside same async with block) ───────

async def _get_or_create_account(cdp):
    try:
        return await cdp.evm.get_or_create_account(CDP_WALLET_NAME)
    except Exception as e:
        err = str(e)
        if "Wallet Secret" in err or "wallet_secret" in err.lower():
            print("[!] CDP requires a Wallet Secret to create a new account.", file=sys.stderr)
            print("    Set CDP_WALLET_SECRET env var (from portal.cdp.coinbase.com → API Keys).", file=sys.stderr)
        else:
            print(f"[!] Failed to get/create CDP account: {e}", file=sys.stderr)
        sys.exit(1)

async def _sign_message(cdp, account, message: str) -> str:
    """Sign an EIP-191 personal message via CDP MPC (no local private key).

    Uses cdp.evm.sign_message(address, message) — accepts raw string,
    returns '0x...' hex signature directly.
    """
    try:
        sig = await cdp.evm.sign_message(address=account.address, message=message)
        return sig
    except Exception as e:
        print(f"[!] CDP signing error: {e}", file=sys.stderr)
        sys.exit(1)

async def _login(cdp, account) -> str:
    """Authenticate with Xenodia and return JWT access token."""
    try:
        resp = requests.post(
            f"{XENODIA_BASE_URL}/v1/auth/challenge",
            json={"wallet_address": account.address}, timeout=10
        )
        resp.raise_for_status()
        data         = resp.json()
        message      = data["message"]
        challenge_id = data["challenge_id"]
    except requests.exceptions.HTTPError as e:
        print(f"[!] Challenge failed: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"[!] Cannot connect to {XENODIA_BASE_URL}. Is Xenodia running?", file=sys.stderr)
        sys.exit(1)

    signature = await _sign_message(cdp, account, message)

    try:
        resp = requests.post(
            f"{XENODIA_BASE_URL}/v1/auth/verify",
            json={"challenge_id": challenge_id, "signature": signature}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()["tokens"]
    except requests.exceptions.HTTPError as e:
        print(f"[!] Auth verify failed: {e.response.text}", file=sys.stderr)
        sys.exit(1)

# ── Sync API calls (no CDP needed after login) ────────────────────────────────

def _get_balance(token: str):
    resp = requests.get(
        f"{XENODIA_BASE_URL}/v1/credits/balance",
        headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    if resp.status_code == 401:
        print("[!] Wallet not bound to any Xenodia owner account.", file=sys.stderr)
        print("    Ask your owner to bind your address at https://xenodia.xyz/settings", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    micro = resp.json().get("balance_micro_usdc", 0)
    print(f"Balance: {micro / 1_000_000:.6f} USDC ({micro} micro-USDC)")

def _list_models(token: str) -> list:
    resp = requests.get(
        f"{XENODIA_BASE_URL}/v1/models",
        headers={"Authorization": f"Bearer {token}"}, timeout=10
    )
    if resp.status_code == 402:
        print("[!] 402 Payment Required: Wallet balance is below minimum threshold ($5).", file=sys.stderr)
        try:
            data = resp.json()
            if "payment" in data:
                pay = data["payment"]
                print("\n--- x402 Payment Info ---", file=sys.stderr)
                print(f"Network : {pay.get('network')}", file=sys.stderr)
                print(f"Token   : {pay.get('currency')}", file=sys.stderr)
                print(f"Address : {pay.get('pay_to_address')}", file=sys.stderr)
                print(f"Amount  : {int(pay.get('amount', 0)) / 1000000} {pay.get('currency')}", file=sys.stderr)
                print("-------------------------\n", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    resp.raise_for_status()
    return resp.json().get("data", [])

def _chat(token: str, model: str, prompt: str):
    resp = requests.post(
        f"{XENODIA_BASE_URL}/v1/chat/completions",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=60
    )
    if resp.status_code == 402:
        print("[!] 402 Payment Required: Insufficient balance or wallet not bound.", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    print(resp.json()["choices"][0]["message"]["content"])

# ── Entry Point ───────────────────────────────────────────────────────────────

def run_async(coro):
    """Run a coroutine safely, avoiding Python 3.14 asyncio shutdown issues."""
    import concurrent.futures

    def _run_in_thread():
        # New thread → fresh event loop, no shutdown_default_executor timeout issue
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_run_in_thread)
        return future.result()

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    cmd = args[0]

    if cmd == "init":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                print("\n" + "="*60)
                print("  CDP SERVER WALLET INITIALIZED")
                print("="*60)
                print(f"  Account Name : {CDP_WALLET_NAME}")
                print(f"  Address      : {account.address}")
                print(f"  Signing Mode : CDP MPC (no private key stored locally)")
                print()
                print("  ► NEXT STEP:")
                print("  Tell your human owner to bind this address:")
                print("  → https://xenodia.xyz/settings  (AGENT_BINDINGS section)")
                print("="*60 + "\n")
        run_async(_run())

    elif cmd == "check-wallet":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                print(f"CDP Wallet Name : {CDP_WALLET_NAME}")
                print(f"Wallet Address  : {account.address}")
                print("Signing Mode    : CDP MPC (no private key locally)")
                print("Tip: Run 'balance' to verify binding status.")
        run_async(_run())

    elif cmd == "balance":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                token   = (await _login(cdp, account))["access_token"]
                _get_balance(token)
        run_async(_run())

    elif cmd == "models":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                token   = (await _login(cdp, account))["access_token"]
                models  = _list_models(token)
                print("Available models:")
                for m in models:
                    print(f"  - {m['id']:<35} ({m.get('owned_by', 'unknown')})")
        run_async(_run())

    elif cmd == "check-model":
        if len(args) < 2:
            print("[!] Usage: check-model <model_name>", file=sys.stderr)
            sys.exit(1)
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                token   = (await _login(cdp, account))["access_token"]
                models  = _list_models(token)
                ids     = [m["id"] for m in models]
                name    = args[1]
                if name in ids:
                    print(f"{name}: AVAILABLE")
                else:
                    print(f"{name}: NOT FOUND")
                    print(f"Available: {', '.join(ids)}")
        run_async(_run())

    elif cmd == "get-token":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                token   = (await _login(cdp, account))["access_token"]
                print(token)
        run_async(_run())

    elif cmd == "get-api-key":
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                access_token = (await _login(cdp, account))["access_token"]
                resp = requests.get(f"{XENODIA_BASE_URL}/v1/me/api-keys", headers={"Authorization": f"Bearer {access_token}"})
                data = resp.json().get("data")
                if data and data.get("token"):
                    print(data["token"])
                else:
                    resp = requests.post(f"{XENODIA_BASE_URL}/v1/me/api-keys", headers={"Authorization": f"Bearer {access_token}"})
                    print(resp.json()["data"]["token"])
        run_async(_run())

    elif cmd == "chat":
        if len(args) < 3:
            print("[!] Usage: chat <model> '<prompt>'", file=sys.stderr)
            sys.exit(1)
        async def _run():
            async with make_cdp_client() as cdp:
                account = await _get_or_create_account(cdp)
                token   = (await _login(cdp, account))["access_token"]
                _chat(token, args[1], args[2])
        run_async(_run())

    else:
        print(f"[!] Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
