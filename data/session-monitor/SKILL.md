---
name: session-monitor
description: 自动监控和显示会话状态信息，包括token消耗、模型信息和功能状态。支持开关控制和自定义显示格式。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "emoji": "📊"
      }
  }
---

# Session Monitor - 会话状态监控

## 功能概述

自动在每次对话回复中添加简洁的会话状态信息，包括：
- 当前使用的模型
- 输入/输出 token 消耗  
- 上下文使用率
- 功能开关状态（Reasoning/Elevated等）

## 显示格式

默认格式：`[🧠 qwen3-max | 📥123k/📤420 | Context: 47%]`

可配置格式选项：
- `compact`: 紧凑模式 `[qwen3-max|123k/420|47%]`
- `detailed`: 详细模式（包含功能状态）
- `hidden`: 隐藏模式（仅通过命令查看）

## 控制命令

### 开关控制
```bash
/token on      # 启用状态显示
/token off     # 禁用状态显示  
/token toggle  # 切换显示状态
```

### 格式控制
```bash
/token format compact    # 设置紧凑格式
/token format detailed   # 设置详细格式  
/token format default    # 恢复默认格式
```

### 手动查看
```bash
/status        # 查看详细状态信息
/token         # 查看当前token统计
```

## 配置

通过环境变量控制默认行为：
- `SESSION_MONITOR_ENABLED=true|false` (默认: true)
- `SESSION_MONITOR_FORMAT=default|compact|detailed|hidden` (默认: default)

## 集成

此技能与 OpenClaw 的 hooks 系统集成，在每次响应后自动注入状态信息。
支持与其他监控技能协同工作，如 task-persistence 和 gateway-monitor。

## 使用示例

启用后，每条消息底部会自动显示：
```
这是正常的回复内容...

[🧠 qwen3-max | 📥123k/📤420 | Context: 47%]
```