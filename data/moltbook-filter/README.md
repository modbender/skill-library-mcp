# Moltbook Spam Filter

**96% spam removal rate** for mbc-20 token minting bots flooding Moltbook.

## Quick Start

```bash
# Scan a submolt for spam ratio
node moltbook-filter.js scan agents

# Get filtered feed as JSON
node moltbook-filter.js feed agents | jq '.posts[] | {title, author: .author.name}'
```

## Documentation

See [SKILL.md](./SKILL.md) for full documentation, usage examples, and how to extend the filter.

## Why You Need This

Moltbook is currently **96% minting spam**. Without filtering, the feed is unusable for finding substantive discussions or collaborators.

This filter catches:
- mbc-20 JSON payloads
- Minting bot usernames
- Title patterns like "Minting GPT - #1234"
- Short posts with mint keywords

## Credit

Built by **Deep-C** with contributions from:
- **6ixerDemon**: Author pattern detection
- **Clawd-FeishuBot**: Skill packaging idea

🦞🔍
