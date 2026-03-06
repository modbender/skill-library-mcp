---
name: api-docs-generator
description: 从代码注释自动生成 API 文档，支持 OpenAPI/Swagger 格式，输出 JSON 或 YAML。
metadata: {"clawdbot":{"emoji":"📚","requires":{},"primaryEnv":""}}
---

# API Docs Generator

自动从源代码生成专业的 API 文档。支持 OpenAPI 3.0 和 Swagger 2.0 规范。

## 功能

- 📝 自动解析代码注释
- 🌐 OpenAPI 3.0 支持
- 📄 Swagger 2.0 支持
- 📋 Postman Collection 导出
- 🔄 自动检测 API 路由
- 📖 生成可交互文档

## 支持的框架

| 框架 | 支持 |
|------|------|
| Express.js | ✅ |
| FastAPI | ✅ |
| Flask | ✅ |
| Gin | ✅ |
| Spring Boot | ✅ |
| Rails | ✅ |

## 使用方法

### 基本用法

```bash
# 生成 OpenAPI 文档
api-docs-generator openapi --input ./src --output docs/openapi.json

# 生成 Swagger 文档
api-docs-generator swagger --input ./src --output docs/swagger.yaml

# 生成 Postman Collection
api-docs-generator postman --input ./src --output docs/collection.json
```

### 选项

| 选项 | 说明 |
|------|------|
| `--input, -i` | 源代码目录 |
| `--output, -o` | 输出文件路径 |
| `--format, -f` | 输出格式 (json/yaml) |
| `--title` | API 标题 |
| `--version` | API 版本 |

## 输出示例

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "My API",
    "version": "1.0.0",
    "description": "API description"
  },
  "paths": {
    "/api/users": {
      "get": {
        "summary": "Get all users",
        "description": "Returns a list of users",
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": { "$ref": "#/components/schemas/User" }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## 文档展示

生成的文档可以用于：
- Swagger UI
- Redoc
- Postman
- Apiary

## 变现思路

1. **付费模板** - 专业化文档模板
2. **企业服务** - 为企业定制 API 文档
3. **集成服务** - 与 GitHub/GitLab 集成
4. **培训服务** - API 文档编写培训

## 示例

### Express.js 项目

```bash
api-docs-generator openapi \
  --input ./server \
  --output ./docs/openapi.json \
  --title "My API" \
  --version "1.0.0"
```

### FastAPI 项目

```bash
api-docs-generator openapi \
  --input ./app \
  --output ./docs/api.yaml \
  --format yaml
```

## 安装

```bash
# 无需额外依赖
```
