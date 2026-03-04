---
name: openclaw-behavior-plan
description: Generates structured behavior plans for OpenClaw agents based on user requirements. Use when the user asks to create a plan, design agent behavior, plan multi-step tasks for OpenClaw, or when they describe a goal that needs step-by-step execution.
---

# OpenClaw 行为计划生成（openclaw-behavior-plan）

**触发时**：输出「正在触发 openclaw-behavior-plan skill」。

根据用户描述的目标或需求，生成适合 OpenClaw Agent 执行的结构化行为计划。计划应可映射到 TOOLS.md/SKILLS.md 中的工具与技能，支持多步推理循环（Load → Call → Parse → Execute → Append → Loop）。

## 1. 计划结构模板

生成计划时使用以下结构：

```markdown
# 行为计划：[任务标题]

## 目标
[一句话描述用户期望的最终结果]

## 前置条件
- [ ] 所需工具/技能是否可用
- [ ] 必要信息是否已获取

## 执行步骤

### 步骤 1: [步骤名称]
- **目的**: [本步要达成什么]
- **工具/技能**: [execute_shell | search_web | read_file | 某 skill 的 action]
- **输入**: [参数或依赖]
- **预期输出**: [本步完成后得到什么]

### 步骤 2: [步骤名称]
...

### 步骤 N: [步骤名称]
...

## 异常与回退
- 若 [某步骤] 失败 → [备选方案或重试策略]

## 完成标准
- [ ] [可验证的完成条件 1]
- [ ] [可验证的完成条件 2]
```

## 2. 生成原则

1. **步骤可执行**：每步对应 TOOLS.md 或 SKILLS.md 中的具体能力，避免抽象描述。
2. **依赖顺序**：后步骤依赖前步骤的输出时，明确写出「依赖步骤 N 的 [输出]」。
3. **工具选择**：
   - 需要当前信息 → `search_web`
   - 需要读/写文件 → `read_file` / `write_file`
   - 需要执行脚本 → `execute_shell`
   - 需要第三方服务 → 对应 skill（如 calendar、email、slack）
4. **合理粒度**：单步不宜过大（难以失败定位），不宜过小（增加循环次数）。
5. **异常处理**：对可能失败的步骤（网络、权限、格式错误）给出回退或重试说明。

## 3. 与 OpenClaw 推理循环的对应

| 计划步骤 | 推理循环中的体现 |
|---------|------------------|
| 步骤 1 执行 | Load → Call → Parse(tool_call) → Execute → Append |
| 步骤 2 执行 | 下一轮 Loop，基于步骤 1 结果继续 |
| 完成标准 | LLM 产出 final 文本、无待执行 tool_call 时停止 |

## 4. 输出格式

- 直接输出完整计划（Markdown），无需额外包装。
- 若用户需求模糊，先列出 1–2 个澄清问题，再生成计划。
- 若涉及敏感操作（如 `execute_shell` 删除、修改系统），在计划中标注「需用户确认」。

## 5. 更多示例

详见 [examples.md](examples.md)。
