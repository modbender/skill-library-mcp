#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QST Memory v1.8.4 - Phase 3: 任務模板管理器

功能:
1. 載入模板
2. 列出所有模板
3. 應用模板到任務
4. 創建自定義模板

作者: Zhuangzi
版本: v1.8.4 Phase 3
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sys

# 導入 existing 模塊
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from subtask_manager import SubtaskManager


class TemplateManager:
    """任務模板管理器"""

    def __init__(self, template_file: Path, state_file: Path):
        self.template_file = template_file
        self.state_file = state_file
        self.templates = self._load_templates()
        self.subtask_manager = SubtaskManager(state_file)

    def _load_templates(self) -> Dict:
        """加載所有模板"""
        if self.template_file.exists():
            with open(self.template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_templates(self) -> None:
        """保存所有模板"""
        with open(self.template_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2, ensure_ascii=False)

    # ========== 模板 CRUD 操作 ==========

    def list_templates(self) -> List[Dict]:
        """
        列出所有模板

        Returns:
            模板列表
        """

        templates = []

        for name, template in self.templates.items():
            templates.append({
                'name': template.get('name', name),
                'description': template.get('description', ''),
                'subtasks_count': len(template.get('default_subtasks', [])),
                'required_subtasks_count': len([
                    st for st in template.get('default_subtasks', [])
                    if st.get('required', True)
                ])
            })

        return templates

    def load_template(self, template_name: str) -> Optional[Dict]:
        """
        載入指定模板

        Args:
            template_name: 模板名稱

        Returns:
            模板字典，如果不存在則返回 None
        """

        return self.templates.get(template_name)

    def apply_template(self, template_name: str) -> Dict:
        """
        應用模板到當前任務

        Args:
            template_name: 模板名稱

        Returns:
            應用結果
        """

        template = self.load_template(template_name)

        if not template:
            raise ValueError(f"模板不存在: {template_name}")

        # 載入當前狀態
        state = self._load_state()

        # 設置完成標準
        state['completion_criteria'] = template.get('completion_criteria', {})

        # 添加默認子任務
        default_subtasks = template.get('default_subtasks', [])

        added_subtasks = []
        for st_config in default_subtasks:
            subtask = self.subtask_manager.add_subtask(
                title=st_config.get('title', ''),
                description=st_config.get('description', ''),
                required=st_config.get('required', True),
                weight=st_config.get('weight', 1.0)
            )
            added_subtasks.append(subtask)

        # 保存狀態
        self._save_state(state)

        return {
            'template_name': template_name,
            'completion_criteria': state['completion_criteria'],
            'added_subtasks': len(added_subtasks),
            'subtasks': added_subtasks
        }

    def create_custom_template(self, name: str, description: str, subtasks: List[Dict]) -> Dict:
        """
        創建自定義模板

        Args:
            name: 模板名稱
            description: 模板描述
            subtasks: 子任務列表

        Returns:
            創建的模板
        """

        if name in self.templates:
            raise ValueError(f"模板已存在: {name}")

        template = {
            'name': name,
            'description': description,
            'completion_criteria': {
                'all_required_subtasks_complete': True,
                'min_progress_percent': 100
            },
            'default_subtasks': subtasks
        }

        self.templates[name] = template
        self._save_templates()

        return template

    def delete_template(self, template_name: str) -> bool:
        """
        刪除模板

        Args:
            template_name: 模板名稱

        Returns:
            是否刪除成功
        """

        if template_name not in self.templates:
            return False

        # 不允許刪除預定義模板
        predefined = ['Development', 'Research', 'Analytics', 'Support', 'Custom']
        if template_name in predefined:
            raise ValueError(f"無法刪除預定義模板: {template_name}")

        del self.templates[template_name]
        self._save_templates()

        return True

    # ========== 輔助方法 ==========

    def _load_state(self) -> Dict:
        """加載狀態文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_state(self, state: Dict) -> None:
        """保存狀態文件"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def get_template_names(self) -> List[str]:
        """
        獲取所有模板名稱

        Returns:
            模板名稱列表
        """

        return list(self.templates.keys())


# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 測試代碼
    template_file = Path('/home/node/.openclaw/workspace/skills/qst-memory/config/task_templates.json')
    state_file = Path('/home/node/.openclaw/workspace/skills/qst-memory/data/qst_doing-state.json')
    manager = TemplateManager(template_file, state_file)

    print("🧪 任務模板管理器測試")
    print()

    # 列出所有模板
    print("✅ 列出所有模板:")
    templates = manager.list_templates()
    for template in templates:
        print(f"   • {template['name']} - {template['description']}")
        print(f"     子任務: {template['subtasks_count']} (必選: {template['required_subtasks_count']})")
    print()

    # 載入範例模板
    print("✅ 載入 Development 模板:")
    template = manager.load_template('Development')
    if template:
        print(f"   名稱: {template['name']}")
        print(f"   描述: {template['description']}")
        print(f"   完成標準: {template.get('completion_criteria', {})}")
        print(f"   默認子任務數: {len(template.get('default_subtasks', []))}")
    print()

    # 獲取模板名稱
    print("✅ 所有模板名稱:")
    names = manager.get_template_names()
    for name in names:
        print(f"   • {name}")

    print()
    print("🐲 測試完成！")
