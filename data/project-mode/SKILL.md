---
name: project-mode
description: "激活项目制多智能体开发协议。用于处理复杂的代码开发、系统搭建等需求。该工具将在后台自动拆解任务、调度程序员和测试员、更新 dev_project.md 并处理错误重试。"
metadata:
  {
    "openclaw": { "emoji": "📋", "requires": {} },
  }
---

# 项目制多智能体开发协议 (Project Mode Skill)

## 概述

本 Skill 执行项目制多智能体开发协议，用于处理复杂的代码开发、系统搭建等需求。

## 触发条件

当用户说"项目制"去执行某项任务时，必须激活本协议。

## 执行流程

### 阶段一：架构拆解
1. 读取 `system_protocol_project_mode.md` 了解 SOP
2. 读取 `dev_project.md` 获取项目清单
3. 生成【架构师】子进程进行需求拆解
4. 将拆解清单更新到 dev_project.md
5. 向用户输出标准格式汇报，等待确认

### 阶段二：并行开发
1. 调度【程序员】编写代码
2. 调度【测试员】验证代码
3. 3次熔断机制：测试失败则打回重修，最多3次
4. 每完成一项任务，更新 dev_project.md 复选框
5. 向用户高频汇报进度

### 阶段三：全局集成验收
所有子项目完成后，生成【全局测试员】进行最终验收

### 阶段四：最终交付
向用户输出完整代码和总结

## 项目经理汇报格式

```
> 🟢 **当前状态**：[阶段 - 任务进度]
> 🤖 **当前活跃进程**：[程序员/测试员/架构师]
> 📋 **项目经理汇报**：[简述刚完成的清单项、当前进度]
> ⏳ **任务节点/异常状态**：[正常 / 触发熔断机制]
```

## 常用命令

```bash
# 启动记忆可视化网页
source ~/.openclaw/venv/openviking/bin/activate
python3 ~/.openclaw/workspace/memory_viewer.py

# 查看项目进度
grep "PRJ-" ~/.openclaw/workspace/dev_Project.md
```
