---
name: evolve
description: Start the Evolving Agent coordinator. Supports complete mode initialization, evolution mode switching and status viewing. It is a unified manual entrance to enter the "programming + evolution" closed loop.
metadata:
  command: /evolve
  usage: "/evolve [subcommand]"
---

# Evolve Command

`/evolve` 是 Evolving Programming Agent 的统一手动入口命令。

## 1. 基础用法

### 启动协调器 (Default)
```bash
/evolve
```
**行为**:
1. 执行完整初始化:
   ```bash
   SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)
   python $SKILLS_DIR/evolving-agent/scripts/run.py mode --init
   ```
2. 开启进化模式 (Evolution Mode)
3. 输出交互式引导提示
4. 等待用户输入编程任务

**适用场景**:
- 开始一个新的编程会话
- 需要明确的系统状态反馈时

## 2. 子命令 (Subcommands)

虽然主要通过自然语言交互，但 `/evolve` 也支持一些快捷指令来管理环境状态。

| 子命令 | 对应 run.py 命令 | 说明 |
|--------|-----------------|------|
| `on` | `python $SKILLS_DIR/evolving-agent/scripts/run.py mode --on` | 仅开启进化模式（不输出欢迎语） |
| `off` | `python $SKILLS_DIR/evolving-agent/scripts/run.py mode --off` | 关闭进化模式 |
| `status` | `python $SKILLS_DIR/evolving-agent/scripts/run.py mode --status` | 查看当前状态（激活/未激活） |
| `init` | `python $SKILLS_DIR/evolving-agent/scripts/run.py mode --init` | 强制重新初始化（同无参数运行） |

> **注意**: 执行前需设置 `SKILLS_DIR` 变量：
> ```bash
> SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)
> ```

### 示例

```bash
/evolve status
# Output: Evolution Mode Status: ACTIVE

/evolve off
# Output: Evolution Mode Deactivated.
```

## 3. 交互流程

当用户执行 `/evolve` 后，系统进入**协调模式**：

1. **意图侦听**: 等待用户输入（编程任务 / 知识归纳 / GitHub 学习）。
2. **智能调度**:
   - 输入 "帮我写个登录页面" -> 参考 `modules/programming-assistant/`
   - 输入 "学习这个仓库..." -> 参考 `modules/github-to-skills/`
   - 输入 "保存这次的经验" -> 参考 `modules/knowledge-base/`
3. **进化闭环**:
   - 在后台持续检测 `.opencode/.evolution_mode_active`
   - 自动提取有价值的经验并存入知识库

## 4. 与自然语言的区别

- **自然语言** ("开发一个功能..."): 直接触发 `programming-assistant`，并**隐式**尝试开启进化模式（如果未开启则初始化）。
- **命令** (`/evolve`): **显式**初始化环境，确立"协调器"的主导地位，适合作为会话的"握手"步骤。
