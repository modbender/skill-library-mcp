---
name: crypto-daily-report
description: 加密货币日报生成技能。当用户要求生成日报、出日报、发日报、加密新闻日报时激活。按固定板块结构采集数据、处理脱水、排版后分三条消息发送到 Telegram 加密新闻 Topic。
---

# 加密货币日报 Skill

## 触发词
"出日报" / "生成日报" / "加密日报" / "日报" / "发日报"

## 输出目标
Telegram 加密新闻 Topic（threadId: 182747，chatId: 680162114）
分三条消息发送（见【排版规范】）

## 静默执行原则（重要）
- 执行过程中**不向用户输出任何中间状态文字**，包括：
  - "开始采集数据"、"并行启动所有数据源"
  - "数据采集完成，开始组装日报"
  - "三条消息字符数均在限制内，开始发送"
  - "日报已发送完毕"
  - 任何执行进度说明、重点提示、分析总结
- 三条消息发送完毕后，主会话回复**仅用 NO_REPLY**，不追加任何内容

---

## 执行流程

### Step 1：并行数据采集（全部同时发起）

**快讯网站（主力，用 web_fetch）：**
- BlockBeats: `https://www.theblockbeats.info/newsflash`
- Odaily: `https://www.odaily.news/zh-CN/newsflash`
- PANews: `https://www.panewslab.com/zh/newsflash`
- CoinDesk: `https://www.coindesk.com/latest-crypto-news`

**价格数据：**
```bash
python3 skills/crypto-daily-report/scripts/fetch_prices.py
```

**Meme 趋势：**
```bash
python3 skills/crypto-daily-report/scripts/fetch_meme_trending.py
```

**DeFi 生息：**
```bash
python3 skills/crypto-daily-report/scripts/fetch_defi_yields.py 5
```

**RootData 热榜（内部权重，不对外展示标签）：**
```bash
python3 skills/rootdata/scripts/rootdata.py hot --limit 20
python3 skills/rootdata/scripts/rootdata.py funding --limit 10
```

**OpenNews 高分补漏（score≥75）：**
```bash
TOKEN=$(grep OPENNEWS_TOKEN ~/.openclaw/.env | cut -d'=' -f2)
curl -s -X POST "https://ai.6551.io/open/news_search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"minScore": 75, "limit": 20, "page": 1}'
```

---

### Step 2：融资信息补全（重要）

RootData 融资列表拿到后，**逐个去 BlockBeats 搜索项目名**补充机构信息：
```
https://www.theblockbeats.info/search?q=<项目名>
```
- 找到对应快讯后用 web_fetch 读取原文
- 从原文提取：领投机构、参投机构（≤3个）
- ⚠️ 禁止用 Tavily 猜测机构名，必须从快讯原文获取
- ⚠️ 每个项目必须有独立链接，禁止将 A 项目的链接用在 B 项目上
- 若 BlockBeats 搜索无结果，尝试 Odaily 或 PANews，仍无则标注"参投机构未披露"

---

### Step 3：内容处理与脱水

处理原则：
- **去重**：同一事件只在最相关板块出现一次
- **脱水**：每条新闻提炼核心信息，1-2句话
- **重要性过滤**：优先 OpenNews 高分（≥75）、快讯头条、RootData 今日新上榜项目
- **时效过滤**：只展示当日新闻；融资动态只展示最近一周

---

### Step 4：按板块组装

#### 板块结构

**① 头条新闻**
- 1-2 条，仅当日最重要

**② 融资动态**
- 最近一周，≤5条
- 每条：项目名、业务介绍（1句）、金额/轮次、参与机构（≤3个）、一条链接

**③ 重大更新**
- ≤5条，涵盖：产品上线、主网/测试网、重要公告、大事件
- 大额代币解锁仅最重要的一条作为更新展示

**④ Alpha 前线**
- 飙升 Meme 速递（GeckoTerminal 实时数据）
- 社区热议 Alpha 项目（3-4条，RootData热榜 + opentwitter 结合）
- 热门赛道叙事（1段，当日最强叙事）

**⑤ 链上与 DeFi**
- 链上数据：CEX 净流入/流出（Coinglass）、鲸鱼动向，不展示爆仓金额
- 生息机会：DeFiLlama yields API 数据，展示协议/资产/链/APY/TVL

**⑥ 观点洞见**
- 精选 ≤3条，来源：KOL推文、机构报告、研报

**⑦ 交易数据**
- 现货：BTC / ETH / SOL / HYPE
- ETF 资金流向
- 期货/衍生品（简洁1-2句）
- 市场判断（2-3句）

**⑧ 宏观与政策**
- 加密监管：≤1条
- 宏观经济数据（简洁，含近期重要数据发布提醒）

---

### Step 5：排版与发送

分三条消息发送，格式如下：

---

**消息一：头条 + 融资**

```
📰 *加密货币日报 · YYYY年M月D日*
_来源：BlockBeats · Odaily · PANews · CoinDesk · Binance 实时_

━━━━━ 🔴 头条 ━━━━━

*[标题]*
[1-2句正文]
→ [来源链接]

━━━━━ 💰 融资动态 ━━━━━

▪ *项目名 · 金额 轮次*
业务介绍（1句）
机构1、机构2、机构3参投 · 日期
→ [链接]
```

**消息二：重大更新 + Alpha 前线 + 链上DeFi**

```
━━━━━ 🚀 重大更新 ━━━━━

▪ *项目名（代币）事件标题*
1-2句描述
→ [链接]

━━━━━ 🎯 Alpha 前线 ━━━━━

*飙升 Meme 速递*（GeckoTerminal Solana 实时）
代币名 · +X% · 量 $XM · FDV $XM
→ [DEX链接]

*社区热议 Alpha 项目*

▪ *项目名* — 1句描述，热度说明
→ [链接]

*热门赛道叙事*
[1段文字]

━━━━━ 📊 链上与 DeFi ━━━━━

*链上数据*
[CEX流向等]

*生息机会*（DeFiLlama 实时）
协议 · 资产 · 链 · APY X% · TVL $XM
→ [链接]
```

**消息三：观点 + 交易数据 + 宏观**

```
━━━━━ 💬 观点洞见 ━━━━━

▪ *来源名称*：内容（1-2句）
→ [链接]

━━━━━ 📈 交易数据 ━━━━━

*现货价格*（Binance，HH:MM BJ）
BTC  $XX,XXX · +X.XX%
ETH  $X,XXX · +X.XX%
SOL  $XX.XX · +X.XX%
HYPE  $XX.XX · +X.XX%（合约）

*ETF*：[一句话]
→ [链接]

*期货*：[一句话爆仓数据]

*判断*：[2-3句]

━━━━━ 🌐 宏观与政策 ━━━━━

[宏观数据 + 近期重要发布提醒]
→ [CME FedWatch链接]

*监管*：[1句]
→ [链接]
```

---

## 错误处理与降级策略

### 数据源故障处理

| 数据源 | 故障类型 | 降级策略 |
|--------|---------|---------|
| BlockBeats/Odaily/PANews | 超时/403 | 跳过该站，其余三站补全；所有站均失败则标注 [快讯暂时不可用] |
| CoinDesk | 超时 | 跳过，不影响其他板块 |
| Binance 现货 API | 超时/限流 | 重试2次（间隔1.5s），仍失败输出 [DATA UNAVAILABLE] |
| Binance 合约 API（HYPE） | 超时 | 同上，标注 HYPE: [DATA UNAVAILABLE] |
| GeckoTerminal（Meme） | 403/超时 | 自动降级到 DEXScreener token-boosts；两者均失败则标注"今日 Meme 数据暂不可用" |
| DeFiLlama yields | 超时 | 重试2次，仍失败输出 "[DATA UNAVAILABLE] 请访问 defillama.com/yields" |
| RootData | 超时/限额 | 跳过融资/热榜板块，标注 [RootData 暂不可用] |
| OpenNews API | 超时/401 | 跳过补漏步骤，仅用快讯网站内容 |
| BlockBeats 搜索（融资机构） | 无结果 | 依次尝试 Odaily → PANews；仍无则标注"参投机构未披露" |

### 重试规范
- 脚本内置重试：最多2次，指数退避（1s, 2s）
- 整体采集超时：单个数据源超过15s视为失败，跳过，不阻塞其他板块
- 绝不因单点失败中断整个日报

### 标记规范
- `[DATA UNAVAILABLE]` — 数据源无响应
- `[未验证]` — 来源可信度存疑
- `⚠️ 降级数据` — 使用了备用数据源

---

## 字数控制规范

**Telegram 单条消息上限：4096 字符（UTF-16 code units）**
**建议每条不超过 3800 字符（留 ~200 字符余量）**

### 发送前检查
每条消息组装完成后，用以下方式估算字符数：
```python
# 快速估算：中文字符按1.5倍计，emoji 按2倍计
def estimate_chars(text):
    count = 0
    for ch in text:
        cp = ord(ch)
        if cp > 0xFFFF:   count += 2   # emoji
        elif cp > 0x4E00: count += 1   # 中文等 BMP 字符
        else:             count += 1
    return count
```
或用脚本：`echo "消息内容" | python3 skills/crypto-daily-report/scripts/check_length.py`

### 各消息字数预算

| 消息 | 内容 | 建议上限 |
|------|------|---------|
| 消息一 | 头条 + 融资 | 1500 字符 |
| 消息二 | 重大更新 + Alpha + DeFi | 3000 字符 |
| 消息三 | 观点 + 交易 + 宏观 | 1800 字符 |

### 超出时的压缩优先级
1. 压缩"热门赛道叙事"段落（最长，最可压缩）
2. Alpha 项目描述缩减到1句
3. Meme 速递减少条目（5条→3条）
4. 观点洞见减少到2条
5. 生息机会减少到3条

---

## 全局规范

- **禁止表格**（Telegram 不渲染）
- **禁止二级缩进**
- **每条内容只保留一个链接**
- **禁止展示 RootData 内部权重标签**
- **反幻觉**：所有数据必须来自本次会话实际查询，不确定的标注 [未验证]
- **时效**：快讯只用当日内容；价格数据记录抓取时间

## 脚本位置

```
skills/crypto-daily-report/scripts/
├── fetch_prices.py        # BTC/ETH/SOL 现货 + HYPE 合约价格
├── fetch_meme_trending.py # GeckoTerminal Solana trending Meme
├── fetch_defi_yields.py   # DeFiLlama 主流协议生息机会
└── fetch_news.sh          # 并行抓取四个快讯网站（备用）
```

## 数据源速查

| 数据 | 来源 | 方式 |
|------|------|------|
| 快讯 | BlockBeats/Odaily/PANews/CoinDesk | web_fetch |
| 价格 | Binance API | fetch_prices.py |
| Meme | GeckoTerminal | fetch_meme_trending.py |
| DeFi yield | DeFiLlama | fetch_defi_yields.py |
| 融资/热榜 | RootData | rootdata.py |
| 高分新闻 | OpenNews 6551 API | curl POST |
| Alpha KOL | OpenTwitter 6551 API | curl POST |
| 融资机构详情 | BlockBeats 搜索 | web_fetch 原文 |
| ETF 数据 | CoinDesk / Coinglass | web_fetch |
| 链上数据 | Coinglass | web_fetch |
