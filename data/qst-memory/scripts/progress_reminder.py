#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QST Memory v1.8.4 - Phase 2: 定期進度提醒

功能:
1. 檢測停滯（8 分鐘無更新）
2. 停滯時自動降級優先級
3. 15 分鐘：標記 STAGNANT
4. 30 分鐘：標記 BLOCKED
5. 60 分鐘：嘗試自動完成

作者: Zhuangzi
版本: v1.8.4 Phase 2
"""

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import sys

# 導入 existing 模塊
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from completion_detector import CompletionDetector


class ProgressReminder:
    """定期進度提醒（停滯檢測器）"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.completion_detector = CompletionDetector(state_file)
        self.state = self._load_state()
        self.config = self._load_config()

    def _load_state(self) -> Dict:
        """加載狀態文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_config(self) -> Dict:
        """加載配置"""
        # 默認配置（8 分鐘停滯）
        default_config = {
            'enabled': True,
            'reminder_interval_minutes': 5,
            'stagnation_threshold_minutes': 8,
            'stagnation_action': 'downgrade',
            'stagnation_actions': [
                {'stagnation_minutes': 8, 'action': 'lower_priority'},
                {'stagnation_minutes': 15, 'action': 'mark_stagnant'},
                {'stagnation_minutes': 30, 'action': 'mark_blocked'},
                {'stagnation_minutes': 60, 'action': 'auto_complete_if_possible'}
            ]
        }

        # 從 state 中讀取配置
        return self.state.get('progress_reminder', default_config)

    def _save_state(self) -> None:
        """保存狀態文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    # ========== 停滯檢測核心 ==========

    def check_stagnation(self) -> Optional[Dict]:
        """
        檢測停滯並執行對應操作

        Returns:
            停滯操作事件，如果無停滯則返回 None
        """

        # 檢查是否啟用
        if not self.config.get('enabled', True):
            return None

        # 檢查狀態是否為 DOING
        status = self.state.get('status', '')
        if status != 'doing':
            return None

        # 計算停滯時間
        stagnation_minutes = self._get_stagnation_minutes()

        if stagnation_minutes is None:
            return None

        # 獲取應該執行的操作
        action_config = self._get_stagnation_action(stagnation_minutes)

        if not action_config:
            return None

        # 執行操作
        action_event = self._execute_stagnation_action(
            action_config['action'],
            stagnation_minutes
        )

        return action_event

    def _get_stagnation_minutes(self) -> Optional[float]:
        """
        獲取停滯時間（分鐘）

        Returns:
            停滯分鐘數，如果無法計算則返回 None
        """

        updated_time_str = self.state.get('updated_time') or self.state.get('start_time')

        if not updated_time_str:
            return None

        try:
            updated_time = datetime.fromisoformat(updated_time_str)
            now = datetime.now(timezone.utc)

            time_delta = now - updated_time
            minutes = time_delta.total_seconds() / 60

            return max(0, minutes)
        except:
            return None

    def _get_stagnation_action(self, stagnation_minutes: float) -> Optional[Dict]:
        """
        根據停滯時間獲取對應的操作

        Args:
            stagnation_minutes: 停滯分鐘數

        Returns:
            操作配置，如果無操作則返回 None
        """

        stagnation_actions = self.config.get('stagnation_actions', [])

        # 找到最接近但不超過停滯時間的操作
        for action_config in reversed(stagnation_actions):
            action_minutes = action_config.get('stagnation_minutes', 0)
            if stagnation_minutes >= action_minutes:
                return action_config

        return None

    def _execute_stagnation_action(self, action: str, stagnation_minutes: float) -> Dict:
        """
        執行停滯操作

        Args:
            action: 操作類型
            stagnation_minutes: 停滯分鐘數

        Returns:
            事件字典
        """

        event = {
            'type': 'STAGNATION_ACTION',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'stagnation_minutes': stagnation_minutes,
            'message': ''
        }

        if action == 'lower_priority':
            self._lower_priority()
            event['message'] = f'任務停滯 {stagnation_minutes:.1f} 分鐘，已降級優先級'
            event['priority_from'] = self.state.get('priority')
            event['priority_to'] = self.state.get('priority')

        elif action == 'mark_stagnant':
            self._mark_stagnant()
            event['message'] = f'任務停滯 {stagnation_minutes:.1f} 分鐘，已標記為 STAGNANT'
            event['previous_status'] = 'doing'
            event['new_status'] = 'stagnant'

        elif action == 'mark_blocked':
            self._mark_blocked()
            event['message'] = f'任務停滯 {stagnation_minutes:.1f} 分鐘，已標記為 BLOCKED'
            event['previous_status'] = self.state.get('status')
            event['new_status'] = 'blocked'

        elif action == 'auto_complete_if_possible':
            completed = self._auto_complete_if_possible()
            event['message'] = f'任務停滯 {stagnation_minutes:.1f} 分鐘，嘗試自動完成: {"成功" if completed else "失敗（不滿足條件）"}'
            event['auto_completed'] = completed

        # 保存事件
        self._add_event(event)

        return event

    # ========== 停滯操作 ==========

    def _lower_priority(self) -> None:
        """降級優先級"""
        priority_map = {
            'critical': 'high',
            'high': 'normal',
            'normal': 'low',
            'low': 'low'
        }

        current_priority = self.state.get('priority', 'normal')
        new_priority = priority_map.get(current_priority, 'low')

        self.state['priority'] = new_priority
        self._save_state()

    def _mark_stagnant(self) -> None:
        """標記為 STAGNANT"""
        self.state['status'] = 'stagnant'
        self._save_state()

    def _mark_blocked(self) -> None:
        """標記為 BLOCKED"""
        self.state['status'] = 'blocked'
        self._save_state()

    def _auto_complete_if_possible(self) -> bool:
        """
        嘗試自動完成如果滿足條件

        Returns:
            是否成功自動完成
        """

        can_complete = self.completion_detector.detect_completion()

        if can_complete:
            self.state['status'] = 'completed'
            self.state['end_time'] = datetime.now(timezone.utc).isoformat()
            self._save_state()
            return True

        return False

    # ========== 事件發布 ==========

    def _add_event(self, event: Dict) -> None:
        """添加事件到事件文件"""
        events_file = self.state_file.parent / 'qst_events.json'

        # 載入現有事件
        events = []
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)

        # 添加新事件
        events.append(event)

        # 保存事件
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

    # ========== 輔助方法 ==========

    def get_stagnation_status(self) -> Dict:
        """
        獲取停滯狀態

        Returns:
            停滯狀態字典
        """

        stagnation_minutes = self._get_stagnation_minutes()

        return {
            'enabled': self.config.get('enabled', True),
            'stagnation_threshold': self.config.get('stagnation_threshold_minutes', 8),
            'current_stagnation_minutes': stagnation_minutes,
            'is_stagnant': stagnation_minutes is not None and stagnation_minutes >= self.config.get('stagnation_threshold_minutes', 8),
            'next_action': self._get_stagnation_action(stagnation_minutes) if stagnation_minutes else None
        }


# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 測試代碼
    state_file = Path('/home/node/.openclaw/workspace/skills/qst-memory/data/qst_doing-state.json')
    reminder = ProgressReminder(state_file)

    print("🧪 定期進度提醒測試")
    print()

    # 顯示當前配置
    print("⚙️  配置:")
    print(f"   啟用: {reminder.config.get('enabled', True)}")
    print(f"   停滯閾值: {reminder.config.get('stagnation_threshold_minutes', 8)} 分鐘")
    print()

    # 獲取停滯狀態
    status = reminder.get_stagnation_status()
    print("📊 停滯狀態:")
    print(f"   當前停滯: {status['current_stagnation_minutes'] or 'N/A'} 分鐘")
    print(f"   是否停滯: {status['is_stagnant']}")
    if status['next_action']:
        print(f"   下一步操作: {status['next_action']['action']} (在 {status['next_action']['stagnation_minutes']} 分鐘)")
    print()

    # 檢測停滯
    event = reminder.check_stagnation()

    if event:
        print(f"📢 停滯操作:")
        print(f"   類型: {event['type']}")
        print(f"   操作: {event['action']}")
        print(f"   停滯時間: {event['stagnation_minutes']:.1f} 分鐘")
        print(f"   消息: {event['message']}")
    else:
        print("✅ 無需執行停滯操作")

    print()
    print("🐲 測試完成！")
