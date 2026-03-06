# 03 — 多 Agent 协作

## Agent 角色分工

```
👔 PM Agent (Planner)
   模型：Gemini / OpenAI / Claude 最新旗舰（大上下文+思考）
   职责：需求分析、任务拆解、Design Doc
   规则：只读代码，不写代码

🔨 Dev Agent (Implementor)
   模型：各厂商轻量级模型（快速执行）
   职责：按 Design Doc 逐步实现
   规则：只改指定文件

🧪 QA Agent (Reviewer)
   模型：各厂商最强推理模型（严格审查）
   职责：代码 review、测试、安全检查
   规则：不直接改代码，只提建议

📚 Doc Agent (Documenter)
   模型：各厂商最轻量模型（低成本）
   规则：不改功能代码
```

---

## Agent 间 Handoff 协议

```markdown
# HANDOFF.md

## From: PM Agent → To: Dev Agent
## Date: YYYY-MM-DD HH:MM

### 任务摘要
### Design Doc 位置
### 实现顺序（含依赖关系）
### 注意事项（不要改哪些目录）
### 验收标准
```

---

## 多 Agent 工作流

```
你(人类) 描述需求
  → PM Agent 分析 → DESIGN.md + HANDOFF.md
  → Dev Agent 执行（新 session）→ 代码 + LOG.md
  → QA Agent 审查（新 session）→ REVIEW.md
  → 你(人类) 最终验收
```

---

## Git Worktree 并行开发

Plan 确定后，spawn 多个子 Agent 并行开发不同模块，各自独立 worktree，最后 review 后 merge。

```bash
# 创建 worktree
git worktree add worktree/feature-auth -b feature/auth
git worktree add worktree/feature-dashboard -b feature/dashboard

# 每个 Agent 在各自 worktree 工作
# 完成后逐个 review → 按依赖顺序 merge → 集成测试

# 清理
git worktree remove worktree/feature-auth
```

### 子 Agent 规则模板

```
你负责实现 [模块名]。
工作目录: worktree/feature-xxx/
Design Doc: docs/DESIGN-xxx.md

规则:
1. 只修改当前 worktree 的文件
2. 不要修改 shared/ 或 core/
3. 需要改共享代码 → 写入 CONFLICT.md
4. 每完成一步 → git commit
5. 完成后 LOG.md 写 "DONE — 等待 review"
```

### 冲突预防

- Design Doc 中明确划分文件所有权
- shared/ core/ 并行期间冻结
- 接口先行：先定义 interface，各自实现
- Merge 顺序：底层 → 上层，每 merge 一个跑测试

### OpenClaw 中的实现

```yaml
sessions_spawn:
  task: "读取 docs/DESIGN-auth.md，在 worktree/feature-auth/ 中实现"
  label: "dev-auth"
  model: "your-preferred-model"  # 按需选择
```

---

## 原生多 Agent 编排工具

> 工具详细对比和选型建议见 [06-tools.md](06-tools.md)。这里只列出与多 Agent 协作直接相关的要点。

- **Claude Code Agent Teams**: Teammates 互相 challenge，适合需要讨论的复杂任务
- **Kimi Agent Swarm**: 最多 100 并行，Critical Path 调度
- **Git Worktree**: 最大可控性，手动管理但可审计
- **OpenClaw sessions_spawn**: 轻量，可混合不同模型

---

## Race Condition 防护

### 方案 1（推荐）：每个 Agent 独立文件

```
logs/LOG-auth.md        ← Agent A 独占
logs/LOG-dashboard.md   ← Agent B 独占
status/auth.status      ← Agent A 独占
conflicts/              ← 所有 Agent 可写，Orchestrator 处理
```

**文件所有权矩阵**确保零竞争。

### 方案 2：Git Worktree 物理隔离

每个 Agent 在各自 worktree 中，LOG.md 物理上就不是同一个文件。

### 方案 3：Lock 文件（不推荐）

AI Agent 无法可靠执行 shell 锁，方案 1/2 更可靠。

### 方案 4：Append-Only + Agent 前缀（轻量折中）

```
[2026-02-28 05:30][auth     ] Step 1: 创建 middleware ✅
[2026-02-28 05:31][dashboard] Step 1: 创建布局 ✅
```

**写入 Agent 规则的一句话：**
```
"你只能写入 logs/LOG-{模块名}.md 和 status/{模块名}.status。
 其他文件只读。跨模块协调写入 conflicts/。每条 LOG 带 ISO 时间戳。"
```

---

## 两个 Agent 协作完成同一任务

| 场景 | 协作模式 |
|------|---------|
| 前后端联调 | **接口契约制** — 冻结 interface，各自实现 |
| 先后依赖 | **串行流水线** — A 完成写交接文件，B 读取继续 |
| 写+审 | **乒乓模式** — A 写 → B review → A 改，最多 3 轮 |
| 方案选型 | **辩论模式** — 各自分析 → 互相 challenge → 人类决策 |
| 同文件不同区域 | **分段编辑** — 用注释标记区域（最后手段） |

---

## 时间戳与进度追踪

### LOG 格式规范

```markdown
### [2026-02-28T05:30:12Z] Step 1: 创建 auth middleware ✅
- 耗时: 8 min
- 文件: src/middleware/auth.ts (新建)
- commit: a1b2c3d
- 验证: 单元测试通过 (3/3)
```

### Status 文件格式

```yaml
agent: auth
module: 认证系统
status: done          # waiting | in_progress | blocked | done | failed
started_at: 2026-02-28T05:30:12Z
completed_at: 2026-02-28T06:04:35Z
total_duration_min: 34
blocked_by: null
```

### Leader 汇总脚本

**Bash 版：**
```bash
#!/bin/bash
for status_file in status/*.status; do
  agent=$(grep "^agent:" "$status_file" | cut -d' ' -f2)
  state=$(grep "^status:" "$status_file" | cut -d' ' -f2)
  case $state in
    done) icon="✅" ;; in_progress) icon="⏳" ;; blocked) icon="🚫" ;; *) icon="❓" ;;
  esac
  echo "$icon [$agent] $state"
done
```

**PowerShell 版（Win11 适配）：**
```powershell
Get-ChildItem status\*.status | ForEach-Object {
    $content = Get-Content $_.FullName
    $agent = ($content | Select-String "^agent:").ToString().Split(":")[1].Trim()
    $state = ($content | Select-String "^status:").ToString().Split(":")[1].Trim()
    $icon = switch ($state) {
        "done"        { "✅" }
        "in_progress" { "⏳" }
        "blocked"     { "🚫" }
        "failed"      { "❌" }
        default       { "❓" }
    }
    Write-Host "$icon [$agent] $state"
}
```
