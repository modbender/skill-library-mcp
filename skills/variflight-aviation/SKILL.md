---
name: variflight-aviation
description: 飞常准航班信息查询 - 实时航班动态、航线搜索、舒适度评估、机场天气、飞机追踪
version: 1.0.0
author: lixiao
license: MIT

metadata:
  openclaw:
    emoji: "✈️"
    category: "travel"
    tags: ["flight", "aviation", "travel", "weather", "transport", "mcp", "variflight"]

    env:
      - X_VARIFLIGHT_KEY
      - VARIFLIGHT_API_KEY

    install:
      npm: "@variflight-ai/variflight-mcp"

    os:
      - darwin
      - linux
      - win32

    permissions:
      - network
      - env-read
      - file-read

    requirements: |
      系统要求：Node.js >= 18.0.0，npm >= 9.0.0

      配置要求：
      1. 注册 https://mcp.variflight.com/
      2. 创建 API Key
      3. 设置环境变量 X_VARIFLIGHT_KEY

      技术说明：使用 stdio 模式与 MCP 服务器通信
---

## 功能概述

本 Skill 通过飞常准 MCP 服务器提供全球航班信息查询服务，采用**按需启动**架构：

1. 每次调用命令时自动启动 MCP 服务器
2. 执行查询操作
3. 完成后自动关闭 MCP 服务器，释放资源

## 配置说明

### 方法 1：环境变量（推荐）

**注意**：Variflight 官方使用 `X_VARIFLIGHT_KEY`

```bash
export X_VARIFLIGHT_KEY="your_api_key_here"
```

或使用兼容变量名：
```bash
export VARIFLIGHT_API_KEY="your_api_key_here"
```

### 方法 2：本地配置文件

创建 `config.local.json`（已加入 .gitignore）：

```json
{
  "apiKey": "your_api_key_here"
}
```

⚠️ 注意：请勿将包含真实 API Key 的 config.local.json 提交到 Git！

## 可用命令

### 1. search - 航线搜索

```bash
@variflight-aviation search <dep> <arr> <date>
```

按出发地、目的地、日期搜索航班。

**参数：**
- `dep`: 出发机场 IATA 代码（如 PEK）
- `arr`: 到达机场 IATA 代码（如 SHA）
- `date`: 日期，格式 YYYY-MM-DD

**示例：**
```bash
@variflight-aviation search PEK SHA 2026-02-20
```

### 2. info - 航班号查询

```bash
@variflight-aviation info <fnum> <date>
```

按航班号查询详细信息。

**参数：**
- `fnum`: 航班号（如 MU2157）
- `date`: 日期，格式 YYYY-MM-DD

**示例：**
```bash
@variflight-aviation info HU7601 2026-02-20
```

### 3. comfort - 舒适度指数

```bash
@variflight-aviation comfort <fnum> <date>
```

获取航班舒适度评估，包括准点率、机型评分等。

**示例：**
```bash
@variflight-aviation comfort CA1501 2026-02-20
```

### 4. weather - 机场天气

```bash
@variflight-aviation weather <airport>
```

查询机场未来3天天气预报。

**参数：**
- `airport`: 机场 IATA 代码（如 PEK）

**示例：**
```bash
@variflight-aviation weather PEK
```

### 5. transfer - 中转方案

```bash
@variflight-aviation transfer <depcity> <arrcity> <date>
```

查询最优中转方案。

**参数：**
- `depcity`: 出发城市代码（如 BJS）
- `arrcity`: 到达城市代码（如 SHA）
- `date`: 日期，格式 YYYY-MM-DD

**示例：**
```bash
@variflight-aviation transfer BJS SHA 2026-02-20
```

### 6. track - 飞机追踪

```bash
@variflight-aviation track <anum>
```

实时追踪飞机位置。

**参数：**
- `anum`: 飞机注册号（如 B-308M）

**示例：**
```bash
@variflight-aviation track B-308M
```

## 数据格式说明

### 机场代码（IATA）
- PEK: 北京首都
- PKX: 北京大兴
- SHA: 上海虹桥
- PVG: 上海浦东
- CAN: 广州白云
- SZX: 深圳宝安
- CTU: 成都天府
- HGH: 杭州萧山
- XIY: 西安咸阳
- CKG: 重庆江北

### 城市代码
- BJS: 北京（含 PEK/PKX）
- SHA: 上海（含 SHA/PVG）
- CAN: 广州
- SZX: 深圳

### 日期格式
- 标准格式：YYYY-MM-DD
- 示例：2026-02-20

## 返回数据示例

### 航班搜索返回
```json
{
  "code": 200,
  "message": "Success",
  "data": [
    {
      "FlightNo": "HU7601",
      "FlightCompany": "海南航空股份有限公司",
      "FlightDepcode": "PEK",
      "FlightArrcode": "SHA",
      "FlightDeptimePlanDate": "2026-02-20 07:25:00",
      "FlightArrtimePlanDate": "2026-02-20 09:35:00",
      "FlightState": "计划",
      "OntimeRate": "93.33%",
      "ftype": "78A",
      "FlightHTerminal": "T2",
      "FlightTerminal": "T2",
      "CheckinTable": "F,G",
      "distance": "1178"
    }
  ]
}
```

## 隐私与安全声明

1. **API Key 本地存储**：仅存储在用户本地环境变量或配置文件中
2. **不上传云端**：敏感信息不会上传到 ClawHub 或任何远程服务器
3. **日志脱敏**：日志中 API Key 等敏感信息已脱敏处理
4. **Git 保护**：`config.local.json` 已加入 `.gitignore`，防止意外提交

## 故障排除

### 错误：API Key not configured / 401 Unauthorized
**原因**：未配置 API Key 或 Key 无效  
**解决**：
- 确认已设置 `X_VARIFLIGHT_KEY` 环境变量
- 确认 API Key 已激活（验证邮箱）
- 确认 Key 未过期

### 错误：MCP server start timeout
**原因**：MCP 服务器启动超时  
**解决**：
- 检查网络连接
- 确认 API Key 有效
- 检查 Node.js 版本 >= 18.0.0

### 错误：No flights found / 未找到航班
**原因**：未找到航班数据  
**解决**：
- 确认日期格式正确（YYYY-MM-DD）
- 确认机场/城市代码正确
- 确认该航线在指定日期有航班

### 错误：Command not found
**原因**：命令拼写错误  
**解决**：使用上述列出的标准命令名称

## 相关链接

- [飞常准 MCP 官方文档](https://mcp.variflight.com/)
- [Model Context Protocol 规范](https://modelcontextprotocol.io/)
- [OpenClaw 文档](https://docs.openclaw.ai/)
- [GitHub 仓库](https://github.com/your-username/variflight-aviation-skill)

## 许可证

MIT License © 2026 lixiao