# 小史任务管理器（Little Steve Task Manager）

在 IM 中直接管理任务：新增、查看、排序、更新状态、完成任务。

小史任务管理器强调**快速可用、低学习成本、与日常工作流高度融合**。无需切换到复杂工具，直接在聊天里就能完成任务管理闭环；同时支持每日汇总与自动状态更新配置，适合个人执行管理、项目推进和日常待办追踪。

## 主要能力
- 任务状态：open / doing / blocked / done
- 优先级：P0 > P1 > P2 > P3
- 列表排序：优先级 -> 截止日 -> 创建时间
- 每日汇总提醒（可配置）
- 自动状态更新（可配置）

## 依赖
- `jq`

macOS:
```bash
brew install jq
```

## 常用命令
```bash
# 新增
bash scripts/task.sh add --title "语音链路实测" --priority P1 --due "2026-03-03" --tags "openai-whisper"

# 列表
bash scripts/task.sh list --status open

# 更新状态
bash scripts/task.sh update --id 1 --status doing

# 完成
bash scripts/task.sh done --id 1
```

## 数据文件
- `data/tasks.json`
- `data/settings.json`

## 发布建议
使用 `clawhub-publisher` 打包并发布：
```bash
bash ../clawhub-publisher/scripts/publish.sh --skill-dir /workspace/skills/little-steve-task-manager
```
