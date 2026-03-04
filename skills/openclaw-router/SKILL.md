---
name: openclaw-router
version: 1.0.0
description: "Intelligent Model Routing - Save 60% on AI Costs / 智能路由系统 - 节省 60% 成本"
author: pepsiboy87
homepage: https://github.com/pepsiboy87/openclaw-router

metadata:
  category: automation
  tags: [routing, model-selection, cost-optimization, llm, ai, i18n, global]
  languages: [en, zh]
  regions: [global, china, us, eu, asia]
  requirements:
    openclaw: ">=2026.2.24"
    python: ">=3.8"
    system:
      memory_min_gb: 2
      disk_min_gb: 1
  
pricing:
  type: freemium
  currencies:
    USD:
      premium: 9.99
      enterprise: 29.99
    CNY:
      premium: 29
      enterprise: 199
    EUR:
      premium: 9.99
      enterprise: 29.99
  free_tier:
    requests_per_month: 1000
    features_en: [Basic Routing, Token Tracking, Environment Detection, Config Wizard]
    features_zh: [基础路由，Token 追踪，环境检测，配置向导]
  premium_tier:
    features_en: [Unlimited Requests, User Preference Learning, Budget Management, Time Optimization, Multi-Model Support, Detailed Reports, Priority Support]
    features_zh: [无限请求，用户偏好学习，预算管理，时段优化，多模型支持，详细报告，优先支持]
---

# OpenClaw Router Skill

**通用智能路由系统 - 自动选择最佳模型，节省 60% 成本**

---

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install openclaw-router
```

### 配置

安装后自动运行配置向导，或手动运行：

```bash
openclaw router config --init
```

### 启用

```bash
openclaw router enable
```

---

## ✨ 功能特性

### 🎯 智能模型选择

- ✅ 5 维度自评（知识/推理/上下文/质量/工具）
- ✅ 任务类型识别（代码/创意/分析/战略/学习/日常）
- ✅ 用户偏好学习
- ✅ 成本预算管理

### 💰 成本优化

- ✅ 本地模型优先（免费）
- ✅ 边界情况验证（L2）
- ✅ 复杂任务专家（L3）
- ✅ **预计节省 60% 成本**

### 🌍 全场景支持

- ✅ 纯本地部署
- ✅ 纯云端部署
- ✅ 混合部署
- ✅ 多云端部署
- ✅ 企业私有化

### 📊 透明追踪

- ✅ Token 用量显示
- ✅ 成本实时追踪
- ✅ 套餐剩余监控
- ✅ 预算告警

---

## 📋 支持的模型

### 本地模型（Ollama）

| 模型 | 适用场景 | 成本 |
|------|----------|------|
| qwen2.5:7b | 简单问答 | ¥0 |
| qwen2.5:14b | 日常开发 | ¥0 |
| qwen2.5:72b | 复杂任务 | ¥0 |

### 云端模型

| 提供商 | 模型 | 适用场景 | 成本/1k tokens |
|--------|------|----------|---------------|
| 阿里云 | qwen3.5-plus | 日常主力 | ¥0.002 |
| 阿里云 | qwen3-max | 复杂推理 | ¥0.04 |
| 阿里云 | kimi-k2.5 | 长文本 | ¥0.04 |
| OpenAI | gpt-4 | 创意/英文 | ¥0.03 |
| Anthropic | claude-3 | 安全敏感 | ¥0.03 |

---

## ⚙️ 配置说明

### 配置文件位置

```
~/.openclaw/router_config.yaml
```

### 配置示例

```yaml
version: "1.0.0"

models:
  primary:
    id: "qwen2.5:14b-32k"
    location: "local"
  
  verifier:
    id: "dashscope/qwen3.5-plus"
    location: "cloud"
  
  expert:
    id: "dashscope/qwen3-max"
    location: "cloud"

thresholds:
  mode: "balanced"
  auto_pass: 3.5
  verify_min: 3.0
  verify_max: 3.5
  escalate_below: 3.0

budget:
  monthly: 200
  currency: "CNY"
  alert_at: [50, 80, 95]
```

---

## 💰 定价

### 免费版

- ✅ 基础路由
- ✅ Token 追踪
- ✅ 每月 1000 次请求

### 付费版（¥29/月）

- ✅ 无限请求
- ✅ 用户偏好学习
- ✅ 预算管理
- ✅ 时段优化
- ✅ 优先支持

### 企业版（¥199/月）

- ✅ 所有付费功能
- ✅ 多用户管理
- ✅ 自定义模型池
- ✅ API 访问
- ✅ SLA 保障

---

## 📖 文档

- [配置指南](docs/CONFIGURATION.md)
- [API 文档](docs/API.md)
- [使用示例](docs/EXAMPLES.md)
- [常见问题](docs/FAQ.md)

---

## 🤝 贡献

欢迎贡献代码！

```bash
git fork https://github.com/pepsiboy87/openclaw-router
git clone git@github.com:your-username/openclaw-router.git
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

---

## 📄 许可证

MIT License

---

## 📞 支持

- **文档：** https://github.com/pepsiboy87/openclaw-router
- **Issue：** https://github.com/pepsiboy87/openclaw-router/issues
- **邮箱：** pepsiboy87@example.com

---

_让每个 AI 助手都拥有智能路由能力！_
