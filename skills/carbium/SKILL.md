---
name: carbium
description: "Use Carbium Solana infrastructure for RPC calls, gRPC/Yellowstone real-time streaming, DEX swap quotes and execution (CQ1 engine), and pump.fun token sniping. Use when building on Solana with Carbium endpoints — trading bots, arbitrage engines, DEX integrations, wallets, on-chain event monitors, or any application needing low-latency Solana data and execution. Covers full transaction lifecycle: read, stream, quote, swap, bundle (Jito), and snipe."
license: MIT
metadata:
  homepage: https://carbium.io
  docs: https://docs.carbium.io
  repository: https://github.com/carbium-io
  author: Carbium
  support: https://discord.gg/jW7BUkQS5U
---

# Carbium Skill

Carbium is full-stack Solana infrastructure — Swiss-engineered, bare-metal, sub-22ms block streaming, no cloud middlemen.

## Endpoints at a glance

| Product | URL |
|---|---|
| RPC | `https://rpc.carbium.io/?apiKey=YOUR_RPC_KEY` |
| gRPC / Stream | `wss://grpc.carbium.io/?apiKey=YOUR_RPC_KEY` |
| Swap API | `https://api.carbium.io` (header: `X-API-KEY`) |
| Docs | `https://docs.carbium.io` |

## Auth & Security

- Env vars: `CARBIUM_RPC_KEY`, `CARBIUM_API_KEY`
- **Never** embed keys in frontend code or commit to version control
- One RPC key covers both RPC and gRPC endpoints
- Swap API key is separate (free account at `https://api.carbium.io/login`)

## When to use what

| Goal | Use | Key needed |
|---|---|---|
| Read balances / send tx | RPC | RPC key |
| Real-time on-chain events | gRPC stream | RPC key (Business+) |
| Get swap quote | Swap API `/api/v2/quote` | API key |
| Execute swap | Swap API `/api/v2/swap` | API key |
| Jito-bundled swap | Swap API `/api/v2/swap/bundle` | API key |
| Snipe pump.fun tokens | gRPC + raw bonding curve tx | RPC key (Business+) |
| Arbitrage / MEV bot | gRPC + Swap API | Both |

## Full API reference

See [references/carbium-api.md](references/carbium-api.md) for:
- Complete RPC, gRPC, and Swap API examples (JS/TS, Python, Rust)
- pump.fun sniping full implementation (bonding curve math, buy/sell instructions)
- Operational guardrails (retry logic, reconnect backoff, error table)
- Pricing tiers and feature matrix
