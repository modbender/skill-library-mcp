# Scripts (Node.js) — nadfunagent

All scripts are **Node.js** (no Python). Run from repo root or from the skill directory.

**Data directory:** `NADFUNAGENT_DATA_DIR` (default `$HOME/nadfunagent`). Override report path with `POSITIONS_REPORT_PATH`.

| Script | Purpose |
|--------|---------|
| `check_positions.js` | Output current positions (holdings) as JSON from Agent API. |
| `write_positions_report.js` | Read one JSON object from stdin and write to `positions_report.json`. |
| `save_tokens.js` | Read token addresses (0x...) one per line from stdin and append to `found_tokens.json`. |

**Examples:**

```bash
# From repo root or skill directory
node scripts/check_positions.js 0xYourWalletAddress
echo '{"timestamp":"...","wallet":"0x...","positions":[],"summary":{}}' | node scripts/write_positions_report.js
echo -e "0xabc...\n0xdef..." | node scripts/save_tokens.js

# Custom data directory
NADFUNAGENT_DATA_DIR=/tmp/nadfunagent echo '{}' | node scripts/write_positions_report.js
```

**Dependencies:** Node.js built-ins only (`fs`, `path`, `fetch` in Node 18+).
