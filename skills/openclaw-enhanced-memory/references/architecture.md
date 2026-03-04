# Tagged Memory — Architecture Reference

## Overview

Tagged Memory is a file-system-based memory system designed for OpenClaw AI agents. It replaces the default flat `MEMORY.md` with a structured, categorized, and searchable memory store.

## Design Principles

1. **Files over databases** — Memory is plain Markdown files on disk. No external services, no API keys, no dependencies. `grep` always works.
2. **Categories over chronology** — Instead of one timeline, memories live in purpose-specific directories (food, training, relations, etc.).
3. **Tags over full-text search** — Inline `[category:value]` tags provide precise, structured retrieval without NLP overhead.
4. **Archive over delete** — Old memories move to `archived/` but are never removed. Nothing is lost.

## Component Diagram

```
┌─────────────────────────────────────────────┐
│                  Agent                       │
│                                              │
│  "What did I eat?"    "Who is Zhang Hao?"   │
└──────┬────────────────────────┬──────────────┘
       │                        │
       ▼                        ▼
┌──────────────────┐  ┌──────────────────────┐
│ memory_retrieval │  │  memory_tag_search   │
│ _strategy.py     │  │  .py                 │
│                  │  │                      │
│ Classifies query │  │ Scans [cat:val] tags │
│ → routes to dirs │  │ AND logic across     │
│                  │  │ all .md files        │
└──────┬───────────┘  └──────────┬───────────┘
       │                         │
       ▼                         ▼
┌─────────────────────────────────────────────┐
│              memory/ (filesystem)            │
│                                              │
│  current/   food/   training/   RELATION/   │
│  archived/  misc/   system/     connections │
└─────────────────────────────────────────────┘
       ▲
       │ monthly
┌──────┴───────────┐
│ memory_lifecycle │
│ _manager.py      │
│                  │
│ Moves files >6mo │
│ to archived/     │
└──────────────────┘
```

## Tag Format Specification

Tags follow the pattern: `[category:value]`

- **category**: A short classifier (e.g., 人物, 类型, 地点, 项目, 情绪)
- **value**: The specific entity or attribute
- Multiple tags per line are supported
- Search uses AND logic across multiple query tags

### Examples

```markdown
- Lunch at the new ramen place [类型:午餐] [地点:ramen-shop] [情绪:satisfied]
- Call with Liu Hui about invoice [人物:刘辉] [类型:开票信息] [项目:billing]
- Yoyo's vet checkup — all clear [宠物:悠悠] [类型:health-check]
```

## Retrieval Strategy — Query Classification

The retrieval strategy uses regex pattern matching to classify queries:

| Query Type | Trigger Keywords | Search Scope |
|-----------|-----------------|--------------|
| food | 吃, 午饭, 晚饭, 早餐, 外卖... | `food/`, `current/` |
| training | 训练, 运动, 健身, 跑步... | `training/`, `current/` |
| relation | Person names, 朋友, 家人... | `RELATION/`, `connections.md` |
| yoyo | 悠悠, 狗狗, 宠物... | `RELATION/悠悠.md`, `connections.md` |
| system | 系统, 配置, bug, 崩溃... | `system/` |
| mood | 心情, 开心, 难过... | `current/` |
| project | 项目, 代码, git... | `current/`, `misc/` |
| default | (unclassified) | `current/` |

## Lifecycle Rules

| Rule | Detail |
|------|--------|
| Active window | 180 days (configurable) |
| Archive trigger | File modification time > threshold |
| Archive location | `memory/archived/YYYY-MM/` |
| Deletion policy | **Never** — all archives are permanent |
| Modules archived | `current`, `food`, `training`, `misc` |
| Protected dirs | `RELATION/`, `connections.md`, `system/` (not auto-archived) |
