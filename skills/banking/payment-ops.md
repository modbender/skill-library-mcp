# Payment Operations Guide

Use this guide for payment execution and settlement troubleshooting.

## Rail Selection Snapshot

| Rail | Typical Speed | Reversibility | Primary Risk |
|------|---------------|---------------|--------------|
| Internal transfer | Immediate | Medium | Wrong-account routing |
| ACH batch | Same day to next day | Medium | Cutoff miss and return codes |
| Domestic wire | Same day | Low | Irreversible after release |
| Card settlement | 1-3 days | Medium | Chargeback and dispute windows |
| International transfer | 1-5 days | Low | Compliance and beneficiary mismatch |

## Pre-Execution Controls

Before any transfer flow:

1. Confirm sender authority and account status.
2. Validate beneficiary details using approved source.
3. Confirm amount, currency, and fee handling.
4. Check cutoff window and expected settlement time.
5. Verify required approvals were completed.

## Reconciliation Triage

When balances do not match:

1. Verify timing mismatch first (cutoff, weekend, timezone).
2. Check duplicate postings and partial settlements.
3. Compare ledger amount against processor statement.
4. Isolate one transaction ID and trace full lifecycle.
5. Record root cause and prevention control.

## High-Risk Signals

- New beneficiary plus urgent same-day release request.
- Amount far above normal customer pattern.
- Repeated correction requests after approval.
- Manual override request with no documented reason.

Treat high-risk signals as incident candidates and switch to `incident-response.md`.
