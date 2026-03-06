# Memoria System

一个完整的长期记忆管理系统，为AI助手提供类人类的多层记忆架构。

## 概述

Memoria System 实现了类似人类认知系统的记忆分层架构：

- **语义记忆 (Semantic)** - 事实、概念、知识
- **情景记忆 (Episodic)** - 事件、经历、对话
- **程序记忆 (Procedural)** - 技能、流程、习惯
- **工作记忆 (Working)** - 当前会话上下文
- **索引 (Index)** - 快速检索目录

## 安装

```bash
openclaw skill install memoria-system
```

## 快速开始

1. **初始化记忆目录**
   ```bash
   ./memory-migrate.sh init
   ```

2. **创建每日记忆**
   ```bash
   ./memory-migrate.sh daily "2026-02-26"
   ```

3. **备份记忆**
   ```bash
   ./memory-backup.sh
   ```

4. **健康检查**
   ```bash
   ./memory-health-check.sh
   ```

## 目录结构

```
memory/
├── semantic/          # 事实知识
│   ├── facts.md
│   ├── concepts.md
│   └── knowledge/
├── episodic/          # 事件经历
│   ├── YYYY-MM-DD.md
│   └── events/
├── procedural/        # 技能流程
│   ├── skills.md
│   ├── workflows.md
│   └── scripts/
├── working/           # 当前上下文
│   ├── current.md
│   └── session/
└── index/             # 索引目录
    ├── tags.json
    ├── timeline.json
    └── search/
```

## 核心脚本

| 脚本 | 功能 |
|------|------|
| `memory-backup.sh` | 增量备份记忆数据 |
| `memory-migrate.sh` | 迁移/初始化记忆结构 |
| `memory-rollback.sh` | 回滚到指定版本 |
| `memory-health-check.sh` | 完整性检查与修复 |

## 配置

编辑 `config.json` 自定义：
- 备份保留策略
- 索引更新频率
- 存储路径

## 许可证

MIT
