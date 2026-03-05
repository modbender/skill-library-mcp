# Maccabi pharmacy stock check - search prescription medication stock at every nearby branch

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-purple)

> **[Agent Skills](https://agentskills.io) format** - works with OpenClaw, Claude, Cursor, Codex, and other compatible clients

Search for medications and check real-time stock availability at Maccabi Pharm locations in Israel.

## The problem

You need a prescription medication. You go to Maccabi's website, search for the drug, pick a pharmacy - out of stock. Pick another - also out of stock. Try a third. Meanwhile, the branch two blocks away had it the whole time.

With this tool installed, your AI assistant can check every Maccabi Pharm branch in your city in one search. Ask it the morning you're planning to go, and know exactly which pharmacy has your medication before you leave the house. You can also set up a cron job or scheduled reminder to check stock automatically - no manual searching at all.

## Installation

```bash
npx skills add alexpolonsky/agent-skill-maccabi-pharm-search
```

<details>
<summary>Manual install (any agent skills client)</summary>

```bash
# OpenClaw
git clone https://github.com/alexpolonsky/agent-skill-maccabi-pharm-search ~/.openclaw/skills/maccabi-pharm-search

# Claude
git clone https://github.com/alexpolonsky/agent-skill-maccabi-pharm-search ~/.claude/skills/maccabi-pharm-search

# Cursor
git clone https://github.com/alexpolonsky/agent-skill-maccabi-pharm-search ~/.cursor/skills/maccabi-pharm-search
```

</details>

<details>
<summary>Standalone CLI</summary>

No installation required - just run with Node.js:

```bash
git clone https://github.com/alexpolonsky/agent-skill-maccabi-pharm-search
cd agent-skill-maccabi-pharm-search
node scripts/pharmacy-search.js search "nurofen"
```

Requires Node.js 16+ with no external dependencies.

</details>

## What you can ask

> "Is Nurofen in stock at any Maccabi pharmacy in Tel Aviv?"

- "Which Maccabi pharmacies in Haifa have Nurofen in stock right now?"
- "I need Nurofen - where can I find it in Ramat Gan?"
- "Check if Acamol is available at any branch near me"

Or use the CLI directly:
```bash
node scripts/pharmacy-search.js search "nurofen"
node scripts/pharmacy-search.js stock 58299
```

## Automation examples

Ask your AI agent to set up recurring checks:

- "Check every morning if Nurofen is back in stock at any Maccabi pharmacy in Tel Aviv and let me know"
- "Each day I need to pick up my medication - check which branches have it and tell me the closest one"
- "Check every morning at 8am and alert me when Nurofen Forte becomes available at a pharmacy in Ramat Gan"

## Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Search drug catalog, get Largo codes |
| `stock <largo_code> [city]` | Check real-time stock at pharmacies |
| `branches maccabi [city]` | List Maccabi Pharm locations |
| `cities` | List all 51 available city codes |
| `test` | Run functionality test |

Common city codes: Tel Aviv `5000` (default), Jerusalem `3000`, Haifa `4000`, Beer Sheva `9000`.

<details>
<summary>All city codes</summary>

Run `node scripts/pharmacy-search.js cities` to see all 51 available city codes.

Common examples:
- Tel Aviv: 5000 (default)
- Jerusalem: 3000
- Haifa: 4000
- Beer Sheva: 9000
- Bat Yam: 6200
- Netanya: 7400

</details>

<details>
<summary>Output example</summary>

```bash
$ node scripts/pharmacy-search.js search "nurofen"
NUROFEN LIQUID 20 CAP
  Largo Code: 58299
  Prescription: No

$ node scripts/pharmacy-search.js stock 58299
=== Pharmacies with Stock ===
מכבי פארם-ת"א-בלפור 10
   בלפור 10, תל אביב - יפו
   03-9193013
```

</details>

<details>
<summary>Programmatic use</summary>

```javascript
import { MaccabiAdapter } from './scripts/pharmacy-search.js';

const maccabi = new MaccabiAdapter();
const results = await maccabi.searchDrug('nurofen');
const stock = await maccabi.checkStock('58299', '5000');
```

</details>

## How it works

Queries the same endpoints that power Maccabi Pharm's website.

## Limitations

- Only supports Maccabi Pharm locations (not other pharmacy chains)
- Stock data may be delayed or inaccurate
- City codes are region-specific (not street-level)

## Legal

Independent open-source tool. Not affiliated with or endorsed by Maccabi Healthcare Services. Stock information comes from the same APIs that power the website and may not reflect actual availability. Always confirm stock by calling the pharmacy before visiting. Provided "as is" without warranty of any kind.

## Author

[Alex Polonsky](https://alexpolonsky.com) - [GitHub](https://github.com/alexpolonsky) - [LinkedIn](https://www.linkedin.com/in/alexpolonsky/) - [Twitter/X](https://x.com/alexpo)

Part of [Agent Skills](https://github.com/alexpolonsky/agent-skills) - [Specification](https://agentskills.io/specification)
