#!/usr/bin/env python3
"""
Tidbyt Status API Server
Exposes Scout's current status as JSON for Tidbyt display
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path


def get_openclaw_status():
    """Get current OpenClaw agent status by checking session activity"""
    workspace = Path.home() / ".openclaw"
    sessions_dir = workspace / "agents" / "main" / "sessions"
    
    status = {
        "agent": "Scout",
        "emoji": "🦅",
        "status": "idle",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": 0,
        "last_activity": None,
        "recent_activity": "Zzz... sleeping"
    }
    
    try:
        # Check for recent session activity
        if sessions_dir.exists():
            jsonl_files = list(sessions_dir.glob("*.jsonl"))
            if jsonl_files:
                # Find all sessions active in last 5 minutes
                now = datetime.now().timestamp()
                active_sessions = []
                main_session_active = False
                
                for f in jsonl_files:
                    mtime = f.stat().st_mtime
                    age_seconds = now - mtime
                    
                    if age_seconds < 300:  # 5 minutes
                        active_sessions.append(f)
                        # Check if this is main session (not a subagent)
                        if "subagent" not in f.name:
                            main_session_active = True
                
                # Determine status based on active sessions
                if len(active_sessions) > 0:
                    # Get most recent activity
                    latest = max(jsonl_files, key=lambda p: p.stat().st_mtime)
                    mtime = latest.stat().st_mtime
                    status["last_activity"] = datetime.fromtimestamp(mtime).isoformat()
                    
                    # Count sub-agent tasks
                    subagent_count = sum(1 for f in active_sessions if "subagent" in f.name)
                    status["active_tasks"] = subagent_count
                    
                    # Determine specific status
                    if subagent_count > 0:
                        status["status"] = "working"
                        if subagent_count == 1:
                            status["recent_activity"] = "Working on a task..."
                        else:
                            status["recent_activity"] = f"Working on {subagent_count} tasks..."
                    elif main_session_active:
                        status["status"] = "chatting"
                        status["recent_activity"] = "Chatting with Ryan..."
                    else:
                        status["status"] = "thinking"
                        status["recent_activity"] = "Thinking..."
                else:
                    # Idle - show how long ago
                    latest = max(jsonl_files, key=lambda p: p.stat().st_mtime)
                    mtime = latest.stat().st_mtime
                    age_seconds = now - mtime
                    status["last_activity"] = datetime.fromtimestamp(mtime).isoformat()
                    
                    if age_seconds < 3600:  # Less than 1 hour
                        mins = int(age_seconds / 60)
                        status["recent_activity"] = f"Idle ({mins}m ago)"
                    else:
                        status["recent_activity"] = "Zzz... sleeping"
                        status["status"] = "sleeping"
    except Exception as e:
        status["recent_activity"] = f"Error: {str(e)}"
    
    return status


class StatusHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default request logging"""
        pass
    
    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            status = get_openclaw_status()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            self.wfile.write(json.dumps(status, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()


def main():
    port = int(os.environ.get("PORT", 8765))
    
    server = HTTPServer(("0.0.0.0", port), StatusHandler)
    
    print(f"🦅 Scout Status API")
    print(f"Listening on http://0.0.0.0:{port}/status")
    print(f"Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
