# Roadmap

## 已完成 ✅

- **v0.1–v0.5** — 基础 Digest 浏览、SQLite 存储、i18n、Google OAuth、Sources CRUD、Source Packs 分享、JSON/RSS Feed、Mark 收藏
- **v0.6** — Soft Delete Sources（软删除避免 pack zombie）

## 近期 🔨

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P0 | **Multi-tenant Phase 1** | raw_items 表 + 采集管道，Source 级采集与 Digest 生成解耦 |
| P1 | **Multi-tenant Phase 2** | 基于用户订阅组合生成个性化 Digest |
| P1 | **Sources 集成 Cron** | Cron 读取 `/api/sources?active=true` 而非硬编码 Twitter |

## 中期方向 🧭

### 1. AI Agent Embed
嵌入 AI 编辑助理（Chat Widget），让用户可以与 Digest 内容互动：
- 右下角气泡式 Chat Box
- 行为感知：观察用户浏览模式，主动推荐
- 问答：针对当期 Digest 内容深入追问
- 场景示例："这条新闻的背景是什么？" "帮我追踪这个话题"

### 2. Agent Friendly
让整个系统对 AI Agent 友好，降低自动化接入门槛：
- 结构化 API 输出（JSON Schema 规范）
- MCP Server 支持（让 Claude/GPT agent 直接操作 Digest）
- Webhook 回调（Source 更新、Digest 生成完成事件通知）
- 幂等操作设计（agent 重试安全）

### 3. Channel 推送
Digest 通过多渠道主动分发，用户选择接收方式：
- **Telegram Bot** — 定时推送 + 按需查询
- **Feishu/Lark** — 群机器人 / DM 推送
- **Email** — 定期邮件摘要（daily/weekly）
- **Slack** — Webhook / Bot 集成
- **Discord** — Channel 推送
- **RSS/JSON Feed** — 已完成 ✅
- 用户维度：每人可选推送渠道 + 频率偏好

## 远期 🔭

| 功能 | 说明 |
|------|------|
| **Source Market** | 社区 Source 发现页，热门 Pack 推荐，分类浏览 |
| **订阅组合缓存** | 相同订阅组合共享 Digest，降低 LLM 成本 |
| **多语言 Digest** | 同一 Source Pool 生成不同语言版本 |
| **付费层级** | Source 数量限制、高级 Source 类型、更高生成频率 |

## AI 测试（探索中）

- 现有: curl E2E 脚本（66 assertions, 18 categories）
- 计划: Playwright + Midscene（字节开源）做 UI 级 AI 测试
- 方向: 自然语言写断言，和 Agent Friendly 路线一致
