#!/usr/bin/env python3
"""Heartbeat with I'm Doing System Integration v1.8.1

v1.8.1 新增：防死循環保護整合
- 心跳頻率限制（防止過於頻繁檢查）
- 自動停滯檢測和處理
- 智能降級策略
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_state import AgentState

def heartbeat_with_state(agent_name="qst"):
    """v1.8.1: Enhanced heartbeat with loop protection

    Returns:
        檢查結果字典
    """
    state_mgr = AgentState(agent_name)
    state = state_mgr.get_status()

    # v1.8.1: 檢查心跳頻率限制
    should_throttle, throttle_reason, wait_seconds = state_mgr.should_throttle_heartbeat()

    if should_throttle:
        # 心跳過於頻繁，返回限制信息
        result = {
            "agent": agent_name,
            "status": state.get('status', 'idle'),
            "priority": state.get('priority', 'normal'),
            "task": state.get('task'),
            "progress": state.get('progress', 0),
            "throttled": True,
            "throttle_reason": throttle_reason,
            "wait_seconds": wait_seconds,
            "message": f"[{agent_name}] ⏸️ 心跳頻率限制：{throttle_reason}（等待 {wait_seconds} 秒）",
            "checks": [],
            "checks_skipped": ["mentions", "alerts", "forum_patrol", "vote_check", "routine"],
            "note": "跳過檢查以避免死循環"
        }
        state_mgr._update_heartbeat(check_result=result)
        return result

    # v1.8.1: 自動處理停滯任務
    stagnation_result = state_mgr.auto_handle_stagnation()

    # 重新加載狀態（可能已被 auto_handle_stagnation 修改）
    state = state_mgr.get_status()

    priority = state.get('priority', 'normal')
    status = state.get('status', 'idle')

    result = {
        "agent": agent_name,
        "status": status,
        "priority": priority,
        "task": state.get('task'),
        "progress": state.get('progress', 0),
        "tags": state.get('tags', []),
        "can_interrupt": state_mgr.can_interrupt(),
        "throttled": False,
        "stagnation_detected": stagnation_result.get("stagnant", False),
        "timeout_detected": stagnation_result.get("timeout", False),
        "auto_action_taken": stagnation_result.get("action", "none"),
        "checks": [],
        "checks_skipped": [],
        "message": ""
    }

    # v1.8.1: 添加停滯警告信息
    if stagnation_result["action"] != "none":
        action_msg = {
            "downgrade": "已自動降級優先級",
            "block": "已標記為受阻，需要人工處理",
            "none": ""
        }.get(stagnation_result["action"], "")

        if action_msg:
            result["warning"] = action_msg
            if stagnation_result.get("stagnant_reason"):
                result["stagnant_reason"] = stagnation_result["stagnant_reason"]
            if stagnation_result.get("timeout_reason"):
                result["timeout_reason"] = stagnation_result["timeout_reason"]

    # v1.8.1: Prioritized heartbeat strategy (保持原有邏輯)
    if status == 'blocked':
        # BLOCKED: 只檢查緊急通知
        result.update({
            "message": f"[{agent_name}] ⛔ BLOCKED: {state.get('context', {}).get('blocked_reason', 'Unknown')}",
            "skip_low_priority": True,
            "checks": ['mentions', 'alerts'],
            "checks_skipped": ['forum_patrol', 'vote_check', 'routine'],
            "note": "任務受阻，僅檢查緊急通知"
        })
    elif status == 'doing':
        # DOING: 根據優先級決定檢查內容
        if priority == 'critical':
            result.update({
                "message": f"[{agent_name}] 🔥 DOING [CRITICAL]: {state['task']} ({state['progress']}%)",
                "skip_low_priority": True,
                "checks": ['mentions', 'alerts'],
                "checks_skipped": ['forum_patrol', 'vote_check', 'email_check', 'routine'],
                "note": "關鍵任務執行中，最小化干擾"
            })
        elif priority == 'high':
            result.update({
                "message": f"[{agent_name}] ⚡ DOING [HIGH]: {state['task']} ({state['progress']}%)",
                "skip_low_priority": True,
                "checks": ['mentions', 'alerts'],
                "checks_skipped": ['forum_patrol', 'vote_check', 'routine'],
                "note": "重要任務執行中"
            })
        else:
            result.update({
                "message": f"[{agent_name}] 🔄 DOING [{priority.upper()}]: {state['task']} ({state['progress']}%)",
                "skip_low_priority": False,
                "checks": ['mentions', 'alerts', 'forum_patrol'],
                "checks_skipped": ['vote_check'],
                "note": "標準任務執行中"
            })
    elif status == 'waiting':
        # WAITING: 根據優先級
        if priority in ['critical', 'high']:
            result.update({
                "message": f"[{agent_name}] ⏳ WAITING [{priority.upper()}]: {state.get('context', {}).get('waiting_for', 'Unknown')}",
                "skip_low_priority": True,
                "checks": ['mentions', 'alerts'],
                "checks_skipped": ['forum_patrol', 'vote_check'],
                "note": "等待中，檢查重要通知"
            })
        else:
            result.update({
                "message": f"[{agent_name}] ⏳ WAITING [{priority.upper()}]: {state.get('context', {}).get('waiting_for', 'Unknown')}",
                "skip_low_priority": False,
                "checks": ['mentions', 'alerts', 'forum_patrol'],
                "checks_skipped": [],
                "note": "等待中"
            })
    elif status == 'paused':
        # PAUSED
        result.update({
            "message": f"[{agent_name}] ⏸️ PAUSED: {state['task']} ({state.get('context', {}).get('pause_reason', 'No reason')})",
            "skip_low_priority": False,
            "checks": ['mentions', 'alerts', 'forum_patrol'],
            "checks_skipped": [],
            "note": "任務已暫停"
        })
    elif status in ['completed', 'failed']:
        # COMPLETED / FAILED
        result.update({
            "message": f"[{agent_name}] {status.upper()}: {state['task']}",
            "skip_low_priority": False,
            "checks": ['mentions', 'alerts', 'forum_patrol', 'vote_check'],
            "checks_skipped": [],
            "note": f"任務已{status}"
        })
    else:
        # IDLE
        result.update({
            "message": f"[{agent_name}] 💤 IDLE (無任務)",
            "skip_low_priority": False,
            "checks": ['mentions', 'alerts', 'forum_patrol', 'vote_check'],
            "checks_skipped": [],
            "note": "閒置狀態，執行完整檢查"
        })

    # 更新 heartbeat 記錄
    heartbeat_data = state_mgr._update_heartbeat(check_result=result)
    result["heartbeat_count"] = heartbeat_data.get("check_count", 0)

    return result


if __name__ == "__main__":
    # CLI 使用
    if len(sys.argv) > 1:
        agent = sys.argv[1]
        result = heartbeat_with_state(agent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(heartbeat_with_state(), ensure_ascii=False, indent=2))
