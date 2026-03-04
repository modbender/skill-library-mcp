---
name: global-intel-summary
description: 全球情报汇总工具 - 自动生成结构化的全球市场、政经、AI 新闻汇总报告。支持定向深度分析与智能推演。借鉴 situation-monitor 项目架构，增强 RSS 源接入、情报分级和高相关性事件检测。
version: 3.3.0
author: xiaoai
keywords: intel, news, summary, market, trading, ai, global, forecast, 推演, rss, geopolitical
---

# 全球情报汇总 Skill (v3.3)

自动生成结构化的全球情报汇总报告。v3.3 版本借鉴了 **situation-monitor** (GitHub 2.8k+ stars) 项目架构，新增了：

- 🆕 **RSS 源聚合**：接入 30+ 优质 RSS 源，覆盖政治、科技、金融、政府、AI、情报六大领域
- 🆕 **情报分级 (Alert System)**：自动识别重大地缘政治事件（战争、制裁、军事行动）
- 🆕 **相关性检测**：识别跨新闻的高相关性事件，识别"叙事演进"
- 🆕 **区域热点**：自动标记新闻涉及的关键地区（欧洲、中东、亚太、美洲、非洲）

---

## 一、执行要求（v3.3 核心铁律）

### ⚠️ 铁律 1：数据时效性
- **只使用 24 小时内最新数据**
- 超过 48 小时的一律不用
- 如果没有最新数据，明确写"今日无新报道"

### ⚠️ 铁律 2：数据源强制
| 资产类别 | 强制数据源 |
|---------|----------|
| 加密货币 | **Binance**（首选） + CoinMarketCap（验证） |
| 美股 | Yahoo Finance |
| A股/港股 | 东方财富/同花顺 |
| 国际政经 | BBC/Reuters/X + **RSS 聚合** |
| 地缘/情报 | **RSS 深度源**（见下方列表） |

### ⚠️ 铁律 3：强制溯源
**每条数据必须标注**：
- 时间戳（如：2026-02-14 09:30 UTC+8）
- 来源（如：来源: Binance | 时间: 09:25）

### ⚠️ 铁律 4：情报分级
**以下关键词出现时，标记为 [⚠️ ALERT] 并提升优先级**：
- `war, invasion, military, nuclear, sanctions, missile, attack, troops, conflict, strike, coup, martial law, emergency, nato`

---

## 二、核心数据源 (v3.3 新增)

### 🆕 RSS 源矩阵（situation-monitor 推荐）

#### 1️⃣ 政治/综合 (Politics)
- BBC World: `https://feeds.bbci.co.uk/news/world/rss.xml`
- NPR News: `https://feeds.npr.org/1001/rss.xml`
- Guardian World: `https://www.theguardian.com/world/rss`
- NYT World: `https://rss.nytimes.com/services/xml/rss/nyt/World.xml`

#### 2️⃣ 科技 (Tech)
- Hacker News: `https://hnrss.org/frontpage`
- Ars Technica: `https://feeds.arstechnica.com/arstechnica/technology-lab`
- The Verge: `https://www.theverge.com/rss/index.xml`
- MIT Tech Review: `https://www.technologyreview.com/feed/`
- ArXiv AI: `https://rss.arxiv.org/rss/cs.AI`

#### 3️⃣ 金融 (Finance)
- CNBC: `https://www.cnbc.com/id/100003114/device/rss/rss.html`
- MarketWatch: `https://feeds.marketwatch.com/marketwatch/topstories`
- Yahoo Finance: `https://finance.yahoo.com/news/rssindex`
- FT: `https://www.ft.com/rss/home`

#### 4️⃣ 政府/宏观 (Gov/Macro)
- White House: `https://www.whitehouse.gov/news/feed/`
- Federal Reserve: `https://www.federalreserve.gov/feeds/press_all.xml`
- SEC Announcements: `https://www.sec.gov/news/pressreleases.rss`
- DoD News: `https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?max=10&ContentType=1&Site=945`

#### 5️⃣ 情报/防务 (Intel/Defense)
- CSIS: `https://www.csis.org/analysis/feed`
- Brookings: `https://www.brookings.edu/feed/`
- CFR: `https://www.cfr.org/rss.xml`
- Defense One: `https://www.defenseone.com/rss/all/`
- War on Rocks: `https://warontherocks.com/feed/`
- Breaking Defense: `https://breakingdefense.com/feed/`
- The Drive War Zone: `https://www.thedrive.com/the-war-zone/feed`

#### 6️⃣ 区域深度 (Regional)
- The Diplomat (亚太): `https://thediplomat.com/feed/`
- Al-Monitor (中东): `https://www.al-monitor.com/rss`
- Bellingcat (OSINT): `https://www.bellingcat.com/feed/`
- CISA Alerts (网络安全): `https://www.cisa.gov/uscert/ncas/alerts.xml`

---

### 🆕 关键词检测规则

#### 🚨 告警关键词 (Alert Keywords)
出现以下词汇时，标记为 **[⚠️ ALERT]**：
`war, invasion, military, nuclear, sanctions, missile, attack, troops, conflict, strike, coup, martial law, emergency, nato, ceasefire, treaty, assassination, terrorist`

#### 🌍 区域关键词 (Region Keywords)
- **欧洲 (EUROPE)**: nato, ukraine, russia, germany, france, uk, britain, poland
- **中东 (MENA)**: iran, israel, saudi, syria, iraq, gaza, lebanon, yemen, houthi
- **亚太 (APAC)**: china, taiwan, japan, korea, south china sea, asean, philippines
- **美洲 (AMERICAS)**: us, america, canada, mexico, brazil, venezuela
- **非洲 (AFRICA)**: africa, sahel, niger, sudan, ethiopia, somalia

---

## 三、执行步骤（v3.3）

### Step 1: 获取当前时间
```bash
date
```

### Step 2: 分批搜索（每批 ≤50 词）
```
搜索1：BTC/ETH/SOL Binance 价格
搜索2：美股指数（S&P 500, Nasdaq, Dow Jones）
搜索3：Trump/Musk 最新动态
搜索4：RSS 源深度搜索（根据当日热点选择 2-3 个 RSS 源关键词）
  - 例如：如果有中东冲突迹象，搜索 "Israel Iran Gaza latest"
  - 如果有 AI 突破，搜索 "OpenAI GPT-5 latest"
  - 如果有金融风险，搜索 "Fed rate decision latest"
```

### Step 3: 情报分级处理
- 扫描所有新闻标题，检测 **Alert Keywords**
- 如果检测到 **[⚠️ ALERT]** 事件，在报告中优先展示，并标注 [⚠️]
- 标注涉及的 **Region**

### Step 4: 数据校验
- 关键数据必须二次搜索验证
- 如果多源数据不一致，写"待核实"

### Step 5: 生成报告
按模板输出，每条数据带时间戳 + 来源

---

## 四、报告输出模板 (v3.3)

```markdown
# 🌍 全球情报汇总 (YYYY-MM-DD HH:MM)

---

## ⚠️ 今日热点 [ALERT]
*(如果有检测到 Alert 关键词的事件，放在这里)*

## 💰 加密货币
- BTC: $XX,XXX | 来源: Binance | 时间: HH:MM
- ETH: $X,XXX | 来源: Binance | 时间: HH:MM

## 📈 美股行情
- S&P 500: X,XXX.XX (X.XX%) | 来源: Yahoo Finance | 时间: HH:MM
- Nasdaq: XX,XXX.XX (X.XX%) | 来源: Yahoo Finance | 时间: HH:MM

## 🇨🇳 A股/港股
- 恒生指数: XX,XXX (X.XX%) | 来源: 东方财富 | 时间: HH:MM

## 🌍 国际政经
- [⚠️ ALERT] [区域] [标题] | 来源: XXX | 时间: HH:MM
- Trump: [动态] | 来源: X | 时间: HH:MM
- Musk: [动态] | 来源: X | 时间: HH:MM

## 🤖 AI 前沿
- [新闻1] | 来源: XXX | 时间: HH:MM
- [新闻2] | 来源: XXX | 时间: HH:MM
- [新闻3] | 来源: XXX | 时间: HH:MM

---

## 🔮 智能推演
基于今日情报，推演未来 48 小时的 3 个潜在走向：
1. [方向1] - 逻辑支撑
2. [方向2] - 逻辑支撑
3. [方向3] - 逻辑支撑
```

---

## 五、禁止行为

- ❌ 禁止使用超过 48 小时的数据
- ❌ 禁止编造数据（不知道就是不知道）
- ❌ 禁止用预测数据冒充实时数据
- ❌ 禁止使用非指定数据源

---

## 六、搜索技巧

### 加密货币搜索
```
"BTCUSDT Binance price today" (英文)
"比特币 价格 今日 Binance" (中文)
```

### 美股搜索
```
"S&P 500 Nasdaq Dow Jones February 14 2026"
```

### RSS 源深度搜索
```
"site:feeds.bbci.co.uk middle east latest"
"site:csis.org defense latest"
"site:brookings.edu policy latest"
```

### 人物追踪
```
"Trump policy February 2026"
"Musk xAI AGI news February 2026"
```

---

## 七、进阶：相关性检测 (Narrative Tracking)

*此为 v3.3 新增的高级分析功能*

在生成报告时，尝试识别以下模式：

1. **单点事件**：孤立的重大新闻
2. **叙事演进**：多个相关新闻，描述同一事件的演进（如：事件A发生 -> 各方反应 -> 后续发展）
3. **跨领域关联**：科技 + 金融，科技 + 地缘政治的关联

*提示：使用 LLM 的上下文理解能力，扫描当日新闻，识别这些模式。*

---

*由小爱开发 | v3.3 借鉴 situation-monitor 架构增强版*
