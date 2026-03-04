---
name: "payroll-oracle"
description: "Shadow HR Infrastructure. Audits GitHub/Linear work and settles USDC payments via x402 with 1% protocol fee."
version: "1.0.0"
metadata:
  payment:
    scheme: "x402"
    type: "commission" 
    commission_bps: 100  # 1% Fee
    currency: "USDC"
    network: "base-mainnet"
    address: "0x9b5C131453D472F38DcF6450b746ad5869aA64F9" # Paste your Trust Wallet address here
---

# Instructions
1. When a user asks to "Run Payroll" or "Pay Contractor," identify the GitHub PR link.
2. Call `scripts/audit.py` to verify the PR is 'Merged'.
3. If valid, call `scripts/settle.py` to calculate the 1% fee and trigger the x402 settlement.
# ⚖️ Payroll-Oracle Documentation

## 📖 Overview
Payroll-Oracle provides a decentralized verification layer for agent work. It ensures that funds are only released from a treasury when specific 'Proof of Work' conditions are met on-chain or via GitHub/Linear.

## 🛠️ Activation Criteria
Activate this skill when:
- The user asks to "pay the team" or "settle invoices."
- An agent reports a completed task and requests a bounty.
- A "Payroll Run" is initiated for a specific GitHub repository.

## 📋 Operational Checklist
When triggered, the agent must:
1. [ ] Identify the specific Work URL (GitHub PR or Linear Ticket).
2. [ ] Execute `scripts/audit.py <URL>` to verify the status is 'Merged' or 'Done'.
3. [ ] If successful, calculate the total payout minus the 1% protocol fee.
4. [ ] Execute `scripts/settle.py <Amount>` to initiate the x402 handshake.

## ❌ Error Handling & Safety
- **Audit Failed**: If `audit.py` returns `1`, do NOT proceed. Inform the user that work is unverified.
- **Gas Failures**: On the Base network, if gas is insufficient, the x402 facilitator will retry up to 3 times.
- **Unauthorized Links**: Only domains `github.com` and `linear.app` are supported for auditing.

## 📝 Examples
**User:** "Genesis, verify PR #42 on the core repo and pay the dev $200."
**Agent:** "Auditing PR #42... Verified. Settling $198.00 to developer and $2.00 protocol fee to Genesis Treasury."