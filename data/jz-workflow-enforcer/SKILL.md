---
name: agent-workflow-enforcer
version: 1.0.0
description: |
  让 AI Agent 的执行流程稳定可控。
  通过 Gate 门禁、强制输出格式、Style Context 持久化，
  把"建议"变成"必须"，解决 Agent 选择性执行的问题。
homepage: https://github.com/example/agent-workflow-enforcer
author: Anonymous
license: MIT
---

# Agent Workflow Enforcer

**核心原则：用代码控制流程，不靠 AI 记忆。**

## 为什么需要这个？

AI Agent 会"忘"规则：
- Context 压缩后，早期指令被淡化
- 写在 prompt 里的规则是"建议"，Agent 可以不听
- 分段任务时风格不一致

**解决方案：把规则写进流程，没过检查点 = 不能继续。**

---

## 机制一：Gate 门禁

任务开始前，强制运行检查脚本：

```bash
python3 {baseDir}/scripts/gate.py <task_type> [options]
```

### 支持的任务类型

| 类型 | 说明 |
|------|------|
| `content` | 内容创作（文章、推文、配图）|
| `code` | 代码修改 |
| `deploy` | 部署操作 |
| `custom` | 自定义（读取 gate-config.yaml）|

### 示例

```bash
# 内容创作门禁
python3 {baseDir}/scripts/gate.py content --platform x --account your-account

# 代码修改门禁
python3 {baseDir}/scripts/gate.py code --scope "核心文件"
```

### 输出

```
═══════════════════════════════════════
🚧 Gate Check: content
═══════════════════════════════════════

📋 Checklist (必须全部确认):
[ ] 1. 已读相关 SKILL.md
[ ] 2. 已确认目标账号/平台
[ ] 3. 已检查 style-context（如适用）

⚠️ 没有完成以上检查 = 不能继续执行
═══════════════════════════════════════
```

**规则：Gate 输出后，Agent 必须逐项确认才能继续。**

---

## 机制二：强制输出格式

在 AGENTS.md 或 system prompt 中添加：

```markdown
## 强制输出格式

### 内容创作任务

第一条回复必须包含：

📋 Content Checklist
□ 已跑 gate
□ 已读相关 skill
□ 已确认账号: [账号]

**没有这个块 = 不能开始任务。**

### 任务完成时

必须包含：

📋 Pre-publish Checklist
□ 格式检查: ✅
□ 风格检查: ✅
□ 输出位置: [路径/链接]

**任何一项 ❌ = 不能发布。**
```

**原理：Agent 可能忘了读文件，但格式要求写死在流程里，它不会忘输出格式。**

---

## 机制三：Style Context 持久化

分段任务时，第一批完成后创建 `style-context.yaml`：

```bash
python3 {baseDir}/scripts/create_style_context.py \
  --project "项目名" \
  --style "风格名" \
  --output ./style-context.yaml
```

### 模板

```yaml
# style-context.yaml
project: project-name
created: 2026-02-25

style:
  name: style-name
  description: "风格描述"
  
  colors:
    primary: "#XXXXXX"
    background: "#XXXXXX"
    
  elements:
    - "元素1"
    - "元素2"
    
  avoid:
    - "避免1"
    - "避免2"

prompt_template: |
  [完整的 prompt 模板]

existing_outputs:
  file1.png: "描述"
  file2.md: "描述"
```

### 后续批次规则

在 AGENTS.md 中添加：

```markdown
## 分段任务规则

检测到分段任务时：
1. 先检查 style-context.yaml 是否存在
2. **存在** → 读取，按记录的风格继续
3. **不存在** → 不能继续，先创建

**没有 style-context = 不能继续分段任务。**
```

---

## 机制四：自动学习（可选）

当用户修改 Agent 输出时，检测差异并学习：

```bash
python3 {baseDir}/scripts/detect_learning.py "原文" "修改后"
```

输出：

```json
{
  "detected": true,
  "original": "进行分析",
  "corrected": "分析",
  "suggested_rule": "避免「进行+动词」冗余结构"
}
```

确认后写入 `learnings.jsonl`，下次自动应用。

---

## 快速开始

### 1. 安装

```bash
# OpenClaw
npx clawhub@latest install agent-workflow-enforcer

# 手动
git clone https://github.com/example/agent-workflow-enforcer ~/skills/agent-workflow-enforcer
```

### 2. 配置 AGENTS.md

把以下内容加到你的 AGENTS.md：

```markdown
## 🚧 Workflow Enforcer

### Gate 门禁
任务开始前运行：`python3 ~/skills/agent-workflow-enforcer/scripts/gate.py <type>`

### 强制输出格式
- 任务开始：必须输出 Checklist 块
- 任务完成：必须输出 Pre-publish 块
- **没有格式块 = 任务不完整**

### 分段任务
- 有 style-context.yaml → 读取后继续
- 没有 → 先创建
```

### 3. 测试

```bash
python3 ~/skills/agent-workflow-enforcer/scripts/gate.py content --platform x
```

---

## 文件结构

```
agent-workflow-enforcer/
├── SKILL.md              # 本文件
├── scripts/
│   ├── gate.py           # 门禁脚本
│   ├── create_style_context.py
│   └── detect_learning.py
├── templates/
│   ├── style-context.yaml
│   ├── gate-config.yaml
│   └── agents-snippet.md  # AGENTS.md 代码片段
└── examples/
    └── content-workflow/
```

---

## 核心原则

> **规则写在 prompt 里 = 建议**
> Agent 可以不听。
>
> **规则写在输出格式里 = 强制**
> 没有格式块 = 回复不完整。
>
> **规则写在 gate 脚本里 = 硬门禁**
> 没跑脚本 = 后续不执行。

**不是靠 AI "记住"，是靠流程卡死。**

---

## License

MIT
