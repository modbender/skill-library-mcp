# xhunt-hot-tweets-skill

[中文说明](README.zh-CN.md)

A shareable OpenClaw/Codex skill that extracts hot tweets from XHunt and returns structured Chinese summaries.

## Problem It Solves

- Manually checking X/Twitter hot topics is noisy and time-consuming.
- This skill pulls XHunt ranking pages (`global`/`cn`, `1h/4h/24h`, optional tags) and returns a stable format:
  - tweet link
  - one-line Chinese summary
  - engagement stats (`views/likes/retweets/score`)
- It supports:
  - `all` mode (no content exclusion)
  - `ai-product-only` mode (focus on AI products/models/tools)

## Requirements

- Access to `https://trends.xhunt.ai`
- Runtime that can use browser snapshot tools for best extraction quality
- Fallback to web fetch is supported but may return incomplete fields

## Install From ClawHub

```bash
npx clawhub login
npx clawhub install xhunt-hot-tweets
openclaw skills info xhunt-hot-tweets
```

## Install From GitHub

```bash
git clone https://github.com/DoTheWorkNow/xhunt-hot-tweets-skill.git
mkdir -p ~/.openclaw/workspace/skills/xhunt-hot-tweets
rsync -a --delete ./xhunt-hot-tweets-skill/ ~/.openclaw/workspace/skills/xhunt-hot-tweets/
openclaw skills info xhunt-hot-tweets
```

Optional refresh:

```bash
openclaw gateway restart
```

## Trigger Examples

- `四小时最火帖子`
- `只要 AI 的最火推文，给我 Top20`
- `给我热门帖子链接+摘要`
