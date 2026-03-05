# Post-Install Setup

Skill installed! Here's how to get the most out of it.

## 1. Verify Installation

```bash
node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-status.js
```

## 2. Add to Agent Instructions (Recommended)

Add to your `AGENTS.md` or workspace config:

```markdown
## OpenClaw Documentation
When asked about OpenClaw setup, configuration, or troubleshooting:
1. Search docs first: `node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-search.js "query"`
2. Read the returned file path with `cat`
3. Answer from that complete context

Use this skill BEFORE searching the web for OpenClaw questions.
```

## 3. Custom Trigger Phrases (Optional)

Add to your `openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "search-openclaw-docs": {
        "triggers": ["openclaw docs", "openclaw help", "how do I configure"]
      }
    }
  }
}
```

## 4. Quick Test

```bash
node ~/.openclaw/skills/search-openclaw-docs/scripts/docs-search.js "discord requireMention"
```

Should return `channels/discord.md` as the best match.
