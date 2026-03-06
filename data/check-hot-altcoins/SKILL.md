---
name: 查看每日热门山寨代币
description: 生成加密货币早报PDF，包含行业动态、FDV排名、热点赛道和风险提示。数据来源于CoinGecko API。
---

# 查看每日热门山寨代币

生成一份专业的加密货币早报PDF，发送到飞书。

## 执行步骤

### 第一步：获取数据
从CoinGecko API获取实时数据。必须分两次请求（API限制）：

**请求1 - 前10大山寨币：**
```bash
curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana,binancecoin,ripple,cardano,dogecoin,chainlink,avalanche-2,polygon,polkadot,stellar&order=market_cap_desc&sparkline=false" > /tmp/coins_part1.json
```

**请求2 - 热点赛道币：**
```bash
curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=fetch-ai,render-token,ocean-protocol,uniswap,aave,near,aptos,pepe,optimism,ondo,kite-ai,world-liberty-financial&order=market_cap_desc&sparkline=false" > /tmp/coins_part2.json
```

### 第二步：处理数据
用Python合并数据，按market_cap降序排序。

### 第三步：生成HTML
将数据填入以下HTML模板，然后保存为PDF。

## 必须包含的内容（6个板块）

### 板块1：昨日行业动态（文字板块）

从知识库读取当日行业重要新闻。如果没有新闻，可以写：
- SEC监管动态
- ETF相关消息
- 市场整体走势

### 板块2：前10大山寨币FDV排名

**表格列：**
- 排名（1-10）
- 币种（如SOL、BNB、XRP）
- 当前价格（如$88.54）
- 24h涨跌（如-5.23%，绿色下跌红色上涨）
- 24h区间（如$86.33-$90.74）
- FDV（如$53.0B）

**币种列表（按市值）：**
1. XRP
2. BNB
3. SOL
4. DOGE
5. ADA
6. LINK
7. XLM
8. AVAX
9. SOL
10. UNI

（排除BTC、ETH、USDT、USDC）

### 板块3：热点赛道

**表格列：**
- 赛道
- 币种
- 价格
- 24h涨跌
- FDV
- 简评

**必须包含的赛道：**

| 赛道 | 币种 | 简评 |
|------|------|------|
| AI/代理 | FET | AI代理龙头 |
| AI/计算 | RENDER | GPU渲染 |
| AI/数据 | OCEAN | 数据市场 |
| DeFi | UNI | DEX龙头 |
| DeFi | AAVE | 借贷龙头 |
| L1 | NEAR | AI+TON协同 |
| L1 | APT | 高性能L1 |
| Layer2 | OP | Layer2龙头 |
| RWA | ONDO | RWA叙事 |

### 板块4：长期关注项目

**表格列：**
- 项目名
- 价格（或"TGE待定"）
- 24h涨跌
- FDV
- 关注理由

**必须包含：**
| 项目 | 价格 | 理由 |
|------|------|------|
| KITE | $0.24 | AI支付首个应用 |
| WLFI | $0.11 | Trump家族背书 |
| Backpack | TGE待定 | 20%股权给持币者，潜在IPO |

### 板块5：风险提示

必须包含4项：
- 宏观风险：美联储政策不确定性
- 监管风险：SEC执法行动持续
- 解锁风险：多项目面临代币解锁
- 技术风险：L1/L2竞争加剧

### 板块6：免责声明

> 本报告仅供参考，不构成投资建议。加密资产风险极高，投资前请自行研究。

## 格式要求

### HTML样式
```html
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 30px; max-width: 900px; margin: 0 auto; font-size: 11pt; line-height: 1.6; }
h1 { color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 12px; }
h2 { color: #333; margin-top: 25px; border-bottom: 1px solid #eee; padding-bottom: 8px; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 9pt; }
th { background: #0066cc; color: white; }
.up { color: #16a34a; }
.down { color: #dc2626; }
.warning { background: #fff3cd; padding: 12px; border-radius: 4px; }
.news-box { background: #f0fdf4; padding: 15px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #16a34a; }
</style>
```

### 转换PDF
用浏览器打开HTML然后导出为PDF：
```bash
# 用浏览器打开
open file:///tmp/早报.html
# 然后用浏览器的"导出为PDF"功能
```

### 发送到飞书
使用message工具发送PDF文件到用户。

## 注意事项（重要！）

1. **只显示FDV，不显示市值** - 这是用户偏好
2. **数据必须从CoinGecko API获取** - 不能用估算或假设
3. **发送前复查数据准确性** - 确认数字正确
4. **未上线项目标注"TGE待定"** - 如Backpack
5. **不显示数据来源** - 用户不需要知道数据从哪里来
6. **格式简洁** - 避免过多* # 等符号
7. **使用中文** - 用户用中文交流
8. **价格格式** - 如$88.54，不要写成$88.5
9. **涨跌颜色** - 上涨绿色，下跌红色
10. **FDV单位** - 大于10亿用B（如$53.0B），小于10亿用M（如$240M）
