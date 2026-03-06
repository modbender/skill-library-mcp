---
name: auto-agent-router
description: "根据消息命令自动路由到子 Agent。**Agent 应该：收到消息时首先检查是否包含 /coder、/writer 等命令，如果是则调用 sessions_spawn 启动对应子 Agent。**"
metadata:
  openclaw:
    emoji: "🤖"
    requires:
      bins: ["python3"]
---

# Auto Agent Router - 自动子 Agent 路由

根据消息中的命令自动路由到合适的子 Agent，实现并发处理和专业化分工。

---

## 🎯 When to Use

### Agent 行为准则

**收到每条消息时，首先检查是否包含命令**：

✅ **USE this skill when:**

- 消息开头是 `/coder` → 启动 coder Agent (qwen3-coder-next)
- 消息开头是 `/writer` → 启动 writer Agent (qwen3.5-plus)
- 消息开头是 `/analyze` → 启动 analyst Agent (qwen3.5-plus)
- 消息开头是 `/research` → 启动 researcher Agent (gemini-3.1-pro)
- 消息开头是 `/review` → 启动 reviewer Agent (qwen3-max)
- 消息开头是 `/devops` → 启动 devops Agent (qwen3.5-plus)
- 消息开头是 `/auto` → 自动判断合适的 Agent

**检查流程**：
1. 收到消息 → 首先检查开头是否包含 `/xxx` 命令
2. 如果有命令 → 调用 `sessions_spawn` 启动对应子 Agent
3. 如果没有命令 → 主 Session 直接处理

---

## 🚫 When NOT to Use

❌ **DON'T use this skill when:**

- 消息中没有命令 → 主 Session 直接处理
- 命令不在消息开头 → 如"请帮我 /coder"不触发
- 简单问答不需要子 Agent → 主 Session 处理即可
- 命令在消息中间或结尾 → 不触发路由

---

## 📋 Trigger Rules

### 触发格式（严格模式）

| 格式 | 示例 | 结果 |
|------|------|------|
| **命令开头** | `/coder 写代码` | ✅ 触发 |
| **@名字 + 命令** | `@小牛马 /coder 写代码` | ✅ 触发 |
| **消息中包含命令** | `请帮我 /coder 写代码` | ❌ 不触发 |

### 可用命令

| 命令 | Agent | 模型 | 用途 |
|------|-------|------|------|
| `/coder` | coder | qwen3-coder-next | 代码任务 |
| `/writer` | writer | qwen3.5-plus | 写作任务 |
| `/analyze` | analyst | qwen3.5-plus | 数据分析 |
| `/research` | researcher | gemini-3.1-pro | 调研任务 |
| `/review` | reviewer | qwen3-max | 审查优化 |
| `/devops` | devops | qwen3.5-plus | 运维操作 |
| `/auto` | 自动判断 | 根据内容 | 智能路由 |

---

## 🔧 How to Use

### 基本用法

**用户发送命令**：
```
/coder 写个 Hello World
```

**Agent 响应**：
```
✅ 🧑‍💻 已启动 **coder** (代码专家) 处理您的任务

─────────────────────
🤖 处理者：Agent: 🧑💻 coder
模型：dashscope/qwen3-coder-next
```

### 带@的命令

**用户发送**：
```
@小牛马 /writer 写周报
```

**处理流程**：
1. 去掉@名字 → `/writer 写周报`
2. 匹配命令 → `/writer`
3. 启动 Agent → writer
4. 返回结果

---

## 📁 Implementation

### 核心组件

```
~/.openclaw/workspace/skills/auto-agent-router/
├── SKILL.md              # 本文档
├── config.json           # 路由配置
├── auto-trigger.py       # 触发检测
├── dingtalk-command.py   # 命令解析
├── router.py             # 路由匹配
└── logger.py             # 日志记录
```

### 调用方式

**检测命令**：
```bash
python3 ~/.openclaw/workspace/skills/auto-agent-router/auto-trigger.py "/coder 写代码"
```

**查看配置**：
```bash
cat ~/.openclaw/workspace/skills/auto-agent-router/config.json
```

**查看日志**：
```bash
tail -f /tmp/auto-route-handler.log
```

---

## 🔄 Workflow

```
用户消息：/coder 写代码
    ↓
1. 检测命令 (auto-trigger.py)
   - 去掉@名字
   - 检查开头是否匹配命令
    ↓
2. 解析命令 (dingtalk-command.py)
   - 提取命令类型
   - 提取任务内容
    ↓
3. 路由匹配 (router.py)
   - 查找 config.json
   - 确定目标 Agent
    ↓
4. 启动 Agent (sessions_spawn)
   - 创建子 Agent Session
   - 分配任务
    ↓
5. 返回结果
   - 子 Agent 完成任务
   - 推送结果给用户
```

---

## 📊 Response Format

### 启动回复

```
✅ 🧑‍💻 已启动 **coder** (代码专家) 处理您的任务

─────────────────────
🤖 处理者：Agent: 🧑💻 coder
模型：dashscope/qwen3-coder-next
```

### 完成回复

```
[子 Agent 的任务结果]

─────────────────────
🤖 处理者：Agent: 🧑💻 coder
运行时间：3s • Tokens: 20k
```

---

## ⚙️ Configuration

### config.json

```json
{
  "enabled": true,
  "autoRoute": true,
  "flexible": false,
  "bot_names": ["小牛马", "xiaoniuma", "AI 助手", "..."],
  "rules": [
    {
      "type": "coding",
      "keywords": ["代码", "函数", "bug"],
      "agent": "coder",
      "model": "dashscope/qwen3-coder-next",
      "priority": "high"
    }
  ],
  "fallback": {
    "agent": null,
    "model": "dashscope/qwen3.5-plus"
  }
}
```

### 自定义 Agent

编辑 `config.json` 的 `rules` 数组添加新规则：

```json
{
  "type": "custom",
  "keywords": ["关键词 1", "关键词 2"],
  "agent": "custom_agent",
  "model": "模型名称",
  "priority": "medium"
}
```

---

## 📝 Notes

- **严格模式**：命令必须在消息开头，中间或结尾不触发
- **@名字可选**：支持带@或不带@的命令
- **自动学习**：支持自动学习新的机器人名字
- **并发处理**：多个子 Agent 可以并行运行
- **Session 隔离**：每个子 Agent 有独立的 Session
- **日志位置**：`/tmp/auto-route-handler.log`

---

## 🧪 Testing

### 测试命令

```bash
# 测试触发
python3 ~/.openclaw/workspace/skills/auto-agent-router/auto-trigger.py "/coder 写代码"

# 测试@命令
python3 ~/.openclaw/workspace/skills/auto-agent-router/auto-trigger.py "@小牛马 /coder 写代码"

# 测试不触发
python3 ~/.openclaw/workspace/skills/auto-agent-router/auto-trigger.py "请帮我 /coder"
```

### 预期结果

| 输入 | 输出 |
|------|------|
| `/coder 写代码` | ✅ 触发，路由到 coder |
| `@小牛马 /coder 写代码` | ✅ 触发，路由到 coder |
| `请帮我 /coder` | ❌ 不触发，主 Session 处理 |

---

## 🔗 Related

- **MEMORY.md** - 包含配置和使用记录
- **sessions_spawn** - 启动子 Agent 的工具

---

**最后更新**: 2026-02-28  
**版本**: 1.0.0
