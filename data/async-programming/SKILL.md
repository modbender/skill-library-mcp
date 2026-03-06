---
name: async-programming
description: |
  异步编程任务处理。当用户请求编程任务时，立即调用子 agent + 立即回复确认，无需等待完成即可继续聊天。
---

# 异步编程任务处理技能

## 触发条件

当用户请求涉及以下内容时，激活此技能：

- ✅ 编写/修改代码
- ✅ 添加新功能
- ✅ 修复 bug
- ✅ 重构代码
- ✅ 创建脚本
- ✅ 项目配置
- ✅ 依赖安装

## 核心原则

**收到编程任务 → 立即调用子 agent + 立即回复确认 = 可以继续聊天**

---

## 执行流程

### 1. 调用子 agent

```javascript
sessions_spawn({
  task: "{具体任务描述，包含项目路径和具体要求}",
  label: "{项目名} - {任务类型}",
  model: "bailian/qwen3-coder-plus",
  mode: "run",
  runTimeoutSeconds: 900
})
```

**参数说明：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `task` | 明确的任务描述 | "给 Stock-Analysis 添加 Excel 导出功能" |
| `label` | 任务标识，格式 `项目名 - 任务类型` | `Stock-Analysis - 功能开发` |
| `model` | 编程任务统一用 coder 模型 | `bailian/qwen3-coder-plus` |
| `runTimeoutSeconds` | 超时时间（秒） | `900` (15 分钟) |

### 2. 立即回复确认（关键！）

**调用子 agent 后，立即回复用户，不要等待完成！**

回复模板：
```
✅ 任务已接收

**正在处理：**
- 项目：{项目名}
- 任务：{任务简述}
- 执行者：子 agent（编程助手）
- 预计时间：2-5 分钟

你可以在等待期间继续问我其他问题，完成后我会通知你。
```

### 3. 完成后汇报

子 agent 完成后会自动发送结果，转发给用户：

```
✅ {任务名} 完成了！

**完成内容：**
- {改动 1}
- {改动 2}

**文件变更：**
- {文件路径 1}
- {文件路径 2}

需要调整或继续开发吗？
```

---

## 多任务并发

用户可以连续下达多个编程任务，子 agent 并行执行：

```
用户："给项目 A 加个功能"
  → 调用子 agent #1
  → 立即回复确认

用户："帮项目 B 修复 bug"
  → 调用子 agent #2
  → 立即回复确认

用户："项目 C 也帮我看看"
  → 调用子 agent #3
  → 立即回复确认
```

**并发限制：** 最多 8 个子 agent 同时运行（`agents.defaults.subagents.maxConcurrent`）

---

## 任务追踪

当用户询问进度时，使用：

```javascript
subagents(action="list")
```

回复格式：
```
**当前任务进度：**

✅ 已完成 (2)
- Stock-Analysis - 功能开发
- Amazon-Analyzer - 数据抓取

⏳ 进行中 (1)
- Skills-Bank - 文档整理 (预计还需 1 分钟)

❌ 失败 (0)
```

---

## 示例对话

### 示例 1：单个任务

```
用户：给 Stock-Analysis 加个导出 Excel 的功能

助手：
✅ 任务已接收

**正在处理：**
- 项目：Stock-Analysis
- 任务：添加 Excel 导出功能
- 执行者：子 agent（编程助手）
- 预计时间：2-5 分钟

你可以在等待期间继续问我其他问题，完成后我会通知你。

---（2 分钟后，子 agent 完成）---

✅ Excel 导出功能完成了！

**完成内容：**
- 新增 `export_to_excel()` 函数
- 支持导出 CSV 和 JSON 结果
- 添加 openpyxl 依赖

**文件变更：**
- /root/Stock-Analysis/stock_analyzer.py (新增 35 行)
- /root/Stock-Analysis/requirements.txt (新增 openpyxl)

需要测试或继续开发吗？
```

### 示例 2：多任务并发

```
用户：帮我给三个项目都加个 README

助手：
✅ 收到！正在并行处理三个项目：

**任务队列：**
1. Stock-Analysis - 完善 README
2. Amazon-Analyzer - 完善 README
3. Skills-Bank - 完善 README

预计 5-8 分钟完成，你可以继续问我其他问题。

---（5 分钟后）---

✅ 三个项目的 README 都完成了！

**完成情况：**
- ✅ Stock-Analysis - 已添加安装和使用说明
- ✅ Amazon-Analyzer - 已添加 API 配置说明
- ✅ Skills-Bank - 已添加技能分类说明

需要调整吗？
```

---

## 注意事项

1. **不要等待子 agent 完成才回复** - 这是核心原则
2. **任务描述要清晰** - 子 agent 需要明确的指令
3. **label 要规范** - 方便追踪和管理
4. **超时处理** - 15 分钟未完成，主动告知用户
5. **错误处理** - 子 agent 失败时，解释原因并提供解决方案

---

## 相关配置

子 agent 配置位于 `openclaw.json`：

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxConcurrent": 8,
        "maxSpawnDepth": 2,
        "model": "bailian/qwen3.5-plus",
        "runTimeoutSeconds": 600,
        "archiveAfterMinutes": 60
      }
    }
  }
}
```

---

*此技能确保贾维斯可以并行处理多个编程任务，同时保持与用户的即时沟通*
