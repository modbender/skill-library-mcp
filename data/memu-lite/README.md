# memU-lite

> 🧠 轻量级结构化记忆系统 for OpenClaw  
> 灵感来自 [memU](https://github.com/NevaMind-AI/memU)，零外部依赖

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://github.com/openclaw/openclaw)

## ✨ 特性

- **三层架构** - Category Layer (概览) + Item Layer (原子记忆) + Resource Layer (原始记录)
- **五种类型** - preference/knowledge/relationship/task/skill
- **标签索引** - 快速检索和关联
- **零依赖** - 纯 Markdown + OpenClaw 原生 `memory_search`/`memory_get` 工具
- **易迁移** - 未来可无缝升级到完整 memU
- **自动化工具** - 提供 memu-add/memu-search/memu-backup/memu-tags/memu-clean 等工具（v1.1.0 新增）
- **过期机制** - 支持记忆自动归档（v1.1.0 新增）

## 📦 安装

### 方式一：ClawHub

```bash
openclaw skills install memu-lite
```

### 方式二：手动安装

```bash
git clone https://github.com/yoo-unison/memu-lite.git
cd memu-lite
./install.sh
```

## 🚀 快速开始

### 1. 初始化

```bash
# 创建记忆目录结构
mkdir -p ~/.openclaw/workspace/memory/{raw,items/{preferences,knowledge,relationships,tasks,skills},indexes}
```

### 2. 创建第一条记忆

在 `items/preferences/` 下创建文件 `P-20260302-001-xxx.md`：

```markdown
## P-20260302-001 用户决策风格偏好

- **类型**: preference
- **来源**: 2026-03-02 对话
- **日期**: 2026-03-02
- **置信度**: high
- **标签**: #偏好 #决策风格
- **内容**: 
  用户要求独立评估，不盲目跟风，偏好轻量方案。
- **关联**: [[R-20260302-001]]
```

### 3. 更新索引

编辑 `MEMORY.md` 添加记忆到索引表格。

## 📖 文档

- [使用指南](SKILL.md) - 完整的 API 和使用说明
- [记忆模板](memory/items/TEMPLATE.md) - 记忆文件格式参考

## 🗂️ 目录结构

```
memory/
├── MEMORY.md                 # 顶层索引 + 快速概览
├── raw/                      # 原始对话记录
├── items/                    # 原子化记忆单元
│   ├── preferences/          # 用户偏好
│   ├── knowledge/            # 领域知识
│   ├── relationships/        # 人际关系
│   ├── tasks/                # 待办事项
│   └── skills/               # 技能方法
└── indexes/                  # 检索辅助
    └── tags.md               # 标签索引
```

## 📊 与 memU 对比

| 特性 | memU | memU-lite |
|------|------|-----------|
| 自动提取 | ✅ | ⚠️ 需主动记录 |
| 主动预判 | ✅ | ❌ |
| 向量检索 | ✅ | ⚠️ 依赖 memory_search |
| 外部依赖 | Postgres + API | ❌ 无 |
| 部署复杂度 | 中 | 低 |

## 🎯 使用场景

- 记住用户偏好和习惯
- 构建项目知识库
- 长期上下文管理
- 多 Agent 记忆共享（通过共享 memory 目录）

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

Apache 2.0

## 🙏 致谢

灵感来自 [memU](https://github.com/NevaMind-AI/memU) - Memory as File System, File System as Memory
