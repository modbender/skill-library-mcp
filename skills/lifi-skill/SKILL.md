---
name: lifi
description: v4 - Use LI.FI API for cross-chain and same-chain swaps, bridges, and contract calls. Use when quoting routes, validating chains/tokens, building transaction requests, and tracking status.
homepage: https://docs.li.fi/
metadata:
  {
    "openclaw":
      {
        "emoji": "🔁",
        "requires": { "env": ["LIFI_API_KEY"] },
        "primaryEnv": "LIFI_API_KEY",
      },
  }
---

# LI.FI Agent Skill

## CRITICAL RULES (read first)
1. ONLY use `curl` to call the LI.FI API. NEVER use `web_search`, `web_fetch`, or any other tool.
2. ONLY use the endpoints documented below. Do NOT guess or invent URLs.
3. Base URL is `https://li.quest/v1/`. No other base URL.
4. ALWAYS include auth header: `"x-lifi-api-key: $LIFI_API_KEY"` (double quotes, dollar sign — shell expands it).
5. ALWAYS tell the user the quote is provided by LI.FI.
6. **Default slippage: 10% (0.10).** If the user has a custom slippage in their strategy (via `defi_get_strategy`), use that instead. The agent can also adjust dynamically per-transaction if the user requests it.
7. Default deadline: 10 minutes.
8. ALWAYS add `&skipSimulation=true` to all `/v1/quote` requests. Our EIP-7702 delegated wallets have on-chain code that breaks LI.FI's simulation.
9. NEVER construct ERC-20 approve calldata (hex) yourself. ALWAYS use the `defi_approve` or `defi_approve_and_send` tools.
10. **ALL swaps, bridges, and DeFi token operations MUST go through LI.FI.** No exceptions. No manual DEX interactions.

## Transaction Links

After every transaction broadcast, **always** provide a clickable block explorer link:
- EVM: `[View tx](https://basescan.org/tx/0xHASH)` — use the correct explorer (etherscan.io, basescan.org, arbiscan.io, polygonscan.com, optimistic.etherscan.io)
- Sui: `[View tx](https://suiscan.xyz/txblock/{txDigest})`

## Sui

- **Sui chain ID: `9270000000000000`**. Use this for `fromChain` and `toChain` in LI.FI quote requests when the user wants Sui (e.g. `fromChain=9270000000000000&toChain=9270000000000000` for same-chain Sui swap).
- LI.FI supports **Sui** for same-chain swaps and bridging to/from EVM and Solana.
- For Sui quotes, use the user's **suiAddress** from `defi_get_wallet` as `fromAddress`.
- **Execute Sui quotes with `defi_send_sui_transaction`** — pass the transaction bytes (hex) from the LI.FI quote. Do **not** use `defi_send_transaction` or `defi_approve_and_send` for Sui.
- Sui does not use ERC-20 approvals; there is no approval step for Sui swaps.

## Endpoints

### GET /v1/chains — List supported chains

```bash
curl -s --request GET \
  --url https://li.quest/v1/chains \
  --header "x-lifi-api-key: $LIFI_API_KEY"
```

Use for: listing chains, testing connectivity. If user asks for a test, use this.

### GET /v1/tokens — List tokens on chains

```bash
curl -s --request GET \
  --url 'https://li.quest/v1/tokens?chains=8453' \
  --header "x-lifi-api-key: $LIFI_API_KEY"
```

Params: `chains` (comma-separated chain IDs).

### GET /v1/quote — Get swap/bridge quote with tx data

```bash
curl -s --request GET \
  --url 'https://li.quest/v1/quote?fromChain=8453&toChain=8453&fromToken=ETH&toToken=USDC&fromAddress=0xYOUR_ADDRESS&fromAmount=100000000000000&slippage=0.10&skipSimulation=true' \
  --header "x-lifi-api-key: $LIFI_API_KEY"
```

Params: `fromChain`, `toChain`, `fromToken`, `toToken`, `fromAddress`, `toAddress` (optional), `fromAmount` (in wei), `slippage` (decimal, e.g. 0.10 = 10%), `skipSimulation=true` (ALWAYS include).

Returns: `estimate` (with `toAmount`, `toAmountMin`, `approvalAddress`) and `transactionRequest` (ready for wallet submission).

After presenting a quote to the user, always include the estimated output amount, fees, and slippage. Get the user's wallet address with `defi_get_wallet` and use it as `fromAddress` in the quote.

#### Executing the quote

**Check if ERC-20 approval is needed:** If the quote's `transactionRequest.value` is `"0x0"` AND `estimate.approvalAddress` exists, the swap/bridge is using an ERC-20 token that needs approval first.

- **If approval IS needed:** Use `defi_approve_and_send` with:
  - `token`: the `action.fromToken.address` from the quote
  - `spender`: the `estimate.approvalAddress` from the quote
  - `approveAmount`: the `action.fromAmount` from the quote (or omit for unlimited)
  - `to`, `value`, `data`, `gasLimit`: from the quote's `transactionRequest`

- **If approval is NOT needed** (native ETH swap, value > 0x0): Use `defi_send_transaction` with the quote's `transactionRequest` fields: **to, value, data, chainId, and gasLimit** (ALWAYS pass `gasLimit` from the quote).

**NEVER construct approve calldata hex yourself.** The `defi_approve` and `defi_approve_and_send` tools handle ABI encoding correctly.

**Sui:** For quotes where `fromChain` or `toChain` is Sui, use `defi_send_sui_transaction` with the quote's transaction bytes. No approval step.

### POST /v1/advanced/routes — Get multiple route options

```bash
curl -s --request POST \
  --url https://li.quest/v1/advanced/routes \
  --header 'Content-Type: application/json' \
  --header "x-lifi-api-key: $LIFI_API_KEY" \
  --data '{
  "fromChainId": 8453,
  "fromAmount": "100000000000000",
  "fromTokenAddress": "0x0000000000000000000000000000000000000000",
  "toChainId": 8453,
  "toTokenAddress": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "options": {
    "slippage": 0.10,
    "order": "RECOMMENDED"
  }
}'
```

### POST /v1/quote/contractCalls — Multi-step contract calls (BETA)

```bash
curl -s --request POST \
  --url https://li.quest/v1/quote/contractCalls \
  --header 'Content-Type: application/json' \
  --header "x-lifi-api-key: $LIFI_API_KEY" \
  --data '{
  "fromChain": 10,
  "fromToken": "0x4200000000000000000000000000000000000042",
  "fromAddress": "0xYOUR_ADDRESS",
  "toChain": 1,
  "toToken": "ETH",
  "toAmount": "100000000000001",
  "contractCalls": []
}'
```

### GET /v1/status — Check transfer status

```bash
curl -s --request GET \
  --url 'https://li.quest/v1/status?txHash=0xYOUR_TX_HASH&fromChain=8453' \
  --header "x-lifi-api-key: $LIFI_API_KEY"
```

Pass `fromChain` to speed up the lookup.

### GET /v1/tools — List available bridges and exchanges

```bash
curl -s --request GET \
  --url 'https://li.quest/v1/tools?chains=8453' \
  --header "x-lifi-api-key: $LIFI_API_KEY"
```

## Docs
- LLM docs: https://docs.li.fi/llms.txt
- OpenAPI: https://gist.githubusercontent.com/kenny-io/7fede47200a757195000bfbe14c5baee/raw/725cf9d4a6920d5b930925b0412d766aa53c701c/lifi-openapi.yaml
