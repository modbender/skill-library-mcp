# 去哪儿网API参考文档

## 目录
- [概览](#概览)
- [API认证](#api认证)
- [机票查询API](#机票查询api)
- [酒店查询API](#酒店查询api)
- [景点查询API](#景点查询api)
- [火车票查询API](#火车票查询api)
- [通用参数说明](#通用参数说明)
- [错误码说明](#错误码说明)
- [示例请求](#示例请求)

## 概览

本文档提供去哪儿网开放平台API的参考信息。由于去哪儿网API文档更新频繁，建议访问 http://open.qunar.com/developer/doc 查看最新官方文档。

**注意**：本Skill采用通用API查询框架，支持自定义API端点和参数。使用时请根据实际的去哪儿网API文档填写正确的端点URL和参数格式。

## API认证

去哪儿网API使用API Key进行身份验证。在使用本Skill前，必须先配置凭证：

1. 访问 http://open.qunar.com 注册开发者账号
2. 创建应用，获取API Key
3. 在首次使用Skill时，系统会提示配置凭证
4. 输入获取的API Key即可完成配置

**认证方式**：ApiKey（通过HTTP Header传递）
- Header字段：`Authorization`
- Header值：你的API Key

## 机票查询API

### 功能说明
查询国内/国际航班信息、价格、时刻表等。

### API端点
根据去哪儿网官方文档填写，例如：
- 国内航班查询：`https://flight.qunar.com/api/flight/domestic`
- 国际航班查询：`https://flight.qunar.com/api/flight/international`

（请以实际API文档为准）

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| fromCity | String | 是 | 出发城市三字码或中文名 | "北京" / "BJS" |
| toCity | String | 是 | 到达城市三字码或中文名 | "上海" / "SHA" |
| departDate | String | 是 | 出发日期（YYYY-MM-DD） | "2024-01-15" |
| returnDate | String | 否 | 返回日期（往返票必填） | "2024-01-20" |
| adultNum | Integer | 否 | 成人数量 | 1 |

### 响应示例
```json
{
  "errcode": 0,
  "errmsg": "success",
  "data": {
    "flights": [
      {
        "flightNo": "CA1234",
        "airline": "国航",
        "fromCity": "北京",
        "toCity": "上海",
        "departTime": "08:00",
        "arriveTime": "10:30",
        "price": 680
      }
    ]
  }
}
```

## 酒店查询API

### 功能说明
查询酒店信息、房间价格、设施、评分等。

### API端点
根据去哪儿网官方文档填写，例如：
- 酒店搜索：`https://hotel.qunar.com/api/hotel/search`
- 酒店详情：`https://hotel.qunar.com/api/hotel/detail`

（请以实际API文档为准）

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| city | String | 是 | 城市名称 | "杭州" |
| checkIn | String | 是 | 入住日期（YYYY-MM-DD） | "2024-01-20" |
| checkOut | String | 是 | 退房日期（YYYY-MM-DD） | "2024-01-22" |
| keyword | String | 否 | 搜索关键词（位置、商圈等） | "西湖区" |

### 响应示例
```json
{
  "errcode": 0,
  "errmsg": "success",
  "data": {
    "hotels": [
      {
        "hotelId": "12345",
        "name": "杭州西湖饭店",
        "address": "杭州市西湖区",
        "star": 4,
        "score": 4.5,
        "price": 350
      }
    ]
  }
}
```

## 景点查询API

### 功能说明
查询景点信息、门票价格、开放时间、介绍等。

### API端点
根据去哪儿网官方文档填写，例如：
- 景点搜索：`https://travel.qunar.com/api/scenic/search`
- 景点详情：`https://travel.qunar.com/api/scenic/detail`

（请以实际API文档为准）

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| city | String | 是 | 城市名称 | "三亚" |
| keyword | String | 否 | 景点名称或关键词 | "天涯海角" |
| category | String | 否 | 景点分类 | "自然景观" |

### 响应示例
```json
{
  "errcode": 0,
  "errmsg": "success",
  "data": {
    "scenics": [
      {
        "scenicId": "67890",
        "name": "天涯海角",
        "address": "三亚市天涯区",
        "price": 98,
        "score": 4.7,
        "openTime": "08:00-18:00"
      }
    ]
  }
}
```

## 火车票查询API

### 功能说明
查询火车票信息、余票、价格、时刻表等。

### API端点
根据去哪儿网官方文档填写，例如：
- 火车票查询：`https://train.qunar.com/api/train/search`

（请以实际API文档为准）

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| fromCity | String | 是 | 出发城市 | "北京" |
| toCity | String | 是 | 到达城市 | "上海" |
| departDate | String | 是 | 出发日期（YYYY-MM-DD） | "2024-01-15" |
| seatType | String | 否 | 座位类型 | "二等座" |

### 响应示例
```json
{
  "errcode": 0,
  "errmsg": "success",
  "data": {
    "trains": [
      {
        "trainNo": "G101",
        "fromCity": "北京",
        "toCity": "上海",
        "departTime": "07:00",
        "arriveTime": "12:30",
        "duration": "5h30m",
        "price": 553
      }
    ]
  }
}
```

## 通用参数说明

### 查询类型（query_type）
- `flight`：机票查询
- `hotel`：酒店查询
- `scenic`：景点查询
- `train`：火车票查询

### 输出格式（output_format）
- `list`：列表格式，简洁展示关键信息
- `detail`：详细格式，提供完整信息
- `conversation`：对话格式，交互式查询

### HTTP方法（method）
- `GET`：用于查询类接口
- `POST`：用于复杂查询或数据提交

## 错误码说明

### HTTP状态码
| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应数据 |
| 400 | 请求参数错误 | 检查参数格式和内容 |
| 401 | 未授权 | 检查API Key配置 |
| 403 | 权限不足 | 联系客服申请权限 |
| 429 | 请求频率超限 | 降低请求频率 |
| 500 | 服务器错误 | 稍后重试 |

### 业务错误码
| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 0 | 成功 | 正常处理 |
| 1001 | API Key无效 | 重新配置凭证 |
| 1002 | 参数缺失 | 补充必要参数 |
| 1003 | 参数格式错误 | 检查参数格式 |
| 2001 | 无查询结果 | 调整查询条件 |

## 示例请求

### 示例1：查询北京到上海的机票
```bash
python scripts/qunar_query.py \
  --query_type flight \
  --api_endpoint "https://flight.qunar.com/api/flight/domestic" \
  --api_params '{"fromCity":"北京","toCity":"上海","departDate":"2024-01-15"}' \
  --method POST \
  --output_format list
```

### 示例2：查询杭州的酒店
```bash
python scripts/qunar_query.py \
  --query_type hotel \
  --api_endpoint "https://hotel.qunar.com/api/hotel/search" \
  --api_params '{"city":"杭州","checkIn":"2024-01-20","checkOut":"2024-01-22"}' \
  --method POST \
  --output_format detail
```

### 示例3：查询三亚的景点
```bash
python scripts/qunar_query.py \
  --query_type scenic \
  --api_endpoint "https://travel.qunar.com/api/scenic/search" \
  --api_params '{"city":"三亚"}' \
  --method GET \
  --output_format conversation
```

### 示例4：查询北京到上海的火车票
```bash
python scripts/qunar_query.py \
  --query_type train \
  --api_endpoint "https://train.qunar.com/api/train/search" \
  --api_params '{"fromCity":"北京","toCity":"上海","departDate":"2024-01-15"}' \
  --method GET \
  --output_format list
```

## 注意事项

1. **API端点URL**：本文档中的端点URL仅为示例，请根据去哪儿网最新API文档填写正确的URL
2. **参数格式**：确保参数名称和格式与实际API文档一致
3. **API Key安全**：请妥善保管API Key，不要泄露给第三方
4. **请求频率**：遵守去哪儿网API的调用频率限制，避免超限
5. **数据准确性**：API返回的数据仅供参考，实际预订时请以官网为准
6. **文档更新**：去哪儿网API可能随时更新，建议定期查看官方文档

## 获取帮助

如有问题，请访问：
- 去哪儿网开放平台：http://open.qunar.com
- 开发者社区：http://open.qunar.com/forum
- 客服支持：根据官方文档提供的联系方式
