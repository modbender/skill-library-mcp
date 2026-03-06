---
name: JSON Formatter
description: 格式化、验证和压缩 JSON 数据。
---

# JSON Formatter

格式化、验证和压缩 JSON 数据。

## 功能

- JSON 格式化（缩进）
- JSON 验证
- JSON 压缩
- 路径提取

## 触发词

- "格式化JSON"
- "json格式化"
- "prettify json"
- "验证json"

## 示例

```
输入: {"a":1,"b":2}
输出: {
  "a": 1,
  "b": 2
}
```

## 输出

```json
{
  "formatted": "...",
  "valid": true,
  "size": 1024,
  "paths": ["$.a", "$.b"]
}
```
