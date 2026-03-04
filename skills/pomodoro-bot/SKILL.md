---
name: pomodoro-bot
description: 专注番茄钟助手。启动25分钟工作倒计时 + 5分钟休息倒计时，支持暂停/跳过。当用户说“开始番茄钟”、“计时25分钟”、“休息时间到”等时触发。
---

# Pomodoro Bot 技能说明

## 触发条件
- 用户明确要求启动/停止/跳过番茄钟
- 提及“番茄钟”、“25分钟”、“专注”、“休息”等关键词
- 需要定时提醒但非一次性任务（区别于 cron 一次性提醒）

## 核心能力
1. 启动工作倒计时（默认25m）
2. 工作结束 → 自动启动休息倒计时（默认5m）
3. 支持 `pause` / `skip` / `reset` 指令
4. 结束时发送总结（如：✅ 完成1个番茄钟）

## 使用方式
- 直接调用：`sessions_spawn agentId=pomodoro-bot task="启动番茄钟，25分钟工作+5分钟休息"`
- 或由主会话根据语义自动触发

## 资源说明
- `scripts/start_pomodoro.sh`：负责创建 cron 任务链（工作→休息→通知）
- `references/config.md`：可配置时长、声音、消息模板
- `assets/timer-icon.png`：可选 UI 图标（用于消息中展示）

> 💡 注意：本技能依赖 `openclaw cron` 实现倒计时，不占用主会话资源。