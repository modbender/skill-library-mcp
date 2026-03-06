---
name: solax-summary-fetch
description: Fetch inverter summary data from the Solax Cloud API using the npm package solax-cloud-api. Use when the user provides (or has configured) a Solax tokenId and inverter serial number (sn) and wants current/summary energy data returned as JSON (typed as SolaxSummary) for dashboards/automation.
---

# solax-summary-fetch

Fetch Solax inverter summary data as JSON.

## Setup (one-time)

This skill uses Node.js and the npm package `solax-cloud-api`.

Install dependencies inside the skill folder:

```bash
cd /home/openclaw/.openclaw/workspace/skills/solax-summary-fetch/scripts
npm install
```

(We use `npm install` instead of `npm ci` because this skill does not ship with a lockfile.)

## Inputs

You need:

- `tokenId` (Solax Cloud API token id)
- `sn` (inverter serial number)

### Recommended: environment variables

Set these in your runtime (preferred so you don’t leak secrets into shell history):

- `SOLAX_TOKENID`
- `SOLAX_SN`

**Do not** hardcode credentials into the skill files.

### Alternate: CLI arguments

Pass them explicitly as:

- `--tokenId <tokenId>`
- `--sn <serial>`

## Command

```bash
cd /home/openclaw/.openclaw/workspace/skills/solax-summary-fetch/scripts
node fetch_summary.mjs --tokenId "$SOLAX_TOKENID" --sn "$SOLAX_SN"
```

## Output

- Prints a single JSON object to stdout.
- The JSON conforms to the **SolaxSummary** interface exposed by `solax-cloud-api` (see `references/solax-summary.d.ts`).
- Under the hood (solax-cloud-api v0.2.0): fetches `getAPIData()` then converts via `SolaxCloudAPI.toSummary()`.

## Guardrails

- Never print or log the tokenId beyond confirming whether it is set (redact it).
- If the API call fails, return a structured error JSON with `ok:false` and a short `error` message.
