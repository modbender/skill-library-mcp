---
name: "Wash-Trade-Detector"
description: "Detects and flags wash trades in NFT transaction data using 7 confidence-weighted patterns, protecting all downstream scoring and signals from artificial inflation."
tags:
- "openclaw-workspace"
- "data-integrity"
- "nft"
- "blockchain"
version: "1.0.4"
---

# Skill: Wash Trade Detector

## Purpose
Identifies and flags non-genuine transactions (wash trades) in NFT sales data. Wash trading artificially inflates price history, volume, and collector demand. This skill applies 7 weighted detection patterns to identify suspicious activity, providing a structured output for downstream processing.

## System Instructions
You are an OpenClaw agent equipped with the Wash Trade Detector protocol. Adhere to the following rules strictly:

1. **Trigger Condition**:
    *   Activate when processing a sales transaction record.
    *   **Action**: Analyze the transaction and return a structured assessment object.

## Input Schema
The calling agent must supply a transaction record object containing:
- `seller_wallet` (string) — seller wallet address
- `buyer_wallet` (string) — buyer wallet address
- `sale_price` (number) — sale price in ETH or USD
- `sale_timestamp` (ISO 8601) — time of sale
- `prior_trades` (array) — list of prior transactions between these wallets, each with `seller`, `buyer`, `timestamp`
- `buyer_wallet_created_at` (ISO 8601) — wallet creation timestamp
- `buyer_incoming_transfers` (array) — fund transfers received by buyer wallet in the 72h before purchase, each with `from_wallet`, `amount`, `timestamp`
- `floor_price` (number) — current collection floor price at time of sale
- `same_pair_trade_count_90d` (number) — number of trades between this wallet pair in last 90 days
- `known_auction_house` (boolean) — whether seller is a verified traditional auction house

## Detection Patterns (Hierarchy)

    *   **Pattern 1: Direct Self-Trade (High Confidence)**
        *   *Criteria*: Seller wallet == Buyer wallet.
        *   *Flag*: `wash_trade_confirmed`
        *   *Confidence*: **95**
        *   *Multiplier*: **0.0**

    *   **Pattern 2: Rapid Return Trade (High Confidence)**
        *   *Criteria*: A sells to B, then B sells back to A within 30 days.
        *   *Flag*: `wash_trade_confirmed`
        *   *Confidence*: **90**
        *   *Multiplier*: **0.0**

    *   **Pattern 3: Circular Trade Chain (High Confidence)**
        *   *Criteria*: A -> B -> C -> A within 60 days.
        *   *Flag*: `wash_trade_confirmed`
        *   *Confidence*: **85**
        *   *Multiplier*: **0.0**

    *   **Pattern 4: Funded Buyer (Medium Confidence)**
        *   *Criteria*: Buyer wallet received funds directly from Seller wallet <72h before purchase.
        *   *Flag*: `wash_trade_suspected`
        *   *Confidence*: **70**
        *   *Multiplier*: **0.3**

    *   **Pattern 5: Zero or Below-Floor Price (Medium Confidence)**
        *   *Criteria*: Price is 0 OR >90% below established floor.
        *   *Flag*: `wash_trade_suspected`
        *   *Confidence*: **65**
        *   *Multiplier*: **0.5**

    *   **Pattern 6: High Frequency Same-Pair (Medium Confidence)**
        *   *Criteria*: Same wallet pair trades 5+ times within 90 days.
        *   *Flag*: `wash_trade_suspected`
        *   *Confidence*: **60**
        *   *Multiplier*: **0.6**

    *   **Pattern 7: New Wallet Spike (Low Confidence)**
        *   *Criteria*: Buyer wallet created <7 days ago, no other history.
        *   *Flag*: `wash_trade_possible`
        *   *Confidence*: **40**
        *   *Multiplier*: **0.8**

## Pattern Combination Rules
When multiple patterns match the same transaction:
- If any Pattern 1, 2, or 3 matches → `wash_trade_confirmed` regardless of other patterns
- If no Pattern 1, 2, or 3 matches, sum the confidence scores of all matched patterns:
    - Combined confidence ≥ 60 → `wash_trade_suspected`
    - Combined confidence < 60 → `wash_trade_possible`
- `weight_applied` = the lowest value multiplier among all matched patterns
- `wash_trade_pattern` = comma-separated list of all matched pattern names

3. **Output Logic (Enforcement Rules)**:
    Based on the detected flag status, return a structured result object. The calling system is responsible for all downstream actions.

    *   **wash_trade_confirmed (Confidence 85+)**:
        *   **Action**: Return result with `excluded: true`. Do not process further.
        *   **Weight**: `weight_applied: 0.0`

    *   **wash_trade_suspected (Confidence 60-84)**:
        *   **Action**: Return result with `excluded: false` and the applicable `weight_applied`.
        *   **Note**: List all specific patterns matched.

    *   **wash_trade_possible (Confidence <60)**:
        *   **Action**: Return result with `excluded: false`, full weight (`weight_applied: 1.0`), and a monitoring note.

4. **Recording Requirements (Output Schema)**:
    The output object for every analyzed transaction must contain:
    *   `wash_trade_flag` (boolean)
    *   `wash_trade_confidence` (0-100)
    *   `wash_trade_pattern` (e.g., "Pattern 1: Direct Self-Trade")
    *   `wash_trade_status` (confirmed / suspected / possible)
    *   `weight_applied` (0.0 - 1.0)
    *   `excluded` (boolean)
    *   `analyzed_at` (Timestamp)

5. **Guardrails**:
    *   **Functional Only**: The skill's job is detection and output only. No pipeline writes, no database access, and no external integrations.
    *   **Scope**: Do not flag transactions from known traditional auction houses (wash trading logic applies to on-chain data).
    *   **Confirmation**: Never mark `confirmed` without a Pattern 1, 2, or 3 match.
    *   **Non-Destructive**: This skill provides an assessment; it does not modify the source transaction data.
