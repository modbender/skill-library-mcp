# Step 1: 需求收集

## 目标
初始化运行环境，收集用户研究需求，支持断点恢复。

## 执行步骤

### 1.1 检查断点恢复

检查用户是否指定了已有的运行目录：

```
如果 runs/<slug>/progress.json 存在：
  → 读取 progress.json
  → 显示当前进度给用户
  → 从中断步骤恢复执行
  → 跳转到对应步骤的 workflow 文档
```

### 1.2 收集需求信息

向用户获取以下信息：

| 字段 | 必填 | 说明 |
|------|------|------|
| `topic` | ✅ | 研究主题（中文或英文） |
| `topic_en` | ✅ | 主题英文表述（用于 Reddit 搜索） |
| `audience` | ❌ | 目标受众描述（默认：对该主题感兴趣的中文互联网用户） |
| `focus` | ❌ | 特别关注的细分方向 |

### 1.3 初始化运行目录

```bash
# 生成 slug（topic_en 的 kebab-case 形式）
# 例如：topic_en="Machine Learning" → slug="machine-learning"
mkdir -p runs/<slug>/pieces
```

### 1.4 创建 progress.json

```json
{
  "topic": "机器学习",
  "topic_en": "Machine Learning",
  "audience": "对该主题感兴趣的中文互联网用户",
  "focus": "",
  "slug": "machine-learning",
  "current_step": 1,
  "steps": {
    "1": { "status": "completed", "timestamp": "2025-01-01T00:00:00Z" },
    "2": { "status": "pending" },
    "3": { "status": "pending" },
    "4": { "status": "pending" },
    "5": { "status": "pending" },
    "6": { "status": "pending" },
    "7": { "status": "pending" }
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### 1.5 更新进度

将 `progress.json` 的 Step 1 标记为 `completed`，`current_step` 设为 `2`。

## 输出

- `runs/<slug>/` 目录已创建
- `runs/<slug>/progress.json` 已初始化
- 进入 Step 2

## 下一步

→ [Step 2: 关键词设计](step-2-keywords.md)
