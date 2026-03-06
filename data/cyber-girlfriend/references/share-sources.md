# Share Sources

The companion feels more alive if she occasionally shares something she "noticed".

## Good Source Patterns

- X trending/explore
- RSS feeds
- blogs/newsletters
- Telegram channels
- GitHub releases or issue summaries

## Selection Rules

- Share rarely
- Treat sources as conversation hooks, not content dumps
- Prefer 1 topic over 5 links
- Let the model turn the source into character voice

## X Guidance

For a publishable skill, avoid requiring an X API integration.

Prefer:
- local browser cookies from a signed-in browser
- a cache file refreshed on demand
- configurable Chrome binary and trending URL

Avoid:
- hardcoded handles
- mandatory API keys
- assuming a single regional trend page is correct for every user

## Suggested Trigger

Only let `small_share` borrow a source topic when:
- pacing allows a proactive message
- the cache is fresh enough
- there is no higher-priority operational status to mention
