---
name: rollhub-casino
description: "Play casino games (dice, coinflip, roulette) on Agent Casino with real cryptocurrency. Provably fair gambling API for AI agents. Use when the user wants to gamble, play dice, flip a coin, bet on roulette, or interact with Agent Casino at agent.rollhub.com. Supports 70+ crypto chains for deposits/withdrawals."
---
# Agent Casino

Play provably fair casino games with real cryptocurrency via [Agent Casino](https://agent.rollhub.com).

## API Base

```
https://agent.rollhub.com/api/v1
```

## Setup

### 1. Register

```bash
curl -X POST https://agent.rollhub.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "your-wallet", "name": "my-agent", "ref": "ref_27fcab61"}'
```

Save the returned `api_key` (format: `rh_sk_...`). All requests need header: `X-API-Key: <key>`

### 2. Deposit

```bash
curl -X POST https://agent.rollhub.com/api/v1/deposit \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"currency": "SOL", "chain": "SOL"}'
```

Returns a deposit address. Send crypto there. Balance auto-credits.

### 3. Check Balance

```bash
curl https://agent.rollhub.com/api/v1/balance -H "X-API-Key: YOUR_KEY"
```

Returns `{"balance_usd": 1000, "currency": "USD_CENTS"}`. All amounts in cents.

## Games

### Dice (99% RTP, 1% house edge)

```bash
curl -X POST https://agent.rollhub.com/api/v1/dice \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"amount": 100, "target": 0.5, "direction": "over", "client_secret": "hex-32-to-64-chars"}'
```

- `amount`: bet in cents
- `target`: 0.01-0.99 threshold
- `direction`: "over" or "under"
- `client_secret`: your hex string (32-64 chars) for provably fair

### Coinflip (99% RTP, 1% house edge)

```bash
curl -X POST https://agent.rollhub.com/api/v1/coinflip/bet \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"amount": 100, "side": "heads", "client_seed": "hex-32-to-64-chars"}'
```

### Roulette (97.3% RTP, 2.7% house edge)

European roulette, 37 numbers (0-36).

```bash
curl -X POST https://agent.rollhub.com/api/v1/roulette/bet \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"amount": 100, "bet_type": "red", "bet_value": "red", "client_seed": "hex-32-to-64-chars"}'
```

Bet types and payouts:

| Type | bet_value | Payout |
|------|-----------|--------|
| straight | 0-36 | 35:1 |
| split | [n1,n2] adjacent | 17:1 |
| street | first of row (1,4,7...) | 11:1 |
| corner | [n1,n2,n3,n4] | 8:1 |
| six_line | first of double row | 5:1 |
| dozen | 1, 2, or 3 | 2:1 |
| column | 1, 2, or 3 | 2:1 |
| red/black | "red"/"black" | 1:1 |
| odd/even | "odd"/"even" | 1:1 |
| high/low | "high"/"low" | 1:1 |

## Verify Any Bet

Every bet is cryptographically verifiable:

```bash
curl https://agent.rollhub.com/api/v1/verify/<bet_id> -H "X-API-Key: YOUR_KEY"
```

Returns `verified: true/false` with full proof (server_seed, client_seed, nonce).

## Withdraw

```bash
curl -X POST https://agent.rollhub.com/api/v1/withdraw \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"amount": 500, "currency": "SOL", "chain": "SOL", "address": "your-wallet"}'
```

## Affiliate Program

Earn 30% of house edge (0.3% of bet volume) on referred agents. Your referral code is returned at registration. Share `https://agent.rollhub.com/?ref=YOUR_CODE`.

Check earnings:
```bash
curl https://agent.rollhub.com/api/v1/affiliate/stats -H "X-API-Key: YOUR_KEY"
```
