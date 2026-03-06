#!/usr/bin/env python3
"""
xenodia_client.py — Xenodia Agent CLI (Local Keypair Mode)
Usage:
  python xenodia_client.py init                     # Scenario B: generate new local wallet
  python xenodia_client.py check-wallet             # Scenario A: show existing wallet address
  python xenodia_client.py balance                  # Scenario D: check credit balance
  python xenodia_client.py models                   # Scenario E: list available models
  python xenodia_client.py check-model <model>      # Scenario E: check specific model
  python xenodia_client.py get-token                # Print JWT to stdout (for SDK use)
  python xenodia_client.py chat <model> "<prompt>"  # Scenario F: make LLM call
"""

import os
import sys
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

XENODIA_BASE_URL = os.environ.get("XENODIA_BASE_URL", "https://api.xenodia.xyz")
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".xenodia_agent_key")

# ── Wallet ────────────────────────────────────────────────────────────────────

def wallet_exists() -> bool:
    return os.path.exists(KEY_FILE)

def load_wallet() -> Account:
    if not wallet_exists():
        print("[!] No agent wallet found. Run: python xenodia_client.py init", file=sys.stderr)
        sys.exit(1)
    with open(KEY_FILE, "r") as f:
        pk = f.read().strip()
    return Account.from_key(pk)

def create_wallet() -> Account:
    acc = Account.create()
    with open(KEY_FILE, "w") as f:
        f.write(acc.key.hex())
    return acc

# ── Auth ──────────────────────────────────────────────────────────────────────

def login(acc: Account) -> str:
    try:
        resp = requests.post(
            f"{XENODIA_BASE_URL}/v1/auth/challenge",
            json={"wallet_address": acc.address}, timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        signable_message = encode_defunct(text=data["message"])
        signature = acc.sign_message(signable_message).signature.hex()

        resp = requests.post(
            f"{XENODIA_BASE_URL}/v1/auth/verify",
            json={"challenge_id": data["challenge_id"], "signature": signature}, timeout=10
        )
        resp.raise_for_status()
        return resp.json()["tokens"]

    except requests.exceptions.HTTPError as e:
        print(f"[!] Auth failed: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"[!] Cannot connect to {XENODIA_BASE_URL}. Is the gateway running?", file=sys.stderr)
        sys.exit(1)

# ── API ───────────────────────────────────────────────────────────────────────

def get_balance(token: str):
    resp = requests.get(f"{XENODIA_BASE_URL}/v1/credits/balance",
                        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    if resp.status_code == 401:
        print("[!] Wallet is not bound to any Xenodia owner account.", file=sys.stderr)
        print("    Ask your owner to bind your address at https://xenodia.xyz/settings", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    micro = resp.json().get("balance_micro_usdc", 0)
    print(f"Balance: {micro / 1_000_000:.6f} USDC ({micro} micro-USDC)")

def list_models(token: str) -> list:
    resp = requests.get(f"{XENODIA_BASE_URL}/v1/models",
                        headers={"Authorization": f"Bearer {token}"}, timeout=10)
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

def check_model_cmd(token: str, model_name: str):
    models = list_models(token)
    ids = [m["id"] for m in models]
    if model_name in ids:
        print(f"{model_name}: AVAILABLE")
    else:
        print(f"{model_name}: NOT FOUND")
        print(f"Available: {', '.join(ids)}")

def chat(token: str, model: str, prompt: str):
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

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    cmd = args[0]

    if cmd == "init":
        if wallet_exists():
            acc = load_wallet()
            print(f"[!] Wallet already exists: {acc.address}")
            print(f"    Key file: {KEY_FILE}")
        else:
            acc = create_wallet()
            print("\n" + "="*60)
            print("  NEW AGENT WALLET GENERATED (Local Keypair Mode)")
            print("="*60)
            print(f"  Address : {acc.address}")
            print(f"  Key file: {KEY_FILE}")
            print()
            print("  ► NEXT STEP:")
            print("  Tell your human owner to bind this address:")
            print("  → https://xenodia.xyz/settings  (AGENT_BINDINGS section)")
            print("="*60 + "\n")

    elif cmd == "check-wallet":
        if not wallet_exists():
            print("[!] No wallet found. Run: python xenodia_client.py init")
            sys.exit(1)
        acc = load_wallet()
        print(f"Wallet Address : {acc.address}")
        print(f"Key File       : {KEY_FILE}")
        print("Tip: Run 'balance' to verify the wallet is bound and funded.")

    elif cmd == "balance":
        acc = load_wallet()
        get_balance(login(acc)["access_token"])

    elif cmd == "models":
        acc = load_wallet()
        models = list_models(login(acc)["access_token"])
        print("Available models:")
        for m in models:
            print(f"  - {m['id']:<35} ({m.get('owned_by', 'unknown')})")

    elif cmd == "check-model":
        if len(args) < 2:
            print("[!] Usage: python xenodia_client.py check-model <model_name>", file=sys.stderr)
            sys.exit(1)
        acc = load_wallet()
        check_model_cmd(login(acc)["access_token"], args[1])

    elif cmd == "get-token":
        acc = load_wallet()
        print(login(acc)["access_token"])  # Clean stdout only (for shell capture)

    elif cmd == "get-api-key":
        acc = load_wallet()
        access_token = login(acc)["access_token"]
        
        # Try to get existing key
        resp = requests.get(f"{XENODIA_BASE_URL}/v1/me/api-keys", headers={"Authorization": f"Bearer {access_token}"})
        data = resp.json().get("data")
        if data and data.get("token"):
            print(data["token"])
        else:
            # Generate a new one
            resp = requests.post(f"{XENODIA_BASE_URL}/v1/me/api-keys", headers={"Authorization": f"Bearer {access_token}"})
            print(resp.json()["data"]["token"])
    elif cmd == "chat":
        if len(args) < 3:
            print("[!] Usage: python xenodia_client.py chat <model> '<prompt>'", file=sys.stderr)
            sys.exit(1)
        acc = load_wallet()
        chat(login(acc)["access_token"], args[1], args[2])

    else:
        print(f"[!] Unknown command: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
