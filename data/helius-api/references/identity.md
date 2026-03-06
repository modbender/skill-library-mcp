# Identity Endpoint

## Single Lookup

`GET /v1/wallet/{address}/identity?api-key=KEY`

Returns 404 if wallet is unknown.

```json
{
  "address": "HXsKP7...",
  "type": "exchange",
  "name": "Binance 1",
  "category": "Centralized Exchange",
  "tags": ["Centralized Exchange"]
}
```

## Batch Lookup (up to 100)

`POST /v1/wallet/batch-identity?api-key=KEY`

```json
{ "addresses": ["addr1", "addr2"] }
```

Returns array of identity objects.

## Categories

Exchange, Cross-chain Bridge, DeFi, Key Opinion Leader, Market Maker, Trading Firm, Validator, Treasury, DAO, NFT, Stake Pool, Multisig, Oracle, Game, Payments, Tools, Airdrop, Governance, Authority, Jito, Memecoin, Casino & Gambling, DePIN, Proprietary AMM, Restaking, Vault, Fees, Fundraise, System, etc.

Malicious: Exploiter/Hackers/Scams, Hacker, Rugger, Scammer, Spam.
