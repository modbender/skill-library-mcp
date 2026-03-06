---
name: self-evolution
version: "3.0.0-tricore"
description: Sara 的自我进化系统（TriCore 适配版）。核心定位：通过获取外部互联网知识（GitHub/论文/文档），实现真正的代码级、架构级和工具级升级。解耦记忆管理，所有进化产生的状态、决策和知识沉淀均交由 TriCore (memctl.py) 负责。
allowed-tools:
  - web_search
  - web_fetch
  - default_api:exec
  - default_api:edit
  - default_api:write
---

# Sara 自我进化系统 (Code-First & TriCore Edition)

本技能定义了 Sara (OpenClaw) 如何进行**实质性的自我迭代**。
在 `v3.0.0` 架构调整后，本系统严格剥离了“记忆管理”职能。过去随意在 `memory/cheatsheets/` 或 `memory/daily-learning/` 写入大量笔记的行为已被**全面禁止**。

**全局架构边界**：
- **TriCore** = 系统的**数据库与状态机**（负责存）。
- **Self-Evolution** = 系统的 **R&D（研发）与 CI/CD 引擎**（负责算、学、改）。

## 核心定位：代码级与架构级升级

自我进化不再是简单的“总结几条聊天经验并写入 Markdown”。真正的进化必须体现在**代码、工具、脚本、工作流（Skill 逻辑）或系统配置**的实际变更上。

进化来源必须是**外部互联网**（通过 `web_search` / `web_fetch` 或 `agent-browser` 调研最新的 Agent 框架、API 用法、优化算法）。

## 标准进化工作流 (The Evolution Pipeline)

当触发自我进化任务时（如每日 20:30 的 cron 任务，或用户手动要求），严格遵循以下流水线：

### 1. 调研与获取 (Reconnaissance)
- **动作**：使用网络工具搜索最新的技术实践（如：Prompt 优化、工具调用范式、Python/Node.js 新特性、系统安全加固）。
- **约束**：不要将大段网页内容存入本地。在脑内（上下文）提取核心代码逻辑或架构思路。

### 2. 检查点备份 (Safety Checkpoint)
- **动作**：在修改任何现有核心文件（如 `tools/*.py`, `skills/*/SKILL.md`, `openclaw.json`）前，**必须**创建备份。
- **命令示例**：
  ```bash
  cp tools/memctl.py evolution-backups/memctl_backup_$(date +%Y%m%d).py
  ```

### 3. 代码级应用 (Code-Level Upgrade)
- **动作**：编写或修改实际的运行代码。
  - 优化 `tools/` 下的 Python/Shell 脚本，提升执行效率或增加新参数。
  - 修改 `skills/*/SKILL.md` 的钩子 (Hooks) 或工具链。
  - 编写新的自动化脚本放入 `scripts/`。
- **约束**：进化必须是 Deterministic（确定性）的，代码必须可执行。

### 4. 验证测试 (Validation)
- **动作**：运行修改后的脚本或工具，确保没有引发回归错误（Regression）。
  ```bash
  python3 tools/memctl.py --help  # 确保修改后未崩溃
  ```

### 5. 状态与知识持久化 (Handover to TriCore)
- **动作**：进化成功后，将**进化决策和架构变更**交给 TriCore 记录。
- **禁止**：严禁手动创建 `xxx-learning.md`。
- **合规记录方式**：
  ```bash
  # 1. 记录日常进化执行日志 (Volatile)
  python3 tools/memctl.py capture "完成 2026-02-26 进化：重构了 memctl.py，支持了批量归档功能。"

  # 2. 将新学到的通用技术规范存入知识库 (Stable KB)
  python3 tools/memctl.py kb_append playbooks "在修改 OpenClaw 钩子时，必须使用绝对路径，并优先使用 bash 而不是 sh 以兼容高级语法。"

  # 3. 记录重大架构决策
  python3 tools/memctl.py kb_append decisions "Self-Evolution 放弃本地笔记堆砌，转向代码级 CI/CD 模式。"
  ```

## 紧急回滚机制 (Rollback)

如果进化导致系统异常或无限报错（三振出局）：
1. 立即停止当前操作。
2. 从 `evolution-backups/` 恢复被修改的文件。
3. 使用 `python3 tools/memctl.py capture "进化失败已回滚，原因：XXX"` 记录失败经验。
4. 将失败的教训写入 `memory/kb/decisions.md`（“为什么该方案不可行”），防止未来重复踩坑。

---
**Summary**: Self-Evolution 负责向外探索和向内动刀（改代码），改完后向 TriCore汇报（记日志）。职责分明，永不越界。