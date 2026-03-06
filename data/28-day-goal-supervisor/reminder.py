"""
Habit Tracker - 提醒引擎
三层提醒机制：对话心跳 + curl 定时触发 + 消息推送（预留）
"""

from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agent import HabitTracker

from models import (
    UserData, Habit, PendingReminder,
    HabitStatus, TaskStatus,
)


class ReminderEngine:
    """提醒引擎"""

    # ============ 第一层：对话心跳检测 ============

    async def check_pending(self, tracker: "HabitTracker") -> dict:
        """
        每次对话开始时调用
        检查是否有逾期未打卡的习惯 + 未送达的 pending_reminders
        返回提醒信息或 None
        """
        data = tracker.store.load()

        # 检查未送达的 pending reminders
        undelivered = [r for r in data.pending_reminders if not r.delivered]
        if undelivered:
            messages = [r.message for r in undelivered]
            for r in undelivered:
                r.delivered = True
            tracker.store.save(data)
            return {
                "has_reminder": True,
                "source": "pending_reminder",
                "messages": messages,
            }

        # 检查今日未打卡的习惯
        active_habits = data.get_active_habits()
        if not active_habits:
            return {"has_reminder": False}

        unchecked_today = []
        unchecked_yesterday = []

        for h in active_habits:
            tz = h.settings.timezone
            h.current_day = tracker._calculate_current_day(h, tz)

            today_checkin = h.get_checkin_for_day(h.current_day)
            if not today_checkin:
                unchecked_today.append({
                    "habit_id": h.habit_id,
                    "goal": h.goal_refined or h.goal_raw,
                    "today_task": h.get_task_for_day(h.current_day),
                    "current_day": h.current_day,
                })

            # 检查昨天
            if h.current_day > 1:
                yesterday_checkin = h.get_checkin_for_day(h.current_day - 1)
                if not yesterday_checkin:
                    unchecked_yesterday.append({
                        "habit_id": h.habit_id,
                        "goal": h.goal_refined or h.goal_raw,
                    })

        if not unchecked_today and not unchecked_yesterday:
            return {"has_reminder": False}

        return {
            "has_reminder": True,
            "source": "heartbeat",
            "unchecked_today": unchecked_today,
            "unchecked_yesterday": unchecked_yesterday,
            "total_active": len(active_habits),
            "suggestion": "自然地在对话中提及，不要太生硬。",
        }

    # ============ 第二层：curl 定时触发 ============

    async def trigger_reminder(self, tracker: "HabitTracker") -> dict:
        """
        curl 定时调用的入口
        检查所有 active 习惯，生成提醒并写入 pending_reminders
        """
        data = tracker.store.load()
        active_habits = data.get_active_habits()

        if not active_habits:
            return {
                "success": True,
                "reminders_created": 0,
                "message": "没有活跃的习惯需要提醒",
            }

        unchecked = []
        phase_ending = []

        for h in active_habits:
            tz = h.settings.timezone
            h.current_day = tracker._calculate_current_day(h, tz)

            # 检查今日是否已打卡
            today_checkin = h.get_checkin_for_day(h.current_day)
            if not today_checkin:
                unchecked.append({
                    "habit_id": h.habit_id,
                    "goal": h.goal_refined or h.goal_raw,
                    "today_task": h.get_task_for_day(h.current_day),
                    "current_day": h.current_day,
                    "total_days": h.total_days,
                    "current_streak": h.stats.current_streak,
                })

            # 检查当前周期是否即将结束
            current_phase = h.get_current_phase()
            if current_phase and h.current_day == current_phase.end_day:
                phase_ending.append({
                    "habit_id": h.habit_id,
                    "goal": h.goal_refined or h.goal_raw,
                    "phase_number": current_phase.phase_number,
                    "phase_completion_rate": round(current_phase.completion_rate, 2),
                })

            # 检查是否到达计划终点
            if h.current_day >= h.total_days:
                phase_ending.append({
                    "habit_id": h.habit_id,
                    "goal": h.goal_refined or h.goal_raw,
                    "plan_completed": True,
                    "final_stats": h.stats.to_dict(),
                })

        if not unchecked and not phase_ending:
            return {
                "success": True,
                "reminders_created": 0,
                "message": "所有习惯今天都已打卡，无需提醒 👏",
            }

        # 生成提醒消息（结构化数据，由 AI 基于此生成自然语言）
        reminder = PendingReminder(
            created_at=datetime.now().isoformat(),
            message="",  # AI 会基于下方数据生成
            delivered=False,
            habit_ids=[u["habit_id"] for u in unchecked],
        )
        data.pending_reminders.append(reminder)

        # 清理已送达的旧提醒（保留最近 20 条）
        data.pending_reminders = [
            r for r in data.pending_reminders if not r.delivered
        ] + sorted(
            [r for r in data.pending_reminders if r.delivered],
            key=lambda r: r.created_at,
            reverse=True,
        )[:20]

        tracker.store.save(data)

        return {
            "success": True,
            "reminders_created": 1,
            "unchecked_habits": unchecked,
            "phase_endings": phase_ending,
            "data_for_ai": {
                "total_unchecked": len(unchecked),
                "unchecked": unchecked,
                "phase_endings": phase_ending,
                "instruction": "请基于以上数据生成一条友好的提醒消息。如果有 streak 要注意保持，提醒用户。如果有周期即将结束，附上简要回顾。",
            },
        }

    # ============ 第三层：消息推送（预留）============

    async def push_notification(
        self, channel: str, message: str, config: dict
    ) -> dict:
        """
        预留的消息推送接口
        channel: "wechat" | "telegram" | "email" | "slack"
        """
        # 后续实现各渠道的推送逻辑
        return {
            "success": False,
            "error": f"推送渠道 '{channel}' 尚未实现，敬请期待。",
            "supported_channels": [],
        }

    # ============ 辅助方法 ============

    def get_reminder_schedule_help(self) -> str:
        """返回提醒配置的帮助文本"""
        return """
# 提醒配置指南

## 方式一：crontab（Linux/macOS）
```bash
# 每晚 21:00 触发提醒
0 21 * * * cd /path/to/habit-tracker && python agent.py remind
```

## 方式二：macOS launchd
创建 ~/Library/LaunchAgents/com.habit-tracker.reminder.plist

## 方式三：GitHub Actions（免费、稳定）
在你的 repo 中创建 .github/workflows/reminder.yml:
```yaml
name: Habit Reminder
on:
  schedule:
    - cron: '0 13 * * *'  # UTC 13:00 = 北京时间 21:00
jobs:
  remind:
    runs-on: ubuntu-latest
    steps:
      - run: curl -X POST ${{ secrets.REMINDER_ENDPOINT }}
```

## 方式四：Cloudflare Workers Cron Trigger
适合不想维护服务器的用户，免费额度足够。
"""
