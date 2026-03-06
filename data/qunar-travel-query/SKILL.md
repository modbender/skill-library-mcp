---
name: qunar-travel-query
description: 提供去哪儿网旅游信息查询能力；当用户需要查询机票、酒店、景点门票或火车票信息时使用
---

# 去哪儿网旅游查询 Skill

## 任务目标
- 本 Skill 用于：通过去哪儿网开放平台API查询旅游相关信息
- 能力包含：机票查询、酒店查询、景点查询、火车票查询
- 触发条件：用户提出查询航班、酒店、景点或火车票的需求时

## 前置准备

### 凭证配置
首次使用时需要配置去哪儿网API Key凭证。当智能体检测到未配置凭证时，会自动触发凭证配置流程：
- 凭证名称：qunar_api_key
- 所需信息：去哪儿网开放平台API Key
- 获取方式：访问 http://open.qunar.com 注册开发者账号，创建应用获取API Key

### API文档参考
在使用前，建议阅读 [references/api_reference.md](references/api_reference.md) 了解各类查询的API端点和参数格式。

## 操作步骤

### 标准流程

1. **意图识别**
   - 智能体分析用户查询意图，识别查询类型（机票/酒店/景点/火车票）
   - 识别关键参数：出发地、目的地、日期、人数等
   - 确认用户期望的输出格式（列表/详细/对话式）

2. **参数收集与验证**
   - 根据查询类型收集必要参数：
     - 机票：出发城市、到达城市、出发日期、返回日期（可选）
     - 酒店：城市名称、入住日期、退房日期
     - 景点：城市名称、景点名称（可选）
     - 火车票：出发城市、到达城市、出发日期
   - 智能体与用户确认缺失的关键参数

3. **API查询**
   - 调用 `scripts/qunar_query.py` 执行查询
   - 脚本参数：
     - `query_type`: 查询类型（flight/hotel/scenic/train）
     - `api_endpoint`: API端点URL（根据 [references/api_reference.md](references/api_reference.md) 确定）
     - `api_params`: 查询参数字典
     - `method`: HTTP方法（GET/POST，默认POST）
     - `output_format`: 输出格式（list/detail/conversation）

4. **结果处理与展示**
   - 智能体根据API返回数据进行解析
   - 根据用户选择的输出格式生成结果：
     - **列表格式**：简洁展示关键信息（价格、时间、排名）
     - **详细格式**：提供完整信息和分析建议
     - **对话格式**：交互式查询，逐步细化需求

5. **推荐与建议（可选）**
   - 智能体基于查询结果提供个性化推荐
   - 分析价格趋势、最佳选择、注意事项等

### 可选分支

- **当查询失败**：检查API Key配置、网络连接、参数格式，向用户说明错误原因
- **当需要更换API Key**：指导用户重新配置凭证
- **当查询结果为空**：建议用户调整查询参数或查询条件

## 资源索引

- **必要脚本**：见 [scripts/qunar_query.py](scripts/qunar_query.py)（用途：统一的API查询接口，处理HTTP请求、鉴权、错误处理）
- **API参考**：见 [references/api_reference.md](references/api_reference.md)（用途：提供去哪儿网各类API的端点、参数说明和示例）

## 使用示例

### 示例1：机票查询
- **功能说明**：查询北京到上海的航班信息
- **执行方式**：智能体 + 脚本
- **关键步骤**：
  1. 智能体识别用户意图（机票查询）
  2. 收集参数：出发地="北京"，目的地="上海"，出发日期="2024-01-15"
  3. 调用脚本：`python scripts/qunar_query.py --query_type flight --api_endpoint "<机票API端点>" --api_params '{"fromCity":"北京","toCity":"上海","departDate":"2024-01-15"}' --output_format list`
  4. 智能体解析结果，生成航班列表

### 示例2：酒店推荐
- **功能说明**：推荐杭州高性价比酒店
- **执行方式**：智能体 + 脚本
- **关键步骤**：
  1. 智能体识别用户意图（酒店查询）
  2. 收集参数：城市="杭州"，入住日期="2024-01-20"，退房日期="2024-01-22"
  3. 调用脚本：`python scripts/qunar_query.py --query_type hotel --api_endpoint "<酒店API端点>" --api_params '{"city":"杭州","checkIn":"2024-01-20","checkOut":"2024-01-22"}' --output_format detail`
  4. 智能体分析价格、评分、位置，提供推荐建议

### 示例3：景点门票查询
- **功能说明**：查询三亚热门景点和门票价格
- **执行方式**：智能体 + 脚本
- **关键步骤**：
  1. 智能体识别用户意图（景点查询）
  2. 收集参数：城市="三亚"
  3. 调用脚本：`python scripts/qunar_query.py --query_type scenic --api_endpoint "<景点API端点>" --api_params '{"city":"三亚"}' --output_format conversation`
  4. 智能体以对话方式逐步介绍景点信息

## 注意事项

- **首次使用**：必须先配置API Key凭证，否则查询会失败
- **API端点**：用户需要根据 [references/api_reference.md](references/api_reference.md) 提供正确的API端点
- **参数格式**：确保查询参数符合去哪儿网API规范
- **错误处理**：脚本会返回详细的错误信息，智能体会根据错误信息提供解决方案
- **输出格式**：根据用户需求选择合适的输出格式，智能体会相应调整展示方式
- **安全提示**：API Key仅保存在当前环境，不会泄露给第三方

## 常见问题

**Q: 如何获取去哪儿网API Key？**
A: 访问 http://open.qunar.com 注册开发者账号，创建应用后即可获得API Key。

**Q: 查询失败怎么办？**
A: 检查以下几点：1) API Key是否正确配置；2) API端点URL是否正确；3) 查询参数格式是否符合要求；4) 网络连接是否正常。

**Q: 如何更换API Key？**
A: 智能体可以引导你重新配置凭证，或者在系统设置中更新API Key。

**Q: 支持哪些查询类型？**
A: 目前支持机票查询、酒店查询、景点查询、火车票查询。
