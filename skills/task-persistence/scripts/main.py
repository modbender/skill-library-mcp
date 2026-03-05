#!/usr/bin/env python3
"""
Main entry point for task-persistence skill.
Supports full monitoring mode, task-only mode, and snapshot-only mode.
Also handles gateway restart detection and notification.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from task_queue import TaskQueueManager
from task_persistence import TaskPersistenceManager
from session_snapshot import SessionSnapshotManager
from gateway_monitor import GatewayMonitor


def get_workspace():
    return os.getenv("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def check_restart_and_report(workspace: str) -> dict:
    """
    Check if gateway just restarted and return a status report.
    This is the primary function called on session start or heartbeat.
    """
    manager = TaskPersistenceManager(workspace)
    queue = TaskQueueManager(workspace)
    snapshot_mgr = SessionSnapshotManager(workspace)

    report = {
        "timestamp": datetime.now().isoformat(),
        "restart_detected": False,
        "active_tasks": [],
        "recovered_tasks": [],
        "latest_snapshot": None,
        "message": ""
    }

    # Recover crashed tasks
    recovered = queue.recover_from_crash()
    if recovered:
        report["recovered_tasks"] = recovered

    # Get active tasks
    active_tasks = manager.get_active_tasks()
    report["active_tasks"] = active_tasks

    # Check latest snapshot
    latest = snapshot_mgr.get_latest_snapshot("main")
    if latest:
        report["latest_snapshot"] = {
            "timestamp": latest.get("timestamp"),
            "model": latest.get("model"),
            "active_tasks_count": len(latest.get("active_tasks", []))
        }

    # Build human-readable message
    parts = []
    if recovered:
        parts.append(f"🔄 恢复了 {len(recovered)} 个中断任务")
    if active_tasks:
        parts.append(f"📋 {len(active_tasks)} 个活跃任务")
    if latest:
        parts.append(f"💾 最近快照: {latest.get('timestamp', '')[:19]}")
    if not parts:
        parts.append("✅ 系统状态正常，无待恢复任务")

    report["message"] = " | ".join(parts)
    return report


def main():
    parser = argparse.ArgumentParser(description="Task Persistence Main Controller")
    parser.add_argument(
        "--mode",
        choices=["full", "tasks-only", "snapshot-only", "check-restart", "status"],
        default="check-restart",
        help="Operation mode"
    )
    parser.add_argument("--workspace", help="Workspace path", default=None)
    parser.add_argument("--session-id", help="Session ID for snapshots", default="main")
    parser.add_argument("--session-data", help="Session data JSON file for snapshot")

    args = parser.parse_args()
    workspace = args.workspace or get_workspace()

    if args.mode == "check-restart":
        report = check_restart_and_report(workspace)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\n{report['message']}")

    elif args.mode == "status":
        queue = TaskQueueManager(workspace)
        manager = TaskPersistenceManager(workspace)
        status = {
            "queue": queue.get_queue_status(),
            "active_tasks": manager.get_active_tasks(),
            "suggestions": manager.get_recovery_suggestions()
        }
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.mode == "snapshot-only":
        snapshot_mgr = SessionSnapshotManager(workspace)
        if args.session_data:
            with open(args.session_data, 'r') as f:
                session_data = json.load(f)
            path = snapshot_mgr.create_snapshot(session_data, args.session_id)
            print(f"Snapshot saved: {path}")
        else:
            snapshot = snapshot_mgr.get_latest_snapshot(args.session_id)
            print(json.dumps(snapshot or {}, indent=2, ensure_ascii=False))

    elif args.mode == "tasks-only":
        queue = TaskQueueManager(workspace)
        recovered = queue.recover_from_crash()
        status = queue.get_queue_status()
        print(json.dumps({"recovered": recovered, "status": status}, indent=2, ensure_ascii=False))

    elif args.mode == "full":
        # Full mode: check restart + print report
        report = check_restart_and_report(workspace)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\n📊 Task Persistence Report")
        print(f"   {report['message']}")

        # Start background gateway monitor
        monitor = GatewayMonitor(workspace)
        print("\n👁️  Starting gateway monitor (Ctrl+C to stop)...")
        try:
            monitor.start_monitoring()
            import signal
            signal.pause()
        except KeyboardInterrupt:
            monitor.stop_monitoring()


if __name__ == "__main__":
    main()
