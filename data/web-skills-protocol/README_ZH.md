# Web Skills Protocol

Github: https://github.com/0xtresser/Web-Skills-Protocol

> **skills.txt** — 教 AI 智能体如何使用你的网站。

[English](README.md) | 中文

---

1994 年，`robots.txt` 告诉爬虫**不要**做什么。

2024 年，`llms.txt` 告诉大语言模型该**读**什么内容。

2026 年，`skills.txt`（或 `agents.txt`）教 AI 智能体如何去**操作**。

**Web Skills Protocol (WSP)** 是一个开放标准，让网站发布技能文件（skill files），教 AI 智能体如何与网站交互——包括 API 调用、操作流程和功能说明——而不是让 AI 去抓取 HTML 猜测。

**WSP 没有发明新格式。** AI 智能体技能（agent skill）——即包含 YAML 元数据和 Markdown 指令的文件，用于教 AI 如何执行任务——已经是 AI 智能体生态中的既有标准（被 Claude、OpenClaw 等广泛使用）。WSP 只是把这个已有的技能格式搬到了 Web 上，加了一层发现机制：一个 `skills.txt` 文件告诉智能体网站提供哪些技能，就像 `robots.txt` 告诉爬虫哪些页面不要访问一样。

## 问题

AI 智能体正在访问你的网站。它们解析 HTML、猜测按钮、通过抓包逆向你的 API。这种方式脆弱、低效、而且经常挂掉。

网站没有一种标准方式来告诉 AI：*「嘿，这才是正确使用我的方法。」*

## 解决方案

在网站根目录放一个 `skills.txt`（或 `agents.txt`）文件，列出你的能力，把技能定义发布在 `/skills/`（或 `/agents/`）目录下。搞定。

```
your-website.com/
├── skills.txt              ← 发现文件（或 agents.txt）
└── skills/                 ← 技能目录（或 /agents/）
    ├── search/
    │   └── SKILL.md        ← 「这是搜索商品的方法」
    └── order/
        └── SKILL.md        ← 「这是下单的方法」
```

WSP 同时支持**替代命名**：`agents.txt` 和 `/agents/`——同样的协议，同样的格式，不同的名字。用哪个都行，AI 智能体两个都会检查。

AI 智能体先检查 `skills.txt`（或 `agents.txt`），找到合适的技能，然后按你的说明操作——而不是自己瞎猜。

## 为什么不是新格式？

AI 智能体技能已经存在。数以千计的技能每天被 AI 智能体（如 Claude）发布和使用——每个技能就是一个简单的 `SKILL.md` 文件，包含 YAML frontmatter（name、description、version）和 Markdown 指令。这个格式已经被验证、被采纳、能工作。

WSP 原样继承了这个标准。唯一的新增是一个 **Web 发现机制**：

```
已有标准：  SKILL.md（YAML frontmatter + Markdown 指令）
WSP 新增：  skills.txt → 告诉智能体去哪找对应的 SKILL.md
```

换个比方：WSP 之于 agent skill，就像 RSS 之于 XML——不是新格式，而是在已有格式上加了一个约定的位置和发现方式。

## 演进历程

```
robots.txt (1994)  →  「亲爱的机器人，不要爬 /admin」          →  访问控制
llms.txt   (2024)  →  「亲爱的 LLM，这是我们的文档」          →  内容
skills.txt (2026)  →  「亲爱的智能体，这是调用 API 的方法」   →  能力
```

## 安装

一行命令为你的 AI 智能体添加 WSP 自动发现能力：

**OpenClaw**

```bash
mkdir -p ~/.openclaw/workspace/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.openclaw/workspace/skills/web-skills-protocol/SKILL.md
```

**OpenCode**

```bash
mkdir -p ~/.claude/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.claude/skills/web-skills-protocol/SKILL.md
```

**Claude Code**

```bash
mkdir -p ~/.claude/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.claude/skills/web-skills-protocol/SKILL.md
```

**Codex (OpenAI)**

Codex 从 `AGENTS.md` 读取指令。将技能追加到你的项目：

```bash
curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  >> AGENTS.md
```


## 快速开始

### 1. 创建 `/skills.txt`（或 `/agents.txt`）

```markdown
# Bob's Online Store

> 电子产品和数码配件的电商平台。

商品搜索无需认证。其他端点需要 API Key——在 https://bobs-store.com/developers 获取。

## Skills

- [Product Search](/skills/search/SKILL.md): 按关键词、分类或价格区间搜索商品
- [Place Order](/skills/order/SKILL.md): 添加购物车并通过 API 完成下单
```

### 2. 创建技能文件

`/skills/search/SKILL.md`（或 `/agents/search/SKILL.md`）:

```markdown
---
name: search
description: >
  Search and browse products in Bob's Online Store catalog.
  Use when the user wants to find products by keyword, category, price, or brand.
version: 1.0.0
auth: none
base_url: https://api.bobs-store.com/v1
---

# Product Search

## Endpoint

GET /products

## Parameters

| Parameter  | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| q          | string | yes      | Search query                    |
| category   | string | no       | Filter by category              |
| min_price  | number | no       | Minimum price                   |
| max_price  | number | no       | Maximum price                   |
| sort       | string | no       | Sort by: relevance, price, rating |
| page       | number | no       | Page number (default: 1)        |

## Example

Request:
​```
GET /products?q=wireless+headphones&sort=rating&max_price=100
​```

Response:
​```json
{
  "products": [
    {
      "id": "prod_8x7k",
      "name": "SoundWave Pro Wireless Headphones",
      "price": 79.99,
      "rating": 4.7,
      "in_stock": true
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
​```
```

就这样。AI 智能体访问你的网站时会：

1. 获取 `/skills.txt`（或 `/agents.txt`）→ 发现可用技能
2. 匹配用户意图 → 选择合适的技能
3. 按照 SKILL.md 的说明 → 正确调用你的 API

## skills.txt 格式

发现文件有**固定的层级结构**——不是自由格式的 Markdown：

```
# {站点名称}                           ← H1：必须。恰好一个。

> {站点描述}                          ← 引用块：建议。

{通用信息：认证、频率限制...}       ← 正文：可选。

## Skills                              ← H2：必须。至少一个分组。

- [Skill Name](url): Description      ← 列表项：固定格式。
- [Another Skill](url): Description

## Optional                            ← H2 "Optional"：智能体可跳过。

- [Extra Skill](url): Description
```

**规则：**

| 元素 | 格式 | 是否必须 |
|------|------|---------|
| 站点名称 | `# 名称`（H1） | 是——恰好一个 |
| 描述 | `> 文本`（引用块） | 建议 |
| 正文 | 段落 | 否 |
| 技能分组 | `## 分组名`（H2） | 是——至少一个 |
| 技能条目 | `- [名称](path/SKILL.md): 描述` | 是——每个分组至少一个 |

H2 分组 `## Optional` 有特殊含义：智能体在上下文有限时可以跳过这些技能。其他 H2 分组均视为主要技能。

## SKILL.md 格式

每个技能文件是标准的 **AgentSkills** 文档——与 AI 智能体平台（Claude、OpenClaw 等）已在使用的 `SKILL.md` 格式完全一致。WSP 不修改这个格式。

- **YAML frontmatter**（`---`）：`name`、`description`、`version`（必填）+ 可选字段如 `auth`、`base_url`、`rate_limit`
  - `rate_limit` 是一个对象，包含两个可选子字段：`agent`（发布者建议的 AI 智能体频率限制，如 `20/minute`）和 `api`（实际 API 频率限制，如 `100/minute`）
- **Markdown 正文**：给智能体的指令——端点、参数、示例、工作流

如果你写过 agent skill，就已经知道怎么写 web skill 了。完整示例见 [examples/](examples/)。

## 双路径兼容

WSP 支持两种命名约定——选你喜欢的：

| 组件 | 主要约定 | 替代约定 |
|------|---------|---------|
| 发现文件 | `/skills.txt` | `/agents.txt` |
| 技能目录 | `/skills/` | `/agents/` |
| 技能文档 | `/skills/{name}/SKILL.md` | `/agents/{name}/SKILL.md` |

两种约定使用**完全相同的格式**。`skills.txt` 的视角是「网站能教什么」；`agents.txt` 沿用 `robots.txt` 的命名风格——「与智能体对话」。

**网站方：** 选一种约定，保持一致。
**AI 开发者：** 你的智能体必须两个都检查（先 `skills.txt`，再 `agents.txt`）。

## 适用场景

### 对网站主

**为什么要发布 skills？**

- **掌握主动权。** 定义 AI 智能体如何使用你的网站——别让它们瞎猜。
- **替代爬虫。** 结构化的 skill 比 HTML 解析更快、更可靠。
- **减少负载。** 一次 API 调用胜过 50 次页面抓取。
- **智能体流量变现。** 要求 API Key、追踪用量、提供付费层级。
- **渐进式接入。** 从一个 `skills.txt`（或 `agents.txt`）开始，逐步添加技能。

### 对 AI 开发者

**为什么要检查 skills？**

- **结构化指令**，不用解析不可预测的 HTML。
- **自动发现**——获取一次 `/skills.txt`（或 `/agents.txt`）就能知道所有能力。
- **可靠集成**——按照网站官方说明操作，而不是脆弱的 hack。
- **更好的结果**——API 返回结构化数据，而不是渲染后的网页。

安装 [web-skills-protocol 智能体技能](skill/SKILL.md)，让你的 AI 智能体自动发现和使用已发布的技能。

## 与其他标准的关系

| 标准          | 用途                   | 关系                                   |
|--------------|----------------------|----------------------------------------|
| robots.txt   | 爬虫访问控制            | WSP 不覆盖 robots.txt，两者共存。          |
| llms.txt     | 为 LLM 提供内容摘要     | 互补。llms.txt = 阅读，skills.txt/agents.txt = 操作。  |
| OpenAPI      | 面向开发者的 API 规范    | 技能可以引用 OpenAPI 规范来补充细节。        |
| MCP          | AI 工具的运行时协议      | WSP 是 Web 原生的发现标准；MCP 是运行时传输。 |
| sitemap.xml  | 搜索引擎的页面索引       | skills.txt/agents.txt 是面向 AI 智能体的能力索引。      |

## 项目结构

```
Web-Skills-Protocol/
├── README.md           ← English
├── README_ZH.md        ← 你在这里
├── SPEC.md             ← 正式协议规范
├── skill/              ← 智能体技能（安装后自动发现 web skills）
│   └── SKILL.md
└── examples/           ← 示例实现
    ├── bobs-store/     ← 电商示例
    └── devtools-saas/  ← SaaS 平台示例
```

## 规范

完整协议规范请参阅 [SPEC.md](SPEC.md)。

## 实际案例

[**awesomeai.info**](https://www.awesomeai.info/) — 追踪 2800+ 个 AI 相关 GitHub 仓库和 OpenClaw 智能体技能的数据看板。该网站已在生产环境采用 WSP。

亲自试试：

```bash
# 1. 发现网站能做什么
curl https://www.awesomeai.info/skills.txt

# 2. 查看具体技能
curl https://www.awesomeai.info/skills/explore-ai-repos/SKILL.md

# 3. 按照技能描述调用 API
curl "https://awesomeai.info/api/repos?q=llm&sort=stars&pageSize=5"
```

该网站发布了两个技能——均为公开接口，无需认证：

| 技能 | 接口 | 功能 |
|------|------|------|
| [explore-ai-repos](https://www.awesomeai.info/skills/explore-ai-repos/SKILL.md) | `GET /api/repos` | 按关键词、star 数、AI 评分、增长趋势搜索/筛选 AI 仓库 |
| [explore-ai-skills](https://www.awesomeai.info/skills/explore-ai-skills/SKILL.md) | `GET /api/skills` | 按分类、关键词、热度搜索/浏览 OpenClaw 智能体技能 |

这就是 WSP 在真实世界中的样子——一个 `skills.txt` 文件加几个 `SKILL.md`，任何 AI 智能体就能立即理解和使用这个网站。

## 示例

虚拟示例（电商和 SaaS 平台）请查看 [examples/](examples/) 目录。

## 参与贡献

这是一个早期阶段的开放标准，欢迎贡献：

- **规范反馈** — 提 issue 讨论协议设计
- **参考实现** — 为不同类型的网站添加示例
- **智能体集成** — 在你的 AI 智能体中加入 skills.txt（或 agents.txt）支持
- **采用它** — 在你的网站上发布 skills.txt（或 agents.txt）

## 许可证

Web Skills Protocol 规范采用 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) 许可。

示例代码和智能体技能采用 [MIT](https://opensource.org/licenses/MIT) 许可。
