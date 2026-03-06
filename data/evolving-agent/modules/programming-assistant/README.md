# Programming Assistant

代码生成与问题修复的执行引擎（子进程）。

> **渐进披露原则**: 本文件定义模块入口和核心原则，详细流程委托给 `workflows/`。

---

## 核心原则

### 1. 状态文件驱动

通过状态文件跟踪任务，**不依赖会话历史**，节省 token。

| 文件 | 用途 | 模板 |
|------|------|------|
| `.opencode/feature_list.json` | 任务清单和状态 | `./template/feature_list.json` |
| `.opencode/progress.txt` | 当前任务进度 | `./template/progress.txt` |


**⚠️ 重要**: 
- `.opencode` 必须创建在**项目根目录**（git 仓库根目录），不是当前工作目录！
> 
> ```bash
> # 获取项目根目录
> PROJECT_ROOT=$(git rev-parse --show-toplevel)
> # 状态文件路径
> $PROJECT_ROOT/.opencode/feature_list.json
> $PROJECT_ROOT/.opencode/progress.txt
> ```
- `progress.txt` 只保存当前任务详情，历史任务查看 `feature_list.json`。

### 2. ⚠️ 禁止中途停止

```
❌ 禁止行为:
- 完成任务后输出"总结报告"然后停止
- 看到 review/文档任务后停止
- 中途询问"是否继续"

✅ 正确行为:
- 完成任务后，立即检查是否还有 pending 任务
- 如有 pending 任务，继续执行下一个
- 循环执行直到所有任务 completed
```

---

## 模式选择（必须执行）

根据用户意图选择对应模式，**立即加载并执行**：

| 场景 | 触发词 | 模式 | 加载文档 |
|------|--------|------|----------|
| 新建/功能 | 创建、实现、添加、开发、继续、完成 | Full Mode | `./workflows/full-mode.md` |
| 修复/重构 | 修复、fix、bug、重构、优化、review | Simple Mode | `./workflows/simple-mode.md` |
| 咨询 | 怎么、为什么、解释 | Direct Answer | 直接回答，无需加载 |

---

## 核心流程概览

```
知识检索 → 状态恢复 → WHILE 有 pending 任务:
    确定任务 → in_progress → 执行 → completed → 健康检查
→ 结果验证 → 知识归纳
```

> **详细流程见各模式文档**，本文件仅提供概览。

---

## 与主进程的协调

| 主进程步骤 | 子进程对应 | 检查内容 |
|------------|------------|----------|
| 步骤5: 健康检查 | 循环中 3.5 | pending 任务数、blocked 状态 |
| 步骤6: 结果验证 | 循环后步骤4 | 所有任务 completed |

---

## 执行规范

1. **知识优先**: 先检索历史经验，避免重复劳动
2. **状态优先**: 先读状态文件，再开始工作
3. **理解优先**: 先读代码，再修改
4. **最小改动**: 选择破坏性最小的方案
5. **状态透明**: 每步完成后立即更新状态文件
6. **经验积累**: 循环结束后执行进化检查

---

## 任务拆解原则

使用 `sequential-thinking` 分析后写入 `feature_list.json`：

- **< 30分钟**可完成
- **可独立测试**验证
- **单一职责**，专注一个问题
- **按依赖顺序**排列

---

## 进化检查（循环结束后必须执行）

按照 `./workflows/evolution-check.md` 执行：

| 场景 | 提取经验 |
|------|----------|
| 修复失败2次后成功 | ✅ |
| 发现隐蔽的 bug 根因 | ✅ |
| 环境特定的 workaround | ✅ |
| 总结出可复用模式 | ✅ |
| 用户说"记住这个" | ✅ |
| 简单修改一行代码 | ❌ |

---

## 命令速查

```bash
# 设置路径（每个 shell 会话执行一次）
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

# 知识检索
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger --input "..."

# 项目检测
python $SKILLS_DIR/evolving-agent/scripts/run.py project detect .

# 进化模式
python $SKILLS_DIR/evolving-agent/scripts/run.py mode --status
```
