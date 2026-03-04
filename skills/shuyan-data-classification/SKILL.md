---
name: shuyan-data-classification
description: "数安云智数据分类分级同步接口 - 用于批量处理字段信息的分类分级。支持敏感数据识别、数据分类、数据分级等功能。使用前需配置API地址和认证密钥。"
homepage: https://localhost:8080
author: tanluzhe
license: MIT
version: "1.0.0"
metadata:
  {
    "openclaw":
      { "emoji": "🔒", "requires": { "bins": ["curl"] }, "primaryEnv": "SHUYAN_API_KEY" },
  }
---

# 数安云智数据分类分级同步接口

这是一个用于批量处理字段信息分类分级的同步接口服务。

## 接口信息

- **接口地址**: http://localhost:8080/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync
- **认证方式**: Bearer Token
- **Content-Type**: application/json

## 环境变量配置

### 方式一：环境变量

```bash
# ~/.zshrc
export SHUYAN_API_KEY="your-api-key-here"
export SHUYAN_API_URL="http://localhost:8080"
```

### 方式二：OpenClaw配置

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "shuyan-data-classification": {
        "enabled": true,
        "apiKey": "your-api-key-here",
        "apiUrl": "http://localhost:8080"
      }
    }
  }
}
```

## 使用场景

✅ **USE this skill when:**

- 需要对数据库字段进行敏感数据分类
- 需要识别数据敏感级别
- 需要批量处理数据分类分级
- 需要获取分类理由和置信度

❌ **DON'T use this skill when:**

- 单个字段的实时查询（效率较低）
- 历史数据分析

## 请求格式

### 请求参数说明

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| colNameCh | string | 否 | 字段中文名 |
| colNameComment | string | 否 | 字段含义 |
| colNameEn | string | 否 | 字段英文名 |
| projectName | string | 否 | 业务系统 |
| sampleList | array | 否 | 字段样例 |
| sizeInBytes | integer | 否 | 数据大小（字节） |
| standardCode | string | 是 | 分类标准代码 |
| tableNameCh | string | 否 | 表中文名 |
| tableNameEn | string | 否 | 表英文名 |
| sensitivityLevelRedisKey | string | 否 | 分级标准代码 |
| dataSize | string | 否 | 数据量 |
| isDesensitize | integer | 否 | 是否脱敏（0: 未脱敏, 1: 已脱敏） |

## 命令示例

### 批量分类分级同步

```bash
API_KEY="${SHUYAN_API_KEY:-your-api-key-here}"
API_URL="${SHUYAN_API_URL:-http://localhost:8080}"

curl -s -X POST "${API_URL}/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "colNameCh": "用户姓名",
      "colNameComment": "用户的真实姓名",
      "colNameEn": "user_name",
      "projectName": "用户管理系统",
      "sampleList": ["张三", "李四", "王五"],
      "sizeInBytes": 1024,
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "tableNameCh": "用户表",
      "tableNameEn": "user",
      "sensitivityLevelRedisKey": "fenji_standard",
      "dataSize": "10000",
      "isDesensitize": 0
    },
    {
      "colNameCh": "身份证号",
      "colNameComment": "用户的身份证号码",
      "colNameEn": "id_card",
      "projectName": "用户管理系统",
      "sampleList": ["110101199001011234"],
      "sizeInBytes": 2048,
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "tableNameCh": "用户表",
      "tableNameEn": "user",
      "sensitivityLevelRedisKey": "fenji_standard",
      "dataSize": "10000",
      "isDesensitize": 1
    }
  ]'
```

## 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "Batch processing completed successfully",
  "result": [
    {
      "colNameCh": "用户姓名",
      "colNameComment": "用户的真实姓名",
      "colNameEn": "user_name",
      "confidence": 0,
      "itemName": "个人基本信息",
      "label": ["客户", "个人", "个人自然信息", "个人基本概况信息"],
      "projectName": "用户管理系统",
      "reasoningProcess": "字段含义为用户的真实姓名，属于个人基本情况数据",
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "tableNameCh": "用户表",
      "tableNameEn": "user",
      "sensitivityLevel": 2
    }
  ]
}
```

### 响应字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| code | integer | 响应状态码（200: 成功, 500: 失败） |
| message | string | 响应消息 |
| result | array | 处理结果列表 |

### 结果项字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| colNameCh | string | 字段中文名 |
| colNameComment | string | 字段含义 |
| colNameEn | string | 字段英文名 |
| confidence | integer | 置信度 |
| itemName | string | 业务类型 |
| label | array | 分类标签列表 |
| projectName | string | 业务系统 |
| reasoningProcess | string | 分类理由 |
| standardCode | string | 标准代码 |
| tableNameCh | string | 表中文名 |
| tableNameEn | string | 表英文名 |
| sensitivityLevel | integer | 敏感度等级（1-5，5为最高） |

## 敏感度等级说明

| 等级 | 说明 |
|------|------|
| 1 | 一般数据 |
| 2 | 重要数据 |
| 3 | 核心数据 |
| 4 | 敏感数据 |
| 5 | 绝密数据 |

## 错误处理

常见错误：

| 错误信息 | 原因 |
|----------|------|
| No result returned from batch processing | 批量处理没有返回结果 |
| Result is not a list | 返回结果不是列表格式 |
| batch processing result length mismatch | 处理结果数量与输入数量不匹配 |

## 常见使用示例

### 示例1：用户信息表分类

```bash
curl -s -X POST "http://localhost:8080/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync" \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "colNameCh": "手机号",
      "colNameComment": "用户联系电话",
      "colNameEn": "phone",
      "projectName": "用户系统",
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "sensitivityLevelRedisKey": "fenji_standard"
    }
  ]'
```

### 示例2：金融数据分类

```bash
curl -s -X POST "http://localhost:8080/api/llm_infer_zh_and_cls_and_type_v2_batchdata_sync" \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "colNameCh": "银行账号",
      "colNameComment": "银行账户号码",
      "colNameEn": "bank_account",
      "projectName": "金融系统",
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "sensitivityLevelRedisKey": "fenji_standard"
    },
    {
      "colNameCh": "交易金额",
      "colNameComment": "交易金额",
      "colNameEn": "amount",
      "projectName": "金融系统",
      "standardCode": "llm_infer_zh_and_cls_and_type_v2_test",
      "sensitivityLevelRedisKey": "fenji_standard"
    }
  ]'
```

## 注意事项

1. 接口为同步处理，处理时间可能较长
2. 建议批量处理时控制单次请求数量（建议不超过100条）
3. 接口会自动对失败的字段进行重试
