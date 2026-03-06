# Signet Guardian

Payment guard middleware for AI agents. Enforces a single policy layer (payments on/off, per-transaction limit, monthly cap) so any payment-capable skill can route through it before and after spending.

- **Preflight** — Check if a payment is allowed (ALLOW / DENY / CONFIRM_REQUIRED).
- **Record** — Append a completed payment to the ledger (enforces monthly cap under lock).
- **Report** — View spending for today or month.
- **Policy** — Show or edit limits and rules.

Full behaviour and agent contract: see [SKILL.md](./SKILL.md).

## Requirements

- Node.js 18+
- `tsx` (used via `npx`, or install locally)

## Install

```bash
pnpm install
# or: npm install
```

## Configuration

**Source of truth:** The CLI reads policy from **OpenClaw config** first (`signet.policy` in e.g. `~/.openclaw/openclaw.json`), then falls back to `references/policy.json`. So you can edit policy in the **Control UI (Dashboard)** if the extension is installed; see [openclaw-extension/README.md](./openclaw-extension/README.md).

Policy shape (file or config `signet.policy`). Example:

```json
{
  "paymentsEnabled": true,
  "maxPerTransaction": 20,
  "maxPerMonth": 500,
  "currency": "GBP",
  "requireConfirmationAbove": 5,
  "blockedMerchants": [],
  "allowedMerchants": []
}
```

Create or edit with:

```bash
npx tsx scripts/signet-cli.ts signet-policy --edit
```

Interactive wizard (no JSON editing):

```bash
npx tsx scripts/signet-cli.ts signet-policy --wizard
```

Migrate existing file-based policy into OpenClaw config (one-time):

```bash
npx tsx scripts/signet-cli.ts signet-policy --migrate-file-to-config
```

## Seeing Signet in the OpenClaw dashboard

### Install from GitHub (manual)

If you cloned this repo, the dashboard will show Signet only after the plugin is in OpenClaw’s extensions path.

1. **Open the dashboard**

   ```bash
   openclaw dashboard
   ```

   (or visit <http://127.0.0.1:18789/>)

2. **Install the plugin into the OpenClaw extensions path** (not only inside the skills repo):

   ```bash
   mkdir -p ~/.openclaw/workspace/.openclaw/extensions
   cp -r ~/.openclaw/workspace/skills/signet-guardian/openclaw-extension/signet-guardian \
     ~/.openclaw/workspace/.openclaw/extensions/
   ```

   Adjust the source path if your clone lives elsewhere (e.g. `$PWD/openclaw-extension/signet-guardian`).

3. **Restart the gateway**

   ```bash
   openclaw gateway restart
   ```

4. **In the dashboard** go to **Settings → Config** and look under:
   - `plugins.entries.signet-guardian.config.policy`  
   That’s where the Signet policy UI should appear.

   If it doesn’t, run:

   ```bash
   openclaw plugins list | grep -i signet
   ```

   and use the output to verify the plugin is loaded.

### Install via plugin (recommended when published)

When Signet is published as an OpenClaw plugin (e.g. on npm), install it with the plugin installer so the dashboard picks it up with no manual copy:

```bash
openclaw plugins install @signet-labs/signet-guardian
openclaw gateway restart
openclaw dashboard
```

Then you’ll see `plugins.entries.signet-guardian.config.policy` in the config UI automatically. The plugin is installed under `~/.openclaw/extensions/<id>/` and enabled for you.

*(Until the package is published, use the “Install from GitHub (manual)” steps above.)*

## Usage

Use the project’s `references/` by setting the skill dir:

```bash
export OPENCLAW_SKILL_DIR="$PWD"   # or OPENCLAW_BASE_DIR="$PWD"
```

| Command | Purpose |
|--------|--------|
| `npx tsx scripts/signet-cli.ts signet-policy --show` | Print current policy (config, then file) |
| `npx tsx scripts/signet-cli.ts signet-policy --edit` | Edit policy file in `$EDITOR` |
| `npx tsx scripts/signet-cli.ts signet-policy --wizard` | Interactive policy setup |
| `npx tsx scripts/signet-cli.ts signet-policy --migrate-file-to-config` | Copy file policy into OpenClaw config |
| `npx tsx scripts/signet-cli.ts signet-preflight --amount 10 --currency GBP --payee "shop.com" --purpose "Order"` | Check if payment is allowed |
| `npx tsx scripts/signet-cli.ts signet-record --amount 10 --currency GBP --payee "shop.com" --purpose "Order" --idempotency-key "order-123"` | Record a completed payment |
| `npx tsx scripts/signet-cli.ts signet-report --period month` | Show spending for the month |

Preflight returns JSON: `{"result":"ALLOW","reason":"..."}` or `"DENY"` / `"CONFIRM_REQUIRED"`. Exit code is 0 for ALLOW/CONFIRM_REQUIRED and 1 for DENY.

## Testing

Run the script that uses the repo’s `references/` and exercises preflight, record, and report:

```bash
./test-guardian.sh
```

## License

See repository.
