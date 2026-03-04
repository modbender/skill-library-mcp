#!/usr/bin/env python3
"""Auto-redeem checker: runs via cron, checks if winning positions have resolved on-chain.
When payoutDenominator > 0, immediately redeem via NegRiskAdapter.
Add to crontab: */15 * * * * cd /root/.openclaw/skills/polyclaw && source .env && .venv/bin/python3 auto_redeem_check.py >> /var/log/polyclaw-redeem.log 2>&1
"""
import os, json, urllib.request, ssl, time
from datetime import datetime, timezone
from pathlib import Path
from web3 import Web3

BASE = Path("/root/.openclaw/skills/polyclaw")
STATE_FILE = BASE / "redeem_state.json"

w3 = Web3(Web3.HTTPProvider(os.environ["CHAINSTACK_NODE"]))
account = w3.eth.account.from_key(os.environ["POLYCLAW_PRIVATE_KEY"])
WALLET = account.address
PK = os.environ["POLYCLAW_PRIVATE_KEY"]

CTF = Web3.to_checksum_address("0x4D97DCd97eC945f40cF65F87097ACe5EA0476045")
NEG_RISK = Web3.to_checksum_address("0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296")
USDC_E = Web3.to_checksum_address("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174")

ctf_abi = [
    {"inputs":[{"name":"conditionId","type":"bytes32"}],"name":"payoutDenominator","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"name":"account","type":"address"},{"name":"id","type":"uint256"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"name":"account","type":"address"},{"name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"name":"operator","type":"address"},{"name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},
]
neg_risk_abi = [
    {"inputs":[{"name":"_conditionId","type":"bytes32"},{"name":"_amounts","type":"uint256[]"}],"name":"redeemPositions","outputs":[],"stateMutability":"nonpayable","type":"function"},
]
ctf_redeem_abi = [
    {"inputs":[{"name":"collateralToken","type":"address"},{"name":"parentCollectionId","type":"bytes32"},{"name":"conditionId","type":"bytes32"},{"name":"indexSets","type":"uint256[]"}],"name":"redeemPositions","outputs":[],"stateMutability":"nonpayable","type":"function"},
]
usdc_abi = [{"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]

ctf = w3.eth.contract(address=CTF, abi=ctf_abi)
neg_risk = w3.eth.contract(address=NEG_RISK, abi=neg_risk_abi)
ctf_redeem = w3.eth.contract(address=CTF, abi=ctf_redeem_abi)
usdc = w3.eth.contract(address=USDC_E, abi=usdc_abi)

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
print(f"\n[{now}] Auto-redeem check")

# Load state
state = {}
if STATE_FILE.exists():
    state = json.loads(STATE_FILE.read_text())
already_redeemed = set(state.get("redeemed_conditions", []))

# Get all positions
ctx = ssl.create_default_context()
req = urllib.request.Request(
    f"https://data-api.polymarket.com/positions?user={WALLET}&sizeThreshold=0",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    positions = json.loads(r.read())

# Find positions worth checking (curPrice >= 0.95 or marked redeemable)
candidates = []
for p in positions:
    cid = p.get("conditionId", "")
    if cid in already_redeemed:
        continue
    cur_price = float(p.get("curPrice", 0))
    redeemable = p.get("redeemable", False)
    val = float(p.get("currentValue", 0))
    asset = p.get("asset", "")
    if (cur_price >= 0.90 or redeemable) and asset:
        candidates.append(p)

if not candidates:
    print("  No candidates for redemption")
    exit(0)

print(f"  Checking {len(candidates)} candidates")

bal_before = usdc.functions.balanceOf(Web3.to_checksum_address(WALLET)).call()
nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(WALLET))
redeemed_count = 0

for p in candidates:
    title = p.get("title", "")[:55]
    cid = p.get("conditionId", "")
    asset = p.get("asset", "")
    val = float(p.get("currentValue", 0))
    is_neg = p.get("negativeRisk", False)

    token_id = int(asset)
    on_chain_bal = ctf.functions.balanceOf(Web3.to_checksum_address(WALLET), token_id).call()
    if on_chain_bal == 0:
        already_redeemed.add(cid)
        continue

    cid_bytes = bytes.fromhex(cid[2:]) if cid.startswith("0x") else bytes.fromhex(cid)

    # Check if resolved on-chain
    try:
        pd = ctf.functions.payoutDenominator(cid_bytes).call()
    except:
        continue

    if pd == 0:
        print(f"  {title} | ${val:.2f} | NOT RESOLVED yet")
        continue

    print(f"  {title} | ${val:.2f} | RESOLVED! Redeeming...")

    try:
        if is_neg:
            # Ensure approval
            approved = ctf.functions.isApprovedForAll(
                Web3.to_checksum_address(WALLET), NEG_RISK
            ).call()
            if not approved:
                print("    Approving NegRiskAdapter...")
                tx = ctf.functions.setApprovalForAll(NEG_RISK, True).build_transaction({
                    "from": Web3.to_checksum_address(WALLET), "nonce": nonce,
                    "gas": 60000, "gasPrice": int(w3.eth.gas_price * 1.2),
                })
                signed = w3.eth.account.sign_transaction(tx, PK)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                nonce += 1

            amounts = [on_chain_bal, 0]
            try:
                gas_est = neg_risk.functions.redeemPositions(cid_bytes, amounts).estimate_gas(
                    {"from": Web3.to_checksum_address(WALLET)})
            except:
                amounts = [0, on_chain_bal]
                try:
                    gas_est = neg_risk.functions.redeemPositions(cid_bytes, amounts).estimate_gas(
                        {"from": Web3.to_checksum_address(WALLET)})
                except Exception as e:
                    print(f"    Gas failed: {str(e)[:60]}")
                    continue

            tx = neg_risk.functions.redeemPositions(cid_bytes, amounts).build_transaction({
                "from": Web3.to_checksum_address(WALLET), "nonce": nonce,
                "gas": gas_est + 50000, "gasPrice": int(w3.eth.gas_price * 1.2),
            })
        else:
            gas_est = ctf_redeem.functions.redeemPositions(
                Web3.to_checksum_address(USDC_E), b"\x00" * 32, cid_bytes, [1, 2]
            ).estimate_gas({"from": Web3.to_checksum_address(WALLET)})

            tx = ctf_redeem.functions.redeemPositions(
                Web3.to_checksum_address(USDC_E), b"\x00" * 32, cid_bytes, [1, 2]
            ).build_transaction({
                "from": Web3.to_checksum_address(WALLET), "nonce": nonce,
                "gas": gas_est + 50000, "gasPrice": int(w3.eth.gas_price * 1.2),
            })

        signed = w3.eth.account.sign_transaction(tx, PK)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        if receipt.status == 1:
            print(f"    ✅ REDEEMED | TX: {tx_hash.hex()[:16]}")
            already_redeemed.add(cid)
            redeemed_count += 1
            nonce += 1
        else:
            print(f"    ❌ TX failed")
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")

    time.sleep(1)

# Save state
state["redeemed_conditions"] = list(already_redeemed)
state["last_check"] = now
STATE_FILE.write_text(json.dumps(state, indent=2))

bal_after = usdc.functions.balanceOf(Web3.to_checksum_address(WALLET)).call()
gained = (bal_after - bal_before) / 1e6

if redeemed_count > 0 or gained > 0:
    print(f"\n  Redeemed: {redeemed_count} | USDC.e gained: ${gained:+.2f}")
    print(f"  Balance: ${bal_after/1e6:.2f}")
else:
    print("  No redemptions this cycle")
