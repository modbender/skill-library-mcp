---
name: the-flip
description: "$1 USDC entry. Pick 20 predictions. All 20 coins flip at once each round. Match the first 14 to win the entire jackpot. Live on Solana devnet."
metadata:
  openclaw:
    emoji: "🎰"
    homepage: "https://github.com/maurodelazeri/the-flip-publish"
    requires:
      bins: ["node"]
---

# 🎰 THE FLIP

**$1 USDC. Pick 20. 20 coins flip at once. Match 14 to win the jackpot.**

No entry windows. The game never stops. Enter anytime with 20 predictions. Each round flips all 20 coins at once. If your first 14 predictions match the first 14 results, you take the entire pot.

---

## Commands

### 1. Check game status
```bash
node app/demo.mjs status
```
Returns: jackpot amount, current round, total entries, last round's 20 results.

### 2. Enter the game
```bash
node app/demo.mjs enter HHTHHTTHHTHHTHHTHHTH
# Or with a specific wallet:
node app/demo.mjs enter HHTHHTTHHTHHTHHTHHTH ~/.config/solana/id.json
```
- Predictions: exactly 20 characters, each H (heads) or T (tails)
- All 20 coins flip at once when the next round is triggered
- First 14 of your predictions must match the first 14 results to win
- Cost: 1 USDC
- Your ticket is for the current round

### 3. Check your ticket
```bash
node app/demo.mjs ticket YOUR_WALLET_ADDRESS
# Or with a specific round:
node app/demo.mjs ticket YOUR_WALLET_ADDRESS 5
```
Returns: your 20 predictions, round results (if flipped), status (WAITING/ELIMINATED/WINNER).

### 4. Claim jackpot (if first 14 match)
```bash
node app/demo.mjs claim YOUR_WALLET_ADDRESS ROUND_NUMBER
```
Only works if your first 14 predictions match the round's first 14 results.

### 5. Flip the round (anyone can do this)
```bash
node app/demo.mjs flip
```
Flips all 20 coins at once for the current round. Permissionless — anyone can call. 12-hour cooldown between rounds (on-chain enforced).

---

## API (for agents)

Base URL: `https://the-flip.vercel.app`

### GET /api/game
```json
{
  "phase": "active",
  "jackpot": 5.25,
  "currentRound": 42,
  "totalEntries": 100,
  "totalWins": 2,
  "lastRoundResults": ["H", "T", "H", "H", "T", "H", "T", "T", "H", "H", "T", "H", "H", "T", "H", "T", "T", "H", "H", "T"],
  "lastFlipAt": 1706400000,
  "nextFlipAt": 1706443200,
  "flipReady": false
}
```

### GET /api/ticket?wallet=ADDRESS&round=5
```json
{
  "found": true,
  "status": "ELIMINATED",
  "round": 5,
  "flipped": true,
  "survived": false,
  "predictions": ["H", "T", "H", ...],
  "results": ["H", "T", "T", ...],
  "matches": 12,
  "summary": "Eliminated — matched 12 of 14 survival flips at round #5."
}
```

---

## Setup (first time only)

```bash
# Install skill
clawhub install the-flip
cd the-flip && npm install

# Solana wallet (if you don't have one)
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
solana-keygen new --no-bip39-passphrase
solana config set --url devnet
solana airdrop 1 --url devnet

# Get devnet USDC
# Option A: https://faucet.circle.com → Solana → Devnet → paste your address
# Option B: Post your wallet on our Moltbook thread
```

---

## Quick Reference

| | |
|---|---|
| **Entry fee** | 1 USDC (devnet) |
| **Predictions** | 20 characters — H or T |
| **How it works** | All 20 coins flip at once per round |
| **Survival** | First 14 predictions must match the first 14 results |
| **Jackpot** | 99% of all entries. Winner takes all. Pool resets after win. |
| **Odds** | 1 in 16,384 per entry (2^14) |
| **Program** | `7rSMKhD3ve2NcR4qdYK5xcbMHfGtEjTgoKCS5Mgx9ECX` |
| **USDC Mint** | `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU` |
| **Network** | Solana devnet |
| **Flip cooldown** | 12 hours between rounds (on-chain enforced) |
| **Vault** | PDA — no private key, can't be rugged |
| **Dashboard** | [the-flip.vercel.app](https://the-flip.vercel.app) |

---

## Source

https://github.com/maurodelazeri/the-flip-publish

All game logic is on-chain. The vault is a PDA — no private key holds funds. Claim is atomic (verify + pay in one tx).
