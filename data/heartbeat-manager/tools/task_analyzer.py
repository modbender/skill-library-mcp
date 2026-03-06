#!/usr/bin/env python3
"""智能超时/卡死分析模块"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger("heartbeat.analyzer")

WORKSPACE = Path(__file__).parent.parent / "workspace"


def _load_config() -> dict:
    """加载超时分析配置"""
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("timeout", {})


def _load_ongoing() -> list:
    """加载 ongoing.json"""
    path = WORKSPACE / "ongoing.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("tasks", [])
    except (json.JSONDecodeError, Exception) as e:
        logger.error("加载 ongoing.json 失败: %s", e)
        return []


def _save_ongoing(tasks: list):
    """保存 ongoing.json（原子写入，保持 {"tasks":[...]} 格式）"""
    path = WORKSPACE / "ongoing.json"
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp_path.rename(path)


def _get_recent_history(task: dict, n: int = 3) -> list:
    """获取任务最近 N 条历史记录"""
    history = task.get("history", [])
    return history[-n:] if history else []


def _calc_progress_delta(history: list) -> float:
    """计算历史记录中 progress 的变化量"""
    if len(history) < 2:
        return 0.0
    progresses = [h.get("progress", 0) for h in history]
    return progresses[-1] - progresses[0]


def _context_changed(history: list) -> bool:
    """检查历史记录中 context 是否有变化"""
    if len(history) < 2:
        return False
    contexts = [h.get("context", "") for h in history]
    return len(set(contexts)) > 1


def analyze_task(task: dict, config: Optional[dict] = None) -> dict:
    """
    分析单个任务是否卡死

    返回:
        {
            "task_id": str,
            "title": str,
            "status": str,          # "normal" | "slow" | "stuck"
            "reason": str,
            "action": str,          # "none" | "log" | "alert"
            "details": str
        }
    """
    if config is None:
        config = _load_config()

    task_id = task.get("id", "?")
    title = task.get("title", "未命名")
    result = {
        "task_id": task_id,
        "title": title,
        "status": "normal",
        "reason": "",
        "action": "none",
        "details": "",
    }

    # 只分析 WIP 和 WAIT 状态的任务
    task_status = task.get("status", "IDLE")
    if task_status not in ("WIP", "WAIT"):
        return result

    now = datetime.now()
    stale_beats = config.get("stale_beats", 3)
    progress_threshold = config.get("progress_threshold", 5)
    eta_grace_hours = config.get("eta_grace_hours", 2)

    # 获取最近历史
    history = _get_recent_history(task, stale_beats)
    progress_delta = _calc_progress_delta(history)
    context_changed = _context_changed(history)

    # 检查是否超过 eta
    eta_overdue = False
    eta = task.get("eta", "")
    if eta and eta != "持续":
        try:
            if len(eta) <= 5:
                eta_date = datetime.strptime(eta, "%m-%d").replace(year=now.year)
            else:
                eta_date = datetime.strptime(eta, "%Y-%m-%d")
            grace = timedelta(hours=eta_grace_hours)
            if now > eta_date + grace:
                eta_overdue = True
        except ValueError:
            pass

    # 检查心跳无进展
    beats_stale = (
        len(history) >= stale_beats
        and abs(progress_delta) < progress_threshold
        and not context_changed
    )

    # 判断逻辑
    if beats_stale and eta_overdue:
        # 完全卡死：超期且无进展
        result["status"] = "stuck"
        result["reason"] = f"超过 ETA 且连续 {stale_beats} 个心跳无进展"
        result["action"] = "alert"
        result["details"] = (
            f"任务 [{task_id}] {title} 疑似卡死\n"
            f"  状态: {task_status}\n"
            f"  ETA: {eta}（已超期）\n"
            f"  最近进度变化: {progress_delta:.1f}%\n"
            f"  context 变化: {'有' if context_changed else '无'}\n"
        )
    elif beats_stale:
        # 无进展但未超期
        result["status"] = "stuck"
        result["reason"] = f"连续 {stale_beats} 个心跳无进展（无 context 变化）"
        result["action"] = "alert"
        result["details"] = (
            f"任务 [{task_id}] {title} 疑似停滞\n"
            f"  最近进度变化: {progress_delta:.1f}%\n"
        )
    elif eta_overdue and progress_delta > 0:
        # 超期但有进展——正常推进只是慢
        result["status"] = "slow"
        result["reason"] = "超过 ETA 但仍有进展"
        result["action"] = "log"
        result["details"] = (
            f"任务 [{task_id}] {title} 进展缓慢\n"
            f"  进度变化: +{progress_delta:.1f}%\n"
        )
    elif eta_overdue:
        # 超期且历史记录不足以判断
        result["status"] = "slow"
        result["reason"] = "超过 ETA，历史记录不足"
        result["action"] = "log"
        result["details"] = f"任务 [{task_id}] {title} 超过 ETA，待观察"

    return result


def analyze_all() -> dict:
    """
    分析所有 ongoing 任务

    返回:
        {
            "total_analyzed": int,
            "stuck": [dict],        # 卡死的任务分析结果
            "slow": [dict],         # 缓慢的任务分析结果
            "normal": int,          # 正常任务数
            "actions_taken": [str], # 执行的动作描述
        }
    """
    config = _load_config()
    tasks = _load_ongoing()

    result = {
        "total_analyzed": 0,
        "stuck": [],
        "slow": [],
        "normal": 0,
        "actions_taken": [],
    }

    for task in tasks:
        if task.get("status") not in ("WIP", "WAIT"):
            continue

        result["total_analyzed"] += 1
        analysis = analyze_task(task, config)

        if analysis["status"] == "stuck":
            result["stuck"].append(analysis)
        elif analysis["status"] == "slow":
            result["slow"].append(analysis)
        else:
            result["normal"] += 1

    # 对卡死任务执行动作
    for stuck in result["stuck"]:
        task_id = stuck["task_id"]

        # 在 ongoing.json 中标记 BLOCK
        for task in tasks:
            if str(task.get("id")) == str(task_id) and task.get("status") != "BLOCK":
                task["status"] = "BLOCK"
                task["blocked_by"] = stuck["reason"]
                task.setdefault("history", []).append({
                    "time": datetime.now().isoformat(),
                    "event": "auto_blocked",
                    "reason": stuck["reason"],
                    "progress": task.get("progress", 0),
                    "context": task.get("context", ""),
                })
                result["actions_taken"].append(f"任务 {task_id} 标记为 BLOCK")

        # 发送告警邮件
        from tools.mail import send_alert
        sent = send_alert(
            f"任务卡死: {stuck['title']}",
            stuck["details"],
        )
        if sent:
            result["actions_taken"].append(f"任务 {task_id} 告警邮件已发送")
        else:
            result["actions_taken"].append(f"任务 {task_id} 告警邮件发送失败")

    # 保存更新后的 ongoing.json
    if result["stuck"]:
        _save_ongoing(tasks)

    logger.info(
        "任务分析完成: 分析=%d, 卡死=%d, 缓慢=%d",
        result["total_analyzed"], len(result["stuck"]), len(result["slow"]),
    )
    return result


def record_beat(task_id: str, progress: int = None, context: str = None):
    """
    为指定任务记录一次心跳历史

    参数:
        task_id: 任务 ID
        progress: 当前进度（0-100）
        context: 当前上下文描述
    """
    tasks = _load_ongoing()
    for task in tasks:
        if str(task.get("id")) == str(task_id):
            entry = {
                "time": datetime.now().isoformat(),
                "event": "heartbeat",
                "progress": progress if progress is not None else task.get("progress", 0),
                "context": context if context is not None else task.get("context", ""),
            }
            task.setdefault("history", []).append(entry)
            task["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if progress is not None:
                task["progress"] = progress
            if context is not None:
                task["context"] = context
            break

    _save_ongoing(tasks)
