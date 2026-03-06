"""
OASIS Forum - Discussion Scheduler

Parses YAML schedule definitions and yields execution steps
that control the order in which experts speak.

Either schedule_file or schedule_yaml is required. schedule_file
takes priority if both are provided. Even for simple all-parallel
scenarios, a minimal YAML suffices:
  version: 1
  repeat: true
  plan:
    - all_experts: true

Schedule YAML format:
  version: 1
  repeat: true          # true = 每轮重复整个 plan; false = plan 只执行一次
  discussion: false     # true = 论坛讨论模式(JSON回复/投票); false = 执行模式(agent直接执行任务，默认)
  plan:
    # 指定专家发言（按名称匹配）
    # 名称格式直接对应 engine 的专家类型（必须含 '#'）：
    #   "tag#temp#N"          → ExpertAgent (tag 查预设获取 name/persona)
    #   "tag#oasis#随机ID"    → SessionExpert (oasis, tag 查预设获取 name/persona)
    #   "标题#session_id"     → SessionExpert (普通 agent, 不注入)
    #   任何 session 名 + "#new" → 强制创建全新 session（ID 替换为随机 UUID）
    - expert: "critical#temp#1"
      instruction: "请重点分析技术风险"    # 可选：给专家的具体指令

    # 多个专家同时并行发言
    - parallel:
        - expert: "创意专家"
          instruction: "从创新角度提出方案"
        - expert: "数据分析师"

    # 手动注入一条帖子（不经过 LLM）
    - manual:
        author: "主持人"
        content: "请大家聚焦到可行性方面讨论"
        reply_to: null

    # 所有专家并行（等同于不用 schedule 的默认行为）
    - all_experts: true

Execution modes:
  repeat: true  -> plan 在每轮重复执行，max_rounds 控制总轮数
  repeat: false -> plan 中的步骤顺序执行一次即结束（忽略 max_rounds）

If no schedule is provided, the engine will raise a ValueError.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import yaml


class StepType(str, Enum):
    """Types of schedule steps."""
    EXPERT = "expert"           # Single expert speaks (sequential)
    PARALLEL = "parallel"       # Multiple experts speak in parallel
    ALL = "all_experts"         # All experts speak in parallel
    MANUAL = "manual"           # Inject a post manually (no LLM)


@dataclass
class ScheduleStep:
    """A single step in the discussion schedule."""
    step_type: StepType
    expert_names: list[str] = field(default_factory=list)   # for EXPERT / PARALLEL
    instructions: dict[str, str] = field(default_factory=dict)  # expert_name → instruction text
    manual_author: str = ""                                  # for MANUAL
    manual_content: str = ""                                 # for MANUAL
    manual_reply_to: Optional[int] = None                    # for MANUAL


@dataclass
class Schedule:
    """Parsed schedule with steps and config."""
    steps: list[ScheduleStep]
    repeat: bool = False  # True = repeat plan each round; False = run once
    discussion: bool = False  # True = forum discussion mode (JSON reply/vote); False = execute mode (agents just run tasks)


def parse_schedule(yaml_content: str) -> Schedule:
    """
    Parse a YAML schedule string into a Schedule object.

    Raises ValueError on invalid format.
    """
    data = yaml.safe_load(yaml_content)
    if not isinstance(data, dict) or "plan" not in data:
        raise ValueError("Schedule YAML must contain a 'plan' key")

    plan = data["plan"]
    if not isinstance(plan, list):
        raise ValueError("'plan' must be a list of steps")

    repeat = bool(data.get("repeat", False))
    discussion = bool(data.get("discussion", False))

    steps: list[ScheduleStep] = []
    for i, item in enumerate(plan):
        if not isinstance(item, dict):
            raise ValueError(f"Step {i}: must be a dict, got {type(item).__name__}")

        if "expert" in item:
            expert_name = str(item["expert"])
            instr_map = {}
            if "instruction" in item:
                instr_map[expert_name] = str(item["instruction"])
            steps.append(ScheduleStep(
                step_type=StepType.EXPERT,
                expert_names=[expert_name],
                instructions=instr_map,
            ))

        elif "parallel" in item:
            names = []
            instr_map = {}
            for sub in item["parallel"]:
                if isinstance(sub, dict) and "expert" in sub:
                    ename = str(sub["expert"])
                    names.append(ename)
                    if "instruction" in sub:
                        instr_map[ename] = str(sub["instruction"])
                elif isinstance(sub, str):
                    names.append(sub)
                else:
                    raise ValueError(f"Step {i}: parallel entries must have 'expert' key")
            if not names:
                raise ValueError(f"Step {i}: parallel list is empty")
            steps.append(ScheduleStep(
                step_type=StepType.PARALLEL,
                expert_names=names,
                instructions=instr_map,
            ))

        elif "all_experts" in item:
            steps.append(ScheduleStep(step_type=StepType.ALL))

        elif "manual" in item:
            m = item["manual"]
            if not isinstance(m, dict) or "content" not in m:
                raise ValueError(f"Step {i}: manual must have 'content'")
            steps.append(ScheduleStep(
                step_type=StepType.MANUAL,
                manual_author=str(m.get("author", "主持人")),
                manual_content=str(m["content"]),
                manual_reply_to=m.get("reply_to"),
            ))

        else:
            raise ValueError(f"Step {i}: unknown step type, keys={list(item.keys())}")

    return Schedule(steps=steps, repeat=repeat, discussion=discussion)


def load_schedule_file(path: str) -> Schedule:
    """Load and parse a schedule from a YAML file path."""
    with open(path, "r", encoding="utf-8") as f:
        return parse_schedule(f.read())


def extract_expert_names(schedule: Schedule) -> list[str]:
    """Extract all unique expert names referenced in a schedule (preserving order).

    Scans EXPERT and PARALLEL steps for expert_names.
    ALL and MANUAL steps don't reference specific experts so are skipped.
    Returns a deduplicated list in order of first appearance.
    """
    seen: set[str] = set()
    result: list[str] = []
    for step in schedule.steps:
        if step.step_type in (StepType.EXPERT, StepType.PARALLEL):
            for name in step.expert_names:
                if name not in seen:
                    seen.add(name)
                    result.append(name)
    return result
