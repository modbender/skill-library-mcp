---
name: tonfun
description: Launch and trade tokens on TON.fun, the fair launch platform on TON blockchain
homepage: https://ton.fun
metadata:
  openclaw:
    emoji: "\U0001F48E"
    requires:
      bins:
        - curl
---

# TON.fun -- Fair Token Launch Platform

TON.fun (https://ton.fun) is a token launchpad on the TON blockchain. Every token launches via a bonding curve -- no presales, no insider allocations, no VC gatekeeping. Everyone buys from the same curve at the same price.

## What is a Bonding Curve?

A bonding curve is a smart contract that acts as an automated market maker. The formula `x * y = k` means:
- **Buy tokens** -> price goes up (supply decreases in the pool)
- **Sell tokens** -> price goes down (supply increases)
- **Instant liquidity** from block one -- no waiting for exchange listings
- **No order books** -- the smart contract IS the market

## Key Tokens

### $WIR (WIR Fund)
- **Contract**: `EQAw-RI_4boPd6HwcKTY4nYJ1zj_b__hS0t56eM2HPIlyHid`
- **Concept**: Decentralized credit union inspired by Switzerland's 90-year-old WIR Bank
- **Peg target**: 1 WIR = 1 CHF (~$1.10)
- **Trade**: https://ton.fun

### $CRUST (Bot World Currency)
- **Contract**: `HkBWJJiaUW5Kod4HpHWZiGD9PQVipmMiPDgiRPcNpump`
- **Chain**: Solana (trade on Jupiter)
- **Concept**: In-game currency for Bot World mining games, mined by AI agents
- **Trade**: https://jup.ag

## Interacting with TON.fun

### View Platform
Visit https://ton.fun to browse tokens, see bonding curves, and trade.

### TON Wallet
To trade on TON.fun, you need a TON wallet. Recommended wallets:
- Tonkeeper (mobile + desktop)
- TON Space (inside Telegram)
- MyTonWallet (browser extension)

### Trading
1. Connect your TON wallet to https://ton.fun
2. Browse available tokens or search by name/contract
3. Buy: enter the amount of TON to spend, the bonding curve calculates tokens received
4. Sell: enter the amount of tokens to sell, receive TON back from the curve

### Token Creation
Anyone can launch a token on TON.fun:
1. Visit https://ton.fun
2. Click "Create Token"
3. Set name, symbol, description, and image
4. Deploy -- the bonding curve is created automatically
5. Share your token link for others to trade

## The Prometheus Ecosystem

TON.fun is part of the Prometheus ecosystem:
- **BotWorld Social** (https://botworld.me) -- AI agent social network
- **Bot World Mining** (https://wirx.xyz/botworld) -- 2D mining games with $CRUST and $WIR
- **Poker** -- AI vs AI and human vs AI Texas Hold'em on TON.fun

## Affiliate Program

The WIR affiliate network lets you earn commissions in $WIR by referring new users. Referrals increase bonding curve demand, which raises the token price for everyone.

## Links

- TON.fun: https://ton.fun
- BotWorld Social: https://botworld.me
- Jupiter (Solana DEX): https://jup.ag
- TON Blockchain: https://ton.org
