#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QST Memory v1.8.4 - Phase 4: 整合整合測試

測試所有 Phase 1-3 的功能

Phase 1: 子任務列表管理 + 自動進度計算
Phase 2: 自動完成檢測 + 定期進度提醒
Phase 3: 任務完成標準模板

作者: Zhuangzi
版本: v1.8.4 Phase 4
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# 路徑配置
QST_MEMORY_DIR = Path("/home/node/.openclaw/workspace/skills/qst-memory")
sys.path.insert(0, str(QST_MEMORY_DIR / "scripts"))

# 導入模塊
from agent_state import AgentState
from subtask_manager import SubtaskManager
from completion_detector import CompletionDetector
from progress_reminder import ProgressReminder
from template_manager import TemplateManager


class IntegrationTest:
    """整合測試類"""

    def __init__(self):
        self.state_file = QST_MEMORY_DIR / "data" / "qst_doing-state.json"
        self.template_file = QST_MEMORY_DIR / "config" / "task_templates.json"

        self.agent_state = AgentState("qst")
        self.subtask_manager = SubtaskManager(self.state_file)
        self.completion_detector = CompletionDetector(self.state_file)
        self.progress_reminder = ProgressReminder(self.state_file)
        self.template_manager = TemplateManager(self.template_file, self.state_file)

        self.test_results = []

    def run_all_tests(self):
        """運行所有測試"""

        print("🧪 QST Memory v1.8.4 整合測試")
        print("=" * 60)
        print()

        # Phase 1 測試
        self.test_phase1_subtasks()
        self.test_phase1_progress_calc()

        # Phase 2 測試
        self.test_phase2_auto_completion()
        self.test_phase2_stagnation()

        # Phase 3 測試
        self.test_phase3_templates()

        # 總結
        self.print_summary()

    def test_phase1_subtasks(self):
        """Phase 1 測試：子任務列表管理"""

        print("✅ Phase 1 測試：子任務列表管理")
        print("-" * 60)

        try:
            # 清除現有子任務
            if 'subtasks' in self.subtask_manager.state:
                subtask_ids = [st['id'] for st in self.subtask_manager.state['subtasks']]
                for st_id in subtask_ids:
                    self.subtask_manager.delete_subtask(st_id)

            # 添加子任務
            st1 = self.subtask_manager.add_subtask(
                title="測試子任務 1",
                description="這是測試子任務 1",
                required=True
            )
            self.test_results.append(("Phase 1.1", "添加子任務", True))

            st2 = self.subtask_manager.add_subtask(
                title="測試子任務 2",
                description="這是測試子任務 2",
                required=True
            )
            self.test_results.append(("Phase 1.2", "添加第二個子任務", True))

            # 列出子任務
            subtasks = self.subtask_manager.list_subtasks()
            self.test_results.append(("Phase 1.3", f"列出 {len(subtasks)} 個子任務", len(subtasks) == 2))

            # 更新狀態
            self.subtask_manager.update_subtask(st1['id'], status='completed')
            self.test_results.append(("Phase 1.4", "更新子任務狀態", True))

            print(f"   ✅ 添加 {len(subtasks)} 個子任務")
            print(f"   ✅ 列出所有子任務")
            print(f"   ✅ 更新子任務狀態")
            print()

        except Exception as e:
            self.test_results.append(("Phase 1", "子任務列表管理", False))
            print(f"   ❌ 測試失敗: {e}")
            print()

    def test_phase1_progress_calc(self):
        """Phase 1 測試：自動進度計算"""

        print("✅ Phase 1 測試：自動進度計算")
        print("-" * 60)

        try:
            # 計算進度
            progress = self.subtask_manager.calculate_progress()

            self.test_results.append(("Phase 1.5", f"進度計算: {progress}%", 0 < progress < 100))

            print(f"   ✅ 自動計算進度: {progress}%")
            print()

        except Exception as e:
            self.test_results.append(("Phase 1", "自動進度計算", False))
            print(f"   ❌ 測試失敗: {e}")
            print()

    def test_phase2_auto_completion(self):
        """Phase 2 測試：自動完成檢測"""

        print("✅ Phase 2 測試：自動完成檢測")
        print("-" * 60)

        try:
            # 完成所有子任務
            subtasks = self.subtask_manager.list_subtasks()
            for st in subtasks:
                self.subtask_manager.update_subtask(st['id'], status='completed')

            # 檢測自動完成
            can_complete = self.completion_detector.detect_completion()

            self.test_results.append(("Phase 2.1", "自動完成檢測", can_complete))

            print(f"   ✅ 自動完成檢測: {can_complete}")
            print()

        except Exception as e:
            self.test_results.append(("Phase 2", "自動完成檢測", False))
            print(f"   ❌ 測試失敗: {e}")
            print()

    def test_phase2_stagnation(self):
        """Phase 2 測試：停滯檢測"""

        print("✅ Phase 2 測試：停滯檢測")
        print("-" * 60)

        try:
            # 檢測停滯
            stagnation_status = self.progress_reminder.get_stagnation_status()

            self.test_results.append(("Phase 2.2", "停滯檢測", stagnation_status is not None))

            print(f"   ✅ 停滯檢測")
            print(f"      啟用: {stagnation_status['enabled']}")
            print(f"      閾值: {stagnation_status['stagnation_threshold']} 分鐘")
            print(f"      當前停滯: {stagnation_status.get('current_stagnation_minutes') or 'N/A'} 分鐘")
            print()

        except Exception as e:
            self.test_results.append(("Phase 2", "停滯檢測", False))
            print(f"   ❌ 測試失敗: {e}")
            print()

    def test_phase3_templates(self):
        """Phase 3 測試：任務模板"""

        print("✅ Phase 3 測試：任務模板")
        print("-" * 60)

        try:
            # 列出所有模板
            templates = self.template_manager.list_templates()

            self.test_results.append(("Phase 3.1", f"列出 {len(templates)} 個模板", len(templates) > 0))

            print(f"   ✅ 可用模板數: {len(templates)}")
            for template in templates:
                print(f"      • {template['name']} - {template['description']}")

            # 載入 Development 模板
            template = self.template_manager.load_template('Development')

            self.test_results.append(("Phase 3.2", "載入 Development 模板", template is not None))

            print(f"   ✅ 載入 Development 模板")
            print()

        except Exception as e:
            self.test_results.append(("Phase 3", "任務模板", False))
            print(f"   ❌ 測試失敗: {e}")
            print()

    def print_summary(self):
        """打印測試總結"""

        print("=" * 60)
        print("📊 測試總結")
        print("=" * 60)

        total = len(self.test_results)
        passed = sum(1 for _, _, result in self.test_results if result)
        failed = total - passed

        print()
        print(f"總測試數: {total}")
        print(f"通過: {passed} ✅")
        print(f"失敗: {failed} ❌")
        print()

        if failed > 0:
            print("❌ 失敗的測試:")
            for test_name, description, result in self.test_results:
                if not result:
                    print(f"   • {test_name}: {description}")
            print()

        print("🐲 測試完成！")
        print()


# ========== 主程序入口 ==========

if __name__ == '__main__':
    test = IntegrationTest()
    test.run_all_tests()
