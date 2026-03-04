# OpenClaw Router Skill v3.0

**智能模型路由系统 - 节省 60% AI 成本**

[English](README.md) | [中文](README_zh.md)

---

## 🚀 快速开始

### 安装

```bash
# 通过 ClawHub 安装
clawhub install openclaw-router

# 或手动安装
git clone https://github.com/pepsiboy87/openclaw-router.git
cd openclaw-router
bash install_router.sh
```

### 配置

安装后自动运行配置向导：

```bash
# 或手动运行
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
- ✅ **节省 60% 成本**

### 🌍 全球支持

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
| llama3:8b/70b | 通用任务 | ¥0 |
| mistral:7b | 平衡 | ¥0 |

### 云端模型

| 提供商 | 模型 | 适用场景 | 成本/1k tokens |
|--------|------|----------|---------------|
| 阿里云 | qwen3.5-plus | 日常主力 | ¥0.002 |
| 阿里云 | qwen3-max | 复杂推理 | ¥0.04 |
| 阿里云 | kimi-k2.5 | 长文本 262k | ¥0.04 |
| OpenAI | gpt-4 | 创意/英文 | $0.03 |
| OpenAI | gpt-4o | 多模态 | $0.005 |
| Anthropic | claude-3-opus | 最强推理 | $0.015 |
| Anthropic | claude-3-sonnet | 平衡 | $0.003 |

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

## 🧪 测试

### 运行测试套件

```bash
bash run_tests.sh
```

### 预期输出

```
╔══════════════════════════════════════════════════════════╗
║          OpenClaw Router Skill v3.0 测试套件              ║
╚══════════════════════════════════════════════════════════╝

测试 1: 模块导入...
✅ 所有模块导入成功

测试 2: 环境检测...
   Ollama: ✅ 已安装 (2 个模型)
   阿里云：✅ 已配置
   OpenAI: ✅ 已配置
   系统：16.0GB 内存，8 核心

测试 3: 配置推荐...
   ✅ 主路由：qwen2.5:14b-32k (本地)
   ✅ 验证器：dashscope/qwen3.5-plus (云端)
   ✅ 专家：dashscope/qwen3-max (云端)

测试 4: 路由选择...
   5.0 分 → qwen2.5:14b
   3.2 分 → qwen2.5:14b + 验证
   2.0 分 → dashscope/qwen3-max

测试 5: 配置管理...
   ✅ 保存成功
   ✅ 加载成功
   ✅ 验证通过

所有测试通过！Router Skill 已准备就绪。
```

---

## 🌍 全球云服务商

### 自动检测的提供商

| 提供商 | 环境变量 | 地区 |
|--------|----------|------|
| **阿里云** | `DASHSCOPE_API_KEY` | 中国/全球 |
| **OpenAI** | `OPENAI_API_KEY` | 全球 |
| **Anthropic** | `ANTHROPIC_API_KEY` | 全球 |
| **AWS Bedrock** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | 全球 |
| **Azure OpenAI** | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` | 全球 |
| **Google Vertex AI** | `GOOGLE_APPLICATION_CREDENTIALS` | 全球 |

---

## 📖 文档

- [配置指南](docs/CONFIGURATION.md)
- [API 文档](docs/API.md)
- [使用示例](docs/EXAMPLES.md)
- [常见问题](docs/FAQ.md)
- [隐私政策](docs/PRIVACY_POLICY.md)
- [服务条款](docs/TERMS_OF_SERVICE.md)

---

## 🤝 贡献

欢迎贡献！

```bash
# Fork 项目
git fork https://github.com/pepsiboy87/openclaw-router

# 克隆到本地
git clone git@github.com:your-username/openclaw-router.git

# 创建分支
git checkout -b feature/your-feature

# 提交代码
git commit -m "Add your feature"

# 推送
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
