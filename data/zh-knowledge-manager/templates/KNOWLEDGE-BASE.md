# 知识管理协议

## 知识来源

| 来源 | 方式 | 说明 |
|------|------|------|
| 日志自动同步 | `km sync` | 每日从 memory/YYYY-MM-DD.md 提取带 PREFIX 的条目 |
| 对话知识提取 | `km extract` | 从 session dump 中 LLM 提取，需人工审阅 |
| 老板手动指令 | 直接写 `[KB:xxx]` | 老板口述业务规则时直接用此 PREFIX |
| 文档阅读任务 | 见 kb-tasks/ | 阅读外部文档后手动沉淀 |

## 存储结构

```
memory/kb/
├── domains/       ← 业务领域知识（RESEARCH/KB/BOSS 映射到这里）
├── projects/      ← 项目知识（PROJECT/ISSUE 映射到这里）
├── tech/          ← 技术知识（INFRA/CONFIG 映射到这里）
├── people.md      ← 人物与组织
├── glossary.md    ← 术语表
├── decisions.md   ← 关键决策记录
└── sync-state.json ← 去重状态（自动维护，勿手动编辑）
```

## 条目格式

所有 kb/ 文件中的条目统一为：

```markdown
### [PREFIX] 标题
正文要点。
来源: YYYY-MM-DD 日志 | #tag1 #tag2
```

## 日常维护

- **每日**：Heartbeat 自动运行 `km sync --days 1`
- **每周**：运行 `km digest` 检查知识分布和空白
- **每月**：运行 `km stats` 更新 kb-index.md
- **过期处理**：超过 6 个月未更新的条目，标记 `[ARCHIVE]` 前缀
