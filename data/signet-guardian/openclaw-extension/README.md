# Signet Guardian — OpenClaw extension

This folder registers the **Signet Guardian** policy in the OpenClaw config schema so the **Control UI (Dashboard)** can show editable settings instead of raw JSON.

## What it provides

- **Config schema** for `signet.policy` (paymentsEnabled, maxPerTransaction, maxPerMonth, currency, requireConfirmationAbove, blockedMerchants, allowedMerchants).
- **UI hints** (labels, help text, order, group) so the dashboard renders friendly form fields in Settings.

## Install into OpenClaw workspace

Copy or link this folder into your OpenClaw workspace extensions:

```bash
# From the signet-guardian repo root
OPENCLAW_EXT=~/.openclaw/workspace/.openclaw/extensions
mkdir -p "$OPENCLAW_EXT"
cp -r openclaw-extension/signet-guardian "$OPENCLAW_EXT/"
# or: ln -s "$PWD/openclaw-extension/signet-guardian" "$OPENCLAW_EXT/signet-guardian"
```

Exact path may depend on your OpenClaw version; check Gateway docs for where it loads extensions.

## Runtime behavior

- **CLI** reads policy from OpenClaw config first (`signet.policy`), then falls back to `references/policy.json`.
- **Dashboard** edits write to the OpenClaw config; the CLI will pick them up on the next run.
- To migrate an existing file-based policy into config once:  
  `signet-policy --migrate-file-to-config`

## Verifying

1. After installing the extension, open the Control UI Settings.
2. Confirm a “Signet Guardian” or “signet.policy” section with toggles and number fields.
3. Change a value (e.g. max per transaction) and save.
4. Run: `npx tsx scripts/signet-cli.ts signet-policy --show`  
   The printed policy should match what you set in the dashboard.
