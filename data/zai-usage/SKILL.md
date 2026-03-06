---
name: zai-usage
version: 1.1.0
description: Monitor Z.AI GLM Coding Plan usage and quota limits. Track token consumption, view reset times, and check subscription status.
author: openclaw
license: MIT
keywords:
  - z.ai
  - glm
  - usage
  - quota
  - monitoring
  - tokens
homepage: https://z.ai
repository: https://github.com/openclaw/skills
---

# Z.AI Usage Monitor

Track your Z.AI GLM Coding Plan usage in real-time.

## Quick Start

```bash
# Check usage
~/.openclaw/skills/zai-usage/scripts/usage-summary.sh

# Quick status
~/.openclaw/skills/zai-usage/scripts/quick-check.sh
```

## Setup

1. Get your JWT token from https://z.ai/manage-apikey/subscription
   - Open DevTools (F12)
   - Application → Local Storage → `z-ai-open-platform-token-production`

2. Store in `~/.openclaw/secrets/zai.env`:
   ```
   ZAI_JWT_TOKEN=eyJhbGci...
   ```

## What You See

- **5-Hour Quota** - Rolling token usage with reset countdown
- **Monthly Quota** - Monthly token allocation
- **Web Tools** - Search/reader/zread call limits
- **Plan Level** - Lite/Pro subscription status

## Status Icons

| Icon | Usage |
|------|-------|
| ✅ | < 50% |
| ⚠️ | 50-80% |
| 🔴 | > 80% |

## Commands

Ask me:
- "How's our Z.AI usage?"
- "Check credit usage"
- "Are we running low on credits?"

## Requirements

- `curl` - HTTP requests
- `jq` - JSON parsing
- `bc` - Number formatting (optional)

## Sources

- https://github.com/zereraz/tokensight
- https://www.reddit.com/r/ZaiGLM/comments/1pmb7fj/how_to_check_zai_coding_usage/
