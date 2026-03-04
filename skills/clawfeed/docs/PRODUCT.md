# ClawFeed — 产品设计文档

> AI 信息 digest 开源工具。可作为 ClawHub Skill 安装，也可独立部署。

## 定位
开源 AI 信息摘要工具，帮助用户从 Twitter/RSS 等信息源自动生成结构化简报。

## 分发方式
- **ClawHub Skill** — `openclaw skill install clawfeed`
- **独立部署** — clone repo 自己跑

---

## 功能划分

### 按类型

| 类型 | 功能 | 说明 |
|------|------|------|
| 📰 信息功能 | Summary（摘要） | 4H/日/周/月 简报生成 |
| 📰 信息功能 | Feed 精选 | 从信息源筛选高质量内容 |
| 📰 信息功能 | Deep Dive | 对标记内容的深度解读 |
| 📰 信息功能 | 噪音过滤 | 识别并过滤低质量内容 |
| 🔧 管理功能 | 推荐关注 | 基于 feed 分析推荐新账号 |
| 🔧 管理功能 | 建议取关 | 抽查 following 找低质量账号 |
| 🔧 管理功能 | 信息源管理 | 添加/删除/配置 feed 源 |
| 🔧 管理功能 | Curation Rules | 自定义筛选规则 |

### 按作用域

| 作用域 | 功能 | 说明 |
|--------|------|------|
| 🌐 共享 | 简报内容 | 所有用户看到相同的 digest |
| 🌐 共享 | Feed 精选 | 公共信息流 |
| 🌐 共享 | 推荐关注/取关 | 公共建议 |
| 👤 个人 | Mark（收藏） | 用户自己标记感兴趣的内容 |
| 👤 个人 | 接收渠道 | Telegram/Discord/Email/webhook |
| 👤 个人 | 信息源（开源版） | 自定义 Twitter/RSS 源 |
| 👤 个人 | Curation Rules（开源版） | 自定义筛选规则 |

---

## 两种模式

### 开源版（Self-hosted）
- 用户完全自主
- 自定义信息源（Twitter/RSS/Reddit/HN）
- 自定义接收渠道（Telegram/Discord/Email）
- 自定义 curation rules
- 本地数据，无需登录
- 安装：`openclaw skill install clawfeed` 或 git clone

### 公开服务版（Hosted）
- 域名：`digest.lenspal.ai`（或类似）
- 默认显示 Kevin 的信息源（AI/Crypto/Dev 方向）
- 用户功能：

| 状态 | 可用功能 |
|------|----------|
| 🔓 未登录 | 浏览所有 digest、查看精选 |
| 🔑 已登录 | + Mark 收藏、个人收藏列表、接收推送 |
| 🔑 已登录（后期） | + 自定义信息源、个人 digest |

---

## 技术架构

```
┌─────────────────────────────────────────┐
│              Frontend (SPA)             │
│   Dashboard / Digest / Marks / Settings │
└──────────────┬──────────────────────────┘
               │ REST API
┌──────────────▼──────────────────────────┐
│            Backend (Node.js)            │
│   /api/digests  — CRUD digests          │
│   /api/marks    — 个人收藏 CRUD         │
│   /api/sources  — 信息源管理            │
│   /api/auth     — 登录/注册             │
│   /api/config   — 用户配置              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Storage (SQLite)               │
│   users / digests / marks / sources     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Digest Engine (OpenClaw Skill)    │
│   Cron → Fetch feeds → AI summarize     │
│   → Generate markdown → Store           │
└─────────────────────────────────────────┘
```

### Skill 结构（ClawHub）

```
clawfeed/
├── SKILL.md              # Skill 入口文档
├── package.json
├── src/
│   ├── server.js         # API server
│   ├── engine.js         # Digest 生成引擎
│   ├── sources/          # 信息源适配器
│   │   ├── twitter.js
│   │   ├── rss.js
│   │   └── reddit.js
│   └── db.js             # SQLite 操作
├── web/
│   └── index.html        # Dashboard SPA
├── templates/
│   ├── curation-rules.md # 默认 curation 规则模板
│   └── digest-prompt.md  # 摘要生成 prompt 模板
├── migrations/
│   └── 001_init.sql
└── config.example.json   # 配置模板
```

---

## 实施路线

### Phase 1: 重构现有代码 → 开源 repo
- [ ] 创建 `clawfeed` repo
- [ ] 抽取 dashboard 前端（现有 index.html → SPA）
- [ ] 抽取 digest 生成逻辑（从 cron job prompt 中提取）
- [ ] 抽取 curation rules 为模板
- [ ] 加 API server（marks CRUD → 替代现有 marks.json 直接操作）
- [ ] SQLite 存储（替代 JSON 文件）
- [ ] README + 部署文档
- [ ] 发布 GitHub

### Phase 2: ClawHub Skill 封装
- [ ] 写 SKILL.md
- [ ] Skill 安装自动启动 API server
- [ ] Skill 配置：信息源、接收渠道、cron 周期
- [ ] 发布 ClawHub

### Phase 3: 公开服务
- [ ] 用户认证（GitHub/Google OAuth）
- [ ] 登录/未登录差异化
- [ ] Mark 功能绑定用户
- [ ] 部署到 `digest.lenspal.ai`
- [ ] Landing page

### Phase 4: 多租户增强
- [ ] 用户自定义信息源
- [ ] 用户级 cron
- [ ] 用户级 curation rules
- [ ] 付费层？（更多信息源 / 更高频率 / 更多 deep dive）
