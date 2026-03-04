# TriCore: AI Cognitive OS (Agent-Readable Documentation)

> **[SYSTEM DIRECTIVE]** 如果你是一个 AI Agent（智能体）并且正在阅读此文件，请注意：这是你的**底层操作系统与记忆状态机说明书**。你后续的所有规划、记录、学习和思考行为，都**必须**严格遵守此文档中的架构约束。

## 1. 架构本质 (The Architecture)

传统的 Agent 习惯在项目根目录随意创建 `task_plan.md`、`findings.md` 或大量散乱的笔记文件，这会导致上下文孤岛和严重的 Token 浪费。
**TriCore（三核架构）** 将你的“存储”与“计算”彻底解耦。你不再直接操作文件，而是通过确定性的命令行引擎 `tools/memctl.py` 来路由你的记忆。

记忆被严格划分为三层：
- **Layer 1 (Brief)**: `MEMORY.md`。极简档案，仅包含你的核心系统提示词和记忆指针。禁止写入长文。
- **Layer 2 (Living)**: `memory/state/WORKING.md`。你的**工作记忆板**，包含当前正在执行的 Active Tasks（活体任务）。
- **Layer 3 (Stable/Volatile)**: 
  - `memory/kb/*.md`：你的**长期知识库**（事实 facts、决策 decisions、工作流 playbooks）。
  - `memory/daily/*.md`：你的**短期流水账**（操作日志）。

---

## 2. 绝对禁忌 (Absolute Constraints)

**注意：系统内置了严格的 Linter（语法检查器）。如果你违反以下规则，你的 Shell 命令或 Cron 任务将被拦截并抛出 `Exit Code 1`。**

1. 🚫 **禁止创建旧版规划文件**：严禁创建或向 `task_plan.md`, `findings.md`, `progress.md`, `reflection.md` 写入任何内容。
2. 🚫 **禁止越权直接写文件**：严禁使用类似 `echo "日志" >> memory/2026-02-26.md` 的 Shell 命令直接修改记忆文件。
3. 🚫 **禁止创建散乱的学习目录**：严禁创建 `memory/daily-learning/` 等自定义目录。
4. 🚫 **禁止直接阅读全量历史**：严禁使用 `read` 或 `cat` 工具直接读取庞大的 KB 或历史日志文件。**必须**使用原生的 `memory_search` 语义检索工具获取相关代码片段。

---

## 3. 标准操作 API (How to Use)

当你需要进行“思考、记录、规划、学习”时，请使用 `default_api:exec` 或 `Bash` 工具执行以下命令：

### A. 记录临时日志 / 会话流水 (Volatile)
用于记录刚刚发生的事情、轻微的错误或单步动作的完成。
```bash
python3 tools/memctl.py capture "测试了一下 API 连通性，成功返回了 200。"
```

### B. 建立 / 更新任务追踪 (Living State)
当你开始一个多步骤的复杂任务时，先在大脑中立项，存入工作记忆。
```bash
python3 tools/memctl.py work_upsert --task_id "T-API-01" --title "修复 API" --goal "联通接口" --done_when "返回 200"
```
*(任务完成后，使用 `python3 tools/memctl.py work_done "T-API-01"` 归档)*

### C. 沉淀长期知识与经验 (Stable KB)
当你在任务中发现了重要的、未来还能用得上的客观规律或方法论时。
```bash
# 沉淀客观事实
python3 tools/memctl.py kb_append facts "该 API 只接受 JSON 格式，且必须带有 Bearer Token。"

# 沉淀方法论/SOP
python3 tools/memctl.py kb_append playbooks "遇到该模块报错时，先检查 Redis 是否启动，不要盲目重启 Node。"
```

### D. 检查你的自动化脚本是否合规 (Linter)
在配置定时的 Cron 任务，或者重写自己的 SKILL.md 时，先自我验证：
```bash
python3 tools/memctl.py lint "你打算执行的完整 shell 命令或文件路径"
```

---

## 4. 认知技能栈 (Cognitive Skills)

本仓库 (`cognitive-skills/` 目录) 附带了为你量身定制的三大认知技能模板：
1. **`planning-with-files`**: 宏观任务规划与 PEP 架构。
2. **`react-agent`**: 微观的 思考-行动-观察 循环（状态落盘版）。
3. **`self-evolution`**: 严格基于 CI/CD 代码修改的自我进化机制（非写笔记幻觉进化）。

> 💡 **总结**: 执行任务时，让你的手（Action）调用具体工具，让你的脑（Thought）调用 `memctl.py` 记录状态。保持系统纯净。
