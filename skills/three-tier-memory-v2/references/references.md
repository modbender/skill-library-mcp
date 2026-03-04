# Memory Manager - 详细命令参考

## 命令总览

| 命令 | 说明 | 示例 |
|------|------|------|
| `init` | 初始化记忆系统 | `python3 memory_manager.py init` |
| `add` | 添加记忆 | `python3 memory_manager.py add --type short --content "内容"` |
| `search` | 搜索长期记忆 | `python3 memory_manager.py search "查询"` |
| `summary` | 手动触发摘要 | `python3 memory_manager.py summary` |
| `status` | 查看状态 | `python3 memory_manager.py status` |
| `window` | 查看短期窗口 | `python3 memory_manager.py window` |

## add 命令详情

### 添加短期记忆
```bash
python3 memory_manager.py add --type short --content "用户喜欢黑色高定"
```

### 添加中期记忆
```bash
python3 memory_manager.py add --type medium --content "今天讨论了项目架构"
```

### 添加长期记忆
```bash
python3 memory_manager.py add --type long --content "用户的名字是 Lei Zong"
```

## search 命令详情

```bash
# 基础搜索
python3 memory_manager.py search "用户的偏好"

# 指定返回数量
python3 memory_manager.py search "项目进度" --top-k 5
```

## 配置文件详解

`memory/config.yaml`:

```yaml
memory:
  short_term:
    enabled: true           # 是否启用
    window_size: 10         # 滑动窗口大小
    max_tokens: 2000        # 最大 token 数

  medium_term:
    enabled: true           # 是否启用
    summary_threshold: 4000  # 触发摘要的 token 阈值
    summary_model: "glm-4-flash"  # 摘要模型

  long_term:
    enabled: true           # 是否启用
    backend: "chromadb"     # 向量库后端
    top_k: 3                # 检索返回数量
    min_relevance: 0.7      # 最小相似度
```

## 集成到 OpenClaw

在 Skill 中调用：

```python
import subprocess

# 添加短期记忆
subprocess.run([
    'python3', 
    'skills/memory-manager/scripts/memory_manager.py',
    'add', '--type', 'short', '--content', user_message
])

# 搜索记忆
result = subprocess.run([
    'python3',
    'skills/memory-manager/scripts/memory_manager.py',
    'search', user_query,
    '--top-k', '3'
], capture_output=True, text=True)
```

## 数据结构

### sliding-window.json
```json
{
  "messages": [
    {"content": "...", "timestamp": "2026-02-16T14:00:00", "metadata": {}}
  ],
  "updated_at": "2026-02-16T14:30:00"
}
```

### summaries/YYYY-MM-DD.json
```json
{
  "date": "2026-02-16",
  "summaries": [
    {"content": "...", "type": "auto-summary", "timestamp": "..."}
  ]
}
```

### Vector Store (ChromaDB)
- Collection: `memory`
- Document: 原始文本
- Metadata: timestamp, tags, source
