#!/usr/bin/env python3
"""
Session Snapshot Manager - Part of task-persistence skill

Handles automatic session state snapshotting and restoration
using OpenClaw's memory-core plugin and vector search capabilities.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class SessionSnapshotManager:
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.snapshot_dir = self.workspace / "memory" / "session_snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id = None
        
    def create_snapshot(self, session_data: Dict[str, Any], 
                       session_id: str, 
                       include_context: bool = True) -> str:
        """Create a session snapshot with current state and context."""
        snapshot = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "model": session_data.get("model", "unknown"),
            "tokens": {
                "input": session_data.get("input_tokens", 0),
                "output": session_data.get("output_tokens", 0),
                "context_usage": session_data.get("context_usage", 0)
            },
            "active_tasks": session_data.get("active_tasks", []),
            "conversation_history": session_data.get("history", []) if include_context else [],
            "system_state": session_data.get("system_state", {}),
            "pending_operations": session_data.get("pending_ops", [])
        }
        
        # Save snapshot
        snapshot_file = self.snapshot_dir / f"{session_id}_{int(time.time())}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
        # Also save latest snapshot for quick recovery
        latest_file = self.snapshot_dir / f"{session_id}_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
            
        return str(snapshot_file)
    
    def get_latest_snapshot(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest snapshot for a session."""
        latest_file = self.snapshot_dir / f"{session_id}_latest.json"
        if latest_file.exists():
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def restore_session_state(self, session_id: str) -> Dict[str, Any]:
        """Restore session state from latest snapshot."""
        snapshot = self.get_latest_snapshot(session_id)
        if not snapshot:
            return {}
            
        restored_state = {
            "session_id": snapshot["session_id"],
            "restored_at": datetime.now().isoformat(),
            "model": snapshot["model"],
            "tokens": snapshot["tokens"],
            "active_tasks": snapshot["active_tasks"],
            "pending_operations": snapshot["pending_operations"],
            "system_state": snapshot["system_state"]
        }
        
        return restored_state
    
    def cleanup_old_snapshots(self, max_age_hours: int = 24):
        """Clean up snapshots older than specified hours."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        for snapshot_file in self.snapshot_dir.glob("*.json"):
            if snapshot_file.stat().st_mtime < cutoff_time:
                snapshot_file.unlink()
    
    def list_active_sessions(self) -> List[str]:
        """List all sessions with active snapshots."""
        sessions = set()
        for snapshot_file in self.snapshot_dir.glob("*_latest.json"):
            session_name = snapshot_file.stem.replace("_latest", "")
            sessions.add(session_name)
        return sorted(list(sessions))
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of a session."""
        snapshot = self.get_latest_snapshot(session_id)
        if not snapshot:
            return {"status": "no_snapshot", "session_id": session_id}
            
        return {
            "status": "active",
            "session_id": session_id,
            "last_updated": snapshot["timestamp"],
            "model": snapshot["model"],
            "token_usage": snapshot["tokens"],
            "active_tasks_count": len(snapshot["active_tasks"]),
            "pending_operations_count": len(snapshot["pending_operations"])
        }

def main():
    """CLI entry point for session snapshot management."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Session Snapshot Manager")
    parser.add_argument("--workspace", required=True, help="OpenClaw workspace path")
    parser.add_argument("--action", choices=["create", "restore", "status", "list", "cleanup"], 
                       required=True, help="Action to perform")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--data-file", help="JSON file with session data for create action")
    
    args = parser.parse_args()
    
    manager = SessionSnapshotManager(args.workspace)
    
    if args.action == "create":
        if not args.session_id or not args.data_file:
            print("Error: --session-id and --data-file required for create action")
            sys.exit(1)
        with open(args.data_file, 'r') as f:
            session_data = json.load(f)
        snapshot_file = manager.create_snapshot(session_data, args.session_id)
        print(f"Snapshot created: {snapshot_file}")
        
    elif args.action == "restore":
        if not args.session_id:
            print("Error: --session-id required for restore action")
            sys.exit(1)
        restored_state = manager.restore_session_state(args.session_id)
        print(json.dumps(restored_state, indent=2))
        
    elif args.action == "status":
        if not args.session_id:
            print("Error: --session-id required for status action")
            sys.exit(1)
        status = manager.get_session_status(args.session_id)
        print(json.dumps(status, indent=2))
        
    elif args.action == "list":
        sessions = manager.list_active_sessions()
        print(json.dumps({"active_sessions": sessions}, indent=2))
        
    elif args.action == "cleanup":
        manager.cleanup_old_snapshots()
        print("Old snapshots cleaned up")

if __name__ == "__main__":
    main()