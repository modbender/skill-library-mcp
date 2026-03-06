# Blockchain Security

## Wallet Security Hierarchy

1. **Hardware wallet** (Ledger, Trezor) — Best for significant holdings
2. **Software wallet** (MetaMask, Rabby) — Convenient, higher risk
3. **Exchange custody** — Not your keys, not your coins

## Seed Phrase Rules

**NON-NEGOTIABLE:**
- Never share with anyone, ever
- Never screenshot or store digitally
- Never enter on any website
- Write on paper/metal, store offline
- Consider splitting across locations

**If compromised:** All funds at risk, forever. No recovery.

## Transaction Safety

- **Test transactions first** — Send small amount before large
- **Verify addresses** — Copy-paste, then verify first/last characters
- **Check network** — Wrong chain = lost funds
- **Understand irreversibility** — No chargebacks, no undo

## Common Scams

| Scam Type | How It Works | Defense |
|-----------|--------------|---------|
| Phishing | Fake sites clone real ones | Verify URL obsessively, bookmark real sites |
| Fake giveaways | "Send 1 ETH, get 2 back" | No one gives free money |
| Recovery scams | "We can recover lost crypto" | Impossible, always scam |
| Rug pulls | Project disappears with funds | Research team, audit status |
| Romance scams | Fake relationship → "invest" | Never mix dating and crypto |
| Approval scams | Malicious approve() calls | Review what you're signing |

## Smart Contract Risks

- **Audits don't guarantee safety** — Many audited contracts exploited
- **Unlimited approvals** — Revoke unused approvals regularly
- **New protocols** — Higher risk, start small
- **Fork/clone projects** — Often have hidden modifications

## Red Flags

🚩 Promises of guaranteed returns
🚩 Pressure to act quickly
🚩 Requests for seed phrase
🚩 "Support" contacts you first
🚩 Too-good-to-be-true APY
🚩 Anonymous team on new project
🚩 No audit on DeFi protocol

## If Something Goes Wrong

1. **Revoke approvals immediately** — revoke.cash
2. **Move remaining funds** — To new wallet if seed compromised
3. **Document everything** — For potential reporting
4. **Don't trust "recovery services"** — They're scams too
