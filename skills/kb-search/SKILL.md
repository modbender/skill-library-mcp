---
name: kb-search
description: Knowledge Base Search - 搜索 OpenClaw 知识库文档
---

# kb-search Skill

> Knowledge Base Search - 搜索 OpenClaw 知识库文档

---

## 🎯 解决的痛点

| Problem | Solution |
|---------|----------|
| **遇到问题不知道查文档** | 快速搜索知识库 |
| **文档太多找不到** | 关键词 + 类型过滤 |
| **重复踩坑** | 知识库沉淀解决方案 |

---

## ✨ 核心功能

### 1. 🔍 关键词搜索
- 搜索 docs.openclaw.ai 文档
- 高亮匹配内容
- 返回文档摘要

### 2. 📂 类型过滤
| 类型 | 说明 | 图标 |
|------|------|------|
| error | 错误/故障排除 | ❌ |
| config | 配置相关 | ⚙️ |
| guide | 安装/部署 | 📖 |
| cli | CLI命令 | 💻 |
| channel | 通道配置 | 📱 |
| general | 一般文档 | 📄 |

### 3. 📊 智能排序
- 按相关性排序
- 限制返回数量
- 显示匹配度

---

## 🚀 快速开始

**触发条件：**
- `/kb-search <关键词>`
- 遇到报错时自动触发

**执行方式：**
```bash
# 简单搜索
/kb-search subagent

# 按类型搜索
/kb-search "401 认证" --type=error

# 限制数量
/kb-search "gateway" --limit=5
```

---

## 📁 知识库位置

```
~/.openclaw/workspace/docs.openclaw.ai/
├── 01-concepts/     # 核心概念
├── 02-config/       # 配置指南
├── 03-cli/          # CLI命令
├── 04-channels/     # 通道配置
├── 05-skills/       # 技能
└── 06-maintenance/   # 运维保障
```

---

## 💡 使用示例

### 场景1：Subagent 认证失败
```
用户：/kb-search "401 认证"

返回：
🔍 搜索: 401 认证
📚 类型: error
📊 结果: 3 篇文档

1. ❌ cli_security.md
   📁 gateway/security.md
   📝 ...认证失败通常由于 API Key 无效或过期...
```

### 场景2：模型配置问题
```
用户：/kb-search "模型配置"

返回：
🔍 搜索: 模型配置
📚 类型: config
📊 结果: 5 篇文档
```

---

## 📖 故障排查流程

```
问题发生
    ↓
/kb-search <错误信息>
    ↓
查看相关文档
    ↓
根据文档指导解决问题
    ↓
解决成功（可选：补充到知识库）
```

---

## ⚠️ 注意事项

- 依赖 docs.openclaw.ai 文档库
- 当前基于关键词匹配，后续可升级语义搜索
- 建议配合 System Agent 健康监控使用

---

## 📝 更新日志

- **2026-02-19**: 初始化版本
