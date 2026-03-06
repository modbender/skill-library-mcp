# Four.meme Error Codes

## buyToken

| Code       | Meaning |
|-----------|---------|
| GW (GWEI) | Amount precision not aligned to GWEI |
| ZA        | Zero Address – `to` must not be address(0) |
| TO        | Invalid to – `to` must not be PancakePair address |
| Slippage  | Spent amount &gt; maxFunds |
| More BNB  | Insufficient BNB in msg.value |
| A         | X Mode token bought with wrong method – use X Mode buy |

## sellToken

| Code      | Meaning |
|----------|---------|
| GW (GWEI)| Amount precision not aligned to GWEI |
| FR (FeeRate) | Fee rate &gt; 5% |
| SO (Small Order) | Order amount too small |
| Slippage | Received amount &lt; minFunds |

## Identification

- **X Mode (exclusive)**: Off-chain – API token info `version === "V8"`. On-chain – `TokenManager2._tokenInfos[token].template & 0x10000 > 0`.
- **TaxToken**: Off-chain – API response has `taxInfo`. On-chain – `(template >> 10) & 0x3F === 5`.
- **AntiSniperFeeMode**: Off-chain – API `feePlan === true`. On-chain – `TokenManager2._tokenInfoEx1s[token].feeSetting > 0`.
