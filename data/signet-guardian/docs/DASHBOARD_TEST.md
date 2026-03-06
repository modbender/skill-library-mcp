# Manual test: Dashboard edit → CLI reads

Use this to confirm that policy edited in the OpenClaw Control UI is read by the CLI.

## Prerequisites

- OpenClaw extension installed (see [../openclaw-extension/README.md](../openclaw-extension/README.md)).
- Config path: `OPENCLAW_CONFIG_PATH` or `~/.openclaw/openclaw.json`.

## Steps

1. **Open Control UI** (Gateway dashboard) and go to **Settings**.
2. Find the **Signet Guardian** / **signet.policy** section.
3. **Change a value** (e.g. set "Max per transaction" to `25`) and save.
4. In a terminal, run:
   ```bash
   cd /path/to/signet-guardian
   export OPENCLAW_SKILL_DIR="$PWD"   # optional if config has policy
   npx tsx scripts/signet-cli.ts signet-policy --show
   ```
5. **Expected:** The printed JSON shows your updated value (e.g. `"maxPerTransaction": 25`).

## Optional: migrate file → config then verify

1. Ensure `references/policy.json` exists and is valid.
2. Run: `npx tsx scripts/signet-cli.ts signet-policy --migrate-file-to-config`
3. Run: `npx tsx scripts/signet-cli.ts signet-policy --show`
4. **Expected:** Output matches the previous file content; source is now config.
