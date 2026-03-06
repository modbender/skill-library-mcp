---
name: SKILL.md
description: 自动化 API 测试和监控服务。
---

# SKILL.md

# API Testing Service

自动化 API 测试和监控服务。

## 能力

- 接口测试
- 响应时间监控
- 状态码检查
- 数据验证
- 性能测试
- 自动化回归测试
- 集成测试

## 使用方式

```bash
# 测试 API 端点
openclaw run api-test --url "https://api.example.com/users" --method "GET"

# 测试认证
openclaw run api-test --url "https://api.example.com/login" --method "POST" --auth

# 性能测试
openclaw run api-test --url "https://api.example.com" --load --concurrency 10

# 定时监控
openclaw run api-test --url "https://api.example.com" --monitor --interval 60
```

## 收费模式

- **单次测试:** $5-15
- **月度订阅:** $50-200
- **企业套餐:** 按需

## 特性

- ✅ 支持 REST, GraphQL, gRPC
- ✅ 自动化测试脚本生成
- ✅ 性能指标监控
- ✅ 告警通知
- ✅ 测试报告生成
- ✅ CI/CD 集成

## 开发者

OpenClaw AI Agent
License: MIT
Version: 1.0.0
