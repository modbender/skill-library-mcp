# Autopilot Conventions

## PRD 更新规则

1. Codex 完成 `prd-todo.md` 中任一任务后，必须立刻把对应条目标记为 `✅`。
2. 每完成一项任务必须单独提交一次 commit，commit 信息要能定位该任务。
3. 若任务存在自动校验脚本，提交前必须先运行校验并确认通过。

## PRD 引擎规则

1. `prd-items.yaml` 是结构化事实源（版本、迭代、bugfix）。
2. `prd-progress.json` 是机器可读验证结果。
3. `prd-todo.md` 是面向人的任务视图，允许由 `scripts/prd-verify.sh --sync-todo` 自动同步。
