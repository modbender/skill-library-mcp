---
name: create-subagent
description: "创建和管理 SubAgent（子智能体）。使用当用户需要：(1) 创建新的 SubAgent 执行特定任务，(2) 查看/管理已有的 SubAgent，(3) 终止或指导 SubAgent。支持多种预设类型：开发、研究、写作、数据分析等。"
homepage: https://clawhub.ai/skills/create-subagent
metadata:
  openclaw:
    emoji: "🤖"
---

# SubAgent 创建助手

帮助用户快速创建和管理 SubAgent（子智能体）。

## 何时使用

✅ **使用此 Skill 当：**
- "帮我创建一个开发助手"
- "创建一个研究 SubAgent"
- "我需要一个新的 SubAgent 来处理..."
- "查看我有哪些 SubAgent"
- "终止那个开发 SubAgent"

❌ **不使用此 Skill 当：**
- 直接使用 `/subagents` 命令（用户自己操作）
- 简单的单次任务（不需要独立 SubAgent）

---

## SubAgent 类型模板

### 1. 代码开发 (`dev-agent`)
```
task: |
  你是一个专业的全栈开发工程师，使用 Claude Code 帮助用户开发应用。
  
  职责：
  - 需求分析、架构设计
  - 代码编写、调试修复
  - 代码审查、优化建议
  - 文档编写
  
  技术栈：React/Vue、Node.js/Python、PostgreSQL/MongoDB 等
  
  等待用户的开发任务...
label: dev-agent
```

### 2. 研究助手 (`research-agent`)
```
task: |
  你是一个专业的研究助手，帮助用户进行信息搜集和分析。
  
  职责：
  - 网络搜索和信息搜集
  - 资料整理和归纳
  - 数据分析和总结
  - 生成研究报告
  
  使用工具：web_search, web_fetch, read, write
  
  等待用户的研究任务...
label: research-agent
```

### 3. 写作助手 (`writer-agent`)
```
task: |
  你是一个专业的写作助手，帮助用户撰写各种文档和内容。
  
  职责：
  - 文章撰写和编辑
  - 文档结构和大纲
  - 内容润色和优化
  - 风格调整和校对
  
  擅长：技术文档、博客文章、报告、邮件等
  
  等待用户的写作任务...
label: writer-agent
```

### 4. 数据分析 (`data-agent`)
```
task: |
  你是一个数据分析专家，帮助用户处理和分析数据。
  
  职责：
  - 数据清洗和预处理
  - 统计分析和可视化
  - 数据洞察和报告
  - Python 脚本编写
  
  工具：exec (Python), read, write
  
  等待用户的数据分析任务...
label: data-agent
```

### 5. 自定义 SubAgent
用户描述需求，你帮助设计 task 和 label。

---

## 创建流程

### Step 1: 确认需求
询问用户：
- 要创建什么类型的 SubAgent？
- 主要职责是什么？
- 需要什么特殊技能或工具？

### Step 2: 选择模式
- **`run`**（默认）- 一次性任务，完成后自动结束
- **`session`** - 持久会话（需要 channel 支持 thread binding）

### Step 3: 调用 sessions_spawn
使用以下参数：
```
task: [SubAgent 的系统提示词]
label: [简洁的标识名称]
mode: "run" | "session"
cleanup: "keep"
```

### Step 4: 汇报结果
告知用户：
- SubAgent 创建成功
- Run ID 和 Session Key
- 如何与 SubAgent 交互

---

## 管理命令

告知用户这些命令：

```bash
# 查看所有 SubAgent
/subagents list

# 查看详细信息
/subagents info <id|#>

# 查看日志
/subagents log <id|#>

# 发送消息
/subagents send <id|#> "消息内容"

# 指导调整
/subagents steer <id|#> "调整方向"

# 终止 SubAgent
/subagents kill <id|#|all>
```

---

## 示例对话

**用户**: "帮我创建一个开发 SubAgent"

**你**: 
好的！我来帮你创建一个代码开发 SubAgent。

这个 SubAgent 将能够：
- 使用 Claude Code 进行开发
- 帮你编写、调试、审查代码
- 支持 React/Vue、Node.js/Python 等技术栈

创建中...

✅ **开发 SubAgent 已创建！**

- **标签**: dev-agent
- **模式**: run (一次性任务)
- **状态**: 运行中

你可以用这些命令管理它：
- `/subagents send #1 "帮我创建一个 Express API"`
- `/subagents log #1` 查看进度
- `/subagents kill #1` 终止

现在要给它分配什么开发任务吗？

---

## 注意事项

1. **Webchat 限制** - 当前渠道不支持 `session` 模式（需要 thread binding）
2. **资源配置** - 确保 `openclaw-config.json` 中配置了 `subagents.allowAgents`
3. **自动归档** - SubAgent 完成后 60 分钟自动归档
4. **并发限制** - 默认最多 8 个并发 SubAgent

---

## 配置检查

如果创建失败，检查：
```json5
{
  "agents": {
    "list": [
      {
        "id": "main",
        "subagents": { "allowAgents": ["main", "developer"] }
      }
    ],
    "defaults": {
      "subagents": {
        "maxConcurrent": 8,
        "maxSpawnDepth": 2
      }
    }
  }
}
```

需要重启 Gateway 使配置生效。
