---
name: M5Stack Assistant Skill
description: "name: m5stack-assistant description:
  解决M5Stack相关的所有问题，包括产品查询、规格参数、Arduino/UIFlow/ESP-IDF编程、技术支持等。通过M5Stack官方MCP服务检\
  索官方文档、产品规格、接口和示例，根据官方信息完成用户需求，过程中主动查询不清楚的内容。适用于：M5Stack全系列产品咨询、技术规格查询、代码编写、AP\
  I查询、示例..."
---


---
name: m5stack-assistant
description: 解决M5Stack相关的所有问题，包括产品查询、规格参数、Arduino/UIFlow/ESP-IDF编程、技术支持等。通过M5Stack官方MCP服务检索官方文档、产品规格、接口和示例，根据官方信息完成用户需求，过程中主动查询不清楚的内容。适用于：M5Stack全系列产品咨询、技术规格查询、代码编写、API查询、示例查找、故障排除等任务。
---

# M5Stack Assistant Skill

通过M5Stack官方MCP服务解决所有M5Stack相关问题。

## 核心流程

### 1. 理解需求
- 明确用户要做什么
- 判断问题类型：产品咨询 / 规格查询 / 编程问题 / 技术支持 / 故障排除
- 确定涉及的M5Stack设备型号或产品系列
- 识别需要的功能模块

### 2. 问题类型分类与查询策略

#### 产品咨询类
**当用户询问：**
- 产品功能、特性、应用场景
- 产品对比、选型建议
- 包装内容、配件信息

**查询方式：**
- 使用 `filter_type: "product"` 查询产品文档
- 查询数量 `num: 2-3` 获取完整信息

#### 规格参数类
**当用户询问：**
- 技术规格、电气特性
- 尺寸、重量、SKU
- 功耗、热设计、工作温度
- 芯片型号、内存配置、接口定义

**查询方式：**
- 使用 `filter_type: "product"` 查询产品文档
- 如果涉及芯片，考虑设置 `is_chip: true`
- 查询数量 `num: 1-2`

#### 编程开发类
**当用户询问：**
- Arduino / UIFlow / ESP-IDF 编程
- API使用、示例代码
- 库依赖、配置要求
- 引脚定义、硬件连接

**查询方式：**
- 根据开发环境选择 `filter_type`：
  - Arduino → `"arduino"`
  - UIFlow → `"uiflow"`
  - ESP-IDF → `"esp-idf"`
- 查询数量 `num: 2-3`

#### 技术支持与故障排除
**当用户询问：**
- 设备无法正常工作
- 连接问题、通信错误
- 常见问题解答 (FAQ)
- 固件更新、恢复出厂设置

**查询方式：**
- 使用 `filter_type: "product"` 或 `"program"`
- 搜索相关故障排除文档
- 查询数量 `num: 2-3`

### 3. 查询MCP服务
使用M5Stack官方MCP服务检索：
- 产品规格、技术参数
- 相关API文档
- 官方示例代码
- 设备特定的配置和限制
- 故障排除指南

使用提供的Node.js MCP客户端脚本进行查询，详见下方"工具脚本"部分。

### 4. 迭代查询
- 当遇到不清楚的内容时，主动进行进一步查询
- 不要假设不确定的产品规格或API用法
- 查询相关的依赖、兼容性和配置要求

### 5. 编程类任务额外步骤（如适用）

#### 生成代码
- 基于官方示例和文档生成代码
- 保持代码风格与官方示例一致
- 添加必要的注释

#### 代码复查
生成代码后必须进行以下检查：
- 语法正确性
- API调用是否正确
- 引脚配置是否合理
- 是否有遗漏的依赖
- 是否有常见的低级错误（如拼写错误、缺少分号等）
- 代码逻辑是否完整

#### 提供说明
- 解释代码的主要功能
- 说明需要安装的库
- 提供上传和测试的建议

### 6. 整理与回复
- 基于查询到的官方信息整理答案
- 提供准确的规格参数、产品特性
- 引用官方文档来源（如适用）
- 提供清晰的操作步骤或使用建议

## MCP服务使用

### 服务器信息
- **端点**: `https://mcp.m5stack.com/sse`
- **协议**: SSE (Server-Sent Events) + JSON-RPC over HTTPS

### 连接流程
1. **建立SSE连接**: GET `https://mcp.m5stack.com/sse`
2. **获取endpoint**: 接收 `event: endpoint` 事件，获取 `/messages?session_id=xxx`
3. **保持SSE连接**: 持续监听，JSON-RPC响应会通过SSE推送
4. **发送JSON-RPC请求**: POST 到返回的 `/messages?session_id=xxx` 端点
5. **接收响应**: 通过SSE连接接收 `event: message` 事件中的JSON-RPC响应

### 可用工具
MCP 服务器当前提供以下工具：

#### knowledge_search
从M5Stack产品知识库中检索相关信息。

**核心功能：**
- 查询M5Stack产品的技术规格、参数、功能特性
- 检索产品兼容性、连接方式、引脚定义
- 获取编程API、代码示例、固件配置信息
- 查找芯片数据手册和技术细节
- 故障排除和常见问题解答

**必须触发此工具的场景：**
当用户询问涉及以下任何内容时，务必调用此工具：
1. M5Stack品牌及产品（Core、Atom、StickC、Paper、Dial、Capsule、加速卡等系列）
2. 硬件技术（模块、传感器、执行器、连接器、引脚、GPIO、接口、通讯协议如I2C/SPI/UART）
3. 编程开发（API、UIFlow、Arduino、MicroPython、ESP-IDF、固件、库函数、代码示例）
4. 技术参数（电气特性、尺寸、重量、SKU、兼容性、供电、功耗、热设计、性能指标）
5. 芯片相关（ESP32、芯片型号、数据手册、寄存器、技术规格）
6. 产品对比、选型建议、功能差异
7. 常见嵌入式问题解答（FAQ）、故障排除

**参数使用指南：**
- `query`: 用清晰的关键词描述查询内容，必要时结合上下文重构查询语句
- `num`: 根据问题涉及的实体数量设置（默认1）
  * 询问单个产品/功能 → 1
  * 对比2个产品 → 2
  * 询问"有哪些"/"多少种"/"所有" → 3
  * 多步骤操作或复杂问题 → 对应步骤数（最多5）
- `is_chip`: 判断是否需要查询芯片数据手册
  * 明确提到芯片型号、数据手册、寄存器 → true
  * 询问底层技术原理、电气特性 → true
  * 仅询问产品使用、编程API → false
- `filter_type`: 指定查询的知识库类型
  * "product": 查询所有产品文档（包括在售和EOL产品）
  * "product_no_eol": 查询在售产品文档
  * "program": 查询全品类编程相关文档（包括Arduino、UIFlow、ESP-IDF）
  * "arduino": 专门查询Arduino开发相关文档
  * "uiflow": 专门查询UIFlow开发相关文档
  * "esp-idf": 专门查询ESP-IDF开发相关文档
  * "esphome": 查询ESPHome官方文档

### 工具脚本

skill提供以下Node.js脚本（位于 `scripts/` 目录）：

1. **mcp.js** - 简单、好用的MCP客户端
   - 提供 `mcpSearch(query, options)` 函数
   - 使用方式：
     ```javascript
     const { mcpSearch } = require('./mcp.js');
     const result = await mcpSearch('M5Stack CoreS3', { num: 1 });
     ```

## 在Skill中使用MCP客户端

当需要查询M5Stack文档或示例时：

1. 使用 `scripts/mcp.js` 的 `mcpSearch()` 函数查询
2. 或者直接访问M5Stack官方文档站点: https://docs.m5stack.com

## 关键注意事项

1. **始终基于官方资源** - 优先使用M5Stack官方文档和示例
2. **主动查询** - 不要猜测，有疑问就查
3. **严格复查** - 代码生成后必须复查
4. **准确理解问题** - 先明确用户需要什么类型的信息
5. **合理选择filter_type** - 根据问题类型选择合适的文档类型
6. **设备兼容性** - 注意不同M5Stack设备的差异
7. **库依赖** - 明确列出所需的开发库
8. **MCP服务状态** - 如果MCP服务不可用，降级使用官方文档站点
