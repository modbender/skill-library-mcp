# 语义检查流程图

## 完整流程

```
用户消息
    ↓
Step 1: 关键词匹配
    ├── 命中 continue → B分支
    ├── 命中 new_session → C分支
    └── 命中任务类型 → C分支
    
未命中 → Step 2: 指示词检测
    ├── 命中 (这个/那个/它) → B分支
    
未命中 → Step 3: 词汇重叠度
    ├── Jaccard >= 0.1 → B分支
    └── Jaccard < 0.1 → C分支 (默认)
```

## 分支处理

### B 分支 (continue)
- 保持当前模型池
- 输出声明: "延续 保持当前模型池【xx池】"

### C 分支 (新会话)
1. 切换模型池 (session_status --model)
2. 归档上下文到 memory/YYYY-MM-DD.md
3. 发送截止符 prompt
4. 输出声明: "执行xx 新会话 应使用xx池 已切换为xx模型"

## 声明格式

| 分支 | 格式 |
|------|------|
| B | `<action> 保持当前模型池【xx池】` |
| C | `<action> 新会话 应使用xx池 已切换为xx模型` |

## 检测方法输出

```json
{
  "detection_method": "keyword_continue",  // 关键词-延续
  "detection_method": "keyword",          // 关键词-任务类型
  "detection_method": "indicator",         // 指示词
  "detection_method": "embedding_jaccard", // 词汇重叠度
  "detection_method": "default"            // 默认
}
```

## 配置文件

- `config/pools.json` - 模型池定义
- `config/tasks.json` - 任务类型关键词
