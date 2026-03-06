---
name: white-stone-mem
description: 记忆系统 - 包含常识记忆、项目记忆、错题本和每日回顾。按需加载，避免记忆污染。
metadata:
  openclaw:
    emoji: 🧠
---

# 白石记忆系统 (White Stone Memory)

你的个人记忆系统，包含4类记忆，按需加载。

## 记忆分类

### 1. 常识记忆
- **位置**: `memory/knowledge/common.md`
- **内容**: 工作习惯、逻辑思维、产品意识
- **加载**: Agent启动时自动读取

### 2. 项目记忆
- **位置**: `memory/projects/[项目名].md`
- **加载**: 用户明确提及项目时加载
- **不加载**: Agent工作时禁止主动读取，避免污染

### 3. 错题本
- **位置**: `memory/errors/`
- **内容**: 使用错误、经验总结
- **加载**: 所有Agent/Sub-Agent启动时自动加载

### 4. 每日回顾
- **位置**: `memory/daily/[日期].md`
- **时间**: 每天凌晨自动创建
- **内容**: 工作总结、待提炼内容

## 目录结构

```
~/.openclaw/workspace/memory/
├── knowledge/
│   └── common.md
├── projects/
│   └── [项目名].md
├── errors/
│   └── [类别].md
└── daily/
    └── YYYY-MM-DD.md
```

## 重要规则

1. 不主动读取项目记忆 - 只有用户明确要求时才加载
2. 错题本全局共享 - 所有Agent启动时必须加载
3. 常识记忆启动加载 - Agent启动时自动读取
4. 每日回顾定时 - 凌晨创建，可 later 手动补充

---

## 使用方法

### 初始化

首次使用需要创建目录结构：

```bash
mkdir -p memory/knowledge memory/projects memory/errors memory/daily
```

### 常识记忆

```bash
# 读取
cat memory/knowledge/common.md

# 编辑
vim memory/knowledge/common.md
```

### 项目记忆

```bash
# 加载项目记忆（用户明确要求时）
cat memory/projects/[项目名].md
```

### 错题本

```bash
# 读取错题本
cat memory/errors/*.md

# 添加新错误
echo "## 新错误\n- 问题：...\n- 原因：...\n- 解决方案：..." >> memory/errors/general.md
```

### 每日回顾

```bash
# 创建今日回顾
echo "# $(date +%Y-%m-%d) 回顾" > memory/daily/$(date +%Y-%m-%d).md
```

---

## 向量搜索功能 (可选，需配置)

### 概述

在现有关键词搜索基础上，增加向量语义搜索能力。

### 开启方式

在配置文件中启用：

```yaml
memory:
  vector_search:
    enabled: true
```

### 启用后的提示

⚠️ **开启向量搜索需要配置以下之一**：

| 选项 | 说明 |
|------|------|
| **A. Gemini API** | 提供 `GEMINI_API_KEY` 环境变量 |
| **B. 本地 Ollama** | 确保运行 `ollama run qwen3-embedding-0.6B` |

### 配置检查

```bash
# 检查 Ollama 是否运行
curl -s localhost:11434/api/tags
```

### 技术选型

| 组件 | 推荐 |
|------|------|
| Embedding | Gemini API 或 Ollama + qwen3-embedding-0.6B |
| 向量库 | FAISS 或 LanceDB |
| 索引 | HNSW (O(log n)) |

### 命令

```bash
/memory build-index   # 构建索引
/memory search "xxx"  # 搜索
/memory index-status  # 查看状态
```

### 注意

- 默认关闭向量搜索
- 启用后需配置 Gemini API Key 或本地 Ollama
- 新增/修改文件后需重新索引

---

## 更新日志

- 2026-02-28: 新增向量搜索功能设计
