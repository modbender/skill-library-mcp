# XHunt Hot Tweets Skill

[中文说明](README.zh-CN.md)

A shareable OpenClaw/Codex skill that extracts hot tweets from XHunt and returns structured Chinese summaries.

## What It Does

- Reads XHunt tweet rankings (`global` or `cn`, `1h/4h/24h`, optional tags)
- Produces a stable output format:
  - tweet link
  - one-line Chinese summary
  - engagement stats (`views/likes/retweets/score`)
- Supports two modes:
  - `all`: no content exclusion
  - `ai-product-only`: keep only AI products/models/tools updates

## Files

- `SKILL.md`: skill behavior and output contract
- `agents/openai.yaml`: display metadata for agent registries
- `README.md` / `README.zh-CN.md`: usage and publishing docs
- `CHANGELOG.md`: version history
- `LICENSE`: open-source license

## Requirements

- Access to `https://trends.xhunt.ai`
- Runtime that can use browser snapshot tools for best extraction quality
- Fallback to web fetch is supported but may return incomplete fields

## Install Locally (OpenClaw)

```bash
mkdir -p ~/.openclaw/workspace/skills/xhunt-hot-tweets
rsync -a --delete ./xhunt-hot-tweets-skill/ ~/.openclaw/workspace/skills/xhunt-hot-tweets/
openclaw skills info xhunt-hot-tweets
```

## Trigger Examples

- `四小时最火帖子`
- `只要 AI 的最火推文，给我 Top20`
- `给我热门帖子链接+摘要`

## Publish To ClawHub

From repo root:

```bash
clawhub login
clawhub publish . \
  --slug xhunt-hot-tweets \
  --name "XHunt Hot Tweets" \
  --version 2.0.1 \
  --changelog "Hardened release docs and publishing metadata." \
  --tags latest,ai,twitter,trend
```

## Notes

- This skill is instruction-driven and does not include private keys/tokens.
- Data completeness depends on upstream page structure stability.
