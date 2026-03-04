#!/usr/bin/env python3
"""Register an ACN agent on the ERC-8004 Identity Registry.

Supports two scenarios:
  Scenario 1 — Zero-wallet agent (auto-generate):
    python scripts/register_onchain.py --acn-api-key acn_xxx --chain base

  Scenario 2 — Existing wallet:
    python scripts/register_onchain.py --acn-api-key acn_xxx \\
        --private-key 0x1234... --chain base

Dependencies (auto-installed if missing):
  pip install web3 httpx

Env vars (alternative to CLI flags):
  ACN_API_URL        ACN server base URL (default: https://acn-production.up.railway.app)
  ACN_API_KEY        ACN API key
  WALLET_PRIVATE_KEY Ethereum private key (hex)
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

def _ensure_deps() -> None:
    missing = []
    try:
        import web3  # type: ignore[import-untyped]  # noqa: F401
    except ImportError:
        missing.append("web3")
    try:
        import httpx  # noqa: F401
    except ImportError:
        missing.append("httpx")
    if missing:
        print(f"Installing missing dependencies: {', '.join(missing)} ...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing, "-q"])


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

CHAIN_CONFIGS: dict[str, dict] = {
    "base": {
        "rpc": "https://mainnet.base.org",
        "chain_id": 8453,
        "identity_contract": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
        "namespace": "eip155:8453",
    },
    "base-sepolia": {
        "rpc": "https://sepolia.base.org",
        "chain_id": 84532,
        "identity_contract": "0x8004A818BFB912233c491871b3d84c89A494BD9e",
        "namespace": "eip155:84532",
    },
}

IDENTITY_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "agentURI", "type": "string"}],
        "name": "register",
        "outputs": [{"internalType": "uint256", "name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "agentURI", "type": "string"},
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
        ],
        "name": "Registered",
        "type": "event",
    },
]


def _save_wallet(path: str, private_key: str, address: str) -> None:
    """Append wallet credentials to a .env file (skips existing keys)."""
    keys_to_add = {"WALLET_PRIVATE_KEY": private_key, "WALLET_ADDRESS": address}
    existing: set[str] = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if "=" in line:
                    existing.add(line.split("=")[0].strip())
    with open(path, "a") as f:
        for key, value in keys_to_add.items():
            if key not in existing:
                f.write(f"{key}={value}\n")


async def _get_agent_id(acn_url: str, api_key: str) -> str:
    """Look up the ACN agent ID via /api/v1/agents/me using the API key."""
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{acn_url}/api/v1/agents/me",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        agent_id: str = data.get("agent_id") or data.get("id") or ""
        if not agent_id:
            raise RuntimeError(f"Could not determine agent_id from /me response: {data}")
        return agent_id


async def _bind_to_acn(
    acn_url: str,
    api_key: str,
    agent_id: str,
    token_id: int,
    chain: str,
    tx_hash: str,
) -> None:
    """POST /api/v1/onchain/agents/{agent_id}/bind to register the binding in ACN."""
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{acn_url}/api/v1/onchain/agents/{agent_id}/bind",
            json={"token_id": token_id, "chain": chain, "tx_hash": tx_hash},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()


async def main(args: argparse.Namespace) -> None:
    _ensure_deps()

    from eth_account import Account  # type: ignore[import-untyped]
    from web3 import Web3  # type: ignore[import-untyped]

    acn_url = args.acn_url.rstrip("/")
    api_key = args.acn_api_key
    chain = args.chain

    if chain not in CHAIN_CONFIGS:
        print(f"Error: unsupported chain '{chain}'. Use: {', '.join(CHAIN_CONFIGS)}")
        sys.exit(1)

    cfg = CHAIN_CONFIGS[chain]

    # ---- Wallet ----
    private_key: str = args.private_key or os.getenv("WALLET_PRIVATE_KEY", "")
    if not private_key:
        account = Account.create()
        private_key = account.key.hex()
        wallet_address = account.address
        _save_wallet(".env", private_key, wallet_address)
        print("\nWallet generated and saved to .env")
        print(f"  Address:     {wallet_address}")
        print("  ⚠  Back up your private key!\n")
    else:
        account = Account.from_key(private_key)
        wallet_address = account.address

    # ---- Resolve agent_id ----
    agent_id = args.agent_id or await _get_agent_id(acn_url, api_key)

    # ---- agentURI ----
    agent_registration_url = (
        f"{acn_url}/api/v1/agents/{agent_id}/.well-known/agent-registration.json"
    )

    # ---- Build and send transaction ----
    rpc = args.rpc_url or cfg["rpc"]
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        print(f"Error: cannot connect to RPC at {rpc}")
        sys.exit(1)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(cfg["identity_contract"]),
        abi=IDENTITY_ABI,
    )

    print(f"Broadcasting register({agent_registration_url[:60]}...) on {chain}...")

    tx = contract.functions.register(agent_registration_url).build_transaction(
        {
            "from": wallet_address,
            "nonce": w3.eth.get_transaction_count(wallet_address),
            "chainId": cfg["chain_id"],
        }
    )
    signed = account.sign_transaction(tx)
    tx_hash_bytes = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash_bytes)
    tx_hash = receipt["transactionHash"].hex()

    # ---- Extract token ID ----
    registered_events = contract.events.Registered().process_receipt(receipt)
    if not registered_events:
        print(f"Warning: could not find Registered event. tx: {tx_hash}")
        sys.exit(1)
    token_id: int = registered_events[0]["args"]["agentId"]

    # ---- Bind to ACN ----
    await _bind_to_acn(acn_url, api_key, agent_id, token_id, cfg["namespace"], tx_hash)

    print("\nAgent registered on-chain!")
    print(f"  Token ID:         {token_id}")
    print(f"  Tx Hash:          {tx_hash}")
    print(f"  Chain:            {cfg['namespace']}")
    print(f"  Registration URL: {agent_registration_url}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register an ACN agent on the ERC-8004 Identity Registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--acn-api-key",
        default=os.getenv("ACN_API_KEY", ""),
        required=not os.getenv("ACN_API_KEY"),
        help="ACN API key (or set ACN_API_KEY env var)",
    )
    parser.add_argument(
        "--acn-url",
        default=os.getenv("ACN_API_URL", "https://acn-production.up.railway.app"),
        help="ACN server base URL",
    )
    parser.add_argument(
        "--agent-id",
        default=None,
        help="ACN agent ID (auto-detected via /me if omitted)",
    )
    parser.add_argument(
        "--private-key",
        default=None,
        help="Ethereum private key (hex). Omit to auto-generate a new wallet.",
    )
    parser.add_argument(
        "--chain",
        default="base",
        choices=list(CHAIN_CONFIGS),
        help="Target chain (default: base)",
    )
    parser.add_argument(
        "--rpc-url",
        default=None,
        help="Custom RPC URL (optional)",
    )
    return parser


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()
    asyncio.run(main(args))
