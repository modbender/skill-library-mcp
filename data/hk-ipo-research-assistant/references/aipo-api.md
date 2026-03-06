# AiPO API 文档

数据源：https://aipo.myiqdii.com

## 概述

AiPO 数据网是港股打新的数据宝藏，提供：
- 孖展数据（各券商孖展资金）
- 评级数据（各机构评级评分）
- 暗盘数据（暗盘价格、成交）
- IPO 详情（保荐人、基石投资者等）
- 配售结果（中签率、申购人数）
- 保荐人历史项目

## 验证机制

所有 API 都需要 `RequestVerificationToken` 头。获取方式：

```python
resp = client.get("https://aipo.myiqdii.com/aipo/newstock")
token = re.search(r'name="__RequestVerificationToken"[^>]+value="([^"]+)"', resp.text).group(1)
headers = {"RequestVerificationToken": token, "Referer": "https://aipo.myiqdii.com/aipo/newstock"}
```

## API 列表

### 1. 评级列表 `/Home/GetNewStockRatingList`

获取新股综合评级列表。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sector | string | 否 | 板块过滤: ""=全部, "主板", "创业板" |
| pageIndex | int | 是 | 页码，从1开始 |
| pageSize | int | 是 | 每页数量 |

**返回示例**:
```json
{
  "result": 1,
  "data": {
    "totalRows": 998,
    "dataList": [
      {
        "symbol": "00325",
        "shortName": "布魯可",
        "sector": "主板",
        "number": 2,          // 评分家数
        "avgScore": 95.0,     // 综合评分 (0-100)
        "maxScore": 95.0,
        "minScore": 95.0
      }
    ]
  }
}
```

### 2. 评级详情 `/Home/GetAgencyRatingInfo`

获取单只新股各机构评级详情。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码，带 E 前缀 (如 "E00325") |

**返回示例**:
```json
{
  "result": 1,
  "msg": "{\"data\":[{\"ratingagency\":\"輝立證券\",\"rating\":\"孖展認購\",\"score\":95.0,\"ratingurl\":\"...\"}]}"
}
```

注意：`msg` 字段是 JSON 字符串，需要二次解析。

### 3. IPO 简况 `/Home/NewStockBrief`

获取新股基本信息，包括保荐人、发行价、市值等。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码，带 E 前缀 |

**返回示例** (`msg` 解析后):
```json
{
  "data": {
    "institutioninfo": {
      "principaloffice": "中國上海市...",
      "registrars": "香港中央證券登記有限公司",
      "chairman": "朱偉松",
      "secretary": "朱元成,余詠詩",
      "principalactivities": "..."
    },
    "issuanceinfo": {
      "industry": "玩具及消閑",
      "sponsors": "高盛(亞洲)有限責任公司,華泰金融控股(香港)有限公司",
      "bookrunners": "高盛(亞洲)有限責任公司,華泰金融控股(香港)有限公司",
      "leadagent": "...",
      "coordinator": "...",
      "ipoprice": {"ceiling": "60.350", "floor": "55.650"},
      "ipopricing": "60.350",
      "ipodate": {"start": "2024-12-31", "end": "2025-01-07"},
      "listeddate": "2025-01-10",
      "marketcap": "147.91億",
      "pe": -64.50,
      "minimumcapital": 18287.59,
      "shares": 300
    }
  }
}
```

### 4. 基石投资者 `/Home/GetInvestorInfoByCode`

获取基石投资者列表。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码，带 E 前缀 |

**返回示例**:
```json
{
  "result": 1,
  "data": [
    {
      "investorName": "UBS Asset Management (Singapore) Ltd.",
      "shareholding": 2574600.0,
      "shareholding_percentage": 9.28,
      "releaseDate": "2025-07-10T00:00:00",
      "marketValue": 167220270.0,
      "profile": "UBS AM Singapore為..."
    }
  ]
}
```

### 5. 配售结果 `/Home/GetPlacingResult`

获取配售结果，包括申购人数、中签率等。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码，带 E 前缀 |

**返回示例** (`msg` 解析后):
```json
{
  "data": {
    "name": "布魯可",
    "num": "126841",        // 申购人数
    "lot": "300",           // 一手股数
    "sz": "18105.0000",     // 入场费
    "rate": "4020/1",       // 中签率描述
    "claw_back": "43.5000", // 回拨比例%
    "list": [               // 分组配售明细
      ["300", "37497", null, "0.1000", "37497份申請中的3750份將獲分配300股股份", "0", "18287.5900", null]
    ]
  }
}
```

### 6. 保荐人历史 `/Home/SpoHisProjects`

获取保荐人/承销商历史项目表现。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| market | string | 是 | 市场，固定 "mkt_hk" |
| sponsor | string | 是 | 保荐人名称 |
| type | int | 是 | 0=保荐人, 2=账簿管理人, 5=承销团 |
| pageIndex | int | 是 | 页码 |
| pageSize | int | 是 | 每页数量 |
| order | string | 否 | 排序字段 |
| sort | string | 否 | 排序方向 (asc/desc) |

**返回示例**:
```json
{
  "result": 1,
  "data": {
    "totalRows": 114,
    "dataList": [
      {
        "symbol": "E02714",
        "shortName": "牧原股份",
        "listedDate": "2026-02-06T00:00:00",
        "grayPriceChg": 5.13,     // 暗盘涨跌幅%
        "firstDayChg": 3.9,       // 首日涨跌幅%
        "zdf": 4.72,              // 至今涨跌幅%
        "nowprice": 40.84         // 当前价格
      }
    ]
  }
}
```

### 7. 暗盘数据 `/Home/GetGreyList`

获取暗盘交易数据列表。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| symbol | string | 否 | 股票代码（不带E） |
| sector | string | 否 | 板块过滤 |
| pageIndex | int | 是 | 页码 |
| pageSize | int | 是 | 每页数量 |
| orderField | string | 否 | 排序字段 (resultDate, grayPriceChg) |
| orderBy | string | 否 | 排序方向 (desc, asc) |

**返回示例**:
```json
{
  "result": 1,
  "data": {
    "dataList": [
      {
        "symbol": "00325",
        "shortName": "布魯可",
        "ipoPricing": 60.35,
        "grayPrice": 109.0,
        "grayPriceChg": 80.6,
        "grayZl": 1234567,       // 暗盘成交量
        "grayZe": 123456789,     // 暗盘成交额
        "resultDate": "2025-01-09T00:00:00",
        "listedDate": "2025-01-10T00:00:00"
      }
    ]
  }
}
```

### 8. 孖展列表 `/Home/GetMarginList`

获取当前招股中 IPO 的孖展数据。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sector | string | 否 | 板块过滤 |
| pageIndex | int | 是 | 页码 |
| pageSize | int | 是 | 每页数量 |

### 9. 孖展详情 `/Home/GetMarginInfo`

获取单只股票各券商孖展明细。

**方法**: GET

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| stockCode | string | 是 | 股票代码，带 E 前缀 |

## CLI 使用示例

```bash
# 评级列表
hkipo aipo rating-list --limit 10

# 单只评级详情
hkipo aipo rating 00325

# IPO 简况
hkipo aipo brief 00325

# 基石投资者
hkipo aipo cornerstone 00325

# 配售结果
hkipo aipo placing 00325

# 保荐人历史
hkipo aipo sponsor-history "高盛(亞洲)有限責任公司" --limit 20

# 暗盘数据
hkipo aipo grey-list --limit 10
```

## Python 使用示例

```python
from hkipo.aipo import (
    fetch_rating_list,
    fetch_rating_detail,
    fetch_ipo_brief,
    fetch_cornerstone_investors,
    fetch_placing_result,
    fetch_sponsor_history,
    fetch_grey_list,
)

# 评级列表
ratings = fetch_rating_list(sector="主板", page_size=20)

# 单只评级
detail = fetch_rating_detail("00325")
for r in detail:
    print(f"{r.agency_name}: {r.score}分 - {r.rating}")

# IPO 简况
brief = fetch_ipo_brief("00325")
print(f"保荐人: {brief['sponsors']}")
print(f"市值: {brief['market_cap']}")

# 基石投资者
investors = fetch_cornerstone_investors("00325")
for i in investors:
    print(f"{i.name}: {i.shareholding_pct}%")

# 保荐人历史
history = fetch_sponsor_history("高盛(亞洲)有限責任公司", sponsor_type=0)
for h in history:
    print(f"{h['code']} {h['name']}: 首日{h['first_day_change_pct']}%")
```

## 注意事项

1. **Token 过期**：Token 有时效性，长时间请求可能需要重新获取
2. **股票代码格式**：部分 API 需要 `E` 前缀（如 E00325），部分不需要
3. **JSON 嵌套**：部分 API 的 `msg` 字段是 JSON 字符串，需要二次解析
4. **数据延迟**：数据可能有 15-30 分钟延迟
5. **Rate Limit**：暂未发现明确限制，但建议控制请求频率
