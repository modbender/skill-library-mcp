# 📤 ClawHub Skills 上传完整指南

**版本：** 1.0.0  
**日期：** 2026-03-02  
**状态：** ✅ 完整教程

---

## 🎯 上传前准备

### 必需文件清单

- [x] ✅ `clawhub.json` - 元数据配置
- [x] ✅ `SKILL.md` - Skill 描述
- [x] ✅ `README.md` - 主文档（英文）
- [x] ✅ `README_zh.md` - 主文档（中文）
- [x] ✅ `src/` - 源代码目录
- [x] ✅ `docs/` - 文档目录
- [x] ✅ 许可证文件（LICENSE）

### 可选文件

- [ ] `screenshots/` - 截图
- [ ] `examples/` - 示例
- [ ] `tests/` - 测试
- [ ] `config/` - 配置模板

---

## 📝 步骤 1: 准备 clawhub.json

### 完整配置示例

```json
{
  "name": "openclaw-router",
  "version": "1.0.0",
  "description": "Intelligent Model Routing - Save 60% on AI Costs / 智能路由系统 - 节省 60% 成本",
  "author": "pepsiboy87",
  "license": "MIT",
  "homepage": "https://github.com/pepsiboy87/openclaw-router",
  "repository": "https://github.com/pepsiboy87/openclaw-router",
  
  "category": "automation",
  "tags": [
    "routing",
    "model-selection",
    "cost-optimization",
    "llm",
    "ai",
    "i18n",
    "global"
  ],
  
  "languages": ["en", "zh"],
  "regions": ["global", "china", "us", "eu", "asia"],
  
  "pricing": {
    "type": "free",
    "license": "MIT",
    "note": "Free and open source (MIT License). All core features free forever."
  },
  
  "requirements": {
    "openclaw": ">=2026.2.24",
    "python": ">=3.8"
  },
  
  "entry_point": "src/__init__.py",
  "main_script": "router_config_wizard.py"
}
```

### 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `name` | ✅ | Skill 名称（唯一） | `openclaw-router` |
| `version` | ✅ | 版本号（语义化） | `1.0.0` |
| `description` | ✅ | 简短描述（中英） | `Intelligent Model Routing...` |
| `author` | ✅ | 作者名 | `pepsiboy87` |
| `license` | ✅ | 许可证 | `MIT` |
| `category` | ✅ | 分类 | `automation` |
| `tags` | ✅ | 标签（5-10 个） | `["routing", "ai", ...]` |
| `homepage` | ✅ | 项目主页 | GitHub URL |
| `repository` | ✅ | 代码仓库 | GitHub URL |

---

## 📝 步骤 2: 准备 SKILL.md

### 完整配置示例

```markdown
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
  requirements:
    openclaw: ">=2026.2.24"
    python: ">=3.8"
  
pricing:
  type: free
  license: MIT
  note: "Free and open source. Paid support available."
---

# OpenClaw Router Skill

**智能模型路由系统 - 节省 60% AI 成本**

---

## 🚀 快速开始

### 安装

```bash
clawhub install openclaw-router
```

### 配置

```bash
openclaw router config --init
```

### 启用

```bash
openclaw router enable
```

---

## ✨ 功能特性

- ✅ 5 维度智能自评
- ✅ 自动模型选择
- ✅ 环境自动检测
- ✅ Token 用量追踪
- ✅ 成本预算管理
- ✅ 多语言支持（EN/ZH）
- ✅ 全球化合规

---

## 💰 定价

**完全免费！** (MIT 许可证)

**付费支持（可选）：**
- 优先支持：¥29/月
- 企业版：¥199/月

---

## 📖 文档

- [配置指南](docs/CONFIGURATION.md)
- [使用示例](docs/EXAMPLES.md)
- [常见问题](docs/FAQ.md)

---

## 🤝 贡献

欢迎贡献代码！

```bash
git fork https://github.com/pepsiboy87/openclaw-router
```

---

## 📄 许可证

MIT License

---

_让每个 AI 助手都拥有智能路由能力！_
```

---

## 📝 步骤 3: 准备 README.md

### 结构模板

```markdown
# OpenClaw Router Skill v1.0.0

**Intelligent Model Routing - Save 60% on AI Costs**

[English](README.md) | [中文](README_zh.md)

---

## 🚀 Quick Start

### Installation

```bash
clawhub install openclaw-router
```

### Configuration

```bash
openclaw router config --init
```

### Enable

```bash
openclaw router enable
```

---

## ✨ Features

- ✅ 5-dimension self-assessment
- ✅ Intelligent model selection
- ✅ Environment auto-detection
- ✅ Token usage tracking
- ✅ Cost budget management
- ✅ Multi-language support (EN/ZH)
- ✅ Global compliance

---

## 💰 Pricing

**Free and Open Source!** (MIT License)

Optional paid support:
- Priority Support: ¥29/month
- Enterprise: ¥199/month

---

## 📋 Supported Models

### Local Models (Ollama)

| Model | Use Case | Cost |
|-------|----------|------|
| qwen2.5:14b | Daily Development | $0 |
| qwen2.5:72b | Complex Tasks | $0 |

### Cloud Models

| Provider | Model | Use Case | Cost/1k tokens |
|----------|-------|----------|---------------|
| Alibaba Cloud | qwen3.5-plus | Daily | $0.002 |
| Alibaba Cloud | qwen3-max | Complex | $0.04 |
| OpenAI | gpt-4 | Creative | $0.03 |

---

## 🧪 Testing

```bash
bash run_tests.sh
```

---

## 📖 Documentation

- [Configuration Guide](docs/CONFIGURATION.md)
- [Examples](docs/EXAMPLES.md)
- [FAQ](docs/FAQ.md)

---

## 🤝 Contributing

Welcome to contribute!

```bash
git fork https://github.com/pepsiboy87/openclaw-router
```

---

## 📄 License

MIT License

---

_Empower every AI assistant with intelligent routing!_
```

---

## 📝 步骤 4: 打包提交

### 方法 1: 通过 ClawHub 网站（推荐）

**步骤：**

1. **访问 ClawHub**
   ```
   https://clawhub.com/upload
   ```

2. **登录 GitHub 账号**
   - 点击 "Sign in with GitHub"
   - 授权 ClawHub

3. **填写提交信息**
   
   **基本信息：**
   ```
   Skill Name: openclaw-router
   Version: 1.0.0
   Category: automation
   License: MIT
   ```
   
   **描述：**
   ```
   Intelligent model routing system. Save 60% on AI costs.
   Supports 6 cloud providers, 46+ models, multi-language (EN/ZH),
   global compliance (GDPR/CCPA/PIPL).
   
   智能模型路由系统。节省 60% AI 成本。
   支持 6 大云服务商、46+ 模型、多语言、全球合规。
   ```
   
   **标签：**
   ```
   routing, model-selection, cost-optimization, llm, ai, i18n, global
   ```

4. **上传代码**
   
   **选项 A: GitHub 仓库**
   ```
   Repository URL: https://github.com/pepsiboy87/openclaw-router
   Branch: main
   ```
   
   **选项 B: 上传压缩包**
   ```
   文件：router_skill_v1.0.0.tar.gz
   ```

5. **验证配置**
   - ClawHub 自动验证 `clawhub.json`
   - 检查必需文件
   - 验证代码结构

6. **提交审核**
   - 点击 "Submit for Review"
   - 等待确认邮件
   - 预计审核时间：1-3 天

---

### 方法 2: 通过 ClawHub CLI

**步骤：**

1. **安装 ClawHub CLI**
   ```bash
   npm install -g clawhub
   ```

2. **登录**
   ```bash
   clawhub login
   ```

3. **验证配置**
   ```bash
   cd /root/.openclaw/workspace/router_skill
   clawhub validate
   ```

4. **提交**
   ```bash
   clawhub submit
   ```
   
   或带消息：
   ```bash
   clawhub submit -m "Router Skill v1.0.0 - Intelligent model routing"
   ```

5. **查看状态**
   ```bash
   clawhub status
   ```

---

### 方法 3: 通过 Git 推送

**步骤：**

1. **初始化 Git 仓库**
   ```bash
   cd /root/.openclaw/workspace/router_skill
   git init
   git add .
   git commit -m "Router Skill v1.0.0 - Initial release"
   ```

2. **添加远程仓库**
   ```bash
   git remote add origin https://github.com/pepsiboy87/openclaw-router.git
   ```

3. **推送到 GitHub**
   ```bash
   git push -u origin main
   ```

4. **在 ClawHub 登记**
   - 访问：https://clawhub.com/import
   - 输入 GitHub 仓库 URL
   - 自动导入配置

---

## ✅ 提交前检查清单

### 文件完整性

- [ ] ✅ `clawhub.json` 存在且有效
- [ ] ✅ `SKILL.md` 存在
- [ ] ✅ `README.md` 存在
- [ ] ✅ `src/` 目录存在
- [ ] ✅ `docs/` 目录存在
- [ ] ✅ 许可证文件存在

### 配置验证

- [ ] ✅ `clawhub.json` JSON 格式有效
- [ ] ✅ 所有必需字段已填写
- [ ] ✅ 版本号符合语义化版本
- [ ] ✅ 标签合理（5-10 个）
- [ ] ✅ 分类正确

### 代码质量

- [ ] ✅ 代码无语法错误
- [ ] ✅ 测试通过
- [ ] ✅ 文档完整
- [ ] ✅ 无敏感信息（API Key 等）

### 文档完整性

- [ ] ✅ README.md（英文）
- [ ] ✅ README_zh.md（中文，可选）
- [ ] ✅ 安装说明
- [ ] ✅ 使用说明
- [ ] ✅ 配置说明

---

## 📊 审核流程

### 时间线

| 时间 | 事件 | 操作 |
|------|------|------|
| **提交后** | 自动验证（5-10 分钟） | 等待邮件 |
| **1-3 天** | 人工审核 | 等待通知 |
| **审核后** | 批准/修改通知 | 按反馈处理 |
| **批准后** | 上架 ClawHub | 庆祝！🎉 |

### 可能的审核结果

| 结果 | 概率 | 后续操作 |
|------|------|----------|
| **直接批准** | 80% | 立即上架 |
| **需要修改** | 15% | 按反馈修改后重新提交 |
| **拒绝** | 5% | 解决重大问题后重新提交 |

---

## 💡 提高审核通过率

### 必做事项

1. **完整文档**
   - README 详细
   - 配置说明清晰
   - 使用示例充足

2. **代码质量**
   - 无语法错误
   - 测试通过
   - 注释清晰

3. **配置正确**
   - `clawhub.json` 完整
   - 所有必需字段
   - 版本号正确

4. **遵守规范**
   - MIT 许可证
   - 无侵权内容
   - 无恶意代码

### 加分事项

1. **多语言支持**
   - 英文 + 中文文档
   - i18n 支持

2. **测试覆盖**
   - 单元测试
   - 集成测试
   - 测试报告

3. **截图/演示**
   - 使用截图
   - 演示视频
   - 在线 Demo

4. **社区活跃**
   - GitHub Issues 响应快
   - 定期更新
   - 接受贡献

---

## 🎯 提交信息模板

### 简短描述（280 字符）

```
Intelligent model routing system. Save 60% on AI costs. Supports 6 cloud providers, 46+ models, multi-language (EN/ZH), global compliance (GDPR/CCPA/PIPL). Free and open source (MIT).

智能模型路由系统。节省 60% AI 成本。支持 6 大云服务商、46+ 模型、多语言、全球合规。免费开源（MIT）。
```

### 完整描述

```
OpenClaw Router Skill v1.0.0 - Intelligent model routing system that automatically selects the best AI model for your tasks.

Key Features:
- 5-dimension self-assessment
- Intelligent model selection
- Environment auto-detection
- Token usage tracking
- Cost budget management
- Multi-language support (EN/ZH)
- Global compliance (GDPR/CCPA/PIPL)

Supported Models:
- Local: qwen2.5:7b/14b/72b, llama3, mistral, gemma
- Cloud: Alibaba Cloud, OpenAI, Anthropic, AWS, Azure, Google

Pricing:
- Free and open source (MIT License)
- Optional paid support available

Installation:
clawhub install openclaw-router

Documentation:
https://github.com/pepsiboy87/openclaw-router
```

---

## 📞 常见问题

### Q: 审核需要多久？

**A:** 通常 1-3 天。如果超过 3 天未回复，可以发邮件询问。

---

### Q: 被拒绝了怎么办？

**A:** 
1. 查看拒绝原因
2. 按反馈修改
3. 重新提交

---

### Q: 可以更新已提交的 Skill 吗？

**A:** 可以！
```bash
# 更新版本号
# 修改 clawhub.json 的 version 字段

# 重新提交
clawhub submit
```

---

### Q: 如何删除已提交的 Skill？

**A:** 
1. 登录 ClawHub
2. 进入我的 Skills
3. 点击删除
4. 或联系支持

---

### Q: 可以收费吗？

**A:** 
- ClawHub 目前所有技能都是免费的
- 可以通过 GitHub Sponsors 接受赞助
- 可以提供付费支持服务
- 可以销售企业版/定制版

---

## 🎉 提交成功！

### 提交后做什么？

1. **监控审核状态**
   - 查看邮箱
   - 查看 GitHub Issues

2. **准备营销材料**
   - 技术博客
   - 社交媒体
   - 演示视频

3. **准备用户支持**
   - FAQ 文档
   - Issue 模板
   - 响应模板

4. **收集用户反馈**
   - GitHub Issues
   - 用户调查
   - 使用统计

---

**祝提交顺利！** 🚀

---

_Guide Generated: March 2, 2026 01:35 GMT+8_  
_Version: 1.0.0_  
_Status: Complete_
