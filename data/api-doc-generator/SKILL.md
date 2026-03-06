---
name: API Doc Generator
description: 自动从代码生成 API 文档。
---

# API Doc Generator

自动从代码生成 API 文档。

## 功能

- 分析代码中的函数/方法签名
- 自动提取参数和返回值类型
- 生成 OpenAPI/Swagger 格式文档
- 支持 Python、JavaScript、TypeScript、Go

## 触发词

- "生成API文档"
- "API文档"
- "生成接口文档"
- "openapi"
- "swagger"

## 示例

```
用户: 帮我把这个Python函数生成API文档
助手: (使用此skill生成OpenAPI文档)
```

## 输出格式

```json
{
  "openapi": "3.0.0",
  "info": { "title": "API", "version": "1.0.0" },
  "paths": {
    "/users": {
      "get": {
        "summary": "获取用户列表",
        "parameters": [...],
        "responses": { "200": {...} }
      }
    }
  }
}
```
