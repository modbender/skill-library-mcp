---
name: open-claw-questrade
description: Execute and monitor stock trades for openclaw.ai workflows using Questrade's browser platform with Yahoo Finance cross-checks. Use when Codex is asked to prepare or review Questrade Web order tickets, monitor symbols from Questrade and Yahoo Finance, produce pre-trade or post-trade checklists, reconcile fills, or enforce privacy-safe trading operations where credentials and sensitive account data stay on the user's side only.
---

# Open Claw

## Overview
Use this skill to run a repeatable browser-trading workflow for Questrade with independent quote checks from Yahoo Finance. Keep execution manual in the broker UI, but automate preparation, validation, and monitoring artifacts.

## Workflow Decision Tree
1. Need a quote/monitoring snapshot across symbols: run `scripts/market_snapshot.py`.
2. Need a trade-ready plan with risk controls: run `scripts/build_trade_checklist.py` with Special Safety Check flags.
3. Need to place a trade in Questrade Web: follow `references/questrade-browser-playbook.md`.
4. Need field-level input/output rules: load `references/data-contracts.md`.
5. Need policy gating details: load `references/openclaw-policy-compliance.md`.

## Standard Execution Flow
1. Confirm trading intent: symbol, side, size, account, session constraints.
2. Pull live Yahoo quotes and optional Questrade export using `scripts/market_snapshot.py`.
3. Reject stale data if snapshot age exceeds user threshold.
4. Run Special Safety Check (mandatory) through `scripts/build_trade_checklist.py`:
- `--policy-ack OPENCLAW_POLICY_ACK`
- `--confirm-user-authorized`
- `--confirm-manual-execution`
- `--confirm-no-secrets-shared`
- Live mode also enforces risk cap, data freshness, and drift thresholds.
5. Draft or refine ticket with `scripts/build_trade_checklist.py`.
6. Enforce hard checks before submitting in browser:
- Confirm side and quantity.
- Confirm order type and time-in-force.
- Confirm max risk and stop/exit rule.
- Confirm buying power and open-order conflicts.
7. Submit manually in Questrade Web and record confirmation ID.
8. Capture post-trade state (fill price, remaining quantity, stop/target status).

## Guardrails
- Never claim an order is submitted unless a human confirms broker submission.
- Treat Yahoo as secondary market data, not authoritative execution data.
- Escalate if broker and Yahoo prices diverge beyond the configured tolerance.
- Refuse ambiguous instructions (missing side, quantity, or symbol).
- Require explicit user acknowledgement before high-impact actions.
- Block checklist generation when safety gate requirements fail.

## Privacy Rules (OpenClaw.ai)
- Keep all credentials, MFA tokens, session cookies, API keys, and passwords user-side only.
- Never ask the user to paste secrets into chat, files, or logs.
- Use masked identifiers in generated artifacts by default (account IDs, order IDs, personal details).
- Only include raw sensitive identifiers when the user explicitly asks and confirms local-only usage.
- Store outputs locally and avoid sharing raw broker exports unless redacted.

## Outputs
Generate one or more of these artifacts per task:
- `snapshot.json` or `snapshot.csv` from `scripts/market_snapshot.py`.
- `trade_checklist.md` from `scripts/build_trade_checklist.py`.
- A concise execution log containing timestamp, symbol, side, quantity, order type, and broker confirmation reference.

## Resource Loading Guide
- Load `references/data-contracts.md` when parsing or validating CSV and JSON payloads.
- Load `references/questrade-browser-playbook.md` when the user asks for browser execution steps, troubleshooting, or reconciliation.
- Load `references/openclaw-policy-compliance.md` when enforcing or explaining policy checks.
- Prefer scripts for deterministic output instead of recreating tables/checklists manually.
