# 🛒 bring-list — The Best Bring! Skill for OpenClaw

**Lightweight. Most features. Clean code. Privacy-first.**

The only Bring! skill that runs everywhere — just `curl` and `jq`, no Node.js, no Python, no pip, no npm. Works on any Linux, any container, any VPS out of the box.

## Why bring-list?

There are 6+ Bring! skills on ClawHub. Here's why this one wins:

### 🏆 Most features
Other skills only do add + remove. **bring-list** does everything:
- ✅ Add items (with quantity/description like "low fat, 1L")
- ✅ Add multiple items in one go ("Milk, Bread, Cheese|Gouda, Butter|Irish")
- ✅ Check off items when you've bought them
- ✅ Uncheck items (move back to shopping list)
- ✅ Remove items completely
- ✅ Remove or check off multiple items at once
- ✅ View all your lists and items
- ✅ JSON output for automation

### 🪶 Lightweight
| | **bring-list** | Others |
|---|---|---|
| Needs | `curl` + `jq` | Node.js + npm, or Python + pip |
| Install time | Instant | Minutes of downloading packages |
| Works in containers | Always | Often breaks |

### 🧠 Built for AI agents
- **Step-by-step Agent Setup Guide** — your agent knows exactly how to help you set up
- **Privacy-first credential setup** — your agent asks whether you want to share credentials in chat or enter them privately in your own terminal
- **Default list support** — say "put milk on the list" without naming the list every time
- **Partial name matching** — "einkauf" finds "Einkaufsliste"
- **Smart argument parsing** — the agent figures out what's an item and what's a list name

### 🔒 Clean & secure
- No VirusTotal flags (some other Bring! skills are flagged as suspicious!)
- Credentials stored with `chmod 600` (owner-only)
- No external services — talks directly to Bring! API
- Fully auditable: one bash script, ~850 lines, no magic

## Installation

```bash
clawhub install bring-list
```

## Quick Setup

Tell your agent: *"Set up the Bring shopping list skill"* — it will walk you through it.

Or manually:
```bash
scripts/bring.sh setup
```

You need a [Bring!](https://getbring.com) account (free). If you signed up via Google/Apple, set a direct password first in the Bring! app (Settings → Account → Change Password).

## Just Talk Naturally

- *"Put milk and eggs on the shopping list"*
- *"What's on our list?"*
- *"Check off the butter, we got it"*
- *"Add bread, cheese, and yogurt to the list"*
- *"Remove the tomatoes"*

Your agent handles the rest.

## Configuration

`~/.config/bring/credentials.json`:
```json
{
  "email": "your@email.com",
  "password": "your-password",
  "default_list": "Einkaufsliste",
  "country": "DE"
}
```

- `default_list` — Skip typing the list name every time
- `country` — Item catalog language (default: `DE`). Use `AT`, `CH`, `US`, `FR`, etc.

## Good to Know

- **Shared lists sync instantly** — your partner sees changes in real time
- **Lists must be created/deleted in the Bring! app** — API limitation, not ours
- **Special characters fully supported** — umlauts, quotes, emoji, all fine
- **Token auto-refreshes** — no manual re-login needed

## Privacy

Your credentials never leave your machine. They're stored locally and only sent directly to Bring!'s servers. No third-party services, no telemetry, no cloud.

During setup, your agent gives you the choice: share credentials in chat (convenient, written directly to file and never repeated), or enter them privately in your own terminal via `read -s` (credentials never appear in chat at all).

## License

MIT
