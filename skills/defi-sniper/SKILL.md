---
name: defi-sniper
description: Meta-skill for early token-launch intelligence and execution orchestration across Solana and Base using minara, torchmarket, and torchliquidationbot. Use when users need fast launch detection, on-chain risk triage, social-signal confirmation, and rule-based swap execution with strict guardrails.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"crossed_swords","requires":{"bins":["node","npx"],"env":["MINARA_API_KEY","SOLANA_RPC_URL"],"config":["skills.entries.minara.enabled"]},"note":"Requires local installation of minara, torchmarket, and torchliquidationbot. Solana trading path uses Torch stack; Base path is Minara-first."}}
---

# Purpose

Run a high-speed token opportunity workflow:

1. detect very early pool/token activity,
2. triage contract/market risk,
3. verify social signal quality,
4. execute small, bounded entries when rules pass.

This is an orchestration skill. It coordinates upstream skills and explicit risk policy. It does not guarantee profit.

# Required Installed Skills

- `minara` (inspected latest: `1.1.9`)
- `torchmarket` (inspected latest: `4.2.7`)
- `torchliquidationbot` (inspected latest: `3.0.2`)

Install/update:

```bash
npx -y clawhub@latest install minara
npx -y clawhub@latest install torchmarket
npx -y clawhub@latest install torchliquidationbot
npx -y clawhub@latest update --all
```

# Required Configuration and Credentials

Minimum:
- `MINARA_API_KEY`
- `SOLANA_RPC_URL`

Depending on execution route:
- Minara signer path: Circle Wallet preferred, or chain private-key fallback per Minara docs.
- Torch vault path: `VAULT_CREATOR` and linked agent wallet for vault-routed operations.

Preflight checks before any live execution:
- chain (`solana` or `base`) explicitly selected
- funding source identified (vault or signer account)
- max-risk limits loaded
- dry-run path available

# Chain-Aware Architecture

## Solana path (full stack)

Use:
- Minara for detection/intent parsing,
- Torch Market for deep token + quote + treasury/lending state,
- optional Torch execution patterns (vault-routed),
- external web search for social confirmation.

## Base path (constrained path)

Use:
- Minara for detection/intent/transaction assembly,
- external web search for social confirmation.

Important boundary:
- Torch Market and Torch Liquidation Bot are Solana-focused and should not be assumed to provide Base-native token risk primitives.

# Inputs the LM Must Collect First

- `target_chain`: `solana` or `base`
- `token_symbol_or_mint`
- `max_entry_size` (example: `1 SOL` or base-chain equivalent)
- `max_slippage_bps` (example: `300`)
- `risk_mode`: `observe`, `paper`, `live`
- `sentiment_min_accounts` (minimum credible, non-bot mentions)
- `execution_policy`: `manual-confirm` or `auto-with-guardrails`

If missing, do not run live execution.

# Tool Responsibilities

## Minara (`minara`)

Primary detection/intelligence and swap-intent layer:
- market chat/intel,
- intent-to-swap transaction generation,
- chain-aware execution pathways,
- strategy support across Solana and EVM (including Base).

Use Minara when rapid parsing and transaction assembly are required.

## Torch Market (`torchmarket`)

Solana-native deep state layer:
- token discovery (`getTokens`) and token details (`getToken`),
- buy/sell quote simulation (`getBuyQuote`, `getSellQuote`),
- treasury/lending/position context (`getLendingInfo`, `getLoanPosition`),
- vault-routed transaction builders.

Use Torch Market for on-chain structural checks and quote sanity before Solana entries.

## Torch Liquidation Bot (`torchliquidationbot`)

Execution engine specialized for liquidation keepers:
- continuous scan loop,
- high-speed vault-routed transaction execution patterns,
- strict vault safety boundary.

Important boundary:
- It is purpose-built for liquidation flow (`buildLiquidateTransaction` path), not a generic buy/sell sniper by default.
- Reuse only its operational/safety pattern unless a dedicated swap executor is explicitly available.

# Canonical Signal Chain

Use this chain for launch-sniping decisions.

## Stage 1: Early launch detection

Use Minara intelligence to detect candidate opportunities and parse swap intent context.

Required output:
- token/mint identifier
- chain
- initial liquidity signal if available
- timestamp of first detection

## Stage 2: On-chain risk triage

For Solana candidates, use Torch Market state:
- token status and reserves,
- quote simulation (buy/sell impact),
- treasury and lending context where relevant,
- holder concentration snapshots (if available through token/holder queries).

Risk interpretation policy:
- No single field should be treated as a complete rug/honeypot verdict.
- Require multiple independent indicators before green-lighting.

## Stage 3: Social signal confirmation

Use external web search tools (not bundled in these three skills) to validate whether real accounts are discussing the token.

Minimum checks:
- account quality (non-trivial follower/history signals)
- message diversity (not duplicate bot spam)
- temporal alignment with on-chain launch timing

## Stage 4: Decision matrix

Compute two gates:
- `SecurityGate`: pass/fail
- `SentimentGate`: pass/fail

Execution rule:
- only if both gates are `pass`
- otherwise `no_trade`

## Stage 5: Execution

If execution allowed:
- enforce position cap (example: 1 SOL)
- enforce slippage cap
- record tx hash and rationale
- immediately set post-entry monitoring conditions

# Scenario Mapping (PEPE2.0 on Solana)

For the scenario in this skill request:

1. Minara flags a new Solana token/pool event with initial liquidity context.
2. Torch Market fetches token-level state and quote/treasury context.
3. Social verification runs in parallel via external web search (X/Twitter signal quality).
4. If `SecurityGate=pass` and `SentimentGate=pass`, execute bounded entry (example 1 SOL) with fixed slippage tolerance.
5. Log full decision trail: signals, checks, final action.

# Output Contract

Always return:

- `Detection`
  - chain, token ID, first-seen timestamp

- `OnChainRisk`
  - indicators checked
  - pass/fail with reasons

- `SocialSignal`
  - source summary
  - pass/fail with reasons

- `ExecutionDecision`
  - `trade` or `no_trade`
  - size, slippage, route

- `AuditTrail`
  - exact checks performed
  - unresolved uncertainties

# Risk Guardrails

- Never deploy unbounded size; always cap first entry.
- Never trade without slippage limits.
- Never treat hype alone as trade permission.
- Never claim "safe" based on one heuristic.
- Prefer `no_trade` on ambiguous or conflicting evidence.
- In `auto-with-guardrails` mode, require preconfigured hard limits and fail-closed defaults.

# Operational Modes

## `observe`

Detection and scoring only. No trade.

## `paper`

Simulated entries/exits with recorded hypothetical PnL.

## `live`

Real execution only after preflight and guardrail checks pass.

# Failure Handling

- Missing key/config/env: halt with explicit missing item list.
- Detection without sufficient risk data: downgrade to `observe`.
- Sentiment source unavailable: require manual confirmation or `no_trade`.
- Execution route unavailable on selected chain: return explicit compatibility mismatch.

# Known Limits from Inspected Upstream Skills

- Minara inspected docs describe intent parsing and transaction assembly, but do not expose a dedicated "mempool scanner" endpoint in the inspected `SKILL.md`.
- Torch Market exposes rich Solana token/treasury/lending state and quotes, but no single built-in "honeypot/rug score" flag.
- Torch Liquidation Bot is liquidation-specialized; using it as a generic swap executor is a repurposing pattern, not its native primary workflow.
- Social signal checks require external web/search skills outside this three-skill stack.

Treat these limits as mandatory disclosures in final operator output.
