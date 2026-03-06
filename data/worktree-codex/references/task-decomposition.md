# Worktree Agents — 任务分解参考

## 文件所有权原则

多 Agent 并行时最大的风险是文件冲突。分配任务前必须明确"谁能碰哪些文件"。

**黄金规则：每个文件只有一个 Agent 拥有写权限。**

### 典型分解方式

按层分解（前后端分离项目）：
- Agent A → src/api/ (后端接口)
- Agent B → src/ui/ (前端组件)
- Agent C → tests/ (测试)

按功能分解（工具库项目）：
- Agent A → src/math_utils.py
- Agent B → src/string_utils.py
- Agent Review → 只读审查，不写代码

按阶段分解（流水线）：
- Agent A 先跑完，产出 INTERFACE.md
- Agent B 读取 INTERFACE.md，再开始实现（需要串行，不适合并行）

## Claude Code 调用方式

### 非交互单次模式（推荐）

```bash
"$CLAUDE_BIN" --dangerously-skip-permissions --print -p "任务描述" > output.log 2>&1
```

- `--dangerously-skip-permissions`：允许在 WSL 路径写文件（必须加）
- `--print`：非交互输出模式
- `-p`：直接传入 prompt，不从 stdin 读

### Prompt 设计要点

1. 明确文件所有权边界：`只能修改 src/api.py 和 tests/test_api.py，不得碰其他文件`
2. 明确完成标准：`完成后执行 git add -A && git commit -m "..."，只输出 done`
3. 避免歧义：`实现 multiply(a, b) 返回乘积，divide(a, b) b=0 时抛 ValueError`

## Agent 并发数建议

| 项目规模 | 推荐并发数 | 说明 |
|---------|----------|------|
| 小型 (<5 文件) | 2 | 降低冲突风险 |
| 中型 (5-20 文件) | 3-4 | 按模块分工 |
| 大型 (>20 文件) | 4-6 | 需要严格的文件所有权规划 |

## Worktree 清理

实验完成后清理 worktree：

```bash
cd <repo_dir>
git worktree remove --force <worktree_path>
git branch -d <branch_name>
```
