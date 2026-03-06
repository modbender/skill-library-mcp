#!/usr/bin/env python3
"""Agent State Manager - "I'm Doing" System v1.8.2

v1.8.1 新增：防死循環保護機制
- 任務超時檢測
- 停滯自動處理
- Heartbeat 頻率限制
- 自動降級策略

v1.8.2 新增：用戶優先回應機制
- 用戶優先視窗
- Heartbeat 跳過計數
- 用戶互動追踪
"""
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class AgentStatus(Enum):
    IDLE = "idle"
    DOING = "doing"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # v1.8: 遇到障礙，需要外部協助

class TaskPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
class AgentStatus(Enum):
    IDLE = "idle"
    DOING = "doing"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # v1.8: 遇到障礙，需要外部協助

class TaskPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class AgentState:
    def __init__(self, agent_name: str):
        self.agent = agent_name
        self.state_file = DATA_DIR / f"{agent_name}_doing-state.json"
        self.events_file = DATA_DIR / f"{agent_name}_events.json"
        self.heartbeat_file = DATA_DIR / f"{agent_name}_heartbeat.json"  # v1.8.1
        self.config = self._load_agent_config()

        # v1.8.1: 防死循環保護配置
        self.loop_protection = self.config.get("loop_protection", {
            "critical_timeout_minutes": 30,      # critical 任務超時
            "high_timeout_minutes": 45,          # high 任務超時
            "normal_timeout_minutes": 60,        # normal 任務超時
            "low_timeout_minutes": 120,          # low 任務超時
            "heartbeat_min_interval_seconds": 30,  # 最小 heartbeat 間隔
            "stagnation_threshold_minutes": 15,   # 停滯檢測閾值（進度無變化）
            "auto_downgrade_on_stagnation": True,  # 停滯時自動降級
            "max_stagnant_checks": 10             # 最大停滯檢查次數
        })

    def _load_agent_config(self) -> Dict[str, Any]:
        """載入 Agent 專屬配置"""
        config_file = SKILL_DIR / "config" / f"{self.agent}_config.json"
        default_config = {
            "default_priority": "normal",
            "default_tags": ["general"],
            "custom_task_types": ["Development", "Analysis", "Debug", "Research"],
            "heartbeat_strategy": {
                "critical": ["mentions", "alerts"],
                "high": ["mentions", "alerts"],
                "normal": ["mentions", "alerts", "forum_patrol"],
                "low": ["mentions", "alerts", "forum_patrol", "vote_check"]
            },
            # v1.8.1: 防死循環保護配置
            "loop_protection": {
                "critical_timeout_minutes": 30,
                "high_timeout_minutes": 45,
                "normal_timeout_minutes": 60,
                "low_timeout_minutes": 120,
                "heartbeat_min_interval_seconds": 30,
                "stagnation_threshold_minutes": 15,
                "auto_downgrade_on_stagnation": True,
                "max_stagnant_checks": 10
            }
        }
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return {**default_config, **json.load(f)}
        return default_config

    def _load_state(self) -> Dict[str, Any]:
        """載入任務狀態"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "id": str(uuid.uuid4()),
            "agent": self.agent,
            "status": AgentStatus.IDLE.value,
            "task": None,
            "type": None,
            "priority": self.config.get("default_priority", "normal"),
            "tags": self.config.get("default_tags", ["general"]),
            "progress": 0,
            "start_time": None,
            "updated_time": datetime.now().isoformat(),
            "eta": None,
            "context": {},
            # v1.8.1: 防死循環追蹤
            "progress_history": [],
            "heartbeat_count": 0,
            "last_heartbeat_time": None
        }

    def _save_state(self, state: Dict[str, Any]):
        """保存任務狀態"""
        state["updated_time"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _log_event(self, event_type: str, description: str, details: Dict = None):
        """記錄事件"""
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent": self.agent,
            "description": description,
            "details": details or {}
        }
        events = []
        if self.events_file.exists():
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        events.append(event)
        events = events[-1000:]
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    def _update_heartbeat(self, check_result: Dict[str, Any] = None):
        """v1.8.1: 更新 heartbeat 記錄"""
        heartbeat_data = {
            "last_check_time": datetime.now().isoformat(),
            "check_count": 1,
            "last_check_result": check_result
        }

        if self.heartbeat_file.exists():
            with open(self.heartbeat_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
            heartbeat_data["check_count"] = existing.get("check_count", 0) + 1
            heartbeat_data["check_history"] = existing.get("check_history", [])[-10:]

        # 保持最近 10 次檢查記錄
        if "check_history" not in heartbeat_data:
            heartbeat_data["check_history"] = []

        heartbeat_data["check_history"].append({
            "timestamp": datetime.now().isoformat(),
            "count": heartbeat_data["check_count"],
            "result": check_result
        })
        heartbeat_data["check_history"] = heartbeat_data["check_history"][-10:]

        with open(self.heartbeat_file, 'w', encoding='utf-8') as f:
            json.dump(heartbeat_data, f, ensure_ascii=False, indent=2)

        return heartbeat_data

    # ========== v1.8.1: 防死循環保護方法 ==========

    def is_stagnant(self, state: Dict[str, Any] = None) -> Tuple[bool, str]:
        """檢查任務是否停滯

        Returns:
            Tuple[is_stagnant, reason]
        """
        if state is None:
            state = self._load_state()

        if state["status"] != AgentStatus.DOING.value:
            return False, "任務非執行中"

        # 檢查進度歷史
        progress_history = state.get("progress_history", [])
        if len(progress_history) < 2:
            return False, "進度記錄不足"

        # 檢查最近的進度是否相同（停滯）
        recent_progress = progress_history[-1]["progress"]
        stagnation_count = 0

        for record in reversed(progress_history):
            if record["progress"] == recent_progress:
                stagnation_count += 1
            else:
                break

        if stagnation_count >= 3:
            # 計算停滯時間
            first_stagnant_time = datetime.fromisoformat(progress_history[-stagnation_count]["timestamp"])
            stagnation_minutes = (datetime.now() - first_stagnant_time).total_seconds() / 60
            threshold = self.loop_protection["stagnation_threshold_minutes"]

            if stagnation_minutes >= threshold:
                return True, f"進度停滯 {stagnation_minutes:.0f} 分分鐘（閾值：{threshold} 分鐘）"

        return False, "進度有更新"

    def is_timeout(self, state: Dict[str, Any] = None) -> Tuple[bool, str, int]:
        """檢查任務是否超時

        Returns:
            Tuple[is_timeout, reason, elapsed_minutes]
        """
        if state is None:
            state = self._load_state()

        if state["status"] != AgentStatus.DOING.value:
            return False, "任務非執行中", 0

        start_time = state.get("start_time")
        if not start_time:
            return False, "無開始時間", 0

        elapsed = datetime.now() - datetime.fromisoformat(start_time)
        elapsed_minutes = elapsed.total_seconds() / 60

        priority = state.get("priority", "normal")
        timeout_key = f"{priority}_timeout_minutes"
        timeout = self.loop_protection.get(timeout_key, 60)

        if elapsed_minutes >= timeout:
            return True, f"執行時間 {elapsed_minutes:.0f} 分鐘超限（閾值：{timeout} 分鐘）", elapsed_minutes

        return False, "未超時", elapsed_minutes

    def should_throttle_heartbeat(self) -> Tuple[bool, str, int]:
        """檢查是否需要限制 heartbeat 頻率

        Returns:
            Tuple[should_throttle, reason, seconds_until_next]
        """
        if not self.heartbeat_file.exists():
            return False, "首次檢查", 0

        with open(self.heartbeat_file, 'r', encoding='utf-8') as f:
            heartbeat_data = json.load(f)

        last_check_time = datetime.fromisoformat(heartbeat_data["last_check_time"])
        min_interval = self.loop_protection["heartbeat_min_interval_seconds"]
        elapsed_seconds = (datetime.now() - last_check_time).total_seconds()

        if elapsed_seconds < min_interval:
            remaining = min_interval - elapsed_seconds
            return True, f"Too frequent ({elapsed_seconds:.0f}s < {min_interval}s)", int(remaining)

        return False, "頻率正常", 0


    def should_skip_for_user_priority(self) -> Tuple[bool, str, int]:
        """v1.8.2: 檢查是否應該因用戶優先而跳過 Heartbeat

        用戶優先機制：
        - 當有最近用戶互動時，優先保護用戶對話
        - 在優先視窗內跳過 Heartbeat

        Returns:
            Tuple[should_skip, reason, minutes_remaining]
        """
        config = self.config.get("user_priority_override", {})

        if not config.get("enabled", False):
            return False, "用戶優先模式未啟用", 0

        last_interaction = config.get("last_user_interaction")
        if not last_interaction:
            return False, "未記錄用戶互動", 0

        try:
            last_dt = datetime.fromisoformat(last_interaction)
            elapsed = datetime.now() - last_dt
            window_seconds = config.get("priority_window_minutes", 30) * 60
            elapsed_seconds = elapsed.total_seconds()
            remaining_seconds = window_seconds - elapsed_seconds

            if remaining_seconds > 0:
                skipped_count = config.get("skipped_count", 0)
                max_skips = config.get("max_skipped_heartbeats", 3)

                if skipped_count >= max_skips:
                    return False, f"已達最大跳過次數 ({max_skips})", 0

                minutes_remaining = int(remaining_seconds / 60)
                return True, f"用戶優先視窗（剩餘 {minutes_remaining} 分鐘）", minutes_remaining

            return False, "優先視窗已過期", 0

        except Exception as e:
            return False, f"用戶優先檢查錯誤: {str(e)}", 0

    def increment_skip_count(self):
        """v1.8.2: 增加跳過計數"""
        config_file = SKILL_DIR / "config" / f"{self.agent}_config.json"

        if not config_file.exists():
            return

        with open(config_file, "r", encoding="utf-8") as f:
            agent_config = json.load(f)

        if "user_priority_override" in agent_config:
            agent_config["user_priority_override"]["skipped_count"] = agent_config["user_priority_override"].get("skipped_count", 0) + 1

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(agent_config, f, indent=2, ensure_ascii=False)

            self.config = self._load_agent_config()

    def reset_user_priority(self):
        """v1.8.2: 重置用戶優先計數"""
        config_file = SKILL_DIR / "config" / f"{self.agent}_config.json"

        if not config_file.exists():
            return

        with open(config_file, "r", encoding="utf-8") as f:
            agent_config = json.load(f)

        if "user_priority_override" in agent_config:
            agent_config["user_priority_override"]["skipped_count"] = 0

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(agent_config, f, indent=2, ensure_ascii=False)

            self.config = self._load_agent_config()

    def update_user_interaction(self):
        """v1.8.2: 記錄用戶互動時間"""
        config_file = SKILL_DIR / "config" / f"{self.agent}_config.json"

        if not config_file.exists():
            return

        with open(config_file, "r", encoding="utf-8") as f:
            agent_config = json.load(f)

        if "user_priority_override" not in agent_config:
            agent_config["user_priority_override"] = {}

        agent_config["user_priority_override"]["last_user_interaction"] = datetime.now().isoformat()
        agent_config["user_priority_override"]["skipped_count"] = 0

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(agent_config, f, indent=2, ensure_ascii=False)

        self.config = self._load_agent_config()

    def auto_handle_stagnation(self) -> Dict[str, Any]:
        """v1.8.1: 自動處理停滯任務

        Returns:
            處理結果和動作
        """
        state = self._load_state()
        if state["status"] != AgentStatus.DOING.value:
            return {"action": "none", "reason": "任務非執行中"}

        is_stagnant, stagnant_reason = self.is_stagnant(state)
        is_timeout, timeout_reason, timeout_minutes = self.is_timeout(state)

        action = "none"
        result = {
            "stagnant": is_stagnant,
            "stagnant_reason": stagnant_reason if is_stagnant else None,
            "timeout": is_timeout,
            "timeout_reason": timeout_reason if is_timeout else None,
            "timeout_minutes": timeout_minutes,
            "action": action,
            "state_changes": {}
        }

        if is_timeout:
            # 超時處理策略
            priority = state["priority"]

            if priority == "critical" and self.loop_protection["auto_downgrade_on_stagnation"]:
                # Critical 任務超時 → 降級為 HIGH
                result["action"] = "downgrade"
                result["state_changes"]["priority"] = "high"
                result["state_changes"]["stagnation_warning"] = timeout_reason

                state["priority"] = "high"
                self._save_state(state)
                self._log_event("STAGNATION_AUTO_DOWNGRADE",
                    f"Critical 任務超時自動降級: {timeout_reason}",
                    result)

            elif priority in ["high", "normal"] and timeout_minutes > self.loop_protection[f"{priority}_timeout_minutes"] * 2:
                # High/Normal 任務超時 2 倍 → 標記為 BLOCKED
                result["action"] = "block"
                result["state_changes"]["status"] = "blocked"
                result["state_changes"]["blocked_reason"] = f"任務停滯過久: {timeout_reason}"
                result["state_changes"]["blocked_needs"] = "人工干預"

                state["status"] = "blocked"
                state["context"]["blocked_reason"] = f"任務停滯過久: {timeout_reason}"
                state["context"]["blocked_needs"] = "人工干預"
                self._save_state(state)
                self._log_event("STAGNATION_AUTO_BLOCK",
                    f"任務自動標記受阻: {timeout_reason}",
                    result)

        elif is_stagnant and self.loop_protection["auto_downgrade_on_stagnation"]:
            # 停滯（未超時）→ 自動降級優先級
            if state["priority"] == "critical":
                state["priority"] = "high"
                result["action"] = "downgrade"
                result["state_changes"]["priority"] = "high"
                result["state_changes"]["stagnation_warning"] = stagnant_reason

                self._save_state(state)
                self._log_event("STAGNATION_DOWNGRADE",
                    f"Critical 任務停滯自動降級: {stagnant_reason}",
                    result)
            elif state["priority"] == "high":
                state["priority"] = "normal"
                result["action"] = "downgrade"
                result["state_changes"]["priority"] = "normal"
                result["state_changes"]["stagnation_warning"] = stagnant_reason

                self._save_state(state)
                self._log_event("STAGNATION_DOWNGRADE",
                    f"High 任務停滯自動降級: {stagnant_reason}",
                    result)

        return result

    # ========== 原有方法 ==========

    def start(self, task: str, task_type: str = "Development",
              priority: str = None, tags: List[str] = None,
              context: Dict = None, eta: str = None,
              template: str = None) -> Dict[str, Any]:
        """開始新任務 (v1.8.4: 支持 template 參數)"""
        state = self._load_state()

        # v1.8.1: 檢查死循環保護
        if state["status"] == AgentStatus.DOING.value and state["task"]:
            self._log_event("TASK_INTERRUPTED",
                f"中斷: {state['task']}", {"old_task": state["task"], "new_task": task})

        if not priority:
            priority = self.config.get("default_priority", "normal")
        if not tags:
            tags = self.config.get("default_tags", ["general"])

        if priority not in [p.value for p in TaskPriority]:
            priority = "normal"

        valid_types = self.config.get("custom_task_types", ["Development"])
        if task_type not in valid_types:
            task_type = "Custom"

        # v1.8.4: 應用模板
        if template:
            try:
                from template_manager import TemplateManager
                template_file = DATA_DIR / ".." / "config" / "task_templates.json"
                template_mgr = TemplateManager(template_file, self.state_file)
                template_result = template_mgr.apply_template(template)
                self._log_event("TEMPLATE_APPLIED",
                    f"應用模板: {template}", template_result)
            except Exception as e:
                self._log_event("Template_ERROR",
                    f"模板應用失敗: {e}", {"template": template})

        # v1.8.1: 記錄初始進度
        progress_record = {
            "progress": 0,
            "timestamp": datetime.now().isoformat(),
            "note": "任務開始"
        }

        state.update({
            "id": str(uuid.uuid4()),
            "status": AgentStatus.DOING.value,
            "task": task,
            "type": task_type,
            "priority": priority,
            "tags": tags,
            "progress": 0,
            "start_time": datetime.now().isoformat(),
            "eta": eta,
            "context": context or {},
            # v1.8.1: 重置追蹤數據
            "progress_history": [progress_record],
            "heartbeat_count": 0,
            "last_heartbeat_time": None
        })

        self._save_state(state)
        self._log_event("TASK_START", f"開始 [{priority}]: {task}", state)
        return state

    def update(self, progress: int = None, context: Dict = None) -> Dict[str, Any]:
        """更新任務進度"""
        state = self._load_state()
        if state["status"] not in [AgentStatus.DOING.value, AgentStatus.BLOCKED.value]:
            raise ValueError(f"無法更新：當前 {state['status']}")

        if progress is not None:
            old_progress = state["progress"]
            state["progress"] = min(100, max(0, progress))

            # v1.8.1: 記錄進度歷史
            progress_record = {
                "progress": state["progress"],
                "timestamp": datetime.now().isoformat(),
                "delta": state["progress"] - old_progress,
                "note": "進度更新"
            }

            if "progress_history" not in state:
                state["progress_history"] = []
            state["progress_history"].append(progress_record)
            # 只保留最近 20 條記錄
            state["progress_history"] = state["progress_history"][-20:]

        if context:
            state["context"].update(context)

        self._save_state(state)
        self._log_event("PROGRESS_UPDATE",
            f"進度: {state['task']} ({state['progress']}%)", state)
        return state

    def pause(self, reason: str = None) -> Dict[str, Any]:
        """暫停任務"""
        state = self._load_state()
        if state["status"] not in [AgentStatus.DOING.value, AgentStatus.BLOCKED.value]:
            raise ValueError(f"無法暫停：當前 {state['status']}")
        state["status"] = AgentStatus.PAUSED.value
        state["context"]["pause_reason"] = reason
        self._save_state(state)
        self._log_event("TASK_PAUSED", f"暫停: {reason}", state)
        return state

    def resume(self) -> Dict[str, Any]:
        """恢復任務"""
        state = self._load_state()
        if state["status"] != AgentStatus.PAUSED.value:
            raise ValueError(f"無法恢復：當前 {state['status']}")
        state["status"] = AgentStatus.DOING.value
        state["context"].pop("pause_reason", None)
        self._save_state(state)
        self._log_event("TASK_RESUMED", f"恢復: {state['task']}", state)
        return state

    def wait(self, condition: str) -> Dict[str, Any]:
        """等待特定條件"""
        state = self._load_state()
        state["status"] = AgentStatus.WAITING.value
        state["context"]["waiting_for"] = condition
        self._save_state(state)
        self._log_event("TASK_WAITING", f"等待: {condition}", state)
        return state

    def block(self, reason: str, needs: str = None) -> Dict[str, Any]:
        """v1.8: 標記任務受阻"""
        state = self._load_state()
        state["status"] = AgentStatus.BLOCKED.value
        state["context"]["blocked_reason"] = reason
        state["context"]["blocked_needs"] = needs or "外部協助"
        self._save_state(state)
        self._log_event("TASK_BLOCKED", f"受阻: {reason}", state)
        return state

    def unblock(self) -> Dict[str, Any]:
        """v1.8: 解除受阻狀態"""
        state = self._load_state()
        if state["status"] != AgentStatus.BLOCKED.value:
            raise ValueError(f"無法解除阻礙：當前 {state['status']}")
        state["status"] = AgentStatus.DOING.value
        state["context"].pop("blocked_reason", None)
        state["context"].pop("blocked_needs", None)
        self._save_state(state)
        self._log_event("TASK_UNBLOCKED", f"解除阻礙: {state['task']}", state)
        return state

    def complete(self, result: str = None) -> Dict[str, Any]:
        """完成任務"""
        state = self._load_state()
        state["status"] = AgentStatus.COMPLETED.value
        state["progress"] = 100
        state["context"]["result"] = result
        state["completed_time"] = datetime.now().isoformat()
        self._save_state(state)
        self._log_event("TASK_COMPLETED", f"完成: {result}", state)
        return state

    def fail(self, reason: str = None) -> Dict[str, Any]:
        """任務失敗"""
        state = self._load_state()
        state["status"] = AgentStatus.FAILED.value
        state["context"]["failure_reason"] = reason
        state["failed_time"] = datetime.now().isoformat()
        self._save_state(state)
        self._log_event("TASK_FAILED", f"失敗: {reason}", state)
        return state

    def get_status(self) -> Dict[str, Any]:
        """獲取當前狀態"""
        return self._load_state()

    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取事件歷史"""
        if not self.events_file.exists():
            return []
        with open(self.events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        return events[-limit:]

    def is_doing(self) -> bool:
        """是否正在執行任務"""
        return self._load_state()["status"] == AgentStatus.DOING.value

    def can_interrupt(self) -> bool:
        """檢查任務是否可以被打斷"""
        state = self._load_state()
        if state["status"] not in [AgentStatus.DOING.value, AgentStatus.BLOCKED.value]:
            return True
        priority = state.get("priority", "normal")
        return priority not in ["critical"]

    def get_heartbeat_checks(self) -> List[str]:
        """v1.8: 根據優先級返回心跳檢查項目"""
        state = self._load_state()
        priority = state.get("priority", "normal")
        strategy = self.config.get("heartbeat_strategy", {})
        return strategy.get(f"{priority}", ["mentions", "alerts"])

    def set_priority(self, priority: str) -> Dict[str, Any]:
        """v1.8: 設置優先級"""
        state = self._load_state()
        if priority not in [p.value for p in TaskPriority]:
            raise ValueError(f"無效優先級: {priority}")

        old_priority = state["priority"]
        state["priority"] = priority
        self._save_state(state)
        self._log_event("PRIORITY_CHANGED",
            f"優先級調整: {old_priority} → {priority}", state)
        return state

    def add_tags(self, tags: List[str]) -> Dict[str, Any]:
        """v1.8: 添加標籤"""
        state = self._load_state()
        current_tags = state.get("tags", [])
        new_tags = list(set(current_tags + tags))
        state["tags"] = new_tags
        self._save_state(state)
        return state

    def remove_tags(self, tags: List[str]) -> Dict[str, Any]:
        """v1.8: 移除標籤"""
        state = self._load_state()
        current_tags = state.get("tags", [])
        new_tags = [t for t in current_tags if t not in tags]
        state["tags"] = new_tags
        self._save_state(state)
        return state
