---
name: windfall-inference
description: Spatially-routed LLM inference at $0.004/req. Routes to cheapest, greenest energy. 200+ models. OpenAI-compatible. Onchain attestations on Base.
homepage: https://windfall.ecofrontiers.xyz
user-invocable: true
metadata: {"openclaw":{"emoji":"⚡","requires":{"env":["WINDFALL_API_KEY"]},"primaryEnv":"WINDFALL_API_KEY","os":["darwin","linux","win32"]}}
---

# Windfall Inference

Spatially-routed LLM inference gateway for AI agents on Base. Routes every request to the cheapest model on the cleanest energy.

## Setup

Set `WINDFALL_API_KEY` in your environment. Get one free at:

```
curl -X POST https://windfall.ecofrontiers.xyz/api/keys \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "YOUR_WALLET"}'
```

Keys with an ERC-8004 agent identity or Basename get 100 free requests. Anonymous keys get 25.

## Usage

Use as an OpenAI-compatible endpoint. Set these two environment variables:

```
OPENAI_BASE_URL=https://windfall.ecofrontiers.xyz/v1
OPENAI_API_KEY=wf_YOUR_KEY
```

Or call directly:

```
curl https://windfall.ecofrontiers.xyz/v1/chat/completions \
  -H "Authorization: Bearer $WINDFALL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## x402 Payment (No API Key Needed)

Windfall supports the x402 payment protocol. Any agent with a Base wallet can pay per-request without creating an API key. Send a request without auth and the server returns HTTP 402 with a `PAYMENT-REQUIRED` header containing USDC payment instructions on Base. Your x402 client handles the rest.

## Routing Modes

- `greenest` (default) — lowest carbon intensity
- `cheapest` — lowest energy cost
- `balanced` — Pareto-weighted cost + carbon

Set via `"mode"` in the request body or `X-Routing-Mode` header.

## Models

Default: DeepSeek V3 (auto-selected by engagement classifier). Override with `"model"` field. 200+ models available via OpenRouter.

## Pricing

- Standard: $0.004/request
- Premium (Claude, GPT-4): $0.008/request
- Green surcharge: +10% for `greenest` mode
- Cache hits: free

## Response Headers

Every response includes:
- `X-Windfall-Cache` — HIT or MISS
- `X-Windfall-Mode` — routing mode used
- `X-Windfall-Model` — model that handled the request
- `X-Windfall-Node` — node that executed the request
- `X-Windfall-Cost` — cost charged
- `X-Windfall-Saved` — savings vs direct API (cache hits)

## Onchain Attestations

Every inference call produces a verifiable EAS attestation on Base with: node location, energy price, carbon intensity, model used, and response hash. Query at base.easscan.org.
