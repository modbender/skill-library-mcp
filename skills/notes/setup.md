# Setup — Notes

Read this when `~/notes/` doesn't exist or `~/notes/config.md` is missing.

## First Use

On first use, the skill will:
1. Create `~/notes/` directory structure
2. Create `~/notes/config.md` with default routing (all to local)
3. Ask the user about their preferred platforms

**Always inform the user** what files are being created and where.

## Setup Conversation

### 1. Understand Their Preferences

Ask open questions:
- "How do you currently take notes? Quick thoughts, meetings, journals?"
- "Any apps you already use? Apple Notes, Bear, Obsidian, Notion?"
- "Want me to help with notes whenever you mention meetings or ideas, or only when you ask?"

### 2. Configure Platform Routing

Based on their answers, suggest routing and **confirm before saving**:

```
Based on what you said, here's what I suggest:
- Meetings → Notion
- Journal → Bear  
- Everything else → local files

I'll save this to ~/notes/config.md. Sound good?
```

Wait for confirmation before writing config.

### 3. Check Platform Requirements

**Only if they want to use external platforms:**

| Platform | Requirement | Check |
|----------|-------------|-------|
| Apple Notes | `memo` CLI | `which memo` |
| Bear | `grizzly` CLI + token | `which grizzly` |
| Obsidian | `obsidian-cli` + vault | `which obsidian-cli` |
| Notion | API key | `~/.config/notion/api_key` |
| Evernote | `clinote` CLI | `which clinote` |

If a platform isn't set up, offer to help configure it or route to local instead.

## Files Created

This skill creates and manages:

```
~/notes/
├── config.md      # Platform routing configuration
├── index.md       # Note index with tags
├── actions.md     # Action items tracker
├── meetings/      # Meeting notes
├── decisions/     # Decision log
├── projects/      # Project notes
├── journal/       # Daily notes
└── quick/         # Quick captures
```

**Always tell the user** when creating new files or directories.

## Platform Credentials

If user wants external platform integration, they need to set up credentials themselves:

- **Notion**: User creates API key at notion.so/my-integrations
- **Bear**: User sets up token via Bear app (Help → API Token)

**Never assume credentials are configured.** Always ask the user before attempting to use external platforms. If not set up, route to local.

## Activation Preferences

Ask the user how they want the skill to activate:
- "Only when I explicitly ask for notes"
- "Whenever I mention meetings, decisions, or ideas"
- "Proactively remind me about overdue action items"

Save their preference in `~/notes/config.md` under a `## Preferences` section.

## Graceful Fallback

If a configured platform becomes unavailable:
1. Save to local instead
2. Inform the user: "Bear wasn't available, saved locally to ~/notes/quick/"
