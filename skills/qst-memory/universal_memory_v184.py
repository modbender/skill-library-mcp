#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Memory CLI - 擴展版本（v1.8.4 Phase 1）

新增功能:
- 子任務管理（添加、更新、刪除、列出）
- 自動進度計算

用法:
    python universal_memory.py --agent qst doing subtask add --title "子任務"
    python universal_memory.py --agent qst doing subtask list
    python universal_memory.py --agent qst doing subtask update --id st-xxx --status completed
"""

import json
import uuid
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

# 導入現有的 agent_state 和 subtask_manager
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from agent_state import AgentState
from subtask_manager import SubtaskManager


class UniversalMemoryCLI:
    """Universal Memory CLI - 擴展版本"""

    def __init__(self):
        self.skill_dir = Path(__file__).parent
        self.data_dir = self.skill_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.state_file = self.data_dir / "qst_doing-state.json"
        self.agent_state = AgentState("qst")
        self.subtask_manager = SubtaskManager(self.state_file)

    def run(self):
        """運行 CLI"""

        parser = argparse.ArgumentParser(
            description="Universal Memory CLI v1.8.4 Phase 1"
        )

        # 基本參數
        parser.add_argument(
            "--agent",
            default="qst",
            help="Agent 名稱"
        )

        # 子命令
        subparsers = parser.add_subparsers(dest="command", help="命令")

        # ============ doing 命令 ============

        # doing subtask add
        subtask_add = subparsers.add_parser("subtask", help="子任務管理")
        subtask_subparsers = subtask_add.add_subparsers(dest="subtask_action", help="子任務操作")

        # subtask add
        add_parser = subtask_subparsers.add_parser("add", help="添加子任務")
        add_parser.add_argument("--title", required=True, help="子任務標題")
        add_parser.add_argument("--description", default="", help="子任務描述")
        add_parser.add_argument("--required", action="store_true", default=True, help="是否必選")
        add_parser.add_argument("--no-required", action="store_true", help="是否可選")
        add_parser.add_argument("--weight", type=float, default=1.0, help="權重")
        add_parser.add_argument("--parent", default=None, help="父任務 ID")

        # subtask update
        update_parser = subtask_subparsers.add_parser("update", help="更新子任務")
        update_parser.add_argument("--id", required=True, help="子任務 ID")
        update_parser.add_argument("--status", choices=["pending", "in_progress", "completed"], help="新狀態")
        update_parser.add_argument("--title", help="新標題")
        update_parser.add_argument("--description", help="新描述")

        # subtask delete
        delete_parser = subtask_subparsers.add_parser("delete", help="刪除子任務")
        delete_parser.add_argument("--id", required=True, help="子任務 ID")

        # subtask list
        list_parser = subtask_subparsers.add_parser("list", help="列出所有子任務")
        list_parser.add_argument("--parent", default=None, help="父任務 ID")

        # subtask show
        show_parser = subtask_subparsers.add_parser("show", help="顯示子任務詳情")
        show_parser.add_argument("--id", required=True, help="子任務 ID")

        # 解析參數
        args = parser.parse_args()

        # 執行命令
        if args.command == "subtask":
            self.handle_subtask(args, parser)
        else:
            parser.print_help()

    def handle_subtask(self, args, parser):
        """處理子任務命令"""

        action = args.subtask_action

        if not action:
            subtask_parser = parser._subparsers._actions[3]
            subtask_parser.print_help()
            return

        if action == "add":
            self.subtask_add(args)
        elif action == "update":
            self.subtask_update(args)
        elif action == "delete":
            self.subtask_delete(args)
        elif action == "list":
            self.subtask_list(args)
        elif action == "show":
            self.subtask_show(args)

    # ========== 子任務操作 ==========

    def subtask_add(self, args):
        """添加子任務"""

        required = not args.no_required if hasattr(args, 'no_required') else True

        # 處理 --no-required
        if hasattr(args, 'no_required') and args.no_required:
            required = False

        subtask = self.subtask_manager.add_subtask(
            title=args.title,
            description=args.description,
            required=required,
            weight=args.weight,
            parent_id=args.parent
        )

        print(f"✅ 子任務已添加:")
        print(f"   ID: {subtask['id']}")
        print(f"   標題: {subtask['title']}")
        print(f"   狀態: {subtask['status']}")
        if subtask.get('parent_id'):
            print(f"   父任務: {subtask['parent_id']}")

    def subtask_update(self, args):
        """更新子任務"""

        subtask = self.subtask_manager.update_subtask(
            subtask_id=args.id,
            status=args.status,
            title=args.title,
            description=args.description
        )

        print(f"✅ 子任務已更新:")
        print(f"   ID: {subtask['id']}")
        print(f"   標題: {subtask['title']}")
        print(f"   狀態: {subtask['status']}")

        # 顯示進度
        progress = self.subtask_manager.calculate_progress()
        print(f"   當前進度: {progress}%")

    def subtask_delete(self, args):
        """刪除子任務"""

        success = self.subtask_manager.delete_subtask(args.id)

        if success:
            print(f"✅ 子任務已刪除: {args.id}")

            # 顯示進度
            progress = self.subtask_manager.calculate_progress()
            print(f"   當前進度: {progress}%")
        else:
            print(f"❌ 子任務不存在: {args.id}")

    def subtask_list(self, args):
        """列出所有子任務"""

        subtasks = self.subtask_manager.list_subtasks(parent_id=args.parent)

        if not subtasks:
            print("❌ 沒有子任務")
            return

        print("📋 子任務列表:")
        for i, st in enumerate(subtasks, 1):
            status_icon = {
                'pending': '⏸️',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(st['status'], '❓')

            required_mark = " (必選)" if st.get('required') else " (可選)"

            print(f"   {i}. {status_icon} [{st['status']}] {st['title']}{required_mark}")
            print(f"      ID: {st['id']}")
            if st.get('description'):
                print(f"      描述: {st['description']}")

        # 顯示進度
        progress = self.subtask_manager.calculate_progress()
        print()
        print(f"✅ 當前進度: {progress}%")

    def subtask_show(self, args):
        """顯示子任務詳情"""

        subtask = self.subtask_manager.get_subtask(args.id)

        if not subtask:
            print(f"❌ 子任務不存在: {args.id}")
            return

        print("📄 子任務詳情:")
        print(f"   ID: {subtask['id']}")
        print(f"   標題: {subtask['title']}")
        print(f"   描述: {subtask.get('description', 'N/A')}")
        print(f"   狀態: {subtask['status']}")
        print(f"   必選: {'是' if subtask.get('required', True) else '否'}")
        print(f"   權重: {subtask.get('weight', 1.0)}")
        if subtask.get('parent_id'):
            print(f"   父任務: {subtask['parent_id']}")
        if subtask.get('start_time'):
            print(f"   開始時間: {subtask['start_time']}")
        if subtask.get('completed_time'):
            print(f"   完成時間: {subtask['completed_time']}")


# ========== 主程序入口 ==========

if __name__ == '__main__':
    cli = UniversalMemoryCLI()
    cli.run()
