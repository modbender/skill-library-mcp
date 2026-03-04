# People Relationship Map — OpenClaw Skill

A lightweight personal CRM that lives inside your OpenClaw workspace. Track
people, their connections, and what you know about them — stored as
**Obsidian-friendly Markdown** with a JSON graph index for fast querying.

## Features

- **Add & link people** — build a relationship graph through natural commands
- **Auto-capture** — the agent picks up people mentions from conversations
- **Query & search** — find people by org, tag, tier, or free-text notes
- **Obsidian-native** — each person gets a Markdown card with wikilinks and tags
- **Weekly digest** — cron job nudges you about relationships going stale
- **Mermaid export** — visualize your graph in any Markdown renderer

## Install

Copy the skill folder into your OpenClaw workspace:

```bash
cp -r people-relationship-map ~/.openclaw/workspace/skills/people-relationship-map
```

Then ask your agent to "refresh skills" or restart the gateway.

### Optional: enable the weekly digest cron

Add this to your `~/.openclaw/openclaw.json` under `cron.jobs`:

```json
{
  "name": "relationship-digest",
  "schedule": "0 9 * * 0",
  "command": "python3 skills/people-relationship-map/scripts/relmap.py stale --format message",
  "channel": "whatsapp"
}
```

This sends you a staleness report every Sunday at 9 AM.

## Quick start

Once installed, just talk to your agent naturally:

- "Add Alex Chen — he's an engineer at Acme, we met at the Denver offsite"
- "Alex and Jordan are on the same team"
- "I just had lunch with Sam"
- "Who do I know at Acme?"
- "Tell me about Alex"
- "Who is connected to Jordan?"
- "Show me my stale relationships"

## Storage

Everything lives in `<workspace>/people/`:

| File | Purpose |
|------|---------|
| `_graph.json` | Machine-readable node + edge index |
| `_<slug>.md` | One Markdown card per person |

The Markdown files use Obsidian-compatible `[[wikilinks]]` and `#tags`,
so you can symlink or sync the `people/` folder into your vault.

## Tier system

People are assigned a tier that controls staleness thresholds:

| Tier | Default threshold | Meaning |
|------|-------------------|---------|
| `close` | 14 days | Inner circle — family, close friends, key collaborators |
| `regular` | 30 days | Active relationships — colleagues, regular contacts |
| `acquaintance` | 90 days | Loose ties — conference contacts, distant colleagues |

## License

MIT
