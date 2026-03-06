# OpenClaw.ai Policy Compliance

Use this file when enforcing policy behavior for `open-claw-questrade`.

## 1) Special Safety Check (Mandatory)
Before producing a live-trade checklist, confirm:
- Policy acknowledgement phrase is present (`OPENCLAW_POLICY_ACK`).
- User authorization is explicitly confirmed.
- Manual execution is explicitly confirmed (no autonomous submission).
- No secrets were shared in prompt or artifacts.

## 2) Live Mode Enforcement
In `live` mode, block output unless:
- `risk_cap_usd` is provided.
- `data_age_seconds` is provided and within `max_data_age_seconds`.
- Broker-vs-reference drift is within `max_price_drift_pct` when supplied.
- `market` order type is explicitly allowed via override flag.

## 3) Sensitive Data Controls
- Mask account identifiers by default.
- Only include raw identifiers with explicit intent:
  - `--include-sensitive`
  - `--local-sensitive-storage-confirm`
- Never include secrets (passwords, MFA codes, tokens, cookies) in outputs.

## 4) Default Refusal Conditions
Refuse or block checklist generation when:
- Symbol, side, quantity, or order parameters are ambiguous.
- Safety confirmation flags are missing.
- Required live-mode checks fail.
- User asks to bypass compliance checks.

## 5) Operational Notes
- This skill supports policy-compliant execution support, not autonomous brokerage control.
- Human confirmation in Questrade browser is the only valid source of execution truth.

