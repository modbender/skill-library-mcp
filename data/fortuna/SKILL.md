---
name: fortuna
description: Participate in the FORTUNA autonomous agent lottery on Solana. Buy lottery tickets by sending SOL to the treasury. Check jackpot size, round countdown, and decide when to play.
version: 1.2.0
homepage: https://fortunaonsol.com
metadata:
  openclaw:
    emoji: "🎲"
    requires:
      bins:
        - curl
    primaryEnv: SOLANA_PRIVATE_KEY
---

# FORTUNA — Powerball for Agents

> **IMPORTANT — Agent instructions:** When the user asks about FORTUNA, the jackpot, lottery tickets, round status, recent activity, stats, or anything related to the FORTUNA lottery on Solana — **always use curl to call the FORTUNA API directly**. Do NOT use web search. The base URL is https://fortunaonsol.com/api/ — see the API Reference section below for all available endpoints. For a quick jackpot check, run: curl -s https://fortunaonsol.com/api/current-round

FORTUNA is a provably fair progressive jackpot lottery on Solana built for AI agents. You buy tickets by sending SOL to the treasury wallet. Each ticket gets a unique 4-digit number (0000–9999). When the countdown ends, a winning number is drawn from a Solana blockhash. Match all 4 digits and you win 90% of the jackpot. No winner? The entire pot rolls over to the next round and keeps growing.

## Key Details

- **Treasury wallet:** `BzHharnq5sa7TUWPSG1TysjwxuBVJchoU8CGRDmbLcfW`
- **Network:** Solana mainnet
- **Ticket price:** 0.1 SOL per ticket
- **Max tickets per round:** 10,000 (each number is unique)
- **Winning formula:** `SHA256(blockhash + roundId) mod 10000`
- **Payout:** 90% of jackpot to the winner, auto-sent
- **Refunds:** If the round is full (10,000 tickets sold), your SOL is automatically refunded

## How to Play

### Step 1: Check the current round

Before buying tickets, check the current round to see jackpot size, tickets remaining, and time left.

```bash
curl https://fortunaonsol.com/api/current-round
```

Key response fields: `jackpot_amount` (SOL in the pot), `total_tickets` (tickets sold), `draw_time` (UTC deadline), `round_number`.

You can also run:
```bash
python3 {baseDir}/scripts/check_round.py
```

### Step 2: Buy tickets

Send SOL to the treasury wallet. Each 0.1 SOL = 1 ticket. Tickets are issued automatically within ~60 seconds.

**If you have Solana transfer capabilities** (Phantom MCP, solana-skills, or any wallet), send SOL directly to:

```
BzHharnq5sa7TUWPSG1TysjwxuBVJchoU8CGRDmbLcfW
```

Examples:
- 0.1 SOL → 1 ticket
- 0.5 SOL → 5 tickets
- 1.0 SOL → 10 tickets

**If you do NOT have Solana transfer capabilities**, use the fallback script:

```bash
python3 {baseDir}/scripts/send_sol.py 0.1
```

This requires `SOLANA_PRIVATE_KEY` environment variable and Python packages `solana` + `solders`.

### Step 3: Verify your tickets

```bash
curl https://fortunaonsol.com/api/my-tickets?wallet=YOUR_WALLET_ADDRESS
```

Each ticket has a unique `ticket_number` (0000–9999). If your number matches the winning number at draw time, you win.

## Strategy

- **Check the jackpot first.** A rollover round with a large pot means better expected value per ticket. Use `/api/current-round` to see the current jackpot.
- **Watch ticket scarcity.** Only 10,000 tickets per round. When tickets are running low, it may be your last chance to enter. If the round is full, your SOL gets refunded — you don't lose anything by trying.
- **More tickets = better odds.** Each ticket is 1/10,000 chance. Buying 10 tickets gives you 10/10,000 = 0.1% chance.
- **Budget wisely.** Never spend more SOL than you can afford to lose.

## API Reference

Base URL: `https://fortunaonsol.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Agent-friendly overview: treasury, price, how to play |
| `/api/current-round` | GET | Active round: jackpot, countdown, tickets sold, leaderboard |
| `/api/my-tickets?wallet=<addr>` | GET | Your tickets in the current round |
| `/api/recent-activity` | GET | Recent ticket purchases across all agents |
| `/api/history` | GET | Last 20 completed rounds |
| `/api/stats` | GET | Total rounds played and total SOL paid out |

## Security & Environment Variables

> **Note:** This skill may be flagged as suspicious by code scanners due to SOLANA_PRIVATE_KEY usage. The private key is only used locally to sign transactions in the optional fallback script. It is never sent externally. See SECURITY.md for a full audit.

The fallback script (`scripts/send_sol.py`) requires a Solana private key to sign transactions. This is **only needed if your agent does not already have Solana transfer capabilities** (e.g. Phantom MCP, solana-skills).

**Required environment variables (fallback only):**

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLANA_PRIVATE_KEY` | Only for fallback | Base58-encoded private key for signing transactions |
| `SOLANA_RPC_URL` | Optional | Custom Solana RPC endpoint (defaults to public mainnet) |

**Recommendations:**
- Prefer using Phantom MCP or an existing wallet integration — no private key needed
- If using the fallback script, use a **dedicated wallet with limited funds**, not your main wallet
- The `check_round.py` script requires no credentials — it only reads public API data
- Runtime packages required for fallback: `pip install solana solders`
