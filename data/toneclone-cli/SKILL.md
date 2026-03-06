---
name: toneclone-cli
description: "Write in the user's authentic voice using ToneClone. Generate emails, messages, social posts, and other content that sounds like the user — not generic AI. Use trained personas for different writing styles and knowledge cards for context. Requires ToneClone account and CLI setup at toneclone.ai."
homepage: https://toneclone.ai
metadata: { "openclaw": { "emoji": "✍️", "requires": { "bins": ["toneclone"] }, "install": [ { "id": "brew", "kind": "brew", "formula": "toneclone/toneclone/toneclone", "bins": ["toneclone"], "label": "Install ToneClone CLI (brew)" } ] } }
---

# ToneClone CLI

Generate content in the user's authentic voice using their trained ToneClone personas.

## Setup

ToneClone requires an account and trained personas. Get started at https://toneclone.ai

**Install CLI (Homebrew):**
```bash
brew tap toneclone/toneclone
brew install toneclone
```

**Authenticate:**
```bash
toneclone auth login
```

## Writing Content

```bash
toneclone write --persona="<name>" --prompt="<what to write>"
```

### With Knowledge Cards

```bash
toneclone write --persona="<name>" --knowledge="<card1>,<card2>" --prompt="<prompt>"
```

### Examples

**Chat reply:**
```bash
toneclone write --persona="Chat" \
  --prompt="Reply to: 'Hey, are you free this weekend?' — say yes, suggest Saturday"
```

**Work email:**
```bash
toneclone write --persona="Work Email" --knowledge="Work,Scheduling" \
  --prompt="Follow-up email about project timeline, offer to schedule a call"
```

**Social post:**
```bash
toneclone write --persona="Twitter" \
  --prompt="Announce our new feature launch, keep it punchy"
```

## Providing Context

Pass relevant context in the prompt for better results:
- Thread/conversation being replied to
- Background on the topic
- Recipient info or relationship context

## Quick Commands

| Task | Command |
|------|---------|
| Write content | `toneclone write --persona="Name" --prompt="..."` |
| List personas | `toneclone personas list` |
| List knowledge cards | `toneclone knowledge list` |
| Check auth | `toneclone auth status` |

## Personas vs Knowledge Cards

| Need | Use |
|------|-----|
| Different writing style | Different **persona** |
| Different context/facts | Different **knowledge card** |

## More Info

- Full documentation: https://toneclone.ai/cli
- Create personas & training: https://app.toneclone.ai
- Source code: https://github.com/toneclone/cli
