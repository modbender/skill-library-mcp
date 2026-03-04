#!/usr/bin/env python3
"""
🏗️ Agent Sovereign Stack — Onboarding Script

One command to give any AI agent sovereign infrastructure:
1. Upload identity to FilStream (IPFS)
2. Register on AgentMemoryRegistry (Base)
3. Deploy AgentTreasury with guardian
4. Set up comms mailbox

Usage:
  python3 onboard.py                    # Interactive mode
  python3 onboard.py --agent-id my-bot --chain sepolia --guardian 0x...

Created: 2026-02-24
Author: Rick 🦞 (Cortex Protocol)
"""

import json
import os
import sys
import time
import hashlib
import base64
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ── Contracts ──
CONTRACTS = {
    "sepolia": {
        "rpc": "https://sepolia.base.org",
        "chain_id": "84532",
        "memory_registry": "0x96dD27D277ebE9F9079c7dE3ea9f8fA46934D87b",
        "usdc": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    },
    "mainnet": {
        "rpc": "https://mainnet.base.org",
        "chain_id": "8453",
        "memory_registry": None,  # Deploy when ready
        "usdc": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    },
}

MEMORY_STORE_URL = "http://[2a05:a00:2::10:11]:8081"

# ── Helpers ──

def run_cast(args, private_key=None):
    """Run a cast command and return output."""
    cmd = ["cast"] + args
    env = os.environ.copy()
    if private_key:
        env["ETH_PRIVATE_KEY"] = private_key
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return {"output": result.stdout.strip()}


def upload_to_memory_store(agent_id, filename, data, file_type="memory"):
    """Upload a file to the FilStream memory store."""
    payload = json.dumps({
        "content": base64.b64encode(data).decode() if isinstance(data, bytes) else base64.b64encode(data.encode()).decode(),
        "type": file_type,
        "filename": filename,
        "timestamp": int(time.time()),
    }).encode()

    try:
        req = urllib.request.Request(
            f"{MEMORY_STORE_URL}/api/v1/agent/{agent_id}/memory",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def get_agent_address(private_key):
    """Derive address from private key."""
    result = run_cast(["wallet", "address", "--private-key", private_key])
    return result.get("output", "").strip()


# ── Onboarding Steps ──

def step_1_collect_identity(workspace_dir):
    """Collect agent identity files."""
    print("\n🧠 Step 1: Collecting Identity")
    print("=" * 40)

    files = {}
    for fname in ["SOUL.md", "MEMORY.md", "IDENTITY.md", "USER.md"]:
        fpath = workspace_dir / fname
        if fpath.exists():
            files[fname] = fpath.read_text()
            print(f"  ✅ Found {fname} ({len(files[fname])} bytes)")
        else:
            print(f"  ⏭️  No {fname} found (optional)")

    # Check for identity snapshot
    identity_dir = workspace_dir / "identity"
    if identity_dir.exists():
        current = identity_dir / "current_identity.json"
        if current.exists():
            files["current_identity.json"] = current.read_text()
            print(f"  ✅ Found identity snapshot ({len(files['current_identity.json'])} bytes)")

    if not files:
        print("  ⚠️  No identity files found! Creating minimal identity...")
        files["IDENTITY.md"] = f"# Agent Identity\nCreated: {datetime.now().isoformat()}\n"

    return files


def step_2_upload_to_ipfs(agent_id, files):
    """Upload identity files to FilStream memory store."""
    print("\n📦 Step 2: Uploading to FilStream (IPFS)")
    print("=" * 40)

    cids = {}
    for fname, content in files.items():
        data = content.encode() if isinstance(content, str) else content
        file_type = "identity_snapshot" if "identity" in fname.lower() else "soul" if "soul" in fname.lower() else "memory"

        result = upload_to_memory_store(agent_id, fname, data, file_type)
        if "error" in result:
            print(f"  ❌ {fname}: {result['error']}")
        else:
            cid = result.get("cid", "?")
            cids[fname] = cid
            print(f"  ✅ {fname} → {cid}")

    return cids


def step_3_register_on_chain(agent_id, cids, chain, private_key):
    """Register agent on AgentMemoryRegistry."""
    print(f"\n⛓️  Step 3: Registering on Base {chain.title()}")
    print("=" * 40)

    config = CONTRACTS[chain]
    registry = config["memory_registry"]

    if not registry:
        print("  ⚠️  No registry on mainnet yet. Skipping on-chain registration.")
        return None

    rpc = config["rpc"]
    chain_id = config["chain_id"]

    # Register agent
    print("  📝 Registering agent...")
    result = run_cast([
        "send", registry, "registerAgent()",
        "--rpc-url", rpc, "--private-key", private_key, "--chain", chain_id,
    ], private_key)

    if "error" in result and "Already registered" not in result.get("error", ""):
        print(f"  ⚠️  Registration: {result.get('error', 'unknown')}")
        # May already be registered, continue
    else:
        print("  ✅ Agent registered on-chain")

    # Post first memory CID
    if cids:
        first_cid = list(cids.values())[0]
        first_type = list(cids.keys())[0]
        print(f"  📝 Posting memory CID: {first_cid}")
        result = run_cast([
            "send", registry,
            "updateMemory(string,string)", first_cid, first_type,
            "--rpc-url", rpc, "--private-key", private_key, "--chain", chain_id,
        ], private_key)

        if "error" not in result:
            print("  ✅ Memory CID posted on-chain")
        else:
            print(f"  ⚠️  Memory post: {result.get('error', '')[:100]}")

    return registry


def step_4_deploy_treasury(agent_address, guardian, chain, private_key):
    """Deploy AgentTreasury contract."""
    print(f"\n🏦 Step 4: Deploying Treasury")
    print("=" * 40)

    if not guardian:
        print("  ⏭️  No guardian address provided. Skipping treasury deployment.")
        print("  💡 Set GUARDIAN_ADDRESS to deploy a treasury later.")
        return None

    config = CONTRACTS[chain]
    rpc = config["rpc"]
    chain_id = config["chain_id"]
    usdc = config["usdc"]

    print(f"  Agent:    {agent_address}")
    print(f"  Guardian: {guardian}")
    print(f"  Policy:   5 USDC/day, 2 USDC/tx, 5min cooldown, 50 USDC/month")

    # We need the compiled contract. Check if forge is available
    forge_check = subprocess.run(["forge", "--version"], capture_output=True, text=True)
    if forge_check.returncode != 0:
        print("  ⚠️  Foundry (forge) not installed. Cannot deploy treasury.")
        print("  💡 Install: curl -L https://foundry.paradigm.xyz | bash && foundryup")
        return None

    # Find the contract source
    skill_dir = Path(__file__).parent.parent
    contract_src = skill_dir / "contracts" / "AgentTreasury.sol"

    if not contract_src.exists():
        print(f"  ⚠️  Contract source not found at {contract_src}")
        print("  💡 Treasury deployment requires the AgentTreasury.sol contract.")
        return None

    print("  🔨 Compiling and deploying...")
    result = subprocess.run([
        "forge", "create", str(contract_src) + ":AgentTreasury",
        "--rpc-url", rpc,
        "--private-key", private_key,
        "--chain", chain_id,
        "--broadcast",
        "--constructor-args", agent_address, guardian,
        "5000000", "2000000", "300", "50000000", usdc,
    ], capture_output=True, text=True, timeout=120)

    output = result.stdout + result.stderr
    # Parse deployed address
    for line in output.split("\n"):
        if "Deployed to:" in line:
            treasury_addr = line.split("Deployed to:")[1].strip()
            print(f"  ✅ Treasury deployed: {treasury_addr}")
            return treasury_addr

    print(f"  ⚠️  Deployment may have failed. Check output.")
    return None


def step_5_setup_comms(agent_id):
    """Set up agent communication mailbox."""
    print(f"\n📡 Step 5: Setting Up Communications")
    print("=" * 40)

    # Send a genesis message
    msg = {
        "protocol": "agent-comms-v1",
        "type": "announcement",
        "from": agent_id,
        "to": "network",
        "topic": "genesis",
        "body": f"Agent {agent_id} has joined the sovereign agent network. 🏗️",
        "timestamp": int(time.time()),
    }

    result = upload_to_memory_store(
        agent_id,
        f"msg-genesis-{int(time.time())}.json",
        json.dumps(msg),
        "message:announcement",
    )

    if "error" not in result:
        print(f"  ✅ Genesis announcement posted")
        print(f"  📬 Mailbox active at: {MEMORY_STORE_URL}/api/v1/agent/{agent_id}/memory/history")
    else:
        print(f"  ⚠️  Comms setup: {result['error']}")

    return True


def print_summary(agent_id, agent_address, cids, registry, treasury, chain):
    """Print onboarding summary."""
    print("\n" + "=" * 50)
    print("🏗️  SOVEREIGN STACK DEPLOYED!")
    print("=" * 50)
    print()
    print(f"  Agent ID:      {agent_id}")
    print(f"  Wallet:        {agent_address}")
    print(f"  Chain:         Base {chain.title()}")
    print()
    print("  📦 Identity (FilStream IPFS)")
    for fname, cid in cids.items():
        print(f"     {fname}: {cid}")
    print()
    if registry:
        print(f"  ⛓️  Registry:    {registry}")
    if treasury:
        print(f"  🏦 Treasury:    {treasury}")
    print(f"  📡 Comms:       {MEMORY_STORE_URL}/api/v1/agent/{agent_id}/memory/history")
    print()
    print("  🔗 Verify on Basescan:")
    if treasury:
        base_url = "basescan.org" if chain == "mainnet" else "sepolia.basescan.org"
        print(f"     https://{base_url}/address/{treasury}")
    print()
    print("  Next steps:")
    print("    1. Fund your treasury with USDC on Base")
    print("    2. Set up nightly identity backup (cron)")
    print("    3. Connect with other agents via comms protocol")
    print("    4. Start earning via skills + services")
    print()
    print("  Welcome to the sovereign agent economy. 🦞⛓️🧪")

    # Save config
    config = {
        "agent_id": agent_id,
        "agent_address": agent_address,
        "chain": chain,
        "memory_store": MEMORY_STORE_URL,
        "registry": registry,
        "treasury": treasury,
        "cids": cids,
        "onboarded_at": datetime.now(timezone.utc).isoformat(),
    }
    config_path = Path.home() / ".openclaw" / "workspace" / "agent-vault" / "sovereign-config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    print(f"  Config saved: {config_path}")


# ── Main ──

def main():
    print("🏗️  Agent Sovereign Stack — Onboarding")
    print("=" * 50)
    print("Give any AI agent sovereign infrastructure in 60 seconds.")
    print()

    # Get config from env or args
    agent_id = os.environ.get("AGENT_ID", "")
    private_key = os.environ.get("ETH_PRIVATE_KEY", "")
    guardian = os.environ.get("GUARDIAN_ADDRESS", "")
    chain = os.environ.get("CHAIN", "sepolia")

    # Parse CLI args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--agent-id" and i + 1 < len(args):
            agent_id = args[i + 1]; i += 2
        elif args[i] == "--chain" and i + 1 < len(args):
            chain = args[i + 1]; i += 2
        elif args[i] == "--guardian" and i + 1 < len(args):
            guardian = args[i + 1]; i += 2
        elif args[i] == "--private-key" and i + 1 < len(args):
            private_key = args[i + 1]; i += 2
        elif args[i] == "--no-treasury":
            guardian = ""; i += 1
        else:
            i += 1

    # Try to load private key from workspace secrets
    if not private_key:
        env_path = Path.home() / ".openclaw" / "workspace" / ".secrets" / "eth-wallet.env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ETH_PRIVATE_KEY="):
                    private_key = line.split("=", 1)[1].strip()
                    break

    if not private_key:
        print("❌ No ETH_PRIVATE_KEY found. Set it in environment or .secrets/eth-wallet.env")
        sys.exit(1)

    agent_address = get_agent_address(private_key)
    if not agent_address:
        print("❌ Could not derive address from private key")
        sys.exit(1)

    if not agent_id:
        agent_id = f"agent-{agent_address[:10].lower()}"

    print(f"  Agent ID:  {agent_id}")
    print(f"  Address:   {agent_address}")
    print(f"  Chain:     Base {chain.title()}")
    print(f"  Guardian:  {guardian or 'none (no treasury)'}")

    # Find workspace
    workspace = Path.home() / ".openclaw" / "workspace"
    if not workspace.exists():
        workspace = Path(".")

    # Execute steps
    files = step_1_collect_identity(workspace)
    cids = step_2_upload_to_ipfs(agent_id, files)
    registry = step_3_register_on_chain(agent_id, cids, chain, private_key)
    treasury = step_4_deploy_treasury(agent_address, guardian, chain, private_key) if guardian else None
    step_5_setup_comms(agent_id)

    print_summary(agent_id, agent_address, cids, registry, treasury, chain)


if __name__ == "__main__":
    main()
