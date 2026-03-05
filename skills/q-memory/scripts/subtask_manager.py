#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QST Memory v1.8.4 - Phase 1: 子任務管理器

功能:
1. 添加子任務
2. 更新子任務狀態
3. 刪除子任務
4. 列出所有子任務
5. 自動計算總進度

作者: Zhuangzi
版本: v1.8.4 Phase 1
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional


class SubtaskManager:
    """子任務管理器"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """加載狀態文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_state(self) -> None:
        """保存狀態文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _ensure_subtasks_list(self):
        """確保任務有子任務列表"""
        if 'subtasks' not in self.state:
            self.state['subtasks'] = []
        if 'progress_auto_update' not in self.state:
            self.state['progress_auto_update'] = True

    # ========== 子任務 CRUD 操作 ==========

    def add_subtask(
        self,
        title: str,
        description: str = "",
        required: bool = True,
        weight: float = 1.0,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        添加子任務

        Args:
            title: 子任務標題
            description: 子任務描述
            required: 是否必選（默認 True）
            weight: 權重（默認 1.0）
            parent_id: 父任務 ID（默認 None，支持 3 層級）
            metadata: 額外元數據

        Returns:
            新創建的子任務
        """

        self._ensure_subtasks_list()

        # 檢查層級（最多 3 層）
        if parent_id:
            depth = self._get_depth(parent_id)
            if depth >= 2:  # 0, 1, 2 = 3 層
                raise ValueError("已達最大層級（3 層）")

        # 創建子任務
        subtask = {
            "id": f"st-{uuid.uuid4().hex[:8]}",
            "title": title,
            "description": description,
            "status": "pending",
            "required": required,
            "weight": weight,
            "parent_id": parent_id,
            "start_time": None,
            "completed_time": None,
            "metadata": metadata or {}
        }

        self.state['subtasks'].append(subtask)
        self._save_state()
        self._recalculate_progress()

        return subtask

    def update_subtask(
        self,
        subtask_id: str,
        status: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        required: Optional[bool] = None,
        weight: Optional[float] = None
    ) -> Dict:
        """
        更新子任務

        Args:
            subtask_id: 子任務 ID
            status: 新狀態
            title: 新標題
            description: 新描述
            required: 是否必選
            weight: 新權重

        Returns:
            更新後的子任務
        """

        subtask = self._get_subtask(subtask_id)
        if not subtask:
            raise ValueError(f"子任務不存在: {subtask_id}")

        # 狀態變更時更新時間戳
        if status and status != subtask['status']:
            if status == 'in_progress' and subtask['status'] == 'pending':
                subtask['start_time'] = datetime.now(timezone.utc).isoformat()
            elif status == 'completed':
                subtask['completed_time'] = datetime.now(timezone.utc).isoformat()

        # 更新字段
        if status:
            subtask['status'] = status
        if title:
            subtask['title'] = title
        if description is not None:
            subtask['description'] = description
        if required is not None:
            subtask['required'] = required
        if weight is not None:
            subtask['weight'] = weight

        self._save_state()
        self._recalculate_progress()

        return subtask

    def delete_subtask(self, subtask_id: str, cascade: bool = True) -> bool:
        """
        刪除子任務

        Args:
            subtask_id: 子任務 ID
            cascade: 是否級聯刪除子子任務（默認 True）

        Returns:
            是否刪除成功
        """

        subtask = self._get_subtask(subtask_id)
        if not subtask:
            return False

        # 級聯刪除子子任務
        if cascade:
            child_ids = self._get_children_ids(subtask_id)
            for child_id in child_ids:
                self.delete_subtask(child_id)

        # 刪除子任務
        self.state['subtasks'] = [
            st for st in self.state['subtasks']
            if st['id'] != subtask_id
        ]

        self._save_state()
        self._recalculate_progress()

        return True

    def list_subtasks(self, parent_id: Optional[str] = None) -> List[Dict]:
        """
        列出所有子任務或指定父任務的子任務

        Args:
            parent_id: 父任務 ID（None = 列出所有）

        Returns:
            子任務列表
        """

        if parent_id:
            return [
                st for st in self.state.get('subtasks', [])
                if st.get('parent_id') == parent_id
            ]
        else:
            return self.state.get('subtasks', [])

    def get_subtask(self, subtask_id: str) -> Optional[Dict]:
        """
        獲取指定子任務

        Args:
            subtask_id: 子任務 ID

        Returns:
            子任務或 None
        """

        return self._get_subtask(subtask_id)

    # ========== 進度計算 ==========

    def calculate_progress(self) -> int:
        """
        自動計算總進度

        Returns:
            進度百分比（0-100）
        """

        subtasks = self.state.get('subtasks', [])

        if not subtasks:
            return self.state.get('progress', 0)

        # 只計算必選子任務（無 parent_id 的頂層）
        required_subtasks = [
            st for st in subtasks
            if st.get('required', True) and st.get('parent_id') is None
        ]

        if not required_subtasks:
            return 100

        # 計算完成的必選子任務
        completed_required = len([
            st for st in required_subtasks
            if st['status'] == 'completed'
        ])

        # 計算進度百分數
        progress = int((completed_required / len(required_subtasks)) * 100)

        return progress

    def _recalculate_progress(self) -> None:
        """重新計算並更新進度"""

        if self.state.get('progress_auto_update', True):
            progress = self.calculate_progress()
            self.state['progress'] = progress
            self.state['updated_time'] = datetime.now(timezone.utc).isoformat()

    # ========== 輔助方法 ==========

    def _get_subtask(self, subtask_id: str) -> Optional[Dict]:
        """獲取指定子任務"""
        for st in self.state.get('subtasks', []):
            if st['id'] == subtask_id:
                return st
        return None

    def _get_depth(self, subtask_id: str, max_depth: int = 10) -> int:
        """獲取子任務的深度"""

        depth = 0
        current_id = subtask_id

        for _ in range(max_depth):
            subtask = self._get_subtask(current_id)
            if not subtask:
                break
            parent_id = subtask.get('parent_id')
            if not parent_id:
                break
            current_id = parent_id
            depth += 1

        return depth

    def _get_children_ids(self, parent_id: str) -> List[str]:
        """獲取指定父任務下的所有子任務 ID（遞歸）"""

        direct_children = [
            st['id'] for st in self.state.get('subtasks', [])
            if st.get('parent_id') == parent_id
        ]

        all_children = direct_children.copy()

        for child_id in direct_children:
            all_children.extend(self._get_children_ids(child_id))

        return all_children


# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 測試代碼
    state_file = Path('/home/node/.openclaw/workspace/skills/qst-memory/data/qst_doing-state.json')
    manager = SubtaskManager(state_file)

    print("🧪 子任務管理器測試")
    print()

    # 添加子任務
    print("✅ 添加子任務:")
    st1 = manager.add_subtask(
        title="開發子任務管理功能",
        description="實現子任務的CRUD操作",
        required=True,
        weight=1.0
    )
    print(f"   子任務 1: {st1['title']} (ID: {st1['id']})")

    st2 = manager.add_subtask(
        title="實現自動進度計算",
        description="根據子任務狀態自動計算總進度",
        required=True,
        weight=1.0
    )
    print(f"   子任務 2: {st2['title']} (ID: {st2['id']})")

    print()

    # 列出子任務
    print("✅ 列出子任務:")
    subtasks = manager.list_subtasks()
    for st in subtasks:
        print(f"   [{st['status']}] {st['title']} (ID: {st['id']})")

    print()

    # 更新子任務狀態
    print("✅ 更新子任務狀態:")
    manager.update_subtask(st1['id'], status='completed')
    print(f"   子任務 1 已完成")

    print()

    # 重新列出並查看進度
    print("✅ 重新列出子任務:")
    subtasks = manager.list_subtasks()
    for st in subtasks:
        print(f"   [{st['status']}] {st['title']}")

    print()

    # 查看進度
    progress = manager.calculate_progress()
    print(f"✅ 當前進度: {progress}%")

    print()
    print("🐲 測試完成！")
