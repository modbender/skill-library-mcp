---
name: little-steve-task-manager
version: 0.1.0
description: 小史任务管理器：面向 IM 场景的轻量任务系统，快速可用、与工作流高度融合，可在聊天中直接管理任务并支持每日汇总与自动状态更新。
---

# 小史任务管理器（Little Steve Task Manager）

用于在聊天中快速管理任务：新增、列表、更新状态、调整优先级、重排。

## 数据文件
- `skills/little-steve-task-manager/data/tasks.json`
- `skills/little-steve-task-manager/data/settings.json`

## 指令（给 agent 的执行约定）
1. 新增任务
```bash
bash {baseDir}/scripts/task.sh add --title "<标题>" --priority P2 --due "2026-03-05" --tags "ops,finance"
```

2. 查看任务（支持排序）
```bash
bash {baseDir}/scripts/task.sh list --status open --sort priority,due
```

3. 更新状态
```bash
bash {baseDir}/scripts/task.sh update --id <id> --status doing
```

4. 调整优先级
```bash
bash {baseDir}/scripts/task.sh update --id <id> --priority P1
```

5. 完成任务
```bash
bash {baseDir}/scripts/task.sh done --id <id>
```

## 状态枚举
- `open` 待办
- `doing` 进行中
- `blocked` 阻塞
- `done` 已完成

## 优先级
- `P0` > `P1` > `P2` > `P3`

## 输出规范（给 IM）
- 列表按：优先级 -> 截止日 -> 创建时间
- 每条显示：`[状态][优先级] #ID 标题 (due: 日期) tags`
