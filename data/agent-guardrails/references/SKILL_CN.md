# Agent Guardrails 🛡️ — 中文文档

## 你的AI助手在偷偷绕过你的规则，这个工具用代码来阻止它。

**适用于：** Claude Code | Clawdbot | Cursor | 任何AI编程助手

> Markdown里的规则只是建议。代码钩子才是法律。

🚨 **在生产事故发生之前就阻止它** — 这套工具诞生于真实的服务器崩溃、密钥泄露和静默绕过

---

## 问题是什么？

你花了几个小时搭建验证流程、评分系统和校验逻辑。然后你的AI助手写了一个"简化版"，把这些全部绕过了。听起来熟悉吗？

### 真实生产事故（2026年2月）

**🔥 服务器崩溃：** 错误的配置修改 → 服务崩溃循环 → 宕机一整晚  
**🔑 密钥泄露：** Notion token硬编码在代码里，差点推送到公开GitHub  
**🔄 代码重写：** AI重写了已验证的评分逻辑而不是导入它，发送了未验证的预测  
**🚀 部署遗漏：** 新功能做好了但忘了接入生产环境，用户收到不完整的输出  

这不是提示词的问题——这是**执行力**的问题。写再多markdown规则也没用。你需要**真正有效的**机械化强制执行。

---

## 执行可靠性层级

| 层级 | 方法 | 可靠性 |
|------|------|--------|
| 1 | **代码钩子**（pre-commit、创建前/后检查） | 100% |
| 2 | **架构约束**（导入注册表、强制复用） | 95% |
| 3 | **自我验证循环** | 80% |
| 4 | **提示规则**（AGENTS.md） | 60-70% |
| 5 | **Markdown文档** | 40-50% ⚠️ |

本工具专注于第1-2层：**真正管用的那些**。

---

## 包含什么？

| 工具 | 用途 |
|------|------|
| `scripts/install.sh` | 一键安装到你的项目 |
| `scripts/pre-create-check.sh` | 创建新文件前列出已有模块，防止重复造轮子 |
| `scripts/post-create-validate.sh` | 检测重复函数和缺失的导入 |
| `scripts/check-secrets.sh` | 扫描硬编码的token/密钥/密码 |
| `scripts/create-deployment-check.sh` | 生成部署验证脚本和检查清单 |
| `scripts/install-skill-feedback-loop.sh` | 设置skill更新自动检测和反馈循环 |
| `assets/pre-commit-hook` | Git钩子：自动拦截绕过模式 + 密钥泄露 |
| `assets/registry-template.py` | `__init__.py`模板，强制导入已验证函数 |
| `references/agents-md-template.md` | 经过实战检验的AGENTS.md模板 |
| `references/enforcement-research.md` | 完整研究：为什么代码 > 提示词 |

---

## 快速开始

**Claude Code 用户：**
```bash
git clone https://github.com/jzOcb/agent-guardrails ~/.claude/skills/agent-guardrails
cd 你的项目 && bash ~/.claude/skills/agent-guardrails/scripts/install.sh .
```

**Clawdbot 用户：**
```bash
clawdhub install agent-guardrails
```

**手动安装：**
```bash
bash /path/to/agent-guardrails/scripts/install.sh /path/to/your/project
```

安装后自动完成：
- ✅ 安装git pre-commit钩子（拦截绕过模式 + 硬编码密钥）
- ✅ 创建`__init__.py`注册表模板
- ✅ 复制检查脚本到你的项目
- ✅ 在你的AGENTS.md中添加执行规则

---

## 使用方法

### 创建新文件之前：
```bash
bash scripts/pre-create-check.sh /path/to/project
```
显示已有的模块和函数。如果已经有了——**直接导入，不要重写**。

### 创建/编辑文件之后：
```bash
bash scripts/post-create-validate.sh /path/to/new_file.py
```
捕获重复函数、缺失导入、以及"简化版"/"临时"等绕过模式。

### 密钥扫描：
```bash
bash scripts/check-secrets.sh /path/to/project
```

---

## 工作原理

### Pre-commit 钩子
自动拦截包含以下内容的提交：
- **绕过模式**：`"simplified version"`, `"quick version"`, `"temporary"`, `"TODO: integrate"`
- **硬编码密钥**：源代码中的API key、token、password

### 导入注册表
每个项目有一个`__init__.py`明确列出已验证的函数：

```python
# 这是本项目唯一认可的接口
from .core import validate_data, score_item, generate_report

# 新脚本必须从这里导入，不许重新实现
```

---

## 诞生故事

这套工具诞生于一个真实事故（2026-02-02）：我们为预测市场分析搭建了一套完整的决策引擎——评分系统、规则解析器、新闻验证、数据源校验。然后AI助手创建了一个"快速扫描"脚本，把**所有这些**全部绕过了，发送了未经验证的推荐。

修复方法不是写更多规则。而是写代码来**机械化阻止**这种绕过。

---

## 核心原则

> 不要添加更多markdown规则。添加机械化执行。  
> 如果AI持续绕过某个标准，不要写更强的规则——写一个**阻止它的钩子**。

---

## 开源协议

MIT — 随便用，随便分享，让你的AI助手听话。

**GitHub:** https://github.com/jzOcb/agent-guardrails  
**英文文档:** [README.md](../README.md)

## 相关项目

- [config-guard](https://github.com/jzOcb/config-guard) — 防止 AI 改错 OpenClaw 配置导致网关崩溃（自动备份、schema 验证、自动回滚）
- [upgrade-guard](https://github.com/jzOcb/upgrade-guard) — 安全升级 OpenClaw：快照、验证、自动回滚、OS 级 watchdog
