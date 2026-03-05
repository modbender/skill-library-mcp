---
name: fanfic-writer
version: 2.1.0
description: 自动化小说写作助手 v2.1 - 基于证据的状态管理、多视角QC、原子I/O、每个阶段人工确认
homepage: https://github.com/openclaw/clawd
metadata:
  openclaw:
    emoji: "📖"
    category: "creative"
---
# Fanfic Writer v2.1 - 自动化小说写作系统 / Automated Novel Writing System

**版本 Version**: 2.1.0  
**架构 Architecture**: 基于证据的状态管理 with atomic I/O  
**安全机制 Safety**: Auto-Rescue, Auto-Abort Guardrail, FORCED 连击熔断  
**核心特性**: 每个阶段人工确认

---

## 系统概览 / System Overview

Fanfic Writer v2.1 是一套生产级的小说写作流水线，每个阶段都需要人工确认：

/ Fanfic Writer v2.1 is a production-grade novel writing pipeline with human confirmation at each phase:

- **9 阶段流水线 / 9 Phase Pipeline**: 从初始化到最终QC
- **7 状态面板 / 7 State Panels**: 角色、剧情线、时间线、道具、地点、POV规则、会话记忆
- **证据链 / Evidence Chain**: 所有状态变更带有 (章节, 片段, 置信度) 追踪
- **原子I/O / Atomic I/O**: temp → fsync → rename 模式 + 快照回滚
- **多视角QC / Multi-Perspective QC**: 3-评审协议 + 100分制评分
- **安全机制 / Safety Mechanisms**: Auto-Rescue, Auto-Abort
- **人工确认 / Human Confirmation**: 每个阶段必须确认才能继续

---

## 人工确认流程 / Human Confirmation Flow

根据设计文档，每个阶段都需要人工确认：

| 阶段 Phase | 需要确认的内容 | 状态 Status |
|-----------|---------------|-------------|
| Phase 1 | 书名、类型、字数、存放目录 | 必需 |
| Phase 2 | 风格指南 | 必需 |
| Phase 3 | 主线大纲 | 必需 |
| Phase 4 | 章节规划 | 必需 |
| Phase 5 | 世界观设定 | 必需 |
| Phase 6 | 每章正文后确认进入下一章 | 必需 |
| Phase 7 | Backpatch 确认 | 必需 |
| Phase 8-9 | 最终合并确认 | 必需 |

---

## 快速开始 / Quick Start

### 通过 OpenClaw 调用

```
帮我写一本都市灵异小说
```

AI 会引导你完成每个阶段的确认。

### 通过 CLI

```bash
# 初始化新书 (每个阶段会确认)
python -m scripts.v2.cli init

# 写作 (每章会确认)
python -m scripts.v2.cli write --run-dir <path>
```

---

## 架构 / Architecture

### 目录结构 / Directory Structure

```
novels/
└── {book_title_slug}__{book_uid}/
    └── runs/
        └── {run_id}/
            ├── 0-config/              # 配置层
            ├── 1-outline/             # 大纲层
            ├── 2-planning/           # 规划层
            ├── 3-world/              # 世界观层
            ├── 4-state/              # 运行时状态 (7面板)
            ├── drafts/                # 草稿层
            ├── chapters/              # 最终章节
            ├── anchors/               # 锚点
            ├── logs/                  # 日志
            ├── archive/              # 归档
            └── final/                 # 最终输出
```

---

## 阶段参考 / Phase Reference

| 阶段 Phase | 名称 Name | 描述 Description | 需要确认 |
|-----------|-----------|-----------------|---------|
| 1 | Initialization | 创建工作空间、配置 | ✅ 书名/类型/字数/目录 |
| 2 | Style Guide | 定义叙事风格 | ✅ 风格指南 |
| 3 | Main Outline | 生成书籍级情节结构 | ✅ 主线大纲 |
| 4 | Chapter Planning | 详细章节列表与钩子 | ✅ 章节规划 |
| 5 | World Building | 角色、阵营、规则、道具 | ✅ 世界观 |
| 5.5 | Alignment Check | 验证世界观匹配意图清单 | 自动 |
| 6 | Writing Loop | 清洗→草稿→QC→提交 | ✅ 每章确认 |
| 7 | Backpatch Pass | FORCED章节回补修复 | ✅ 确认 |
| 8 | Merge Book | 合并章节为最终版本 | ✅ 确认 |
| 9 | Whole-Book QC | 最终7点质量检查 | ✅ 确认 |

---

## 阶段6: 写作循环 (核心) / Phase 6: Writing Loop (Core)

### 确认流程 / Confirmation Flow

```
[生成大纲] → 用户确认 → [生成正文] → QC评分 → 用户确认 → [下一章]
```

### QC 评分标准

| 分数 Score | 状态 Status | 动作 Action |
|-----------|------------|------------|
| ≥85 | PASS | 保存，继续 |
| 75-84 | WARNING | 保存（带警告），继续 |
| <75 | REVISE | 重试 |
| 第三次<75 | FORCED | 保存，进Backpatch |

---

## 配置 / Configuration

### 0-book-config.json

```json
{
  "version": "2.1.0",
  "book": {
    "title": "书名",
    "title_slug": "book_slug",
    "book_uid": "8char_hash",
    "genre": "都市灵异",
    "target_word_count": 100000,
    "chapter_target_words": 2500
  },
  "generation": {
    "model": "moonshot/kimi-k2.5",
    "mode": "manual",
    "max_attempts": 3,
    "auto_threshold": 85,
    "auto_rescue_enabled": true
  }
}
```

---

## OpenClaw 集成 / OpenClaw Integration

### 模型说明

**重要**: 这个 skill 不硬编码任何模型。当 OpenClaw 调用此 skill 时，自动使用 OpenClaw 当前配置的模型。

### 函数入口

```python
from scripts.v2.openclaw_entry import run_skill, get_required_confirmations

# 获取某阶段需要确认的内容
confirmations = get_required_confirmations("6_write")
# Returns: ["每章正文生成后确认", "每章评分确认"]

# 运行 skill - 模型由 OpenClaw 自动提供
result = run_skill(
    book_title="我的小说",
    genre="都市",
    target_words=100000,
    mode="manual"
    # oc_context 由 OpenClaw 自动传入，包含当前模型
)
```

### oc_context 参数

OpenClaw 会自动传入 `oc_context` 参数，包含：
- `model_call` - 调用当前模型的方法
- `model_name` - 当前模型名称（可选）
- `generate` - 备选方法（可选）

---

## 开发 / Development

### 模块结构 / Module Structure

```
scripts/v2/
├── __init__.py
├── utils.py              # ID生成、slug、路径
├── atomic_io.py          # 原子写入、快照
├── workspace.py          # 目录管理
├── config_manager.py     # 配置I/O
├── state_manager.py      # 7面板
├── prompt_registry.py    # 模板注册表
├── prompt_assembly.py   # 提示词构建
├── price_table.py       # 费率表管理
├── resume_manager.py    # 断点续传、锁管理
├── phase_runner.py      # 阶段1-5
├── writing_loop.py       # 阶段6
├── safety_mechanisms.py  # 阶段7-9
├── cli.py               # CLI入口
└── openclaw_entry.py    # OpenClaw入口 (v2.1新增)
```

---

## 版本历史 / Version History

### v2.1.0 (2026-02-16)
- ✅ 每个阶段人工确认机制
- ✅ OpenClaw 函数入口
- ✅ 接入真实模型 API
- ✅ 修复 Windows 兼容性
- ✅ 完善中文文档

### v2.0.0 (2026-02-11)
- 初始版本
- 9阶段流水线
- 7状态面板
- 多视角QC

---

## 许可证 / License

MIT License
