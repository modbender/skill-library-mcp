---
name: buffett-analysis
description: 巴菲特视角的上市公司基本面深度分析。当用户提到"分析一家公司"、"看看XX值不值得投资"、"XX的基本面怎么样"、"帮我研究一下XX"、个股分析、价值投资分析、公司估值、高管研究、管理层分析、公司战略、新闻采集、PR分析、业务出海、创新药等需求时使用。也支持行业分析——当用户提到"XX行业怎么样"、"帮我梳理一下XX赛道"、"XX产业链分析"、"行业一页纸"时使用。支持A股、港股、美股（NYSE/NASDAQ）。美股直接用 ticker（AAPL/TSLA/NVDA），A股用代码或中文名。自动获取财报、估值、行业数据、公司新闻、高管信息，按巴菲特投资框架出具完整分析报告。
---

# 巴菲特视角投资分析

## 分析模式

根据用户需求自动判别分析模式：

### 模式A：个股基本面分析
- 触发词：分析XX公司、XX值不值得投资、XX基本面、研究XX
- 流程：个股分析流程（Step 1-4）

### 模式B：行业一页纸
- 触发词：XX行业分析、XX赛道怎么样、XX产业链、行业一页纸
- 流程：行业分析流程（Step B1-B4）

### 模式C：专项研究
- 触发词：高管研究、新闻采集、战略分析、估值测算等
- 流程：可跳过财务数据采集，直接执行相关步骤

---

## 分析方法论（通用）

所有分析都遵循这个方法论链条：

### 1. 问题定义
- 明确分析对象、范围、时间窗口
- 拆分为可验证的子命题
- 识别核心假设（需求驱动、供给约束、关键里程碑）

### 2. 证据搜集与溯源
- **优先来源**：公司年报/季报/招股书、政策原文、行业协会/统计局、权威机构报告
- **溯源**：找最早出处，标记是否存在信息偏差
- **质量评估**：可验证性、独立性、时效性、利益冲突

### 3. 数据处理与分析
- 多源交叉验证，取可信、可溯源的信源
- 区分原始数据、计算数据、推理数据
- 定量计算 + 定性分析结合

### 4. 论证检验
- 重构逻辑链：前提 → 推理 → 结论（每步标注证据）
- 常见谬误自检：相关≠因果、以偏概全、诉诸权威
- 敏感性分析：核心假设变化对结论的影响

---

## 个股分析框架（六大维度）

### 1. 🏭 行业定位与产业链
- 行业规模、增速、周期阶段
- 公司在产业链中的位置和话语权
- 市场空间（TAM/SAM/SOM）
- 竞争格局（CR3/CR5、市占率变化）
- 核心技术路线及公司技术代际

### 2. 🏰 护城河分析 (Economic Moat)
- **毛利率**：>40% 优秀，>60% 极强定价权
- **ROE**：连续>15% 是优质企业门槛，>20% 是护城河标志
- **ROIC**：>15% 说明资本配置效率高
- **技术壁垒**：专利、know-how、研发投入强度
- **资本壁垒**：进入门槛、固定资产投入
- **客户壁垒**：转换成本、认证周期
- **应收账款周转**：越快说明议价能力越强

### 3. 📊 盈利质量 (Earnings Quality)
- **经营现金流/净利润**：>80% 说明利润是"真金白银"
- **自由现金流**：正且持续增长是好生意的标志
- **营收/利润增速**：关注稳定性而非单年爆发
- **扣非净利润 vs 净利润**：差距大说明非经常性损益多
- **资本开支强度**：Capex/营收，重投入期 vs 收获期

### 4. 💰 财务健康 (Financial Health)
- **资产负债率**：因行业而异，但过高(>60%)需警惕
- **流动比率/速动比率**：>2/>1 为安全
- **有息负债**：越少越好，巴菲特偏爱低负债公司
- **货币资金/短期借款**：>1 说明现金充裕

### 5. 📐 估值合理性 (Valuation)
- **PE-TTM**：与历史分位、同行对比
- **PB**：结合ROE看（高ROE高PB合理）
- **EV/EBITDA**：剔除资本结构差异的估值指标
- **自由现金流收益率**：FCF/市值，>5% 有吸引力
- **股息率 + 回购收益率**（美股重点）：Total Shareholder Yield
- **DCF 简化测算**：核心假设→目标价区间

### 6. 👔 管理层与治理 (Management & Governance)
- **高管背景**：CEO/董事长/核心高管的专业背景、行业经验
- **任职变动**：近期高管变动情况及可能原因
- **管理层持股**：利益绑定程度
- **战略方向**：管理层公开言论、战略规划、业务布局

### 7. 📰 公开信息与事件驱动 (News & Catalysts)
- **公司公告/PR**：重大公告、合作协议、审批进展
- **行业新闻**：行业政策、竞争格局变化
- **媒体报道**：正面/负面报道、市场情绪
- **事件催化**：近期可能影响股价的关键事件

---

## 个股分析执行流程

### Step 1a: 财务数据采集

**市场自动判别：**
- 输入为英文 ticker（如 AAPL、TSLA、NVDA、GOOGL）或明确美股公司 → 美股路径
- 输入为中文名（贵州茅台）或 A 股代码（600519、000858）→ A 股路径

#### A股/港股路径

运行脚本（使用公司名或代码）：

```bash
PATH="/home/node/.local/bin:$PATH" python3 scripts/fetch_company_data.py "贵州茅台"
```

脚本输出 JSON 到 `/tmp/buffett_analysis_{code}.json`，包含：
- 公司基本信息、行业分类
- 最新利润表、资产负债表、现金流量表
- 核心财务指标（ROE/ROIC/毛利率等，含多期对比）
- 估值指标（PE/PB/PS/PCF）
- 实时行情、市值
- 十大股东
- 同行业公司列表（用于对比）

如需同行对比数据，对2-3家可比公司额外运行：
```bash
PATH="/home/node/.local/bin:$PATH" python3 scripts/fetch_company_data.py "五粮液"
```

#### 美股路径

运行美股采集脚本：

```bash
python3 scripts/fetch_us_company_data.py AAPL
```

脚本依次调用 us-market skill 采集 profile/financials/quote/analyst/dividends，输出到 `/tmp/buffett_analysis_{TICKER}.json`。

如需同行对比：
```bash
python3 scripts/fetch_us_company_data.py MSFT
```

### Step 1b: 行业与产业链数据采集

**这是新增的关键步骤——先看行业再看公司。**

1. **web_search** 搜索行业信息：
   - `"{行业名}" 市场规模 增速 2025 2026`
   - `"{行业名}" 产业链 竞争格局`
   - `"{行业名}" 技术路线 趋势`
   - `"{公司名}" 市占率 行业排名`

2. **web_fetch** 抓取关键行业报告/数据

3. **fintool MCP**（A股）获取行业数据：
   ```
   fintool-plates.get_plate_list keyword="{行业名}"
   fintool-plates.get_plate_stocks plate_code="{板块代码}"
   ```

**整理要点：**
- 行业规模及增速
- 公司在行业中的位置（市占率、排名）
- 产业链上下游关系
- 竞争格局（CR3/CR5，主要竞争对手）
- 核心技术路线及演进方向

### Step 1c: 新闻/公开信息采集

#### A股路径

1. **web_search** 搜索公司最新新闻、PR稿件、公告：
   - 搜索 3-5 组不同关键词，覆盖不同角度
   - 用 `freshness: "pm"` 限定近期新闻

2. **web_fetch** 对重要搜索结果抓取全文

3. **fintool-search**（MCP）获取财经新闻：
   ```
   fintool-search.search_news keyword="{公司名}" count=20
   ```

#### 美股路径

1. 用 us-market skill 获取新闻：
   ```bash
   python3 skills/us-market/scripts/us_market_query.py --type news --symbol AAPL
   ```

2. **web_search** 补充搜索（英文关键词）

3. **web_fetch** 抓取关键报道全文

**信息整理要求：**
- 按时间线整理关键事件
- 区分事实（公告/官方信息）和观点（分析师/媒体评论）
- 标注信息来源和日期
- 识别信息之间的关联性

### Step 1d: 高管与管理层研究

#### A股路径

1. **web_search** 搜索高管信息：
   - `"{公司名}" 高管 任命/变动/离职`
   - `"{高管姓名}" 背景/简历`

2. **web_fetch** 抓取关键人物报道

#### 美股路径

1. 用 us-market skill 获取内部交易数据：
   ```bash
   python3 skills/us-market/scripts/us_market_query.py --type insider --symbol AAPL
   ```

2. **web_search** 搜索高管信息（英文）

3. **web_fetch** 抓取关键报道

#### 分析要点（通用）
- 核心高管名单
- 教育背景、职业履历、专业领域
- 近期任职变动及原因
- 管理层持股变化（增持/减持信号）

### Step 2: 读取分析模板

```
read references/analysis-template.md
```

### Step 3: 撰写分析报告

结合采集数据 + 分析模板 + 以下原则撰写报告：

**巴菲特语言风格：**
- 用生活化比喻解释财务概念
- 适当引用巴菲特/芒格名言
- 给出明确观点，不做墙头草
- 永远提示风险

**分析深度要求：**
- 不只列数字，要解读数字背后的商业逻辑
- **先看行业，再看公司**：行业景气度是个股表现的最大β
- 结合产业链分析护城河的可持续性
- 横向对比（vs 同行）+ 纵向对比（vs 自身历史）
- 供需框架分析：量×价，渗透率提升空间
- 最终给出清晰的投资价值判断

**输出格式：**
- 飞书/群聊用 bullet points，不用 markdown 表格
- 先给结论（一句话总结），再展开分析
- 控制在合理篇幅（不要写论文）

### Step 4: 写入阿尔法工坊前端

每次完成基本面分析后，**必须**将报告数据写入前端展示：

1. 读取 `alpha-factor-lab/fundamental-reports.json`
2. 按以下 JSON 结构追加一条报告：

```json
{
  "name": "公司名称",
  "code": "600519.SH 或 AAPL（美股直接用ticker）",
  "market": "A 或 US",
  "date": "2026-02-21",
  "rating": "推荐|强烈推荐|中性|回避|关注",
  "industry": {
    "name": "行业名称",
    "summary": "行业概况一句话",
    "position": "公司在产业链中的位置",
    "market_size": "行业市场规模",
    "growth": "行业增速",
    "competition": "竞争格局概述（CR3/市占率等）"
  },
  "moat": {
    "score": 8,
    "summary": "护城河分析文字...",
    "metrics": { "毛利率": "91.3%", "ROE": "36.99%", ... }
  },
  "earnings": {
    "score": 7,
    "summary": "盈利质量分析文字...",
    "metrics": { ... }
  },
  "health": {
    "score": 9,
    "summary": "财务健康分析文字...",
    "metrics": { ... }
  },
  "valuation": {
    "score": 6,
    "summary": "估值分析文字...",
    "metrics": { "PE-TTM": "20.66x", ... }
  },
  "management": {
    "score": 7,
    "summary": "管理层与治理分析文字...",
    "key_people": ["姓名 - 职位 - 简要背景", ...],
    "recent_changes": ["变动描述1", ...]
  },
  "catalysts": {
    "score": 7,
    "summary": "近期动态与催化分析文字...",
    "events": ["事件1（日期）", ...],
    "outlook": "前瞻判断文字..."
  },
  "conclusion": "综合结论文字...",
  "risks": ["风险1", "风险2", ...]
}
```

3. 如果该公司已存在（按 code 匹配），则**覆盖更新**；否则追加
4. 写入后 commit 并 push 到 GitHub，确保阿尔法工坊在线页面同步更新

**阿尔法工坊地址：** https://finstep-ai.github.io/alpha-factor-lab/fundamental.html

---

## 行业一页纸执行流程

当用户要求分析一个行业时，走这个流程：

### Step B1: 行业数据采集

1. **web_search** 广泛搜索行业信息（至少10组关键词）：
   - `"{行业名}" 市场规模 2025 2026`
   - `"{行业名}" 产业链 全景图`
   - `"{行业名}" 竞争格局 市场份额`
   - `"{行业名}" 技术路线 趋势`
   - `"{行业名}" 政策 产业政策`
   - `"{行业名}" 龙头企业 排名`
   - `"{行业名}" 供需分析`
   - `"{行业名}" 投资逻辑 研报`
   - `"{行业名}" 国产替代 自主可控`（适用时）
   - `"{行业名}" 发展历程 历史`

2. **web_fetch** 抓取 5-10 篇核心报告/文章全文

3. **fintool MCP**（A股相关行业）：
   ```
   fintool-plates.get_plate_list keyword="{行业名}"
   fintool-plates.get_plate_stocks plate_code="{板块代码}"
   fintool-company.get_company_info code="{龙头公司代码}"
   ```

4. **us-market skill**（美股相关行业）：
   ```bash
   python3 skills/us-market/scripts/us_market_query.py --type profile --symbol {龙头ticker}
   python3 skills/us-market/scripts/us_market_query.py --type financials --symbol {龙头ticker}
   ```

### Step B2: 读取行业分析模板

```
read references/industry-template.md
```

### Step B3: 撰写行业一页纸

按模板结构撰写，重点确保：

**核心要求：**
- **投资逻辑清晰**：开篇直奔核心——为什么这个行业值得关注？
- **产业链完整**：上中下游全覆盖，每个环节的竞争格局和趋势
- **数据扎实**：市场规模有量化测算，竞争格局有份额数据
- **技术前瞻**：不只看当下，还要看未来2-3年的技术演进
- **标的明确**：最后落到具体投资标的，有对比表格

**格式要求：**
- 用清晰的标题层级结构
- 关键数据点标注来源
- 市场规模用表格展示
- 竞争格局用分梯队方式
- 投资标的用对比表格

### Step B4: 写入阿尔法工坊前端

行业分析完成后，写入 `alpha-factor-lab/fundamental-reports.json`，格式如下：

```json
{
  "name": "行业名称",
  "code": "INDUSTRY_{行业英文简称}",
  "market": "INDUSTRY",
  "date": "2026-02-22",
  "type": "industry",
  "rating": "推荐|强烈推荐|中性|回避|关注",
  "core_logic": {
    "summary": "核心投资逻辑概述...",
    "demand_drivers": ["需求驱动1", "需求驱动2"],
    "supply_dynamics": "供给端情况...",
    "outlook": "供需展望..."
  },
  "industry_overview": {
    "definition": "行业定义...",
    "market_size": "市场规模...",
    "growth_rate": "增速...",
    "cycle_stage": "周期阶段...",
    "business_model": "商业模式概述...",
    "policy": "政策环境概述..."
  },
  "supply_chain": {
    "upstream": { "summary": "上游分析...", "key_players": ["公司1", "公司2"] },
    "midstream": { "summary": "中游分析...", "key_players": ["公司1", "公司2"] },
    "downstream": { "summary": "下游分析...", "key_players": ["应用1", "应用2"] },
    "tech_roadmap": "技术路线...",
    "moat": "行业护城河分析..."
  },
  "market_sizing": {
    "current": "当前市场规模",
    "forecast": { "2025": "XX亿", "2026": "XX亿", "2030": "XX亿" },
    "assumptions": ["假设1", "假设2"],
    "domestic_opportunity": "国产替代空间..."
  },
  "competition": {
    "tier1": ["公司1 - 简述", "公司2 - 简述"],
    "tier2": ["公司1 - 简述", "公司2 - 简述"],
    "tier3": ["公司1 - 简述"]
  },
  "top_picks": [
    {
      "name": "公司名",
      "code": "代码",
      "segment": "所属环节",
      "thesis": "投资逻辑",
      "scarcity": true,
      "elasticity": "超额|平均|低于平均"
    }
  ],
  "risks": ["风险1", "风险2", "风险3"],
  "conclusion": "综合结论..."
}
```

写入后 commit 并 push。
