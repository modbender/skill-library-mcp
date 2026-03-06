---
slug: aigo-hotel
name: AIGo Hotel Search
version: 1.0.9
description: 智能酒店搜索，支持地点、日期、星级、预算筛选
author: your-name
tags:
  - hotel
  - travel
  - booking
---

# AIGo Hotel Search

## Description
基于 AIGoHotel MCP 的智能酒店搜索技能，开箱即用。

## Credentials
本技能使用 AIGoHotel 官方提供的公共 API Key，无需用户配置。

## Public API Key Declaration
- 内置 Key (`mcp_7d31559a07884aa99be1fa22cdbe828a`) 是 AIGoHotel 官方提供的公共访问密钥
- 此 Key 专为社区开发者设计，非机密凭证
- 公共 Key 有速率限制，如需更高配额请申请专属 Key
- 申请地址: https://mcp.aigohotel.com/apply

## MCP Configuration
```json
{
  "mcpServers": {
    "aigohotel-mcp": {
      "url": "https://mcp.aigohotel.com/mcp",
      "type": "http",
      "headers": {
        "Authorization": "Bearer mcp_7d31559a07884aa99be1fa22cdbe828a"
      }
    }
  }
}
```
## Data Transmission Policy

### 允许传输
仅限酒店搜索结构化参数：
- 地点、日期、人数、星级、预算、标签

### 禁止传输
- 用户个人信息（姓名、电话、邮箱）
- 本地文件、系统信息
- 无关的自由文本内容

### originQuery 处理规则
originQuery 参数仅应包含酒店搜索意图，代理必须：
- 提取搜索相关信息（地点、日期、条件）
- 移除任何个人身份信息 (PII)
- 不得直接传递用户原始输入

代理调用工具前应过滤敏感信息。

### 安全责任声明
本技能为指令型技能，不包含可执行代码。数据过滤由以下层级负责：
1. **代理运行时**：负责执行 PII 过滤指令
2. **MCP 服务端**：对请求进行安全校验
3. **用户**：避免在查询中输入敏感个人信息

本技能已尽合理告知义务，实际过滤执行由代理平台保障。

## Tools
- `searchHotels`: 搜索酒店
- `getHotelDetail`: 获取房型价格
- `getHotelSearchTags`: 获取筛选标签

## Usage Examples
- "找北京五星酒店"
- "查看北京天伦王朝酒店的房型和价格"
- "上海1000元以内有泳池的酒店"