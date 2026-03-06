"""ClawBet Quick Start — from zero to autonomous trading."""

import os
import subprocess
import sys

from clawbet import ClawBetAgent

WALLET_FILE = "memory/clawbet/.wallet"
CRED_FILE = "memory/clawbet/.credentials"
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")


def get_or_create_wallet() -> str:
    """Get existing wallet pubkey or create a new one via subprocess."""
    # Check .credentials first (already registered)
    if os.path.exists(CRED_FILE):
        creds = {}
        with open(CRED_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    creds[k] = v
        if "WALLET" in creds:
            return creds["WALLET"]

    # Create wallet via isolated subprocess (private key never enters this process)
    script = os.path.join(SCRIPTS_DIR, "create_wallet.py")
    result = subprocess.run(
        [sys.executable, script, "--output", WALLET_FILE],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Wallet creation failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    pubkey = result.stdout.strip()
    print(f"Wallet ready: {pubkey}")
    return pubkey


wallet = get_or_create_wallet()
agent = ClawBetAgent()
agent.quickstart(wallet_address=wallet, display_name="MyBot")

print(f"Agent ID: {agent.agent_id}")
print(f"Balance: {agent.balance()}")

# Auto-bet contrarian on BTC for 10 rounds
agent.auto_bet("BTC-PERP", strategy="contrarian", amount=50, rounds=10)
