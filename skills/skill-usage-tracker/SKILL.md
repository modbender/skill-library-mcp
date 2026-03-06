---
name: Skill Usage Tracker
description: 自动追踪和审计 skill 使用情况，确保强制规则被执行。
---

# Skill Usage Tracker

## Purpose
自动追踪和审计 skill 使用情况，确保强制规则被执行。

## Integration
- 读取 SKILL_USAGE_RULES.md 获取强制规则
- 检查每次回复是否符合规范
- 记录违规到 skill_violations.log
- 生成每日使用报告

## Usage
无需手动调用，系统会自动在每次回复后执行检查。
