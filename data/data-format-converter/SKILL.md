---
name: Data Format Converter
description: 在不同数据格式间转换：CSV、JSON、XML、YAML、TOML 等。
---

# Data Format Converter

在不同数据格式间转换：CSV、JSON、XML、YAML、TOML 等。

## 功能

- CSV ↔ JSON 转换
- JSON ↔ YAML 转换
- XML ↔ JSON 转换
- TOML ↔ JSON 转换
- 批量转换

## 触发词

- "格式转换"
- "格式互转"
- "convert format"
- "csv to json"

## 支持格式

| 输入 | 输出 |
|------|------|
| CSV | JSON |
| JSON | YAML |
| YAML | JSON |
| XML | JSON |
| TOML | JSON |

## 示例

```
输入 (CSV):
name,age
John,30
Jane,25

输出 (JSON):
[
  {"name": "John", "age": "30"},
  {"name": "Jane", "age": "25"}
]
```
