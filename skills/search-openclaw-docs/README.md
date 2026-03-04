# search-openclaw-docs

📚 OpenClaw agent skill for fast documentation search.

Returns **file paths to read** - find the right doc quickly, then get full context.

**Fully offline** - FTS5 keyword search, no network calls.

## Install

### Via ClawHub
```bash
clawhub install search-openclaw-docs
```

### Manual
```bash
cd ~/.openclaw/skills
git clone https://github.com/karmanverma/search-openclaw-docs.git
cd search-openclaw-docs
npm install
node scripts/docs-index.js rebuild
```

## Usage

```bash
# Search docs
node scripts/docs-search.js "discord requireMention"

# Check index health
node scripts/docs-status.js

# Rebuild index (after OpenClaw update)
node scripts/docs-index.js rebuild
```

## Example Output

```
🔍 Query: discord only respond when mentioned

🎯 Best match:
   channels/discord.md
   "Discord (Bot API)"
   Keywords: discord, requiremention
   Score: 0.70

💡 Read with:
   cat /usr/lib/node_modules/openclaw/docs/channels/discord.md
```

## How It Works

- FTS5 keyword matching on titles, headers, config keys
- Handles camelCase terms like `requireMention`
- Porter stemming for flexible matching
- Index built locally from your OpenClaw version

## License

MIT
