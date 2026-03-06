"""
Habit Tracker - 核心业务逻辑
职责：数据 CRUD、状态流转、统计计算、规则引擎
内容生成（计划、反馈、总结文案）由 AI 通过 SKILL.md 完成
"""

import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from models import (
    UserData, Habit, Phase, DailyTask, CheckIn, TaskResult,
    PendingReminder, Stats, HabitSettings, Rationalization, ConversationTurn,
    HabitType, HabitStatus, TaskStatus, CheckInSource,
    RationalizationStatus, CompletionAction, SummaryFrequency,
    validate_habit, VALID_TASK_STATUSES,
)
from store import HabitStore
from visualizer import HabitVisualizer
from reminder import ReminderEngine


MAX_ACTIVE_HABITS = 5
MAX_RATIONALIZATION_ROUNDS = 4
RETROACTIVE_WINDOW_DAYS = 7
DEFAULT_PHASE_LENGTH = 3
MAX_PHASE_LENGTH = 7
MIN_PHASE_LENGTH = 2


class HabitTracker:
    """习惯追踪器核心引擎"""

    def __init__(self, data_dir: Optional[str] = None):
        self.store = HabitStore(data_dir)
        self.visualizer = HabitVisualizer()
        self.reminder = ReminderEngine()

    def _load(self) -> UserData:
        return self.store.load()

    def _save(self, data: UserData) -> None:
        self.store.save(data)

    def _today(self, tz_str: str = "Asia/Shanghai") -> date:
        return datetime.now(ZoneInfo(tz_str)).date()

    def _calculate_current_day(self, habit: Habit, tz_str: str = "Asia/Shanghai") -> int:
        """计算习惯从创建到今天是第几天"""
        created = datetime.fromisoformat(habit.created_at).date()
        today = self._today(tz_str)
        return (today - created).days + 1

    # ============ 创建习惯 ============

    async def create_habit(self, goal_raw: str, habit_type: str = "progressive") -> dict:
        """
        创建新习惯（draft 状态），进入合理化流程
        返回: {"habit_id": str, "status": "draft", "message": str}
        """
        data = self._load()

        if not data.can_add_habit:
            return {
                "success": False,
                "error": f"已达到并行习惯上限（{MAX_ACTIVE_HABITS}个）。请先完成或放弃一个现有习惯。",
                "active_count": data.active_habit_count,
            }

        habit = Habit(
            habit_id="",  # __post_init__ 会生成
            habit_type=habit_type,
            goal_raw=goal_raw,
        )

        errors = validate_habit(habit)
        if errors:
            return {"success": False, "error": f"数据校验失败: {'; '.join(errors)}"}

        data.habits.append(habit)
        self._save(data)

        return {
            "success": True,
            "habit_id": habit.habit_id,
            "habit_type": habit.habit_type,
            "status": habit.status,
            "goal_raw": goal_raw,
            "rationalization_round": 0,
            "message": "习惯已创建，请开始目标合理化对话。",
        }

    # ============ 目标合理化 ============

    async def update_rationalization(
        self, habit_id: str, ai_message: str = "", user_response: str = ""
    ) -> dict:
        """
        更新合理化对话（记录一轮对话）
        返回当前轮数和是否应该收敛
        """
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}
        if habit.status != HabitStatus.DRAFT.value:
            return {"success": False, "error": "习惯不在 draft 状态"}

        rat = habit.rationalization

        if ai_message:
            rat.conversation.append(ConversationTurn(role="ai", content=ai_message))
        if user_response:
            rat.conversation.append(ConversationTurn(role="user", content=user_response))
            rat.round_count += 1

        should_converge = rat.round_count >= MAX_RATIONALIZATION_ROUNDS

        self._save(data)

        return {
            "success": True,
            "habit_id": habit_id,
            "round_count": rat.round_count,
            "max_rounds": MAX_RATIONALIZATION_ROUNDS,
            "should_converge": should_converge,
            "message": "第4轮了，请直接给出推荐方案让用户确认。" if should_converge else None,
        }

    # ============ 确认习惯 ============

    async def confirm_habit(
        self,
        habit_id: str,
        goal_refined: str,
        completion_criteria: str,
        total_days: int = 28,
        checkin_task: Optional[str] = None,
        reminder_time: str = "21:00",
        timezone: str = "Asia/Shanghai",
        coaching_style: Optional[str] = None,
    ) -> dict:
        """
        确认目标，将习惯从 draft → active
        返回需要 AI 生成初始计划的参数
        """
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}

        habit.goal_refined = goal_refined
        habit.completion_criteria = completion_criteria
        habit.total_days = total_days
        habit.status = HabitStatus.ACTIVE.value
        habit.current_day = 1
        habit.rationalization.status = RationalizationStatus.COMPLETED.value

        if habit.habit_type == HabitType.CHECKIN.value:
            habit.checkin_task = checkin_task or goal_refined

        habit.settings = HabitSettings(
            reminder_time=reminder_time,
            timezone=timezone,
            coaching_style=coaching_style,
        )

        errors = validate_habit(habit)
        if errors:
            return {"success": False, "error": f"数据校验失败: {'; '.join(errors)}"}

        self._save(data)

        return {
            "success": True,
            "habit_id": habit_id,
            "status": "active",
            "needs_plan_generation": habit.habit_type == HabitType.PROGRESSIVE.value,
            "plan_params": {
                "phase_number": 1,
                "phase_length": DEFAULT_PHASE_LENGTH,
                "start_day": 1,
                "goal_refined": goal_refined,
                "completion_criteria": completion_criteria,
                "habit_type": habit.habit_type,
            },
            "message": "目标已确认！" + (
                "请为用户生成初始3天计划。" if habit.habit_type == HabitType.PROGRESSIVE.value
                else "打卡型习惯已就绪，无需拆解计划。"
            ),
        }

    # ============ 保存 AI 生成的计划 ============

    async def save_plan(self, habit_id: str, phase_data: dict) -> dict:
        """
        保存 AI 生成的阶段计划
        phase_data: {"phase_number", "phase_length", "start_day", "daily_tasks": [{"day", "description"}]}
        """
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}

        tasks = [
            DailyTask(day=t["day"], description=t["description"])
            for t in phase_data.get("daily_tasks", [])
        ]

        phase = Phase(
            phase_number=phase_data["phase_number"],
            phase_length=phase_data["phase_length"],
            start_day=phase_data["start_day"],
            daily_tasks=tasks,
        )

        # 检查是否已存在同编号的 phase，如有则替换
        existing_idx = None
        for i, p in enumerate(habit.phases):
            if p.phase_number == phase.phase_number:
                existing_idx = i
                break

        if existing_idx is not None:
            habit.phases[existing_idx] = phase
        else:
            habit.phases.append(phase)

        self._save(data)

        return {
            "success": True,
            "habit_id": habit_id,
            "phase_number": phase.phase_number,
            "days_covered": f"Day {phase.start_day}-{phase.end_day}",
            "task_count": len(tasks),
        }

    # ============ 每日打卡 ============

    async def check_in(
        self,
        habit_id: str,
        task_results: list[dict],
        day: Optional[int] = None,
        note: str = "",
    ) -> dict:
        """
        单个习惯打卡（upsert 逻辑，同一天重复打卡以最后一次为准）
        task_results: [{"task": str, "status": "completed|partial|skipped", "note": ""}]
        """
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}
        if habit.status != HabitStatus.ACTIVE.value:
            return {"success": False, "error": f"习惯状态为 {habit.status}，无法打卡"}

        tz = habit.settings.timezone
        today = self._today(tz)
        habit.current_day = self._calculate_current_day(habit, tz)

        if day is None:
            day = habit.current_day

        # 校验补报窗口
        if day < habit.current_day - RETROACTIVE_WINDOW_DAYS:
            return {"success": False, "error": f"超过补报窗口（{RETROACTIVE_WINDOW_DAYS}天），无法补报 Day {day}"}

        # 校验 task_results 中的 status
        results = []
        for tr in task_results:
            status = tr.get("status", "completed")
            if status not in VALID_TASK_STATUSES:
                status = TaskStatus.COMPLETED.value
            results.append(TaskResult(
                task=tr.get("task", ""),
                status=status,
                note=tr.get("note", ""),
            ))

        is_retroactive = day < habit.current_day

        checkin = CheckIn(
            day=day,
            date=today.isoformat() if not is_retroactive else (today - timedelta(days=habit.current_day - day)).isoformat(),
            source=CheckInSource.SELF_REPORT.value,
            tasks_result=results,
            retroactive=is_retroactive,
        )

        # upsert：同一天覆盖
        existing_idx = None
        for i, c in enumerate(habit.check_ins):
            if c.day == day:
                existing_idx = i
                break

        if existing_idx is not None:
            habit.check_ins[existing_idx] = checkin
        else:
            habit.check_ins.append(checkin)

        # 更新 progressive 类型的 daily_task status
        if habit.habit_type == HabitType.PROGRESSIVE.value:
            for phase in habit.phases:
                for task in phase.daily_tasks:
                    if task.day == day and results:
                        task.status = results[0].status

        # 重算统计
        self._recalculate_stats(habit)

        # 检查是否需要生成新周期计划
        needs_new_phase = self._check_needs_new_phase(habit)

        # 检查是否已完成全部天数
        plan_completed = habit.current_day >= habit.total_days

        self._save(data)

        return {
            "success": True,
            "habit_id": habit_id,
            "day": day,
            "is_retroactive": is_retroactive,
            "stats": habit.stats.to_dict(),
            "needs_new_phase": needs_new_phase,
            "plan_completed": plan_completed,
            "next_phase_params": self._calculate_next_phase_params(habit) if needs_new_phase else None,
            "message": "打卡已记录。" + (" 当前周期已结束，需要生成新的阶段计划。" if needs_new_phase else ""),
        }

    async def batch_check_in(self, results_map: dict[str, list[dict]]) -> dict:
        """
        批量打卡：一次性汇报多个习惯
        results_map: {habit_id: [{"task", "status", "note"}]}
        """
        data = self._load()
        results = {}

        for habit_id, task_results in results_map.items():
            result = await self.check_in(habit_id, task_results)
            results[habit_id] = result

        return {"success": True, "results": results}

    # ============ 统计计算 ============

    def _recalculate_stats(self, habit: Habit) -> None:
        """重算习惯的统计数据"""
        if not habit.check_ins:
            habit.stats = Stats()
            return

        total = habit.current_day
        completed = 0
        partial = 0
        skipped = 0
        missed = 0

        # 按 day 排序
        sorted_checkins = sorted(habit.check_ins, key=lambda c: c.day)

        for ci in sorted_checkins:
            if ci.tasks_result:
                primary_status = ci.tasks_result[0].status
            else:
                primary_status = TaskStatus.MISSED.value

            if primary_status == TaskStatus.COMPLETED.value:
                completed += 1
            elif primary_status == TaskStatus.PARTIAL.value:
                partial += 1
            elif primary_status == TaskStatus.SKIPPED.value:
                skipped += 1
            elif primary_status == TaskStatus.MISSED.value:
                missed += 1

        # 没有打卡的天数算 missed
        checked_days = {ci.day for ci in sorted_checkins}
        for d in range(1, habit.current_day + 1):
            if d not in checked_days:
                missed += 1

        total_with_data = completed + partial + skipped + missed
        completion_rate = (completed + partial * 0.5) / max(total_with_data, 1)

        # 计算 streak
        current_streak = 0
        best_streak = 0
        temp_streak = 0

        for d in range(1, habit.current_day + 1):
            ci = habit.get_checkin_for_day(d)
            if ci and ci.tasks_result and ci.tasks_result[0].status in (
                TaskStatus.COMPLETED.value, TaskStatus.PARTIAL.value
            ):
                temp_streak += 1
                best_streak = max(best_streak, temp_streak)
            else:
                temp_streak = 0

        current_streak = temp_streak

        # 周完成率
        weekly_rates = []
        week_start = 1
        while week_start <= habit.current_day:
            week_end = min(week_start + 6, habit.current_day)
            week_completed = 0
            week_total = 0
            for d in range(week_start, week_end + 1):
                week_total += 1
                ci = habit.get_checkin_for_day(d)
                if ci and ci.tasks_result and ci.tasks_result[0].status in (
                    TaskStatus.COMPLETED.value, TaskStatus.PARTIAL.value
                ):
                    week_completed += 1
            weekly_rates.append(round(week_completed / max(week_total, 1), 2))
            week_start += 7

        habit.stats = Stats(
            completion_rate=round(completion_rate, 2),
            current_streak=current_streak,
            best_streak=best_streak,
            total_completed=completed,
            total_partial=partial,
            total_skipped=skipped,
            total_missed=missed,
            weekly_rates=weekly_rates,
        )

    # ============ 周期管理 ============

    def _check_needs_new_phase(self, habit: Habit) -> bool:
        """检查是否需要生成新的阶段计划"""
        if habit.habit_type == HabitType.CHECKIN.value:
            return False
        if not habit.phases:
            return True

        last_phase = habit.phases[-1]
        return habit.current_day > last_phase.end_day

    def _calculate_next_phase_params(self, habit: Habit) -> dict:
        """根据完成情况计算下一周期的参数"""
        if not habit.phases:
            return {
                "phase_number": 1,
                "phase_length": DEFAULT_PHASE_LENGTH,
                "start_day": 1,
                "difficulty_direction": "normal",
            }

        last_phase = habit.phases[-1]
        rate = last_phase.completion_rate

        # 周期长度调整
        current_length = last_phase.phase_length
        if rate >= 0.9:
            new_length = min(current_length + 2, MAX_PHASE_LENGTH)
            difficulty = "harder"
        elif rate >= 0.6:
            new_length = current_length
            difficulty = "maintain"
        elif rate >= 0.3:
            new_length = max(current_length - 1, MIN_PHASE_LENGTH)
            difficulty = "easier"
        else:
            new_length = MIN_PHASE_LENGTH
            difficulty = "much_easier"

        # 连续两个周期检查
        if len(habit.phases) >= 2:
            prev_phase = habit.phases[-2]
            prev_rate = prev_phase.completion_rate
            if rate >= 0.9 and prev_rate >= 0.9:
                new_length = min(new_length + 1, MAX_PHASE_LENGTH)
            elif rate < 0.3 and prev_rate < 0.3:
                difficulty = "needs_reevaluation"

        new_start = last_phase.end_day + 1
        remaining = habit.total_days - new_start + 1
        if remaining <= 0:
            return {"plan_completed": True}

        new_length = min(new_length, remaining)

        return {
            "phase_number": last_phase.phase_number + 1,
            "phase_length": new_length,
            "start_day": new_start,
            "difficulty_direction": difficulty,
            "previous_completion_rate": round(rate, 2),
            "remaining_days": remaining,
        }

    # ============ 惰性填充缺勤 ============

    async def backfill_missed_days(self, habit_id: str) -> dict:
        """填充缺勤天数为 missed 状态"""
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit or habit.status != HabitStatus.ACTIVE.value:
            return {"success": False, "error": "习惯不存在或非活跃状态"}

        tz = habit.settings.timezone
        habit.current_day = self._calculate_current_day(habit, tz)

        checked_days = {ci.day for ci in habit.check_ins}
        missed_days = []

        for d in range(1, habit.current_day):
            if d not in checked_days:
                missed_days.append(d)
                created_date = datetime.fromisoformat(habit.created_at).date()
                ci = CheckIn(
                    day=d,
                    date=(created_date + timedelta(days=d - 1)).isoformat(),
                    source=CheckInSource.AUTO.value,
                    tasks_result=[TaskResult(task="auto_missed", status=TaskStatus.MISSED.value)],
                )
                habit.check_ins.append(ci)

                # 更新 phase 中的 task status
                if habit.habit_type == HabitType.PROGRESSIVE.value:
                    for phase in habit.phases:
                        for task in phase.daily_tasks:
                            if task.day == d and task.status == TaskStatus.PENDING.value:
                                task.status = TaskStatus.MISSED.value

        if missed_days:
            self._recalculate_stats(habit)
            self._save(data)

        return {
            "success": True,
            "habit_id": habit_id,
            "missed_days_filled": missed_days,
            "count": len(missed_days),
            "within_retroactive_window": [
                d for d in missed_days
                if d >= habit.current_day - RETROACTIVE_WINDOW_DAYS
            ],
        }

    # ============ 习惯状态管理 ============

    async def list_habits(self) -> dict:
        """列出所有习惯及状态"""
        data = self._load()
        habits_info = []
        for h in data.habits:
            tz = h.settings.timezone
            if h.status == HabitStatus.ACTIVE.value:
                h.current_day = self._calculate_current_day(h, tz)

            habits_info.append({
                "habit_id": h.habit_id,
                "habit_type": h.habit_type,
                "goal_raw": h.goal_raw,
                "goal_refined": h.goal_refined,
                "status": h.status,
                "current_day": h.current_day,
                "total_days": h.total_days,
                "completion_rate": h.stats.completion_rate,
                "current_streak": h.stats.current_streak,
                "today_task": h.get_task_for_day(h.current_day) if h.status == HabitStatus.ACTIVE.value else None,
            })

        return {
            "success": True,
            "active_count": data.active_habit_count,
            "max_habits": MAX_ACTIVE_HABITS,
            "can_add": data.can_add_habit,
            "habits": habits_info,
            "is_first_use": len(data.habits) == 0,
        }

    async def pause_habit(self, habit_id: str) -> dict:
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}
        if habit.status != HabitStatus.ACTIVE.value:
            return {"success": False, "error": f"只能暂停 active 状态的习惯，当前为 {habit.status}"}

        habit.status = HabitStatus.PAUSED.value
        self._save(data)
        return {"success": True, "habit_id": habit_id, "status": "paused"}

    async def resume_habit(self, habit_id: str) -> dict:
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}
        if habit.status != HabitStatus.PAUSED.value:
            return {"success": False, "error": f"只能恢复 paused 状态的习惯，当前为 {habit.status}"}

        if not data.can_add_habit:
            return {"success": False, "error": f"已达并行上限（{MAX_ACTIVE_HABITS}个），请先完成或放弃一个"}

        habit.status = HabitStatus.ACTIVE.value
        self._save(data)
        return {"success": True, "habit_id": habit_id, "status": "active"}

    async def abandon_habit(self, habit_id: str) -> dict:
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}

        habit.status = HabitStatus.ABANDONED.value
        self._save(data)
        return {"success": True, "habit_id": habit_id, "status": "abandoned", "stats": habit.stats.to_dict()}

    async def complete_habit(self, habit_id: str, action: str = "archive") -> dict:
        """完成习惯：归档 / 续期 / 转长期"""
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}

        if action == CompletionAction.ARCHIVE.value:
            habit.status = HabitStatus.COMPLETED.value
            habit.completion_action = action
            self._save(data)
            return {"success": True, "action": "archive", "stats": habit.stats.to_dict()}

        elif action == CompletionAction.RENEW.value:
            habit.status = HabitStatus.ACTIVE.value
            habit.completion_action = action
            old_total = habit.total_days
            habit.total_days += 28  # 默认续 28 天
            self._save(data)
            return {
                "success": True,
                "action": "renew",
                "new_total_days": habit.total_days,
                "message": f"已续期，从 {old_total} 天延长到 {habit.total_days} 天",
            }

        elif action == CompletionAction.LONG_TERM.value:
            habit.status = HabitStatus.ACTIVE.value
            habit.completion_action = action
            habit.total_days = 99999  # 无限期
            self._save(data)
            return {"success": True, "action": "long_term", "message": "已转为长期追踪模式"}

        return {"success": False, "error": f"未知的 action: {action}"}

    # ============ 总结 ============

    async def get_summary(self, scope: str = "daily") -> dict:
        """获取总结数据（由 AI 基于此数据生成文案）"""
        data = self._load()
        active_habits = data.get_active_habits()

        if not active_habits:
            return {
                "success": True,
                "scope": scope,
                "has_data": False,
                "message": "当前没有在追踪的习惯。",
            }

        habits_summary = []
        for h in active_habits:
            tz = h.settings.timezone
            h.current_day = self._calculate_current_day(h, tz)

            today_checkin = h.get_checkin_for_day(h.current_day)
            today_task = h.get_task_for_day(h.current_day)

            summary = {
                "habit_id": h.habit_id,
                "goal_refined": h.goal_refined,
                "habit_type": h.habit_type,
                "current_day": h.current_day,
                "total_days": h.total_days,
                "today_task": today_task,
                "today_checked_in": today_checkin is not None,
                "today_status": today_checkin.tasks_result[0].status if today_checkin and today_checkin.tasks_result else None,
                "stats": h.stats.to_dict(),
            }

            if scope == "weekly" and h.stats.weekly_rates:
                current_week_rate = h.stats.weekly_rates[-1] if h.stats.weekly_rates else 0
                prev_week_rate = h.stats.weekly_rates[-2] if len(h.stats.weekly_rates) >= 2 else 0
                summary["week_trend"] = {
                    "current_rate": current_week_rate,
                    "previous_rate": prev_week_rate,
                    "change": round(current_week_rate - prev_week_rate, 2),
                    "direction": "up" if current_week_rate > prev_week_rate else "down" if current_week_rate < prev_week_rate else "stable",
                }

            habits_summary.append(summary)

        total_today = len(active_habits)
        checked_today = sum(1 for s in habits_summary if s["today_checked_in"])

        return {
            "success": True,
            "scope": scope,
            "has_data": True,
            "date": self._today().isoformat(),
            "overview": {
                "total_active": total_today,
                "checked_in_today": checked_today,
                "all_done_today": checked_today == total_today,
            },
            "habits": habits_summary,
        }

    # ============ 可视化 ============

    async def get_visualization(
        self, habit_id: Optional[str] = None, fmt: str = "text"
    ) -> dict:
        """获取可视化内容"""
        data = self._load()

        if habit_id:
            habit = data.get_habit(habit_id)
            if not habit:
                return {"success": False, "error": "习惯不存在"}
            habits = [habit]
        else:
            habits = data.get_active_habits()

        if not habits:
            return {"success": True, "has_data": False, "message": "没有可展示的习惯数据"}

        # 更新 current_day
        for h in habits:
            if h.status == HabitStatus.ACTIVE.value:
                h.current_day = self._calculate_current_day(h, h.settings.timezone)

        if fmt == "svg":
            content = self.visualizer.generate_svg(habits)
        else:
            content = self.visualizer.generate_text(habits)

        return {
            "success": True,
            "has_data": True,
            "format": fmt,
            "content": content,
            "habit_count": len(habits),
        }

    # ============ 计划调整 ============

    async def adjust_plan(
        self, habit_id: str, direction: str = "auto", reason: Optional[str] = None
    ) -> dict:
        """手动触发计划调整，返回参数供 AI 生成新计划"""
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}
        if habit.habit_type == HabitType.CHECKIN.value:
            return {"success": False, "error": "打卡型习惯不需要调整计划"}

        params = self._calculate_next_phase_params(habit)

        if direction in ("easier", "harder"):
            params["difficulty_direction"] = direction

        params["reason"] = reason
        params["goal_refined"] = habit.goal_refined

        return {
            "success": True,
            "habit_id": habit_id,
            "current_stats": habit.stats.to_dict(),
            "next_phase_params": params,
            "message": "请根据参数为用户生成调整后的计划。",
        }

    # ============ 外部数据源（预留）============

    async def report_progress(
        self, habit_id: str, source: str, payload: dict
    ) -> dict:
        """外部数据源上报（预留接口）"""
        data = self._load()
        habit = data.get_habit(habit_id)
        if not habit:
            return {"success": False, "error": "习惯不存在"}

        # 将外部数据转换为标准 check_in 格式
        # 具体转换逻辑根据 source 不同而不同，后续扩展
        task_results = [{
            "task": payload.get("description", habit.goal_refined),
            "status": payload.get("status", "completed"),
            "note": f"[{source}] {payload.get('raw_data', '')}",
        }]

        result = await self.check_in(habit_id, task_results)
        if result["success"]:
            # 更新 source
            checkin_data = self._load()
            h = checkin_data.get_habit(habit_id)
            if h and h.check_ins:
                h.check_ins[-1].source = CheckInSource.EXTERNAL.value
                self.store.save(checkin_data)

        return result


# ============ CLI 入口 ============

def main():
    parser = argparse.ArgumentParser(description="Habit Tracker CLI")
    parser.add_argument("action", choices=[
        "list", "summary", "visualize", "remind", "backfill"
    ])
    parser.add_argument("--habit-id", help="习惯 ID")
    parser.add_argument("--scope", default="daily", help="总结范围: daily/weekly")
    parser.add_argument("--format", default="text", help="可视化格式: text/svg")
    parser.add_argument("--data-dir", help="数据目录")

    args = parser.parse_args()

    import asyncio
    tracker = HabitTracker(data_dir=args.data_dir)

    async def run():
        if args.action == "list":
            result = await tracker.list_habits()
        elif args.action == "summary":
            result = await tracker.get_summary(scope=args.scope)
        elif args.action == "visualize":
            result = await tracker.get_visualization(habit_id=args.habit_id, fmt=args.format)
        elif args.action == "remind":
            result = await tracker.reminder.trigger_reminder(tracker)
        elif args.action == "backfill":
            if args.habit_id:
                result = await tracker.backfill_missed_days(args.habit_id)
            else:
                result = {"error": "backfill 需要 --habit-id 参数"}
        else:
            result = {"error": f"未知操作: {args.action}"}

        print(json.dumps(result, ensure_ascii=False, indent=2))

    asyncio.run(run())


if __name__ == "__main__":
    main()
