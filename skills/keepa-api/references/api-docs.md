# Keepa API 参考文档

## API 认证

Keepa API 使用 API Key 进行认证，所有请求都需要在 URL 参数中包含 `key` 参数。

```
https://api.keepa.com/product?key=YOUR_API_KEY&domain=1&asin=B08XYZ123
```

### 获取 API Key

1. 访问 [Keepa API](https://keepa.com/#!api)
2. 注册账户或登录
3. 进入 Account → API Key
4. 复制你的 API key

## API 端点

### 1. Product (产品查询)

查询单个或多个 ASIN 的产品信息。

**请求**:
```
GET /product
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | API key |
| domain | int | 是 | 亚马逊域名 ID (1=US, 3=UK, 4=DE, 5=FR, 6=JP, 7=CA, 9=AU, 10=IN) |
| asin | string | 是 | ASIN，支持逗号分隔多个 |
| history | int | 否 | 包含历史数据 (1/0) |
| rating | int | 否 | 包含评分 (1/0) |
| updates | int | 否 | 仅获取更新的数据 (1/0) |

**响应示例**:
```json
{
  "products": [
    {
      "asin": "B08XYZ123",
      "title": "Wireless Bluetooth Earbuds",
      "brand": "SoundTech",
      "category": "Electronics",
      "price": 2999,
      "priceNew": 2799,
      "priceUsed": 2299,
      "rating": 4.5,
      "ratingCount": 2847,
      "rank": 1234,
      "salesRank": [
        {"timestamp": 1709251200000, "rank": 1234}
      ],
      "priceHistory": [
        {"timestamp": 1709251200000, "price": 2999}
      ]
    }
  ]
}
```

### 2. Search (搜索)

通过关键词搜索产品。

**请求**:
```
GET /search
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | API key |
| domain | int | 是 | 亚马逊域名 ID |
| query | string | 是 | 搜索关键词 |
| category | int | 否 | 类目 ID |
| page | int | 否 | 页码 |

**响应示例**:
```json
{
  "products": [
    {
      "asin": "B08XYZ123",
      "title": "Wireless Earbuds",
      "price": 2999,
      "rating": 4.5,
      "ratingCount": 2847
    }
  ],
  "totalResults": 48,
  "currentPage": 1
}
```

### 3. Best Sellers (热销榜)

获取类目的热销榜。

**请求**:
```
GET /bestsellers
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | API key |
| domain | int | 是 | 亚马逊域名 ID |
| categoryId | int | 是 | 类目 ID |
| page | int | 否 | 页码 |

### 4. Offers (报价列表)

获取产品的所有卖家报价。

**请求**:
```
GET /offer
```

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | API key |
| domain | int | 是 | 亚马逊域名 ID |
| asin | string | 是 | ASIN |

## Amazon 域名映射

| 域名 ID | 国家 | Amazon 网站 |
|--------|------|-------------|
| 1 | US | amazon.com |
| 3 | UK | amazon.co.uk |
| 4 | DE | amazon.de |
| 5 | FR | amazon.fr |
| 6 | JP | amazon.co.jp |
| 7 | CA | amazon.ca |
| 9 | AU | amazon.com.au |
| 10 | IN | amazon.in |

## 类目 ID 参考

| 类目 | ID |
|------|-----|
| Electronics | 172282 |
| Computers | 541966 |
| Home & Kitchen | 1055398 |
| Beauty & Personal Care | 3760911 |
| Sports & Outdoors | 3375251 |
| Toys & Games | 165793011 |
| Clothing & Accessories | 7141123011 |
| Books | 283155 |
| Office Products | 1064954 |
| Garden & Outdoor | 2972638011 |

## 费率限制

### Token 系统

Keepa API 使用 Token 计费系统：

| 请求类型 | Token 消耗 |
|----------|-----------|
| Product (单个 ASIN) | 1-2 tokens |
| Product (批量 10 个 ASIN) | 10-20 tokens |
| Search | 1 token |
| Best Sellers | 1 token |
| Offers | 1-3 tokens |

### 套餐限制

| 套餐 | 价格 | Tokens/天 |
|------|------|-----------|
| Free | $0 | 100 |
| Basic | €9/mo | 100,000 |
| Pro | €19/mo | 500,000 |
| Ultra | €49/mo | 2,000,000 |

## 数据格式说明

### 价格格式

Keepa API 返回的价格是以分为单位的整数：
- `2999` = $29.99
- `0` = Free
- `null` = 无数据

### 时间戳格式

所有时间戳使用毫秒级 Unix 时间戳：
- `1709251200000` = 2024-03-01 00:00:00 UTC

### 历史数据

价格历史和排名历史以数组形式返回，每个元素包含：
- `timestamp`: 时间戳（毫秒）
- `value`: 值（价格或排名）

## cURL 示例

### 查询单个 ASIN

```bash
curl -s "https://api.keepa.com/product?key=YOUR_API_KEY&domain=1&asin=B08XYZ123&history=1"
```

### 批量查询 ASIN

```bash
curl -s "https://api.keepa.com/product?key=YOUR_API_KEY&domain=1&asin=B08XYZ123,B09ABC456,B07DEF789"
```

### 搜索产品

```bash
curl -s "https://api.keepa.com/search?key=YOUR_API_KEY&domain=1&query=wireless+earbuds"
```

### 获取热销榜

```bash
curl -s "https://api.keepa.com/bestsellers?key=YOUR_API_KEY&domain=1&categoryId=172282"
```

## 错误处理

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 403 | API key 无效 |
| 429 | 超过速率限制 |
| 503 | 服务暂时不可用 |

错误响应示例:
```json
{
  "error": true,
  "error_message": "Invalid API key"
}
```

## 最佳实践

1. **批量查询**: 一次性查询多个 ASIN 节省 tokens
2. **缓存数据**: 避免重复查询相同数据
3. **增量更新**: 使用 `updates=1` 参数获取更新数据
4. **错误重试**: 503 错误可以稍后重试
5. **合理设置天数**: 只请求需要的历史数据范围
