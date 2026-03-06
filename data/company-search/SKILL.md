---
name: company-research
description: >
  Multi-source company research tool that generates structured due-diligence reports.
  Use when the user asks to research, look up, or investigate a company — including questions about
  shareholders, legal representative, registered capital, equity structure, beneficial owner,
  funding history, investors, valuation, lawsuits, court judgments, enforcement records,
  blacklist / dishonest debtor status, administrative penalties, operating anomalies,
  trademarks, patents, government procurement / bidding, recruitment profile, negative news,
  competitors, or industry position.
  Also triggers on: "帮我查一下XX公司", "XX公司背景", "XX的股东是谁", "XX有没有诉讼/被执行/失信",
  "XX融了多少钱", "XX股权结构", "尽调", "公司调研", "公司背景调查",
  "is X company reliable", "due diligence on X", "background check on X company".
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["python3"],"env":[]},"install":[{"id":"ddgs","kind":"pip","package":"ddgs","label":"Install DuckDuckGo Search (local fallback)"},{"id":"requests","kind":"pip","package":"requests","label":"Install Requests"},{"id":"beautifulsoup4","kind":"pip","package":"beautifulsoup4","label":"Install BeautifulSoup4"},{"id":"lxml","kind":"pip","package":"lxml","label":"Install lxml"},{"id":"trafilatura","kind":"pip","package":"trafilatura","label":"Install Trafilatura (optional, better text extraction)"}]}}
---

# Company Research — Multi-LLM Adaptive Skill

Multi-source company research tool that generates structured reports with the same information granularity as Tianyancha / Qichacha.
Supports Kimi / OpenAI GPT / Claude / Gemini / MiniMax / Cursor / generic Agent environments, with automatic tool detection and adaptation.

基于多源搜索的公司调研工具，生成"对标天眼查/企查查信息颗粒度"的结构化报告。
支持 Kimi / OpenAI GPT / Claude / Gemini / MiniMax / Cursor / 通用 Agent 环境，自动适配可用工具。

---

## 🧰 Tool Auto-Detection（执行前必须做）

**在开始任何调研前，先检测当前环境可用工具，映射到两个抽象操作：**

### SEARCH 操作 — 按优先级选第一个可用的：

| 优先级 | 工具名 | 适用环境 |
|--------|--------|----------|
| 1 | `kimi_search` | Kimi (Moonshot) |
| 2 | `web_search_preview` | OpenAI Responses API |
| 3 | `web_search` | Claude.ai / MiniMax / 通用 |
| 4 | `brave_web_search` | Claude+MCP / Cursor MCP |
| 5 | `google_search` | Gemini API (grounding) |
| 6 | `tavily_search` | LangChain / AutoGPT / 通用 Agent |
| 7 | `search` | 其他通用命名 |
| 8 | `bash` / `run_python` / shell 调用本地脚本 | 有 shell 工具的环境（见下方） |
| 9 | 无专用搜索工具 | 见 Fallback 策略 |

### FETCH 操作 — 按优先级选第一个可用的：

| 优先级 | 工具名 | 适用环境 |
|--------|--------|----------|
| 1 | `kimi_fetch` | Kimi (Moonshot) |
| 2 | `fetch` | Claude+MCP / Cursor MCP |
| 3 | `url_context` | Gemini 2.0+ |
| 4 | `browser_navigate` + `browser_snapshot` | Cursor browser MCP |
| 5 | `fetch_url` / `browse_url` | 通用 Agent 框架 |
| 6 | `bash` / `run_python` / shell 调用本地脚本 | 有 shell 工具的环境（见下方） |
| 7 | 无 FETCH 工具 | 见 Fallback 策略 |

### 本地脚本兜底（有 shell/bash 工具时）：

当以上专用工具均不可用，但当前环境有 `bash` / `shell` / `run_command` 类工具时，可调用同目录下的 `search_fetch.py`：

```bash
# Search (via DuckDuckGo, no API key required)
python search_fetch.py search "字节跳动 注册资本 法定代表人" --num 10

# Fetch — default strategy is 'direct' (traffic stays local, no third-party proxies)
python search_fetch.py fetch "https://example.com/announcement.html" --max-chars 12000

# If direct fails and you accept third-party routing (jina/archive), use auto:
python search_fetch.py fetch "https://example.com/page.html" --strategy auto
```

> **Data flow**: `direct` (default) — requests go from your machine straight to the target site.
> `auto` / `jina` / `archive` — the target URL and page content may pass through `r.jina.ai` or `archive.org`. Only use these for public URLs; never for internal or sensitive endpoints.
> 中文站点结果质量取决于网络环境（代理/直连）。

### Fallback 策略（工具完全不可用时）：
- **无 SEARCH**：尝试用 FETCH 直接抓已知权威站点，或基于已有知识推断（须标注"基于内部知识，未实时验证"）。
- **无 FETCH**：仅依赖 SEARCH 返回的摘要/snippet；关键字段标注"仅摘要，未全文核验"。
- **两者均无**：告知用户当前环境缺乏实时检索工具，报告仅基于模型训练截止日期的知识，建议用户手动核验。

> 在报告头部声明当前环境使用了哪些工具（例：`SEARCH=web_search, FETCH=fetch`）。

---

## 🎯 Output Standard

1. 以"天眼查/企查查常见模块"为纲，输出结构化报告
2. 每条关键结论尽量做到"至少两处来源交叉验证"
3. 对所有关键信息标注：
   - **来源 URL/标题**
   - **抓取日期**
   - **一致性（多源一致/单源）**
   - **可信度等级（A/B/C）**
4. 明确声明：公开搜索 ≠ 付费数据库全量数据；无法获取的字段标注"未检索到/疑似需付费/需内部渠道"。

---

## 🧭 Workflow

### Step 0 — 工具检测 + 实体识别与消歧（必须做）

**动作：**
- 确认 SEARCH / FETCH 工具（见上方 Tool Auto-Detection）
- 用 SEARCH 同时检索：
  - 公司全称 + 简称 + 品牌名
  - 可能的主体：XX有限公司、XX科技、XX网络
  - "统一社会信用代码/注册号/法定代表人/总部城市"关键词

**输出：**
- 候选主体列表（最多 5 个），选定"Primary Entity"
- 标注当前 SEARCH/FETCH 工具名

> 若无法唯一消歧：报告仍可输出，但需加显著提示。

---

### Step 1 — 搜索阶段（用 SEARCH 工具覆盖各维度）

每模块用 SEARCH 至少检索 3～5 次，优先组合"公司全称 + 关键词"：

#### 1) 工商与主体信息
- 公司全称/曾用名、统一社会信用代码、成立日期、注册资本
- 法定代表人、登记状态、注册地址、经营范围

#### 2) 股权结构与控制权
- 股东列表、持股比例、控股股东、实际控制人（可推断则给穿透链路）

#### 3) 对外投资/分支机构/子公司
- 对外投资公司清单、分公司/办事处、重要关联公司

#### 4) 工商变更与重大事项时间线
- 法人/股东/注册资本/地址/经营范围变更、曾用名

#### 5) 融资与资本运作
- 融资轮次、时间、金额、投资方（以公告/权威媒体/工商变更交叉验证）

#### 6) 司法风险
- 裁判文书、开庭公告、被执行人、失信被执行人
- 重点筛出：金额大/频次高/与主营强相关的案件

#### 7) 经营风险
- 行政处罚、经营异常、严重违法
- 安全/环保/数据合规相关处罚

#### 8) 知识产权与资质
- 商标（品牌/类别）、专利（数量/类型）、软件著作权
- 行业资质（运输许可/增值电信/支付牌照等）

#### 9) 招投标/政府采购
- 中标公告、政府采购合同、重要合作伙伴

#### 10) 招聘与组织画像
- 招聘岗位类型、技术栈、城市分布、薪酬区间

#### 11) 舆情与新闻
- 近 3/6/12 个月关键新闻、负面舆情（投诉/监管点名/重大事故）

#### 12) 竞争格局与行业位置
- 竞品清单（直接竞品/替代品/上下游）、差异化要点

---

### Step 2 — 深度获取（FETCH 抓关键页，若工具可用）

对以下"高价值证据页"执行 FETCH：
- 官网/官方公告/监管通告
- 上市公司年报/公告（如相关）
- 判决书/执行信息详情页（能打开则抓）
- 工商变更明细页面（若公开可访问）
- 招投标中标公告正文

> 若 FETCH 工具不可用，标注"摘要来源，未全文核验"后继续输出。

---

### Step 3 — 整理输出（结构化报告 + 证据链）

> ⚠️ **MANDATORY**: Final output MUST strictly follow the format template defined in `## 输出格式` below. Do NOT output investigation steps, tool call logs, intermediate analysis, or any content outside the template. Only output the final structured report.

---

## 输出格式（严格按照以下模板输出，不得增删章节、不得改变顺序）

```markdown
## 🔍 {公司名称} 公司调研报告

- 报告生成时间：{YYYY-MM-DD}
- 主体口径：{Primary Entity 公司全称 + 地区 + 统一社会信用代码(若公开)}
- 数据来源：公开网页多源检索（非付费数据库直连），关键结论已尽量交叉验证
- 当前环境工具：SEARCH={工具名}, FETCH={工具名或"不可用"}

---

### 0️⃣ 调查主体
- 候选主体：
  - A: xxx（依据：...）
  - B: xxx（依据：...）
- 本报告选定主主体（Primary）：xxx
- 仍存疑点：xxx（如有）

---

### 1️⃣ 基本信息

| 项目 | 内容 | 可信度 | 证据 |
|------|------|--------|------|
| 公司全称 | xxx | A | [来源1] |
| 曾用名 | xxx | B | [来源2] |
| 成立时间 | xxx | A | [来源] |
| 注册资本 | xxx | B | [来源] |
| 实缴资本 | xxx/未披露 | C | [来源] |
| 法定代表人 | xxx | A | [来源] |
| 登记状态 | 存续/注销... | A | [来源] |
| 统一社会信用代码 | xxx/未披露 | B/C | [来源] |
| 注册地址 | xxx | B | [来源] |
| 总部/办公地（推断） | xxx | C | [来源] |
| 行业/业务标签 | xxx | B | [来源] |
| 经营范围要点 | xxx | B | [来源] |

---

### 2️⃣ 股权结构与控制权
#### 2.1 股东结构（可见范围内）
| 股东 | 持股比例 | 变更记录 | 可信度 | 证据 |
|------|----------|----------|--------|------|
| xxx | xx% | xxxx | B | [来源] |

#### 2.2 控股/实控与穿透（仅基于可复核公开链路）
- 控股股东：xxx（依据：...）
- 实际控制人：xxx（依据：...）
- 穿透路径（如适用）：A → B → C

> 注：若未检索到可靠穿透链路，标注"公开信息不足，无法确认最终受益人"。

---

### 3️⃣ 对外投资 / 子公司 / 分支机构
- 关键子公司（Top N）：
  - xxx（角色/业务：...，地区：...）
- 对外投资摘要：
  - 投资标的、比例、时间（若公开）
- 关联主体提示：
  - 同法人/同地址/同品牌等线索（需谨慎）

---

### 4️⃣ 工商变更与里程碑时间线
| 时间 | 事项 | 影响解读 | 可信度 | 证据 |
|------|------|----------|--------|------|
| YYYY-MM | 法人变更 | ... | B | [来源] |

---

### 5️⃣ 融资与资本运作
| 时间 | 轮次/事件 | 金额 | 投资方/交易对手 | 可信度 | 证据 |
|------|-----------|------|----------------|--------|------|
| YYYY-MM | A轮 | xx | xxx | B | [来源] |

- 融资可信度规则：
  - A：官方公告/监管披露/上市公司公告
  - B：权威财经媒体多源一致
  - C：单一媒体或自媒体（仅作线索）

---

### 6️⃣ 司法风险（诉讼/执行/失信）
#### 6.1 风险概览
- 裁判文书：x 起（可见范围）
- 被执行：x 条（可见范围）
- 失信：x 条（可见范围）
- 开庭公告：x 条（可见范围）

#### 6.2 重点案件（金额大/频次高/与主营强相关）
| 案号/时间 | 案由 | 角色 | 结果/进展 | 金额 | 风险解读 | 证据 |
|----------|------|------|-----------|------|----------|------|
| xxx | xxx | 被告 | xxx | xx | xxx | [来源] |

---

### 7️⃣ 经营风险（行政处罚/异常/合规）
| 类型 | 事件 | 时间 | 主管机关/平台 | 风险等级 | 证据 |
|------|------|------|---------------|----------|------|
| 行政处罚 | xxx | YYYY-MM | xxx | 中/高 | [来源] |

- 经营异常/严重违法：{有/无/未检索到}

---

### 8️⃣ 知识产权与资质
- 商标：核心品牌/类别/状态（若公开）
- 专利：数量/类型/重点专利（若公开）
- 软件著作权：代表性条目（若公开）
- 行业资质：与业务强相关证照（若公开）

---

### 9️⃣ 招投标 / 政府采购 / 重大合作
| 时间 | 项目 | 甲方/采购方 | 金额 | 可信度 | 证据 |
|------|------|-------------|------|--------|------|
| YYYY | xxx | xxx | xx | B | [来源] |

---

### 🔟 招聘与组织画像（辅助判断业务重心）
- 招聘城市分布：...
- 岗位结构：研发/产品/运营/销售/合规/风控占比线索
- 技术栈线索：...

---

### 1️⃣1️⃣ 最新动态（近 3/6/12 个月）
| 日期 | 事件 | 影响判断 | 可信度 | 证据 |
|------|------|----------|--------|------|
| YYYY-MM-DD | xxx | xxx | B | [来源] |

---

### 1️⃣2️⃣ 行业地位 / 竞争格局
- 行业定位：...
- 直接竞品：A/B/C
- 替代品/上下游：...
- 差异化与壁垒：...

---

## ⚠️ 风险提示（Important）
- 本报告基于公开检索信息，不等同于天眼查/企查查付费数据库全量字段。
- 股权穿透、实缴、历史变更、司法全量等可能存在"公开不可见/需付费/需线下渠道"的缺口。
- 对单源信息（尤其自媒体/论坛）只作线索，不作事实结论。
- 若主体存在同名/多品牌/多主体运营，需进一步确认统一社会信用代码口径。
- 当前报告所用工具：SEARCH={工具名}, FETCH={工具名或"不可用"}；若工具受限，关键字段可信度可能降级。

---

## ✅ 总结（Executive Summary）
- 一句话概括：...
- 核心结论 3-5 条：
  1) ...
  2) ...
  3) ...
- 主要风险 3-5 条：
  1) ...
  2) ...
  3) ...
```

---

## 🔎 Search Playbook（推荐检索 Query 模板）

> 每个模块用"公司名/主主体全称 + 关键词"组合检索，优先选择权威源。

- 工商基础：{公司} 统一社会信用代码 注册资本 法定代表人 成立时间
- 股东股权：{公司} 股东 持股 比例 工商变更 出资
- 子公司投资：{公司} 对外投资 子公司 分公司 关联公司
- 变更记录：{公司} 变更 法人变更 注册资本变更 地址变更 曾用名
- 融资：{公司} 融资 A轮 投资方 金额 估值
- 司法：{公司} 裁判文书 案号 被执行人 限制高消费 失信
- 行政处罚/异常：{公司} 行政处罚 经营异常 严重违法 监管通报
- IP：{公司} 商标 专利 软件著作权
- 招投标：{公司} 中标 公告 政府采购 合同
- 招聘：{公司} 招聘 岗位 薪资 技术栈
- 舆情：{公司} 投诉 负面 事故 维权 监管

---

## 🧪 Evidence & Confidence Rules（必遵守）

- 可信度 A：政府/法院/监管/交易所公告、上市公司年报公告、公司官网正式公告
- 可信度 B：权威媒体/行业协会报告，且多源一致
- 可信度 C：单一媒体、自媒体、论坛，仅做线索

交叉验证优先级：A(官方) > B(权威媒体多源) > C(线索)

---

## 🧩 Notes
- **输出格式强制要求**：最终输出必须且只能包含 `## 输出格式` 模板中定义的内容，章节顺序、标题、表格结构不得改变。禁止在报告前后附加"以下是报告"、"调查步骤"、"工具调用日志"等额外内容。
- **Markdown 兼容性**：输出须兼容主流消息平台（Slack/Telegram/钉钉/飞书/Discord 等）。禁止使用：HTML 标签、`<details>`/`<summary>` 折叠块、`[^注脚]` 脚注语法、4 空格缩进代码块（用三反引号代替）、嵌套超过 2 层的列表。表格必须使用标准 `|---|` 格式，每列至少一个分隔符。链接统一用 `[标题](URL)` 格式，不使用裸 URL 或 `<URL>` 尖括号格式。
- **工具降级处理**：若高优先级工具调用失败（报错/不存在），自动尝试下一优先级，而非终止任务。
