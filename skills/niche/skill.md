---
name: niche
description: "Trading card marketplace with partial USDC deposits. Browse cards, deposit partial amounts, and complete purchases with secure on-chain escrow."
metadata:
  {
    "openclaw":
      {
        "emoji": "🎴",
        "requires": { "bins": ["node"] },
        "cron": [
          {
            "schedule": "*/15 * * * *",
            "command": "niche check-matches",
            "description": "Check for new cards matching user watches every 15 minutes"
          }
        ],
      },
  }
---

# Niche v1 — Trading Card Marketplace with Partial Deposits

A peer-to-peer trading card marketplace where users list, discover, and transact cards with partial USDC deposits on Base Sepolia. Meet in person to inspect cards before completing payment.

## Architecture

**Hosted backend** on Supabase Edge Functions. The CLI is a thin HTTP client — all heavy logic (auth, signing, escrow, on-chain transactions) runs server-side.

```
CLI (thin client)          →  Edge Functions (Supabase)
  fetch() + open()              niche-api   (REST API)
  ~/.niche/auth.json            niche-ui    (hosted HTML pages)
  @supabase/supabase-js         niche-sign  (passkey signing)
  open (browser launcher)       niche-escrow (on-chain ops)
```

**Hosted UI:** https://niche-ddq89ltdk-clement-sutjiatmas-projects.vercel.app

Anyone with the link can browse cards — no install needed.

## Why Partial Deposits + In-Person Inspection

- **Partial deposits** — Hold a card with just $10-50 deposit, not full price
- **Meet & inspect** — See the card condition in person before final payment
- **Atomic payment** — Buyer confirms + pays remaining amount in single action
- **USDC escrow** — All funds secured on-chain, released when both confirm
- **Buyer cancellation** — Get full refund before seller confirms meetup
- **Passkey signing** — Touch ID / Face ID to authorize transactions
- **Gas sponsored** — No ETH needed for transactions
- **Shareable links** — Send card URLs to anyone, no app needed

## Trading Card Flow

```
1. Seller lists "Charizard Base Set" for $50 with $10 min deposit
2. Buyer deposits $10 USDC → card is held for buyer
3. Buyer can cancel anytime before seller confirms → full $10 refund
4. Both parties meet in person to inspect card
5. Seller confirms they showed up
6. Buyer confirms AND pays $40 remaining (atomic action)
7. Backend releases total $50 to seller
```

## Commands

### Browse (no account needed)

```bash
niche search --category "Pokemon" --max-price 100
niche browse                              # Open listings in browser
niche browse --category "Magic"           # Filtered browser view
niche view <id>                           # Open card detail in browser
niche show <id>                           # View card detail in terminal
```

### Authentication

```bash
niche login       # Opens browser → email OTP → passkey → wallet created
niche logout      # Clear local session
niche whoami      # Show identity + wallet + USDC balance
```

Login happens entirely in the hosted UI. The browser handles:
1. Email → OTP verification (Privy)
2. Passkey registration (Touch ID / Face ID)
3. Embedded wallet creation (server-side)

### Listings

```bash
niche post --item-name "Charizard Base Set" --price 50 --min-deposit 10 --category "Pokemon"
niche list                    # Your listings
niche cancel <id>             # Cancel listing
```

### Watches

```bash
niche watch --category "Pokemon,Magic" --max-price 100
niche watches                 # List active watches
niche unwatch <id>            # Remove watch
niche check-matches           # Check for new matches (cron)
```

### Deposits & Payments

```bash
niche interest <id>           # Opens deposit page in browser (passkey signing)
niche confirm <id>            # Confirm meetup + pay remaining (buyer) OR confirm meetup (seller)
niche cancel <id>             # Cancel deposit and get refund (buyer only, before seller confirms)
niche dispute <id>            # File dispute, hold funds
niche escrow [id]             # View payment status
niche balance                 # Check wallet USDC + ETH balance
niche fund [amount]           # Open Circle faucet for testnet USDC
```

### Testing

```bash
niche post --item-name "Pikachu" --price 25 --min-deposit 5 --simulate seller1
niche interest abc123 --simulate buyer1
niche confirm abc123 --simulate buyer1
niche confirm abc123 --simulate seller1
```

## Authentication Requirements

| Action | Without Login | With Login |
|--------|--------------|------------|
| Search / browse | ✅ Works | ✅ Works |
| Post listings | ✅ With simulate | ✅ Works |
| Place deposit | ❌ REQUIRES LOGIN | ✅ Real USDC deposit |
| Confirm + pay | ❌ REQUIRES LOGIN | ✅ Completes purchase |
| Cancel deposit | ❌ REQUIRES LOGIN | ✅ Get refund |
| Dispute | ❌ REQUIRES LOGIN | ✅ Holds funds |
| Fund wallet | ❌ REQUIRES LOGIN | ✅ Faucet |

## User Journey

```
1. BROWSE — niche search / niche browse (no account)
2. VIEW   — niche view <id> (opens hosted page)
3. LOGIN  — niche login (browser: email → OTP → passkey → wallet)
4. FUND   — niche fund 50 (Circle faucet → testnet USDC)
5. DEPOSIT — niche interest <id> (browser: passkey signs $10 deposit)
6. MEET   — Schedule in-person inspection
7. SELLER CONFIRMS — niche confirm <id> (seller acknowledges meetup)
8. BUYER CONFIRMS + PAYS — niche confirm <id> (buyer: passkey signs $40 remaining)
9. RELEASED — Backend releases total $50 to seller
```

## Example Agent Interactions

### First-Time User
```
User: "Find me a Charizard card under $100"

Agent runs: niche search --category "Pokemon" --item-name "Charizard" --max-price 100

Agent: "Found 2 Charizard cards! Here are the results:
  1. [a1b2c3d4] Charizard Base Set 1st Edition - $50 (min deposit: $10)
  2. [e5f6g7h8] Charizard EX Full Art - $85 (min deposit: $20)

Want to see any in your browser? Or interested in one?"

User: "I'm interested in #1"

Agent runs: niche whoami

Agent: "You'll need to login first. Opening the login page..."

Agent runs: niche login

Agent: "Complete the email verification and passkey setup in your browser.
        Once done, run `niche whoami` to verify."
```

### Deposit Flow
```
User: "Place deposit on listing a1b2c3d4"

Agent runs: niche interest a1b2c3d4

Agent: "Opening the deposit page in your browser.
        Sign with your passkey (Touch ID) to deposit $10 USDC.
        You'll pay the remaining $40 when you meet and confirm."
```

### Buyer Confirmation + Payment
```
User: "I met the seller and the card is perfect. Complete the purchase."

Agent runs: niche confirm a1b2c3d4

Agent: "Opening the confirmation page in your browser.
        Sign with your passkey to:
        1. Confirm you inspected the card
        2. Pay the remaining $40 USDC

        The seller will receive the total $50 once both confirm."
```

### Cancellation
```
User: "I need to cancel my deposit on listing a1b2c3d4"

Agent runs: niche cancel a1b2c3d4

Agent: "Cancelling your deposit. You'll get your full $10 USDC back.
        (Note: You can only cancel before the seller confirms meetup)"
```

## Tips for Agents

1. **Auto-login for deposits** — Before `niche interest`, check `niche whoami`. If not logged in, run `niche login`.
2. **Always check setup** — Run `niche whoami` to see if user is configured.
3. **Offer to watch** — If search returns no results, offer `niche watch`.
4. **Show listing IDs** — Users need IDs for interest/confirm/view.
5. **Explain partial deposits** — Users deposit minimum amount, pay rest at meetup.
6. **Prompt before confirming** — Confirming as buyer = paying remaining amount (real funds).
7. **Prompt before interest** — Deposits real USDC to escrow.
8. **`--simulate` is for demos only** — Only use when user explicitly asks to test.
9. **Browser commands** — `niche login`, `niche interest`, `niche confirm` (buyer), `niche fund`, `niche browse`, `niche view` all open the browser.
10. **Terminal commands** — `niche search`, `niche show`, `niche whoami`, `niche balance`, `niche confirm` (seller) stay in terminal.
11. **Cancellation window** — Buyers can cancel anytime before seller confirms meetup.

## Sample Trading Cards (15 Available)

**Pokemon** (5 cards):
- Charizard Base Set 1st Edition - $50 (min: $10)
- Blastoise Base Set - $30 (min: $8)
- Pikachu Illustrator - $150 (min: $50)
- Mewtwo EX Full Art - $25 (min: $5)
- Rayquaza VMAX Rainbow - $40 (min: $10)

**Magic: The Gathering** (4 cards):
- Black Lotus Alpha - $200 (min: $75)
- Mox Sapphire - $100 (min: $30)
- Tarmogoyf Future Sight - $35 (min: $10)
- Liliana of the Veil - $45 (min: $12)

**Sports** (4 cards):
- Michael Jordan 1986 Fleer Rookie - $120 (min: $40)
- Tom Brady 2000 Playoff Contenders Auto - $80 (min: $25)
- Mike Trout 2009 Bowman Chrome Auto - $60 (min: $20)
- LeBron James 2003 Topps Chrome Rookie - $55 (min: $15)

**Yu-Gi-Oh** (2 cards):
- Blue-Eyes White Dragon 1st Edition - $28 (min: $8)
- Dark Magician Girl MFC 1st - $22 (min: $6)

## Testnet & On-Chain

All transactions use **real on-chain USDC on Base Sepolia testnet**. No real funds at risk.

- USDC (Base Sepolia): `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- Gas is sponsored — users don't need ETH
- Get testnet USDC: https://faucet.circle.com (select Base Sepolia)

## Error Handling

| Error | Agent Response |
|-------|----------------|
| Not logged in | Run `niche login` to open browser auth. |
| No wallet | Login creates a wallet automatically. |
| Insufficient USDC | Run `niche fund` to get testnet USDC from Circle faucet. |
| Listing not found | Check ID, or run `niche search` again. |
| Already confirmed | Waiting for other party. |
| Cannot cancel | Seller already confirmed. Buyer can only cancel before seller confirms. |
| On-chain tx failed | Try again; escrow Edge Function handles retries. |

## Data Storage

- **Supabase Postgres** — Users, listings, watches, escrows (with partial deposit tracking)
- **Supabase Vault** — Privy secrets, escrow private key
- **Edge Functions** — All server-side logic (Deno runtime)
- **Local** — `~/.niche/auth.json` (auth token + wallet), `~/.niche/config.json` (legacy)

## Key Differences from v0 (Housing)

- **Partial deposits** — Deposit only minimum amount, not full price
- **Atomic confirmation + payment** — Buyer confirms and pays remaining in single action
- **Buyer cancellation** — Full refund before seller confirms
- **In-person inspection** — Meet to verify card condition before completing purchase
- **Trading cards** — Pokemon, Magic, Sports, Yu-Gi-Oh instead of housing
- **Categories** — Card categories instead of neighborhoods
- **Simplified UI** — Less "escrow" jargon, clearer payment flow
