# xhunt-hot-tweets-skill

[English](README.md)

一个可用于 OpenClaw / Codex 的技能：从 XHunt 抓取热门推文，并输出结构化中文摘要。

## 解决的问题

- 人工筛选 X/Twitter 热帖噪音大、耗时高。
- 这个技能会读取 XHunt 榜单（`global`/`cn`，`1h/4h/24h`，可带标签），并按固定格式输出：
  - 推文链接
  - 一句话中文摘要
  - 互动数据（`views/likes/retweets/score`）
- 支持两种模式：
  - `all`：不过滤争议/政治内容
  - `ai-product-only`：只保留 AI 产品/模型/工具相关内容

## 环境要求

- 可访问 `https://trends.xhunt.ai`
- 运行环境最好支持 browser snapshot（优先抓取策略）
- 失败时可降级 web fetch（字段可能不完整）

## 通过 ClawHub 安装

```bash
npx clawhub login
npx clawhub install xhunt-hot-tweets
openclaw skills info xhunt-hot-tweets
```

## 通过 GitHub 安装

```bash
git clone https://github.com/DoTheWorkNow/xhunt-hot-tweets-skill.git
mkdir -p ~/.openclaw/workspace/skills/xhunt-hot-tweets
rsync -a --delete ./xhunt-hot-tweets-skill/ ~/.openclaw/workspace/skills/xhunt-hot-tweets/
openclaw skills info xhunt-hot-tweets
```

可选刷新：

```bash
openclaw gateway restart
```

## 触发示例

- `四小时最火帖子`
- `只要 AI 的最火推文，给我 Top20`
- `给我热门帖子链接+摘要`
