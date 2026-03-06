# Questrade Browser Playbook

Use this playbook when preparing or executing stock trades in Questrade Web for openclaw.ai workflows.

## 0) Privacy Baseline
- Keep credentials, MFA codes, and tokens on the user's device only.
- Never paste passwords, token secrets, or session cookies into prompts or logs.
- Use masked account/order identifiers in generated artifacts unless explicitly overridden.
- Keep broker exports local; redact personal fields before sharing externally.

## 1) Session Preparation
- Confirm the target account (cash, margin, or registered).
- Confirm market session status (pre-market, regular, after-hours).
- Confirm which order types are allowed in the current session.
- Confirm browser tab is logged in and session has not timed out.
- Complete the Special Safety Check before preparing final order ticket fields.

## 2) Build the Order Ticket
- Open the order entry panel in Questrade Web.
- Select the account intentionally. Do not rely on defaults.
- Search and select the exact symbol.
- Set side (`Buy` or `Sell`) and share quantity.
- Set order type:
  - `Market`: no limit/stop price
  - `Limit`: limit price required
  - `Stop`: stop trigger required
  - `Stop Limit`: stop + limit required
- Set time in force (`DAY`, `GTC`, `GTED`) according to strategy.

## 3) Cross-Check Data Before Submit
- Compare broker quote with Yahoo snapshot from `market_snapshot.py`.
- Flag divergence above user tolerance before submission.
- Confirm estimated notional, fees, and available buying power.
- Confirm stop-loss or exit logic is documented.
- If live-mode freshness/drift thresholds fail, block submission and refresh data.

## 4) Submit and Verify
- Review the full ticket one final time.
- Submit order in Questrade Web.
- Capture:
  - Confirmation ID
  - Submitted timestamp (UTC)
  - Initial status (open/partial/filled/rejected/cancelled)

## 5) Post-Trade Monitoring
- Track fills until terminal state.
- Record average fill price and remaining quantity.
- Reconcile against strategy plan and risk limits.
- Save an execution log entry with all final values.

## 6) Failure Modes and Recovery
- Session timeout: re-authenticate, reload ticket, re-validate all fields.
- Quote mismatch: refresh data on both broker and Yahoo sides; do not submit stale ticket.
- Rejected order: capture reject reason and update order type/price logic.
- Partial fill drift: recompute residual risk and adjust stop/exit plan.

## 7) Non-Negotiable Safety Rules
- Never imply order execution without human confirmation in the broker UI.
- Never reuse stale order parameters from previous symbols.
- Never submit with ambiguous side, quantity, or order type.
- Never skip risk checks for urgency.
- Never request or store user secrets outside local user-controlled context.
