---
name: keepa-api
description: Keepa API 客户端 - 亚马逊产品价格历史追踪工具。提供 ASIN 查询、价格历史等数据查询功能。
metadata:
  version: 1.0.0
  dependencies:
    - curl
    - jq
---

# Keepa API 客户端

基于 Keepa API 的亚马逊产品价格历史追踪工具。

## 依赖

- curl (HTTP 请求)
- jq (JSON 解析)

安装依赖:
```bash
# macOS
brew install curl jq

# Ubuntu/Debian
apt-get install curl jq
```

## Usage

```bash
# ASIN 查询 - 获取产品详情和价格历史
/keepa-api asin B08XYZ123

# 批量 ASIN 查询
/keepa-api batch-asin B08XYZ123,B09ABC456,B07DEF789

# 查询价格历史
/keepa-api price-history B08XYZ123 --days 90

# 关键词搜索产品
/keepa-api search "wireless earbuds" --category Electronics

# 查询 Best Sellers
/keepa-api bestsellers --category Electronics --page 1

# 指定亚马逊站点
/keepa-api asin B08XYZ123 --domain JP

# 直接输入 ASIN
/keepa-api
[paste ASIN or product URL]
```

## Options

| Option | Description |
|--------|-------------|
| `--domain <US\|UK\|DE\|...>` | 亚马逊站点 (默认：US) |
| `--days <number>` | 历史数据天数：30, 90, 180 (默认：90) |
| `--category <name>` | 商品类目 (Electronics, Home, Beauty 等) |
| `--output <table\|json>` | 输出格式 (默认：table) |
| `--page <number>` | 分页页码 (用于搜索和 Best Sellers) |

## Core Tools

### 1. Product Query (产品查询)

查询单个 ASIN 的详细信息，包括价格历史、销售排名、评论等。

```bash
/keepa-api asin <ASIN> [--marketplace US] [--days 90]
```

**返回数据**:
- 产品基础信息 (标题、品牌、类目、图片)
- 当前价格 (Amazon 价格、第三方价格)
- 价格历史记录
- 销售排名 (BSR)
- 评论数量和评分
- 库存状态

### 2. Price History (价格历史)

获取产品历史价格数据，支持自定义时间范围。

```bash
/keepa-api price-history <ASIN> [--days 30|90|180|365]
```

**返回数据**:
- 每日价格点
- 价格变化时间线
- 历史最低价/最高价
- 平均价格

### 3. Sales Rank History (销售排名历史)

追踪产品销售排名变化趋势，与 asin 命令一起返回。

```bash
/keepa-api asin <ASIN> --days 90
```

**返回数据**:
- 每日 BSR 排名
- 排名变化趋势
- 类目前 100 记录

### 4. Product Search (产品搜索)

通过关键词搜索亚马逊产品。

```bash
/keepa-api search "<keyword>" [--category <category>] [--page <n>]
```

**返回数据**:
- 匹配产品列表
- ASIN、标题、价格
- 评分和评论数
- 图片链接

### 5. Best Sellers (热销榜)

获取类目热销榜产品。

```bash
/keepa-api bestsellers --category <category> [--page <n>]
```

**返回数据**:
- 热销产品排名
- 产品 ASIN 和信息
- 当前价格

## Three Dimensions

| Dimension | Controls | Options |
|-----------|----------|---------|
| **Data Type** | 数据类型 | product, price, rank, offers, search |
| **Marketplace** | 亚马逊站点 | US, EU, UK, JP, CA, AU, IN |
| **Output Format** | 数据输出格式 | table, json |

## Marketplace Reference

| Marketplace | Code | Domain |
|-------------|------|--------|
| 美国 | US | amazon.com |
| 英国 | UK | amazon.co.uk |
| 德国 | DE | amazon.de |
| 法国 | FR | amazon.fr |
| 日本 | JP | amazon.co.jp |
| 加拿大 | CA | amazon.ca |
| 澳大利亚 | AU | amazon.com.au |
| 印度 | IN | amazon.in |

## Workflow

### Progress Checklist

```
Keepa API Query Progress:
- [ ] Step 0: Check API configuration ⛔ BLOCKING
- [ ] Step 1: Understand data requirement
- [ ] Step 2: Confirm query parameters ⚠️ REQUIRED
- [ ] Step 3: Execute API request
- [ ] Step 4: Parse and display results
```

### Flow

```
Input → [Step 0: Config Check] ─┬─ Configured → Continue
                                │
                                └─ Not configured → Setup required ⛔ BLOCKING
                                                   │
                                                   └─ Complete setup → Save config → Continue
```

### Step 0: Configuration Check ⛔ BLOCKING

**Purpose**: Check Keepa API configuration.

**Configuration paths**:
1. Project-level: `.teamclaw-skills/keepa-api/CONFIG.md`
2. User-level: `~/.teamclaw-skills/keepa-api/CONFIG.md`

**Check command**:
```bash
# Check project-level first
test -f .teamclaw-skills/keepa-api/CONFIG.md && echo "project"

# Then user-level
test -f "$HOME/.teamclaw-skills/keepa-api/CONFIG.md" && echo "user"
```

**First-Time Setup** (if config not found):

Use `AskUserQuestion` with questions:

1. **Keepa API Key** (required):
   - Input your Keepa API key
   - Get key from: https://keepa.com/#!api

2. **Default marketplace**:
   - US (amazon.com)
   - UK (amazon.co.uk)
   - DE (amazon.de)
   - JP (amazon.co.jp)
   - Other

3. **Default history days**:
   - 30 days
   - 90 days (default)
   - 180 days
   - 365 days

4. **Output format**:
   - Table (default, readable)
   - JSON (for integration)

**Configuration file format** (`CONFIG.md`):
```yaml
---
api_key: your-keepa-api-key-here
marketplace: US
default_days: 90
output_format: table
---
```

### Step 1: Understand Data Requirement

**Analyze user request**:
- Data type needed (product/price/rank/offers/search)
- Target ASIN(s) or keyword(s)
- Marketplace
- Time period

### Step 2: Confirm Query Parameters ⚠️

**Display confirmation**:
- Query type
- Target (ASIN/keyword)
- Marketplace
- Days range
- Output format

### Step 3: Execute API Request

**Execute curl request**:
```bash
curl -s "https://api.keepa.com/product?key=$API_KEY&domain=$DOMAIN&asin=$ASIN"
```

### Step 4: Parse and Display Results

**Output format**:
```
═══ Keepa Product Report ═══

ASIN: B08XYZ123
Title: [Product Title]
Brand: [Brand Name]
Category: [Category]

Current Price:
- Amazon: $29.99
- 3rd Party New: $27.99
- 3rd Party Used: $22.99

Sales Rank: #1,234 in Electronics
Rating: 4.5/5 (2,847 reviews)

Price History (90 days):
- Lowest: $24.99 (2024-01-15)
- Highest: $34.99 (2024-02-01)
- Average: $29.50
```

## API Endpoints

### Product Endpoint

```
GET /product
Parameters:
- key: API key
- domain: Amazon domain (1=US, 3=UK, 4=DE, 5=FR, 6=JP, 7=CA, 9=AU, 10=IN)
- asin: ASIN or comma-separated list
- history: Include price history (1/0)
- rating: Include rating (1/0)
```

### Search Endpoint

```
GET /search
Parameters:
- key: API key
- domain: Amazon domain
- query: Search query
- category: Category ID (optional)
- page: Page number (optional)
```

### Best Sellers Endpoint

```
GET /bestsellers
Parameters:
- key: API key
- domain: Amazon domain
- categoryId: Category ID
- page: Page number (optional)
```

## Category IDs

| Category | ID |
|----------|-----|
| Electronics | 172282 |
| Computers | 541966 |
| Home & Kitchen | 1055398 |
| Beauty & Personal Care | 3760911 |
| Sports & Outdoors | 3375251 |
| Toys & Games | 165793011 |
| Clothing | 7141123011 |
| Books | 283155 |
| Office Products | 1064954 |
| Garden & Outdoor | 2972638011 |

## File Structure

```
skills/keepa-api/
├── SKILL.md                 # Skill 定义
├── scripts/
│   └── keepa.sh             # 主脚本 (纯 curl 实现)
├── references/
│   └── api-docs.md          # API 文档参考
└── CONFIG.template.md       # 配置文件模板
```

## Configuration

### Get API Key

1. Visit [Keepa API](https://keepa.com/#!api)
2. Register or login
3. Go to Account → API Key
4. Copy your API key

### Rate Limits

| Plan | Tokens/Day | Cost per Request |
|------|------------|------------------|
| Free | 100 | 1-2 tokens |
| Basic (9€/mo) | 100,000 | 1-2 tokens |
| Pro (19€/mo) | 500,000 | 1-2 tokens |
| Ultra (49€/mo) | 2,000,000 | 1-2 tokens |

### Token Costs

| Request Type | Token Cost |
|--------------|------------|
| Product (single ASIN) | 1-2 tokens |
| Product (batch 10 ASINs) | 10-20 tokens |
| Search | 1 token |
| Best Sellers | 1 token |
| Offers | 1-3 tokens |

## Output Examples

### Product Query Result

```
═══ Keepa Product Report ═══

ASIN: B08XYZ123
Title: Wireless Bluetooth Earbuds
Brand: SoundTech
Category: Electronics > Headphones

Current Price:
- Amazon: $29.99
- 3rd Party New: $27.99
- 3rd Party Used: $22.99
- Lowest in 30 days: $24.99

Sales Rank: #1,234 in Electronics (#45 in Earbud Headphones)
Rating: 4.5/5 (2,847 reviews)

Price History (90 days):
┌──────────────┬────────────┐
│ Date         │ Price      │
├──────────────┼────────────┤
│ 2024-01-15   │ $24.99 (Low)│
│ 2024-02-01   │ $34.99 (High)│
│ Current      │ $29.99     │
└──────────────┴────────────┘

Recommendation: Price is near average. Wait for deal if not urgent.
```

### Search Result

```
═══ Search Results: "wireless earbuds" ═══

Page 1 of 5 (48 results)

#1  B08XYZ123  Wireless Earbuds Pro    $29.99  ★★★★☆ (2,847)
#2  B09ABC456  Bluetooth Earbuds Sport $24.99  ★★★★☆ (1,523)
#3  B07DEF789  True Wireless Earbuds   $39.99  ★★★★★ (987)
...
```

## Best Practices

### 数据准确性
- 价格数据每 15 分钟更新
- 销售排名每小时更新
- 历史数据最多保留 2 年

### API 优化
- 批量查询 ASIN 节省 tokens
- 仅请求需要的字段
- 缓存常用查询结果

### 价格追踪
- 设置价格提醒
- 关注历史低价
- 比较多个卖家

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid API Key | Verify key in Keepa dashboard |
| Token limit exceeded | Wait for daily reset or upgrade plan |
| Product not found | Check ASIN and marketplace |
| Rate limit | Slow down requests |

## References

- [Keepa API Documentation](https://keepa.com/#!api)
- [Category Tree](https://keepa.com/#!category)
- [API Examples](https://github.com/keepacom/api)

## Notes

- 需要有效的 Keepa API key
- 免费账户每日 100 tokens
- 数据更新频率：15 分钟
- 支持 8 个亚马逊站点
