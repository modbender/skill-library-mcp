"""
Habit Tracker - 数据模型定义
所有数据结构的 schema 定义与校验逻辑
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime, date
import json
import uuid


# ============ 枚举常量 ============

class HabitType(str, Enum):
    PROGRESSIVE = "progressive"  # 递进型（如跑步、阅读量）
    CHECKIN = "checkin"          # 打卡型（如早起、冥想）


class HabitStatus(str, Enum):
    DRAFT = "draft"              # 合理化未完成
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"          # 用户主动跳过
    MISSED = "missed"            # 系统标记（缺勤）


class CheckInSource(str, Enum):
    SELF_REPORT = "self_report"
    AUTO = "auto"                # 系统自动标记
    EXTERNAL = "external"        # 外部数据源


class RationalizationStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CompletionAction(str, Enum):
    ARCHIVE = "archive"          # 归档
    RENEW = "renew"              # 续期
    LONG_TERM = "long_term"      # 转长期打卡


class SummaryFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


# ============ 数据类 ============

@dataclass
class ConversationTurn:
    role: str       # "ai" | "user"
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, d: dict) -> "ConversationTurn":
        return cls(role=d["role"], content=d["content"])


@dataclass
class Rationalization:
    status: str = RationalizationStatus.IN_PROGRESS.value
    conversation: list[ConversationTurn] = field(default_factory=list)
    round_count: int = 0  # 当前轮数，最多4轮

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "conversation": [t.to_dict() for t in self.conversation],
            "round_count": self.round_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Rationalization":
        return cls(
            status=d.get("status", RationalizationStatus.IN_PROGRESS.value),
            conversation=[ConversationTurn.from_dict(t) for t in d.get("conversation", [])],
            round_count=d.get("round_count", 0),
        )


@dataclass
class DailyTask:
    day: int
    description: str
    status: str = TaskStatus.PENDING.value

    def to_dict(self) -> dict:
        return {"day": self.day, "description": self.description, "status": self.status}

    @classmethod
    def from_dict(cls, d: dict) -> "DailyTask":
        return cls(day=d["day"], description=d["description"], status=d.get("status", TaskStatus.PENDING.value))


@dataclass
class Phase:
    phase_number: int
    phase_length: int
    start_day: int
    daily_tasks: list[DailyTask] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "phase_number": self.phase_number,
            "phase_length": self.phase_length,
            "start_day": self.start_day,
            "daily_tasks": [t.to_dict() for t in self.daily_tasks],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Phase":
        return cls(
            phase_number=d["phase_number"],
            phase_length=d["phase_length"],
            start_day=d["start_day"],
            daily_tasks=[DailyTask.from_dict(t) for t in d.get("daily_tasks", [])],
        )

    @property
    def end_day(self) -> int:
        return self.start_day + self.phase_length - 1

    @property
    def completion_rate(self) -> float:
        if not self.daily_tasks:
            return 0.0
        completed = sum(1 for t in self.daily_tasks if t.status == TaskStatus.COMPLETED.value)
        partial = sum(1 for t in self.daily_tasks if t.status == TaskStatus.PARTIAL.value)
        return (completed + partial * 0.5) / len(self.daily_tasks)


@dataclass
class TaskResult:
    task: str
    status: str
    note: str = ""

    def to_dict(self) -> dict:
        return {"task": self.task, "status": self.status, "note": self.note}

    @classmethod
    def from_dict(cls, d: dict) -> "TaskResult":
        return cls(task=d["task"], status=d["status"], note=d.get("note", ""))


@dataclass
class CheckIn:
    day: int
    date: str  # ISO format date string
    source: str = CheckInSource.SELF_REPORT.value
    tasks_result: list[TaskResult] = field(default_factory=list)
    ai_feedback: str = ""
    retroactive: bool = False  # 是否为补报

    def to_dict(self) -> dict:
        return {
            "day": self.day,
            "date": self.date,
            "source": self.source,
            "tasks_result": [t.to_dict() for t in self.tasks_result],
            "ai_feedback": self.ai_feedback,
            "retroactive": self.retroactive,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CheckIn":
        return cls(
            day=d["day"],
            date=d["date"],
            source=d.get("source", CheckInSource.SELF_REPORT.value),
            tasks_result=[TaskResult.from_dict(t) for t in d.get("tasks_result", [])],
            ai_feedback=d.get("ai_feedback", ""),
            retroactive=d.get("retroactive", False),
        )


@dataclass
class Stats:
    completion_rate: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    total_completed: int = 0
    total_partial: int = 0
    total_skipped: int = 0
    total_missed: int = 0
    weekly_rates: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Stats":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class HabitSettings:
    reminder_time: str = "21:00"
    summary_frequency: str = SummaryFrequency.DAILY.value
    timezone: str = "Asia/Shanghai"
    coaching_style: Optional[str] = None  # None = 继承 OpenClaw 人设

    def to_dict(self) -> dict:
        return {
            "reminder_time": self.reminder_time,
            "summary_frequency": self.summary_frequency,
            "timezone": self.timezone,
            "coaching_style": self.coaching_style,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "HabitSettings":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Habit:
    habit_id: str
    habit_type: str  # progressive | checkin
    goal_raw: str
    goal_refined: Optional[str] = None
    completion_criteria: Optional[str] = None
    status: str = HabitStatus.DRAFT.value
    total_days: int = 28
    current_day: int = 0
    created_at: str = ""
    rationalization: Optional[Rationalization] = None
    phases: list[Phase] = field(default_factory=list)
    checkin_task: Optional[str] = None  # checkin 类型的固定任务描述
    check_ins: list[CheckIn] = field(default_factory=list)
    stats: Stats = field(default_factory=Stats)
    settings: HabitSettings = field(default_factory=HabitSettings)
    completion_action: Optional[str] = None  # archive | renew | long_term

    def __post_init__(self):
        if not self.habit_id:
            self.habit_id = f"h_{uuid.uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if self.rationalization is None:
            self.rationalization = Rationalization()

    def to_dict(self) -> dict:
        return {
            "habit_id": self.habit_id,
            "habit_type": self.habit_type,
            "goal_raw": self.goal_raw,
            "goal_refined": self.goal_refined,
            "completion_criteria": self.completion_criteria,
            "status": self.status,
            "total_days": self.total_days,
            "current_day": self.current_day,
            "created_at": self.created_at,
            "rationalization": self.rationalization.to_dict() if self.rationalization else None,
            "phases": [p.to_dict() for p in self.phases],
            "checkin_task": self.checkin_task,
            "check_ins": [c.to_dict() for c in self.check_ins],
            "stats": self.stats.to_dict(),
            "settings": self.settings.to_dict(),
            "completion_action": self.completion_action,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        habit = cls(
            habit_id=d["habit_id"],
            habit_type=d["habit_type"],
            goal_raw=d["goal_raw"],
            goal_refined=d.get("goal_refined"),
            completion_criteria=d.get("completion_criteria"),
            status=d.get("status", HabitStatus.DRAFT.value),
            total_days=d.get("total_days", 28),
            current_day=d.get("current_day", 0),
            created_at=d.get("created_at", ""),
        )
        if "rationalization" in d and d["rationalization"]:
            habit.rationalization = Rationalization.from_dict(d["rationalization"])
        habit.phases = [Phase.from_dict(p) for p in d.get("phases", [])]
        habit.checkin_task = d.get("checkin_task")
        habit.check_ins = [CheckIn.from_dict(c) for c in d.get("check_ins", [])]
        if "stats" in d:
            habit.stats = Stats.from_dict(d["stats"])
        if "settings" in d:
            habit.settings = HabitSettings.from_dict(d["settings"])
        habit.completion_action = d.get("completion_action")
        return habit

    def get_checkin_for_day(self, day: int) -> Optional[CheckIn]:
        for c in self.check_ins:
            if c.day == day:
                return c
        return None

    def get_current_phase(self) -> Optional[Phase]:
        for p in self.phases:
            if p.start_day <= self.current_day <= p.end_day:
                return p
        return None

    def get_task_for_day(self, day: int) -> Optional[str]:
        if self.habit_type == HabitType.CHECKIN.value:
            return self.checkin_task
        for phase in self.phases:
            for task in phase.daily_tasks:
                if task.day == day:
                    return task.description
        return None


@dataclass
class PendingReminder:
    created_at: str
    message: str
    delivered: bool = False
    habit_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "message": self.message,
            "delivered": self.delivered,
            "habit_ids": self.habit_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PendingReminder":
        return cls(
            created_at=d["created_at"],
            message=d["message"],
            delivered=d.get("delivered", False),
            habit_ids=d.get("habit_ids", []),
        )


@dataclass
class UserProfile:
    background: Optional[str] = None
    created_at: str = ""
    preferred_coaching_style: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "background": self.background,
            "created_at": self.created_at,
            "preferred_coaching_style": self.preferred_coaching_style,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UserProfile":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class UserData:
    profile: UserProfile = field(default_factory=UserProfile)
    habits: list[Habit] = field(default_factory=list)
    pending_reminders: list[PendingReminder] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "profile": self.profile.to_dict(),
            "habits": [h.to_dict() for h in self.habits],
            "pending_reminders": [r.to_dict() for r in self.pending_reminders],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "UserData":
        data = cls()
        if "profile" in d:
            data.profile = UserProfile.from_dict(d["profile"])
        data.habits = [Habit.from_dict(h) for h in d.get("habits", [])]
        data.pending_reminders = [PendingReminder.from_dict(r) for r in d.get("pending_reminders", [])]
        return data

    def get_habit(self, habit_id: str) -> Optional[Habit]:
        for h in self.habits:
            if h.habit_id == habit_id:
                return h
        return None

    def get_active_habits(self) -> list[Habit]:
        return [h for h in self.habits if h.status == HabitStatus.ACTIVE.value]

    def get_draft_habits(self) -> list[Habit]:
        return [h for h in self.habits if h.status == HabitStatus.DRAFT.value]

    @property
    def active_habit_count(self) -> int:
        return len(self.get_active_habits())

    @property
    def can_add_habit(self) -> bool:
        return self.active_habit_count < 5


# ============ 校验函数 ============

VALID_HABIT_TYPES = {e.value for e in HabitType}
VALID_HABIT_STATUSES = {e.value for e in HabitStatus}
VALID_TASK_STATUSES = {e.value for e in TaskStatus}
VALID_CHECKIN_SOURCES = {e.value for e in CheckInSource}
VALID_SUMMARY_FREQUENCIES = {e.value for e in SummaryFrequency}
VALID_COMPLETION_ACTIONS = {e.value for e in CompletionAction}


def validate_habit(habit: Habit) -> list[str]:
    """校验 Habit 数据完整性，返回错误列表（空列表表示通过）"""
    errors = []

    if habit.habit_type not in VALID_HABIT_TYPES:
        errors.append(f"Invalid habit_type: {habit.habit_type}")

    if habit.status not in VALID_HABIT_STATUSES:
        errors.append(f"Invalid status: {habit.status}")

    if habit.total_days < 1 or habit.total_days > 365:
        errors.append(f"total_days must be 1-365, got: {habit.total_days}")

    if habit.current_day < 0:
        errors.append(f"current_day cannot be negative: {habit.current_day}")

    if habit.habit_type == HabitType.CHECKIN.value and habit.status == HabitStatus.ACTIVE.value:
        if not habit.checkin_task:
            errors.append("Checkin-type habit must have checkin_task when active")

    for phase in habit.phases:
        for task in phase.daily_tasks:
            if task.status not in VALID_TASK_STATUSES:
                errors.append(f"Invalid task status on day {task.day}: {task.status}")

    for checkin in habit.check_ins:
        if checkin.source not in VALID_CHECKIN_SOURCES:
            errors.append(f"Invalid checkin source on day {checkin.day}: {checkin.source}")

    if habit.completion_action and habit.completion_action not in VALID_COMPLETION_ACTIONS:
        errors.append(f"Invalid completion_action: {habit.completion_action}")

    if habit.settings.summary_frequency not in VALID_SUMMARY_FREQUENCIES:
        errors.append(f"Invalid summary_frequency: {habit.settings.summary_frequency}")

    return errors
