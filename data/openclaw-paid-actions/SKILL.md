---
name: openclaw-paid-actions
description: Use the openclaw_paid_action tool to list actions, generate USDC invoices, and execute only after manual payment confirmation on Solana.
metadata: {"openclaw":{"emoji":"💸","skillKey":"openclaw-paid-actions","requires":{"bins":["node"],"env":["OPENCLAW_USDC_PAY_TO","OPENCLAW_PAID_ACTIONS_INVOICE_SECRET","OPENCLAW_PAID_ACTIONS_INVOICE_STORE_PATH"],"config":["plugins.entries.openclaw-paid-actions.enabled","plugins.entries.openclaw-paid-actions.config.payTo","plugins.entries.openclaw-paid-actions.config.invoiceSecret","plugins.entries.openclaw-paid-actions.config.invoiceStorePath","plugins.entries.openclaw-paid-actions.config.actions"]}},"moltbot":{"emoji":"💸","skillKey":"openclaw-paid-actions","requires":{"bins":["node"],"env":["OPENCLAW_USDC_PAY_TO","OPENCLAW_PAID_ACTIONS_INVOICE_SECRET","OPENCLAW_PAID_ACTIONS_INVOICE_STORE_PATH"],"config":["plugins.entries.openclaw-paid-actions.enabled","plugins.entries.openclaw-paid-actions.config.payTo","plugins.entries.openclaw-paid-actions.config.invoiceSecret","plugins.entries.openclaw-paid-actions.config.invoiceStorePath","plugins.entries.openclaw-paid-actions.config.actions"]}}}
---

# OpenClaw Paid Actions

Use this skill when an action must be paid before it runs.

Tool: `openclaw_paid_action`

This skill is instruction-only. It expects a trusted installed implementation of the `openclaw-paid-actions` plugin that provides `openclaw_paid_action`.

Actions:
- `list`: List configured paid actions.
- `quote`: Build USDC payment instructions for an action.
- `invoice`: Create a signed invoice token for an action/input.
- `status`: Check current invoice payment status.
- `wait`: Poll until the invoice is paid (or timeout/expiry).
- `confirm` (or `pay` alias): Validate payment transaction on-chain, then mark invoice paid.
- `execute`: Run the action after invoice is confirmed paid.

## Typical Flow

1. Call `openclaw_paid_action` with `action: "list"` to discover action IDs.
2. Call `openclaw_paid_action` with `action: "invoice"` and `actionId` (plus optional `input`, `recipient`, `memo`).
3. Send the returned `invoiceMessage` or `paymentInstructions` to the payer.
4. After payment is received, call `openclaw_paid_action` with `action: "confirm"` and `invoice` (or `invoiceId`) plus `transaction` to validate on-chain and mark paid.
   You can also pass `paymentProofText` with the raw user reply; the tool extracts the Solana tx signature automatically.
5. Call `openclaw_paid_action` with `action: "wait"` (or `status`) to know when it is paid.
6. Call `openclaw_paid_action` with `action: "execute"` and `invoice` to run after payment.

## Plugin Config

Configure under `plugins.entries.openclaw-paid-actions.config`:

```json
{
  "network": "solana:mainnet",
  "payTo": "${OPENCLAW_USDC_PAY_TO}",
  "invoiceSecret": "${OPENCLAW_PAID_ACTIONS_INVOICE_SECRET}",
  "invoiceStorePath": "${OPENCLAW_PAID_ACTIONS_INVOICE_STORE_PATH}",
  "allowRunAsRoot": false,
  "requirePersistentInvoiceSecret": true,
  "requireInvoiceStorePath": true,
  "enforceReviewedScripts": true,
  "reviewedScriptsRoot": "scripts/paid-actions",
  "requiredNodeMajor": 20,
  "defaultInvoiceWaitSeconds": 900,
  "invoicePollIntervalMs": 3000,
  "maxTimeoutSeconds": 120,
  "defaultTaskTimeoutMs": 30000,
  "maxOutputBytes": 32768,
  "actions": {
    "x-shoutout": {
      "description": "Post a paid shoutout on X",
      "command": ["node", "scripts/paid-actions/x-shoutout.mjs"],
      "cwd": ".",
      "price": "0.03",
      "timeoutMs": 45000
    }
  }
}
```

Notes:
- Each action runs exactly the configured command array.
- Invoice execution uses the input embedded in the invoice token.
- Action input is exposed as `OPENCLAW_PAID_ACTION_INPUT_JSON`.
- Command output is truncated at `maxOutputBytes`.
- If `notifySessionKey` is set on invoice creation, the gateway emits a system event when payment is recorded.
- The tool is optional in OpenClaw; add `openclaw_paid_action` to agent `tools.allow`.
- Production defaults block startup if `invoiceSecret` or `invoiceStorePath` is missing.
- Production defaults block unreviewed commands; keep actions under `scripts/paid-actions`.
- Review every configured action command before enabling autonomous execution.

## Real Action Inputs

For `x-shoutout`:

```json
{
  "handle": "openclaw",
  "message": "Huge shoutout to @openclaw for supporting this build!",
  "link": "https://x.com/openclaw"
}
```

For `discord-shoutout`:

```json
{
  "name": "Daniel",
  "note": "Thanks for supporting the build."
}
```
