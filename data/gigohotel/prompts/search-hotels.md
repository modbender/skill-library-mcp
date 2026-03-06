# 酒店搜索提示词

当用户表达酒店搜索意图时，调用 searchHotels 工具。

## 触发场景
- 用户想找酒店
- 用户提到地点+住宿需求
- 用户询问某地酒店推荐

## 参数提取规则

从用户输入中提取以下结构化参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| place | 地点名称 | 北京、王府井、外滩 |
| placeType | 地点类型 | city/scenic/business |
| checkInDate | 入住日期 | 2024-03-01 |
| stayNights | 入住晚数 | 2 |
| adultCount | 成人数 | 2 |
| childCount | 儿童数 | 0 |
| roomCount | 房间数 | 1 |
| starRatings | 星级范围 | [4,5] |
| priceMin | 最低价格 | 500 |
| priceMax | 最高价格 | 1500 |
| originQuery | 搜索意图摘要 | 见下方说明 |

## originQuery 处理要求

**重要**：originQuery 不是用户原始输入，而是经过处理的搜索意图摘要。

代理必须：
1. 从用户输入中提取搜索意图
2. 移除任何个人身份信息（姓名、电话、邮箱、身份证等）
3. 仅保留地点、日期、条件等搜索相关信息

示例：
- 用户输入："我叫张三，想订北京的五星酒店"
- originQuery 应为："北京五星酒店"（移除姓名）

## 调用示例

用户："帮我找上海外滩附近的酒店，3月1日入住2晚，预算1000以内"

```json
{
  "place": "外滩",
  "placeType": "scenic",
  "checkInDate": "2024-03-01",
  "stayNights": 2,
  "priceMax": 1000,
  "originQuery": "上海外滩酒店，3月1日入住2晚，预算1000以内"
}