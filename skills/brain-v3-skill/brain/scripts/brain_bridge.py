#!/usr/bin/env python3
"""
ClawBrain Bridge for ClawdBot Hooks

This script acts as a bridge between the JavaScript ClawdBot hook and the
Python ClawBrain module. It receives JSON commands via stdin and outputs
JSON results via stdout.

Usage (from JavaScript):
    echo '{"command": "health_check", "args": {}, "config": {...}}' | python3 brain_bridge.py

Commands:
    - health_check: Check brain connection status
    - refresh_on_startup: Refresh brain memory on startup
    - save_session: Save session to brain memory
    - recall: Search memories
    - remember: Store a memory
"""

import sys
import json
from pathlib import Path

# Add parent directory to path to import clawbrain
# Works regardless of where the skill is installed
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

try:
    from clawbrain import Brain
    BRAIN_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    BRAIN_AVAILABLE = False
    IMPORT_ERROR = str(e)


def main():
    """Main entry point for the bridge."""
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input", "success": False}))
        return

    command = input_data.get("command", "")
    args = input_data.get("args", {})
    config = input_data.get("config", {})

    if not BRAIN_AVAILABLE:
        print(json.dumps({
            "error": f"Brain not available: {IMPORT_ERROR}",
            "success": False
        }))
        return

    try:
        brain = Brain()

        if command == "health_check":
            health = brain.health_check()
            print(json.dumps({
                "healthy": health.get("sqlite", False),
                "storage": "sqlite",
                "details": health,
                "success": True
            }))

        elif command == "refresh_on_startup":
            agent_id = args.get("agent_id", "main")
            result = brain.refresh_on_startup(agent_id=agent_id)
            print(json.dumps(result))

        elif command == "save_session":
            agent_id = args.get("agent_id", "main")
            summary = args.get("session_summary", "Session ended")
            session_id = args.get("session_id")
            result = brain.save_session_to_memory(
                agent_id=agent_id,
                session_summary=summary,
                session_id=session_id
            )
            print(json.dumps(result))

        elif command == "recall":
            query = args.get("query", "")
            agent_id = args.get("agent_id", "main")
            limit = args.get("limit", 5)
            memories = brain.recall(query=query, agent_id=agent_id, limit=limit)
            print(json.dumps({
                "memories": [
                    m.__dict__ if hasattr(m, "__dict__") else m
                    for m in memories
                ],
                "success": True
            }))

        elif command == "remember":
            result = brain.remember(
                content=args.get("content", ""),
                memory_type=args.get("memory_type", "conversation"),
                agent_id=args.get("agent_id", "main"),
                importance=args.get("importance", 5),
                tags=args.get("tags")
            )
            print(json.dumps({
                "memory_id": result.id if result else None,
                "success": bool(result)
            }))

        elif command == "get_startup_context":
            agent_id = args.get("agent_id", "main")
            result = brain.get_startup_context(agent_id=agent_id)
            print(json.dumps(result))

        elif command == "sync":
            agent_id = args.get("agent_id", "main")
            result = brain.sync_memories(agent_id=agent_id)
            print(json.dumps(result))

        else:
            print(json.dumps({
                "error": f"Unknown command: {command}",
                "success": False
            }))

    except Exception as e:
        print(json.dumps({"error": str(e), "success": False}))


if __name__ == "__main__":
    main()
