# Three-Tier Memory - 命令参考

## 命令总览

| 命令 | 说明 |
|------|------|
| `init` | 初始化记忆系统 |
| `add` | 添加记忆 |
| `search` | 搜索长期记忆 |
| `summary` | 手动触发摘要 |
| `status` | 查看状态 |
| `window` | 查看短期窗口 |

## add 命令

```bash
# 短期记忆
python3 memory_manager.py add --type short --content "用户喜欢黑色"

# 中期记忆
python3 memory_manager.py add --type medium --content "项目讨论摘要"

# 长期记忆
python3 memory_manager.py add --type long --content "用户邮箱: lei@example.com"
```

## search 命令

```bash
# 搜索
python3 memory_manager.py search "用户的偏好" --top-k 3
```

## Hook 配置

已包含 `hooks/memory-manager-hook/`:

```bash
# 启用 Hook
openclaw hooks enable memory-manager-hook
```

## 文件结构

```
memory/
├── config.json          # 配置
├── sliding-window.json  # 短期记忆
├── summaries/           # 中期记忆
│   └── 2026-02-16.json
└── vector-store/        # 长期记忆 (ChromaDB)
```

## LLM 摘要

使用 GLM-4-Flash 自动生成摘要：
- 提取用户意图
- 总结事实结论
- 记录用户偏好
