# XHunt 热门推文 Skill

[English](README.md)

一个可发布到 OpenClaw / Codex 生态的技能：从 XHunt 抓取热门推文，并输出结构化中文摘要。

## 能力说明

- 读取 XHunt 榜单（`global` 或 `cn`，`1h/4h/24h`，可带标签）
- 稳定输出格式：
  - 推文链接
  - 一句话中文摘要
  - 互动数据（`views/likes/retweets/score`）
- 支持两种过滤模式：
  - `all`：不过滤争议/政治内容
  - `ai-product-only`：仅保留 AI 产品/模型/工具更新

## 文件结构

- `SKILL.md`：技能主规范（触发、参数、抓取、输出、质量门槛）
- `agents/openai.yaml`：发布平台展示元信息
- `README.md` / `README.zh-CN.md`：说明文档
- `CHANGELOG.md`：版本记录
- `LICENSE`：开源协议

## 环境要求

- 可访问 `https://trends.xhunt.ai`
- 运行环境最好支持 browser snapshot（优先抓取策略）
- 失败时可降级 web fetch（字段可能不完整）

## 本地安装（OpenClaw）

```bash
mkdir -p ~/.openclaw/workspace/skills/xhunt-hot-tweets
rsync -a --delete ./xhunt-hot-tweets-skill/ ~/.openclaw/workspace/skills/xhunt-hot-tweets/
openclaw skills info xhunt-hot-tweets
```

## 触发示例

- `四小时最火帖子`
- `只要 AI 的最火推文，给我 Top20`
- `给我热门帖子链接+摘要`

## 发布到 ClawHub

在仓库根目录执行：

```bash
clawhub login
clawhub publish . \
  --slug xhunt-hot-tweets \
  --name "XHunt Hot Tweets" \
  --version 2.0.1 \
  --changelog "Hardened release docs and publishing metadata." \
  --tags latest,ai,twitter,trend
```

## 说明

- 这是指令型 skill，不包含任何私钥或 token。
- 结果完整度受上游页面结构稳定性影响。
