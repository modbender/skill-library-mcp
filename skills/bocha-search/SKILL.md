---
name: bocha-search
description: 博查搜索 API 插件，从全网搜索网页信息，结果准确、摘要完整，适合 AI 使用。
version: 1.0.0
author: Jowin
---

# 博查搜索 (Bocha Search)

基于博查 AI 搜索 API 的网页搜索插件，返回结构化的搜索结果，适合大模型使用。

## 功能特点

- 🔍 全网搜索，结果准确
- 📝 可选返回网页摘要 (summary)
- ⏰ 支持时间范围过滤
- 🌐 Response 格式兼容 Bing Search API

## 配置

### 方式一：配置文件 (推荐)

编辑 `config.json`：
```json
{
  "apiKey": "sk-your-api-key"
}
```

### 方式二：环境变量

```bash
export BOCHA_API_KEY="sk-your-api-key"
```

> API Key 获取：https://open.bochaai.com → API KEY 管理

## 使用方法

```bash
node scripts/search.js <query> [options]
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `<query>` | string | ✅ | 搜索关键词 |
| `--count <n>` | number | ❌ | 返回结果数量，范围 1-50，默认 10 |
| `--freshness <v>` | string | ❌ | 时间范围过滤，默认 noLimit |
| `--summary` | flag | ❌ | 是否返回网页摘要 |

### freshness 取值说明

| 值 | 说明 |
|------|------|
| `noLimit` | 不限时间 (默认，推荐) |
| `oneDay` | 一天内 |
| `oneWeek` | 一周内 |
| `oneMonth` | 一个月内 |
| `oneYear` | 一年内 |
| `YYYY-MM-DD..YYYY-MM-DD` | 自定义日期范围，如 `2025-01-01..2025-04-06` |
| `YYYY-MM-DD` | 指定日期，如 `2025-04-06` |

> ⚠️ 推荐使用 `noLimit`，搜索算法会自动优化时间范围。指定时间范围可能导致无结果。

## 示例

### 基本搜索
```bash
node scripts/search.js "沪电股份"
```

### 限制数量
```bash
node scripts/search.js "人工智能" --count 5
```

### 带摘要
```bash
node scripts/search.js "DeepSeek" --summary
```

### 限定时间范围
```bash
node scripts/search.js "AI新闻" --freshness oneWeek --count 10
```

### 组合使用
```bash
node scripts/search.js "阿里巴巴ESG报告" --count 5 --freshness oneMonth --summary
```

## 输出格式

### 成功响应
```json
{
  "type": "search",
  "query": "搜索词",
  "totalResults": 12345,
  "resultCount": 10,
  "results": [
    {
      "index": 1,
      "title": "网页标题",
      "url": "https://example.com/page",
      "description": "网页内容的简短描述",
      "summary": "网页内容的详细摘要 (需 --summary)",
      "siteName": "网站名称",
      "publishedDate": "2025-01-01T12:00:00+08:00"
    }
  ]
}
```

### 错误响应
```json
{
  "type": "error",
  "code": "401",
  "message": "Invalid API KEY",
  "log_id": "xxxx"
}
```

### 常见错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 400 | 参数缺失 | 检查 query 参数 |
| 401 | API Key 无效 | 检查 config.json 或环境变量 |
| 403 | 余额不足 | 前往 open.bochaai.com 充值 |
| 429 | 请求频率限制 | 稍后重试 |

## API 文档

- 博查开放平台：https://open.bochaai.com
- API 文档：https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK
