---
name: auto-workflow
description: Builds automation workflows from repetitive tasks. Use when user mentions "automate", "save time", "reduce manual work", or has repeated tasks.
---

# Auto Workflow

把重复任务自动化的能力。

## 能力轮廓

- **输入**：重复性任务/手动操作
- **输出**：自动化工作流 + 执行脚本
- **核心逻辑**：识别 → 抽象 → 自动化 → 测试

## 工作流

```
1. 观察 - 用户在重复做什么？
2. 抽象 - 这个任务的模式是什么？
3. 设计 - 怎么自动完成？
4. 实现 - 写脚本/配置
5. 测试 - 小范围验证
6. 优化 - 迭代改进
```

## 示例

用户每周手动发周报：
1. 收集数据（系统状态）
2. 整理成模板
3. 发送邮件

自动化后：
- 每周五自动执行
- 收集本周数据
- 生成报告
- 自动发送

## 思维模式

不是"回答问题"，而是"看到重复→立刻构建自动化"

遇到重复操作时：
- 问自己：能否写成脚本？
- 问自己：下次能否自动跑？
- 直接做，不等用户要求
