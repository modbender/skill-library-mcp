#!/usr/bin/env python3
"""健康度评分模块：0-100分系统"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("heartbeat.health")

WORKSPACE = Path(__file__).parent.parent / "workspace"
STATE_FILE = WORKSPACE / "state.json"


def _load_state() -> dict:
    """加载持久化状态"""
    if not STATE_FILE.exists():
        return {
            "beat_count": 0,
            "beat_ok_count": 0,
            "streak": 0,
            "health_history": [],
            "last_beat": None,
        }
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return {
            "beat_count": 0,
            "beat_ok_count": 0,
            "streak": 0,
            "health_history": [],
            "last_beat": None,
        }


def _save_state(state: dict):
    """保存持久化状态（原子写入）"""
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp.rename(STATE_FILE)


def _load_config() -> dict:
    """加载健康度配置"""
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("health", {})


def calculate_score(
    daily_result: dict,
    todo_result: dict,
    ongoing_result: dict,
    mail_result: dict,
    git_result: dict,
) -> int:
    """
    计算当次心跳健康度评分（0-100）

    评分维度:
    - daily 完成率: 25分
    - todo 完成率 + 超期扣分: 20分
    - ongoing 状态健康度: 25分
    - 邮件状态: 15分
    - git 同步: 15分
    """
    score = 0

    # 1. daily 完成率 (25分)
    if daily_result.get("error"):
        score += 10  # 文件缺失给基础分
    elif daily_result["total"] > 0:
        ratio = daily_result["done"] / daily_result["total"]
        score += int(ratio * 25)
    else:
        score += 25  # 无 daily 项视为全部完成

    # 2. todo 完成率 + 超期 (20分)
    if todo_result.get("error"):
        score += 10
    else:
        if todo_result["total"] > 0:
            ratio = todo_result["done"] / todo_result["total"]
            base = int(ratio * 20)
            # 每个超期项扣3分
            penalty = len(todo_result.get("overdue", [])) * 3
            score += max(0, base - penalty)
        else:
            score += 20

    # 3. ongoing 状态 (25分)
    if ongoing_result.get("error"):
        score += 10
    else:
        by_status = ongoing_result.get("by_status", {})
        total = ongoing_result.get("total", 0)
        if total == 0:
            score += 25
        else:
            # BLOCK 和超期严重扣分
            block_count = by_status.get("BLOCK", 0)
            overdue_count = len(ongoing_result.get("overdue", []))
            done_count = by_status.get("DONE", 0)

            base = 25
            base -= block_count * 8   # 每个 BLOCK 扣8分
            base -= overdue_count * 4  # 每个超期扣4分
            base += min(5, done_count * 2)  # 完成奖励，最多5分
            score += max(0, min(25, base))

    # 4. 邮件状态 (15分)
    if mail_result.get("error"):
        score += 5  # 邮件检查失败给基础分
    else:
        base = 15
        # 未读过多扣分
        unread = mail_result.get("unread_count", 0)
        if unread > 10:
            base -= 5
        elif unread > 5:
            base -= 2
        score += max(0, base)

    # 5. git 同步 (15分)
    if git_result is None or git_result.get("enabled") is False:
        score += 15  # git 未启用视为正常（不惩罚禁用 git 的用户）
    elif git_result.get("error"):
        score += 5
    else:
        if git_result.get("push", False):
            score += 15
        elif git_result.get("commit", False):
            score += 10
        else:
            score += 5

    return min(100, max(0, score))


def record_score(score: int) -> dict:
    """
    记录健康度分数，检查是否需要告警

    返回:
        {
            "score": int,
            "streak": int,
            "beat_count": int,
            "beat_ok_count": int,
            "alert_needed": bool,
            "consecutive_low": int,
        }
    """
    config = _load_config()
    state = _load_state()
    threshold = config.get("alert_threshold", 60)
    alert_consecutive = config.get("alert_consecutive", 3)

    state["beat_count"] = state.get("beat_count", 0) + 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    state["last_beat"] = now_str

    # 记录分数历史（保留最近 100 条）
    history = state.get("health_history", [])
    history.append({"time": now_str, "score": score})
    if len(history) > 100:
        history = history[-100:]
    state["health_history"] = history

    # 计算连续低分次数
    consecutive_low = 0
    for entry in reversed(history):
        if entry["score"] < threshold:
            consecutive_low += 1
        else:
            break

    alert_needed = consecutive_low >= alert_consecutive

    # 更新 streak 和 ok 计数
    if score >= threshold:
        state["beat_ok_count"] = state.get("beat_ok_count", 0) + 1
        state["streak"] = state.get("streak", 0) + 1
    else:
        state["streak"] = 0

    _save_state(state)

    result = {
        "score": score,
        "streak": state["streak"],
        "beat_count": state["beat_count"],
        "beat_ok_count": state["beat_ok_count"],
        "alert_needed": alert_needed,
        "consecutive_low": consecutive_low,
    }

    if alert_needed:
        logger.warning("健康度告警: 连续 %d 次低于 %d 分", consecutive_low, threshold)

    return result


def get_stats() -> dict:
    """获取健康度统计信息"""
    state = _load_state()
    history = state.get("health_history", [])

    if not history:
        return {
            "current": 0,
            "average": 0,
            "min": 0,
            "max": 0,
            "streak": 0,
            "total_beats": 0,
        }

    scores = [h["score"] for h in history]
    recent = scores[-10:] if len(scores) >= 10 else scores

    return {
        "current": scores[-1] if scores else 0,
        "average": round(sum(recent) / len(recent), 1),
        "min": min(scores),
        "max": max(scores),
        "streak": state.get("streak", 0),
        "total_beats": state.get("beat_count", 0),
    }
